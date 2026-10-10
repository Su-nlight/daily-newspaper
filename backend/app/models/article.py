from datetime import datetime

from pydantic import BaseModel, Field


class Article(BaseModel):
    """Mirrors the frontend's Article shape (src/types/index.ts). The corpus
    is exported from the frontend's mock data (`npm run export:corpus`), so
    the chat backend sees the same stories the UI shows. No real ingestion
    yet.
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

    # Optional long-form detail (present for a subset of stories). Gives the
    # model more than a one-line summary to ground story questions in.
    what_happened: str | None = None
    why_it_matters: str | None = None
    key_facts: list[str] = Field(default_factory=list)
