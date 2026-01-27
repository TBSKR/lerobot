from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.pricing import (
    PriceResponse,
    VendorPrice,
    PricingSearchRequest,
    PricingSearchResult,
    SetupPricingResponse,
    ComponentCostItem,
)
from app.db.database import get_db
from app.db.models import Component, ComponentPrice, Setup, SetupComponent
from app.services.pricing_service import PricingService

router = APIRouter()


@router.get("/component/{component_id}", response_model=PriceResponse)
async def get_component_prices(
    component_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all vendor prices for a component."""
    query = select(Component).options(
        selectinload(Component.prices).selectinload(ComponentPrice.vendor),
    ).where(Component.id == component_id)

    result = await db.execute(query)
    component = result.scalar_one_or_none()

    if not component:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Component not found",
        )

    prices = []
    for price in component.prices:
        prices.append(
            VendorPrice(
                vendor_id=price.vendor_id,
                vendor_name=price.vendor.name,
                vendor_slug=price.vendor.slug,
                price=price.price,
                currency=price.currency,
                original_price=price.original_price,
                shipping_cost=price.shipping_cost,
                product_url=price.product_url,
                in_stock=price.in_stock,
                stock_quantity=price.stock_quantity,
                price_fetched_at=price.price_fetched_at,
            )
        )

    # Calculate statistics
    if prices:
        price_values = [p.price for p in prices]
        lowest = min(price_values)
        highest = max(price_values)
        average = sum(price_values) / len(price_values)
    else:
        lowest = highest = average = None

    return PriceResponse(
        component_id=component.id,
        component_name=component.name,
        prices=prices,
        lowest_price=lowest,
        highest_price=highest,
        average_price=Decimal(str(round(average, 2))) if average else None,
    )


@router.post("/search", response_model=list[PricingSearchResult])
async def search_prices(
    request: PricingSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Search for real-time prices using web search."""
    pricing_service = PricingService()

    try:
        results = await pricing_service.search_prices(
            component_name=request.component_name,
            vendor_preference=request.vendor_preference,
            include_shipping=request.include_shipping,
        )
        return results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Price search service unavailable: {str(e)}",
        )


@router.get("/setup/{setup_id}", response_model=SetupPricingResponse)
async def get_setup_pricing(
    setup_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get total cost breakdown for a setup."""
    # Get setup with components
    query = select(Setup).where(Setup.id == setup_id)
    result = await db.execute(query)
    setup = result.scalar_one_or_none()

    if not setup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setup not found",
        )

    # Get setup components with prices
    components_query = select(SetupComponent).where(
        SetupComponent.setup_id == setup_id
    )
    components_result = await db.execute(components_query)
    setup_components = components_result.scalars().all()

    component_items = []
    subtotal = Decimal("0")
    cost_by_category = {}
    vendors_used = set()

    for sc in setup_components:
        # Get component with prices
        comp_query = select(Component).options(
            selectinload(Component.category),
            selectinload(Component.prices).selectinload(ComponentPrice.vendor),
        ).where(Component.id == sc.component_id)

        comp_result = await db.execute(comp_query)
        component = comp_result.scalar_one_or_none()

        if not component:
            continue

        # Find best price (or selected vendor)
        best_price = None
        vendor_name = None
        product_url = None

        for price in component.prices:
            if sc.selected_vendor_id and price.vendor_id == sc.selected_vendor_id:
                best_price = price
                break
            if best_price is None or price.price < best_price.price:
                best_price = price

        if best_price:
            unit_price = best_price.price
            vendor_name = best_price.vendor.name
            product_url = best_price.product_url
            vendors_used.add(vendor_name)
        else:
            unit_price = Decimal("0")

        total_price = unit_price * sc.quantity
        subtotal += total_price

        # Track by category
        cat_name = component.category.name if component.category else "Other"
        cost_by_category[cat_name] = cost_by_category.get(cat_name, Decimal("0")) + total_price

        component_items.append(
            ComponentCostItem(
                component_id=component.id,
                component_name=component.name,
                quantity=sc.quantity,
                unit_price=unit_price,
                total_price=total_price,
                vendor_name=vendor_name,
                product_url=product_url,
            )
        )

    # If no explicit components, use recommendations
    if not component_items and setup.recommendations:
        for rec in setup.recommendations.get("components", []):
            component_items.append(
                ComponentCostItem(
                    component_id=rec.get("component_id", 0),
                    component_name=rec.get("component_name", "Unknown"),
                    quantity=rec.get("quantity", 1),
                    unit_price=Decimal("0"),
                    total_price=Decimal("0"),
                    vendor_name=None,
                    product_url=None,
                )
            )

    return SetupPricingResponse(
        setup_id=setup_id,
        components=component_items,
        subtotal=subtotal,
        estimated_shipping=None,  # Could calculate based on vendors
        total=subtotal,
        currency="USD",
        calculated_at=datetime.utcnow(),
        cost_by_category={k: v for k, v in cost_by_category.items()},
        vendors_used=list(vendors_used),
    )


@router.post("/refresh/{component_id}")
async def refresh_component_prices(
    component_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Trigger a refresh of prices for a component."""
    query = select(Component).where(Component.id == component_id)
    result = await db.execute(query)
    component = result.scalar_one_or_none()

    if not component:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Component not found",
        )

    pricing_service = PricingService()

    try:
        updated_prices = await pricing_service.refresh_prices(component_id, db)
        return {
            "message": "Prices refreshed successfully",
            "component_id": component_id,
            "prices_updated": len(updated_prices),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to refresh prices: {str(e)}",
        )
