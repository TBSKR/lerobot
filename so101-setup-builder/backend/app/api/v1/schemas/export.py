from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class ExportFormat(str, Enum):
    PDF = "pdf"
    JSON = "json"
    CSV = "csv"


class ExportRequest(BaseModel):
    """Request to export setup data."""

    setup_id: UUID
    format: ExportFormat = ExportFormat.PDF
    include_prices: bool = True
    include_recommendations: bool = True
    include_alternatives: bool = False


class ExportResponse(BaseModel):
    """Response with export download info."""

    setup_id: UUID
    format: ExportFormat
    filename: str
    download_url: str | None = None
    content: str | None = None  # For JSON exports
    file_size: int | None = None


class ShoppingListItem(BaseModel):
    """Single item in a shopping list."""

    component_name: str
    quantity: int
    vendor: str
    price: float
    currency: str = "USD"
    product_url: str | None = None
    notes: str | None = None


class ShoppingListResponse(BaseModel):
    """Shopping list with vendor links."""

    setup_id: UUID
    items: list[ShoppingListItem]
    total_items: int
    total_cost: float
    currency: str = "USD"

    # Grouped by vendor
    by_vendor: dict[str, list[ShoppingListItem]] = {}
