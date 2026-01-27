from datetime import datetime
from typing import Any
import uuid

from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Setup(Base):
    """Session-based user setups (UUID, no auth)."""

    __tablename__ = "setups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)

    # Wizard answers stored as JSONB
    # {"experience": "beginner", "budget": 500, "use_case": "learning", ...}
    wizard_profile: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    current_step: Mapped[int] = mapped_column(Integer, default=1)
    wizard_completed: Mapped[bool] = mapped_column(default=False)

    # Setup configuration
    arm_type: Mapped[str] = mapped_column(String(20), default="single")  # single, dual

    # AI recommendations stored as JSONB
    recommendations: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relationships
    components: Mapped[list["SetupComponent"]] = relationship(
        back_populates="setup", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_setups_expires_at", "expires_at"),)

    def __repr__(self) -> str:
        return f"<Setup {self.id}>"


class SetupComponent(Base):
    """Components selected for a setup."""

    __tablename__ = "setup_components"

    id: Mapped[int] = mapped_column(primary_key=True)
    setup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("setups.id"), nullable=False
    )
    component_id: Mapped[int] = mapped_column(ForeignKey("components.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    # Optional overrides
    notes: Mapped[str | None] = mapped_column(Text)
    selected_vendor_id: Mapped[int | None] = mapped_column(ForeignKey("vendors.id"))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    setup: Mapped["Setup"] = relationship(back_populates="components")

    __table_args__ = (
        Index("ix_setup_components_setup_id", "setup_id"),
        Index("ix_setup_components_component_id", "component_id"),
    )

    def __repr__(self) -> str:
        return f"<SetupComponent {self.setup_id}:{self.component_id}>"
