from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, DateTime, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.component import Component
    from app.db.models.vendor import Vendor


class ComponentPrice(Base):
    """Vendor pricing with timestamps for price tracking."""

    __tablename__ = "component_prices"

    id: Mapped[int] = mapped_column(primary_key=True)
    component_id: Mapped[int] = mapped_column(ForeignKey("components.id"), nullable=False)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id"), nullable=False)

    # Pricing
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    original_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # Before discount
    shipping_cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # Product link
    product_url: Mapped[str | None] = mapped_column(String(1000))
    sku: Mapped[str | None] = mapped_column(String(100))

    # Availability
    in_stock: Mapped[bool] = mapped_column(default=True)
    stock_quantity: Mapped[int | None] = mapped_column()

    # Timestamps
    price_fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    component: Mapped["Component"] = relationship(back_populates="prices")
    vendor: Mapped["Vendor"] = relationship(back_populates="prices")

    __table_args__ = (
        Index("ix_component_prices_component_vendor", "component_id", "vendor_id"),
        Index("ix_component_prices_price", "price"),
    )

    def __repr__(self) -> str:
        return f"<ComponentPrice {self.component_id} @ {self.vendor_id}: ${self.price}>"
