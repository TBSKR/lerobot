from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class ComparisonRequest(BaseModel):
    """Request to compare multiple components."""

    component_ids: list[int] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="List of 2-5 component IDs to compare",
    )


class ComparisonItem(BaseModel):
    """Single component in a comparison."""

    id: int
    name: str
    slug: str
    category_name: str
    image_url: str | None = None
    specifications: dict[str, Any]
    lowest_price: Decimal | None = None
    is_default_for_so101: bool
    arm_type: str | None = None


class SpecificationComparison(BaseModel):
    """Comparison of a single specification across components."""

    key: str
    display_name: str
    values: dict[int, Any]  # component_id -> value
    unit: str | None = None


class ComparisonResponse(BaseModel):
    """Side-by-side comparison of components."""

    components: list[ComparisonItem]
    specifications: list[SpecificationComparison]
    price_comparison: dict[int, Decimal | None]  # component_id -> lowest price

    # Highlights
    best_value_id: int | None = None  # Component with best price/feature ratio
    recommended_id: int | None = None  # Default SO-101 component if present

    # Common and differing specs
    common_specs: list[str] = []
    differing_specs: list[str] = []
