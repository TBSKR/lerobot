import json
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.export import (
    ExportFormat,
    ExportRequest,
    ExportResponse,
    ShoppingListItem,
    ShoppingListResponse,
)
from app.db.database import get_db
from app.db.models import Setup, SetupComponent, Component, ComponentPrice
from app.services.export_service import ExportService

router = APIRouter()


@router.post("/pdf")
async def export_pdf(
    request: ExportRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate PDF export of setup."""
    setup = await get_setup_with_components(request.setup_id, db)

    if not setup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setup not found",
        )

    export_service = ExportService()

    try:
        pdf_content = await export_service.generate_pdf(
            setup=setup,
            include_prices=request.include_prices,
            include_recommendations=request.include_recommendations,
            include_alternatives=request.include_alternatives,
        )

        filename = f"so101-setup-{setup.id}-{datetime.utcnow().strftime('%Y%m%d')}.pdf"

        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}",
        )


@router.post("/json", response_model=ExportResponse)
async def export_json(
    request: ExportRequest,
    db: AsyncSession = Depends(get_db),
):
    """Export setup as JSON (LeRobot config format compatible)."""
    setup = await get_setup_with_components(request.setup_id, db)

    if not setup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setup not found",
        )

    # Build LeRobot-compatible config
    config = {
        "version": "1.0",
        "created_at": datetime.utcnow().isoformat(),
        "setup_id": str(setup.id),
        "profile": setup.wizard_profile,
        "arm_type": setup.arm_type,
        "robot_type": f"so101_{setup.arm_type}",
        "components": [],
        "recommendations": setup.recommendations,
    }

    # Add components if present
    for sc in setup.components:
        comp_query = select(Component).options(
            selectinload(Component.category),
            selectinload(Component.prices).selectinload(ComponentPrice.vendor),
        ).where(Component.id == sc.component_id)

        comp_result = await db.execute(comp_query)
        component = comp_result.scalar_one_or_none()

        if component:
            comp_data = {
                "id": component.id,
                "name": component.name,
                "category": component.category.name if component.category else None,
                "quantity": sc.quantity,
                "specifications": component.specifications,
            }

            if request.include_prices and component.prices:
                best_price = min(component.prices, key=lambda p: p.price)
                comp_data["price"] = {
                    "amount": float(best_price.price),
                    "currency": best_price.currency,
                    "vendor": best_price.vendor.name if best_price.vendor else None,
                    "url": best_price.product_url,
                }

            config["components"].append(comp_data)

    content = json.dumps(config, indent=2, default=str)
    filename = f"so101-setup-{setup.id}.json"

    return ExportResponse(
        setup_id=setup.id,
        format=ExportFormat.JSON,
        filename=filename,
        content=content,
        file_size=len(content.encode()),
    )


@router.post("/shopping-list", response_model=ShoppingListResponse)
async def export_shopping_list(
    setup_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Generate shopping list with vendor links."""
    setup = await get_setup_with_components(setup_id, db)

    if not setup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setup not found",
        )

    items = []
    by_vendor = {}
    total_cost = 0.0

    # Process setup components
    for sc in setup.components:
        comp_query = select(Component).options(
            selectinload(Component.prices).selectinload(ComponentPrice.vendor),
        ).where(Component.id == sc.component_id)

        comp_result = await db.execute(comp_query)
        component = comp_result.scalar_one_or_none()

        if not component:
            continue

        # Find best price
        best_price = None
        if component.prices:
            best_price = min(component.prices, key=lambda p: p.price)

        vendor_name = best_price.vendor.name if best_price and best_price.vendor else "Unknown"
        price = float(best_price.price) if best_price else 0.0

        item = ShoppingListItem(
            component_name=component.name,
            quantity=sc.quantity,
            vendor=vendor_name,
            price=price * sc.quantity,
            currency="USD",
            product_url=best_price.product_url if best_price else None,
            notes=sc.notes,
        )

        items.append(item)
        total_cost += item.price

        # Group by vendor
        if vendor_name not in by_vendor:
            by_vendor[vendor_name] = []
        by_vendor[vendor_name].append(item)

    # If no explicit components, use recommendations
    if not items and setup.recommendations:
        for rec in setup.recommendations.get("components", []):
            item = ShoppingListItem(
                component_name=rec.get("component_name", "Unknown"),
                quantity=rec.get("quantity", 1),
                vendor="TBD",
                price=0.0,
                currency="USD",
                notes=rec.get("reason"),
            )
            items.append(item)

    return ShoppingListResponse(
        setup_id=setup_id,
        items=items,
        total_items=sum(item.quantity for item in items),
        total_cost=total_cost,
        currency="USD",
        by_vendor=by_vendor,
    )


async def get_setup_with_components(
    setup_id: UUID,
    db: AsyncSession,
) -> Setup | None:
    """Helper to fetch setup with components."""
    query = select(Setup).options(
        selectinload(Setup.components),
    ).where(Setup.id == setup_id)

    result = await db.execute(query)
    return result.scalar_one_or_none()
