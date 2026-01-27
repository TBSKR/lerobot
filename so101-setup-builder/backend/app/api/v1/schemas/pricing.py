from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class VendorPrice(BaseModel):
    """Single vendor price entry."""

    vendor_id: int
    vendor_name: str
    vendor_slug: str
    price: Decimal
    currency: str = "USD"
    original_price: Decimal | None = None
    shipping_cost: Decimal | None = None
    product_url: str | None = None
    in_stock: bool = True
    stock_quantity: int | None = None
    price_fetched_at: datetime


class PriceResponse(BaseModel):
    """All vendor prices for a component."""

    component_id: int
    component_name: str
    prices: list[VendorPrice]
    lowest_price: Decimal | None = None
    highest_price: Decimal | None = None
    average_price: Decimal | None = None


class PricingSearchRequest(BaseModel):
    """Request for web-based price search."""

    component_name: str
    vendor_preference: str | None = None  # aliexpress, amazon, etc.
    include_shipping: bool = True


class PricingSearchResult(BaseModel):
    """Result from web price search."""

    source: str
    title: str
    price: Decimal
    currency: str = "USD"
    url: str
    seller: str | None = None
    shipping: str | None = None
    fetched_at: datetime


class ComponentCostItem(BaseModel):
    """Cost breakdown for a single component in a setup."""

    component_id: int
    component_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    vendor_name: str | None = None
    product_url: str | None = None


class SetupPricingResponse(BaseModel):
    """Complete cost breakdown for a setup."""

    setup_id: UUID
    components: list[ComponentCostItem]
    subtotal: Decimal
    estimated_shipping: Decimal | None = None
    total: Decimal
    currency: str = "USD"
    calculated_at: datetime

    # Breakdown by category
    cost_by_category: dict[str, Decimal] = {}

    # Vendor summary
    vendors_used: list[str] = []
