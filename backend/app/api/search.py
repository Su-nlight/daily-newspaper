from fastapi import APIRouter, Query

from app.models.article import Article
from app.services import sources

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search", response_model=list[Article])
async def search(
    q: str | None = Query(default=None),
    category: str | None = Query(default=None),
    source: str | None = Query(default=None),
    topic: str | None = Query(default=None),
) -> list[Article]:
    return sources.search_articles(query=q, category=category, source=source, topic=topic)
