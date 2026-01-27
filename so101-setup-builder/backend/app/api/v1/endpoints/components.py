from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.component import (
    ComponentResponse,
    ComponentListResponse,
    ComponentCreate,
    CategoryInfo,
    VendorPriceInfo,
)
from app.db.database import get_db
from app.db.models import Component, Category, ComponentPrice, Vendor

router = APIRouter()


def component_to_response(component: Component) -> ComponentResponse:
    """Convert a Component model to response schema."""
    prices = []
    lowest = None

    for price in component.prices:
        prices.append(
            VendorPriceInfo(
                vendor_id=price.vendor_id,
                vendor_name=price.vendor.name if price.vendor else "Unknown",
                price=price.price,
                currency=price.currency,
                shipping_cost=price.shipping_cost,
                product_url=price.product_url,
                in_stock=price.in_stock,
                price_fetched_at=price.price_fetched_at,
            )
        )
        if lowest is None or price.price < lowest:
            lowest = price.price

    return ComponentResponse(
        id=component.id,
        name=component.name,
        slug=component.slug,
        description=component.description,
        specifications=component.specifications or {},
        is_default_for_so101=component.is_default_for_so101,
        quantity_per_arm=component.quantity_per_arm,
        arm_type=component.arm_type,
        image_url=component.image_url,
        category=CategoryInfo(
            id=component.category.id,
            name=component.category.name,
            slug=component.category.slug,
            icon=component.category.icon,
        ),
        prices=prices,
        lowest_price=lowest,
        created_at=component.created_at,
        updated_at=component.updated_at,
    )


@router.get("", response_model=ComponentListResponse)
async def list_components(
    category_id: Optional[int] = None,
    category_slug: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    is_default_for_so101: Optional[bool] = None,
    arm_type: Optional[str] = None,
    in_stock_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List components with filters and pagination."""
    query = select(Component).options(
        selectinload(Component.category),
        selectinload(Component.prices).selectinload(ComponentPrice.vendor),
    )

    # Apply filters
    if category_id:
        query = query.where(Component.category_id == category_id)

    if category_slug:
        query = query.join(Category).where(Category.slug == category_slug)

    if search:
        search_filter = or_(
            Component.name.ilike(f"%{search}%"),
            Component.description.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    if is_default_for_so101 is not None:
        query = query.where(Component.is_default_for_so101 == is_default_for_so101)

    if arm_type:
        query = query.where(
            or_(Component.arm_type == arm_type, Component.arm_type == "both")
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    components = result.scalars().unique().all()

    # Filter by price if needed (after fetching to include price data)
    items = []
    for component in components:
        response = component_to_response(component)

        # Price filtering
        if min_price is not None and (
            response.lowest_price is None or response.lowest_price < min_price
        ):
            continue
        if max_price is not None and (
            response.lowest_price is None or response.lowest_price > max_price
        ):
            continue

        # Stock filtering
        if in_stock_only and response.prices:
            if not any(p.in_stock for p in response.prices):
                continue

        items.append(response)

    total_pages = (total + page_size - 1) // page_size

    return ComponentListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/so101-defaults")
async def get_so101_defaults(
    arm_type: str = Query("single", regex="^(single|dual)$"),
    db: AsyncSession = Depends(get_db),
):
    """Get default components for SO-101 build."""
    query = select(Component).options(
        selectinload(Component.category),
        selectinload(Component.prices).selectinload(ComponentPrice.vendor),
    ).where(Component.is_default_for_so101 == True)

    if arm_type == "single":
        query = query.where(
            or_(Component.arm_type == "follower", Component.arm_type == "both")
        )

    result = await db.execute(query)
    components = result.scalars().unique().all()

    items = [component_to_response(c) for c in components]

    # Calculate totals
    total_cost = Decimal("0")
    for item in items:
        if item.lowest_price:
            total_cost += item.lowest_price * item.quantity_per_arm
            if arm_type == "dual" and item.arm_type in ("leader", "follower"):
                total_cost += item.lowest_price * item.quantity_per_arm

    return {
        "arm_type": arm_type,
        "components": items,
        "total_components": len(items),
        "estimated_cost": float(total_cost),
    }


@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """List all component categories."""
    result = await db.execute(select(Category).order_by(Category.sort_order))
    categories = result.scalars().all()

    return [
        CategoryInfo(
            id=c.id,
            name=c.name,
            slug=c.slug,
            icon=c.icon,
        )
        for c in categories
    ]


@router.get("/{component_id}", response_model=ComponentResponse)
async def get_component(
    component_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get component details including prices and compatibility."""
    query = select(Component).options(
        selectinload(Component.category),
        selectinload(Component.prices).selectinload(ComponentPrice.vendor),
    ).where(Component.id == component_id)

    result = await db.execute(query)
    component = result.scalar_one_or_none()

    if not component:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Component not found",
        )

    return component_to_response(component)


@router.post("", response_model=ComponentResponse, status_code=status.HTTP_201_CREATED)
async def create_component(
    component: ComponentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new component (admin only in production)."""
    # Check category exists
    cat_result = await db.execute(
        select(Category).where(Category.id == component.category_id)
    )
    if not cat_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found",
        )

    db_component = Component(
        name=component.name,
        slug=component.slug,
        category_id=component.category_id,
        description=component.description,
        specifications=component.specifications,
        is_default_for_so101=component.is_default_for_so101,
        quantity_per_arm=component.quantity_per_arm,
        arm_type=component.arm_type,
        image_url=component.image_url,
    )
    db.add(db_component)
    await db.commit()
    await db.refresh(db_component)

    # Reload with relationships
    query = select(Component).options(
        selectinload(Component.category),
        selectinload(Component.prices),
    ).where(Component.id == db_component.id)

    result = await db.execute(query)
    component = result.scalar_one()

    return component_to_response(component)
