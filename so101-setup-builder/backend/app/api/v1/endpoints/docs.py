from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Documentation

router = APIRouter()


@router.get("")
async def list_documentation(
    category: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List documentation with optional filtering."""
    query = select(Documentation)

    if category:
        query = query.where(Documentation.category == category)

    if search:
        search_filter = or_(
            Documentation.title.ilike(f"%{search}%"),
            Documentation.content.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    docs = result.scalars().all()

    return {
        "items": [
            {
                "id": doc.id,
                "title": doc.title,
                "slug": doc.slug,
                "category": doc.category,
                "tags": doc.tags,
                "excerpt": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
            }
            for doc in docs
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/categories")
async def list_doc_categories(db: AsyncSession = Depends(get_db)):
    """List available documentation categories."""
    query = select(Documentation.category).distinct().where(
        Documentation.category.is_not(None)
    )
    result = await db.execute(query)
    categories = result.scalars().all()

    return {"categories": list(categories)}


@router.get("/{slug}")
async def get_documentation(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single documentation page by slug."""
    query = select(Documentation).where(Documentation.slug == slug)
    result = await db.execute(query)
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documentation not found",
        )

    return {
        "id": doc.id,
        "title": doc.title,
        "slug": doc.slug,
        "content": doc.content,
        "content_html": doc.content_html,
        "category": doc.category,
        "tags": doc.tags,
        "metadata": doc.doc_metadata,
        "source_path": doc.source_path,
        "updated_at": doc.updated_at,
    }


@router.get("/search/fulltext")
async def fulltext_search(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Full-text search across documentation."""
    # Simple ILIKE search for now (full-text search requires proper setup)
    query = select(Documentation).where(
        or_(
            Documentation.title.ilike(f"%{q}%"),
            Documentation.content.ilike(f"%{q}%"),
        )
    ).limit(limit)

    result = await db.execute(query)
    docs = result.scalars().all()

    return {
        "query": q,
        "results": [
            {
                "id": doc.id,
                "title": doc.title,
                "slug": doc.slug,
                "category": doc.category,
                "excerpt": extract_excerpt(doc.content, q),
            }
            for doc in docs
        ],
        "total": len(docs),
    }


def extract_excerpt(content: str, query: str, context_chars: int = 100) -> str:
    """Extract a relevant excerpt from content around the query."""
    lower_content = content.lower()
    lower_query = query.lower()

    pos = lower_content.find(lower_query)
    if pos == -1:
        return content[:200] + "..." if len(content) > 200 else content

    start = max(0, pos - context_chars)
    end = min(len(content), pos + len(query) + context_chars)

    excerpt = content[start:end]
    if start > 0:
        excerpt = "..." + excerpt
    if end < len(content):
        excerpt = excerpt + "..."

    return excerpt
