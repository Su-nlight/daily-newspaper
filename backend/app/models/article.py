from datetime import datetime

from pydantic import BaseModel, Field


class Article(BaseModel):
    """Mirrors the frontend's Article shape (src/types/index.ts) closely
    enough that the two are easy to reconcile, but this backend owns its
    own mock corpus — see app/services/sources.py. No real ingestion yet.
    """

    id: str
    title: str
    summary: str
    category: str
    source: str
    source_url: str
    published_at: datetime
    image_url: str | None = None
    topics: list[str] = Field(default_factory=list)
