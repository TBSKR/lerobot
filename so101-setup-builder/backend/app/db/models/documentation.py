from datetime import datetime
from typing import Any

from sqlalchemy import String, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Documentation(Base):
    """Synced LeRobot documentation."""

    __tablename__ = "documentation"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    source_path: Mapped[str] = mapped_column(String(500), nullable=False)  # Original file path
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_html: Mapped[str | None] = mapped_column(Text)  # Rendered HTML

    # Metadata
    category: Mapped[str | None] = mapped_column(String(100))  # guide, reference, tutorial
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list)
    doc_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)

    # Search
    search_vector: Mapped[Any | None] = mapped_column(TSVECTOR)

    # Timestamps
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        Index("ix_documentation_search_vector", "search_vector", postgresql_using="gin"),
        Index("ix_documentation_category", "category"),
    )

    def __repr__(self) -> str:
        return f"<Documentation {self.slug}>"
