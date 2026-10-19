from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.article import Article, RelevanceLevel


class EditionMetadata(BaseModel):
    """Facts about how an edition was produced. `status` is "seed" for the
    committed mock corpus, "complete" for a clean pipeline run and "degraded"
    when some sources failed or generation fell back (see `warnings`)."""

    generated_at: datetime | None = None
    timezone: str = "UTC"
    pipeline_version: str | None = None
    story_count: int = 0
    source_count: int = 0
    ai_summarized_count: int = 0
    status: Literal["complete", "degraded", "seed"] = "seed"
    warnings: list[str] = Field(default_factory=list)
    personalization_applied: bool = False


class EditionSection(BaseModel):
    slug: str
    title: str
    description: str | None = None
    # Category slugs this section gathers (matches Article.category).
    categories: list[str] = Field(default_factory=list)
    story_ids: list[str] = Field(default_factory=list)


class BriefItem(BaseModel):
    """One line of the 60-second brief. `id` is the story's id."""

    id: str
    headline: str
    summary: str


class PersonalizedStory(BaseModel):
    story_id: str
    level: RelevanceLevel = "low"
    reasons: list[str] = Field(default_factory=list)


class Edition(BaseModel):
    """A daily edition. `stories` is the single master list (rank order);
    `top_story_ids`, `sections`, `brief` and `personalized` reference stories
    by id so nothing is duplicated - clients join on `Story.id`.

    The first four fields are the Module 07 shape; the rest are Module 09.
    """

    id: str
    date: str
    headline: str
    summary: str
    stories: list[Article]

    metadata: EditionMetadata = Field(default_factory=EditionMetadata)
    top_story_ids: list[str] = Field(default_factory=list)
    sections: list[EditionSection] = Field(default_factory=list)
    brief: list[BriefItem] = Field(default_factory=list)
    personalized: list[PersonalizedStory] = Field(default_factory=list)
