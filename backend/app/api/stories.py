from fastapi import APIRouter, HTTPException, Query

from app.models.article import Article
from app.services import sources

router = APIRouter(prefix="/api", tags=["stories"])


@router.get("/stories", response_model=list[Article])
async def list_stories(category: str | None = Query(default=None)) -> list[Article]:
    return sources.list_articles(category=category)


@router.get("/stories/{story_id}", response_model=Article)
async def get_story(story_id: str) -> Article:
    article = sources.get_article(story_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return article
