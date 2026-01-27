from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import String, Text, Boolean, Integer, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.category import Category
    from app.db.models.component_price import ComponentPrice


class Component(Base):
    """All components with JSONB specifications."""

    __tablename__ = "components"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))

    # Specifications stored as JSONB
    # Example: {"model": "sts3215", "gear_ratio": "1/345", "voltage": "12V", ...}
    specifications: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    # SO-101 specific fields
    is_default_for_so101: Mapped[bool] = mapped_column(Boolean, default=False)
    quantity_per_arm: Mapped[int] = mapped_column(Integer, default=1)
    arm_type: Mapped[str | None] = mapped_column(
        String(20)
    )  # 'leader', 'follower', 'both', None

    # Search
    search_vector: Mapped[Any | None] = mapped_column(TSVECTOR)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    category: Mapped["Category"] = relationship(back_populates="components")
    prices: Mapped[list["ComponentPrice"]] = relationship(
        back_populates="component", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_components_search_vector", "search_vector", postgresql_using="gin"),
        Index("ix_components_category_id", "category_id"),
        Index("ix_components_is_default", "is_default_for_so101"),
    )

    def __repr__(self) -> str:
        return f"<Component {self.name}>"
