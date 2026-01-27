from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class VendorPriceInfo(BaseModel):
    """Vendor pricing information for a component."""

    vendor_id: int
    vendor_name: str
    price: Decimal
    currency: str = "USD"
    shipping_cost: Decimal | None = None
    product_url: str | None = None
    in_stock: bool = True
    price_fetched_at: datetime


class CategoryInfo(BaseModel):
    """Category information."""

    id: int
    name: str
    slug: str
    icon: str | None = None


class ComponentBase(BaseModel):
    """Base component fields."""

    name: str
    slug: str
    description: str | None = None
    specifications: dict[str, Any] = Field(default_factory=dict)
    is_default_for_so101: bool = False
    quantity_per_arm: int = 1
    arm_type: str | None = None
    image_url: str | None = None


class ComponentCreate(ComponentBase):
    """Schema for creating a component."""

    category_id: int


class ComponentResponse(ComponentBase):
    """Full component response with prices and category."""

    id: int
    category: CategoryInfo
    prices: list[VendorPriceInfo] = []
    lowest_price: Decimal | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComponentListResponse(BaseModel):
    """Paginated component list response."""

    items: list[ComponentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ComponentFilter(BaseModel):
    """Filters for component search."""

    category_id: int | None = None
    category_slug: str | None = None
    search: str | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    is_default_for_so101: bool | None = None
    arm_type: str | None = None
    in_stock_only: bool = False
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
