#!/usr/bin/env python3
"""Sync documentation from LeRobot repository."""

import asyncio
import re
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.config import get_settings
from app.db.database import Base
from app.db.models import Documentation

settings = get_settings()

# Documentation files to sync
DOC_FILES = [
    {
        "path": "docs/so101_local_guide.md",
        "title": "SO-101 Quick Start Guide",
        "category": "guide",
        "tags": ["so101", "quickstart", "setup"],
    },
    {
        "path": "docs/source/so101.mdx",
        "title": "SO-101 Assembly Instructions",
        "category": "guide",
        "tags": ["so101", "assembly", "hardware"],
    },
]


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text


async def sync_documentation():
    """Sync documentation files to database."""
    # Create engine
    database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(database_url, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Find LeRobot root directory
    lerobot_root = Path(__file__).parent.parent.parent
    print(f"LeRobot root: {lerobot_root}")

    async with async_session() as session:
        for doc_info in DOC_FILES:
            doc_path = lerobot_root / doc_info["path"]

            if not doc_path.exists():
                print(f"Skipping {doc_info['path']} - file not found")
                continue

            print(f"Processing {doc_info['path']}...")

            # Read content
            content = doc_path.read_text(encoding="utf-8")
            slug = slugify(doc_info["title"])

            # Check if exists
            result = await session.execute(
                select(Documentation).where(Documentation.slug == slug)
            )
            existing = result.scalar_one_or_none()

            if existing:
                # Update
                existing.content = content
                existing.title = doc_info["title"]
                existing.category = doc_info.get("category")
                existing.tags = doc_info.get("tags", [])
                existing.source_updated_at = datetime.utcnow()
                existing.updated_at = datetime.utcnow()
                print(f"  Updated: {doc_info['title']}")
            else:
                # Create
                doc = Documentation(
                    title=doc_info["title"],
                    slug=slug,
                    source_path=doc_info["path"],
                    content=content,
                    category=doc_info.get("category"),
                    tags=doc_info.get("tags", []),
                    source_updated_at=datetime.utcnow(),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                session.add(doc)
                print(f"  Created: {doc_info['title']}")

        await session.commit()
        print("\nDocumentation sync complete!")


if __name__ == "__main__":
    asyncio.run(sync_documentation())
