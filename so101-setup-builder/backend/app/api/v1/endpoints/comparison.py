from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.comparison import (
    ComparisonRequest,
    ComparisonResponse,
    ComparisonItem,
    SpecificationComparison,
)
from app.db.database import get_db
from app.db.models import Component, ComponentPrice

router = APIRouter()

# Mapping of specification keys to display names
SPEC_DISPLAY_NAMES = {
    "model": "Model",
    "gear_ratio": "Gear Ratio",
    "voltage": "Operating Voltage",
    "torque": "Torque",
    "speed": "Speed",
    "weight": "Weight",
    "dimensions": "Dimensions",
    "resolution": "Resolution",
    "frame_rate": "Frame Rate",
    "interface": "Interface",
    "power_consumption": "Power Consumption",
    "operating_temp": "Operating Temperature",
    "warranty": "Warranty",
}


@router.post("/compare", response_model=ComparisonResponse)
async def compare_components(
    request: ComparisonRequest,
    db: AsyncSession = Depends(get_db),
):
    """Compare 2-5 components side by side."""
    if len(request.component_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 components required for comparison",
        )

    if len(request.component_ids) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 components can be compared at once",
        )

    # Fetch all components
    query = select(Component).options(
        selectinload(Component.category),
        selectinload(Component.prices).selectinload(ComponentPrice.vendor),
    ).where(Component.id.in_(request.component_ids))

    result = await db.execute(query)
    components = result.scalars().unique().all()

    if len(components) != len(request.component_ids):
        found_ids = {c.id for c in components}
        missing = set(request.component_ids) - found_ids
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Components not found: {missing}",
        )

    # Build comparison items and collect all spec keys
    comparison_items = []
    all_specs = {}
    price_comparison = {}

    for component in components:
        # Get lowest price
        lowest_price = None
        if component.prices:
            lowest_price = min(p.price for p in component.prices)

        comparison_items.append(
            ComparisonItem(
                id=component.id,
                name=component.name,
                slug=component.slug,
                category_name=component.category.name if component.category else "Unknown",
                image_url=component.image_url,
                specifications=component.specifications or {},
                lowest_price=lowest_price,
                is_default_for_so101=component.is_default_for_so101,
                arm_type=component.arm_type,
            )
        )

        price_comparison[component.id] = lowest_price

        # Collect all specification keys
        for key, value in (component.specifications or {}).items():
            if key not in all_specs:
                all_specs[key] = {}
            all_specs[key][component.id] = value

    # Build specification comparisons
    specifications = []
    common_specs = []
    differing_specs = []

    for key, values in all_specs.items():
        display_name = SPEC_DISPLAY_NAMES.get(key, key.replace("_", " ").title())

        spec_comparison = SpecificationComparison(
            key=key,
            display_name=display_name,
            values=values,
            unit=None,  # Could add unit detection
        )
        specifications.append(spec_comparison)

        # Check if values are common or differ
        unique_values = set(str(v) for v in values.values())
        if len(unique_values) == 1 and len(values) == len(components):
            common_specs.append(key)
        else:
            differing_specs.append(key)

    # Determine best value and recommended
    best_value_id = None
    recommended_id = None

    # Find recommended (default SO-101 component)
    for item in comparison_items:
        if item.is_default_for_so101:
            recommended_id = item.id
            break

    # Find best value (lowest price with good specs)
    priced_items = [
        (item.id, item.lowest_price)
        for item in comparison_items
        if item.lowest_price is not None
    ]
    if priced_items:
        best_value_id = min(priced_items, key=lambda x: x[1])[0]

    return ComparisonResponse(
        components=comparison_items,
        specifications=specifications,
        price_comparison=price_comparison,
        best_value_id=best_value_id,
        recommended_id=recommended_id,
        common_specs=common_specs,
        differing_specs=differing_specs,
    )
