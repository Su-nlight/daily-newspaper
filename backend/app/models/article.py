from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

# How prominent a story is in its edition. Deliberately a label, not a number:
# raw ranking scores are never exposed (Module 09).
Importance = Literal["lead", "major", "standard", "minor"]
RelevanceLevel = Literal["none", "low", "medium", "high"]


class SourceAttribution(BaseModel):
    """One publication a story is built from. Every story keeps the full list
    (Module 09: "Every generated story must retain its underlying sources").
    URLs come from fetched source metadata - never from model output.
    """

    publisher: str
    url: str
    title: str | None = None
    published_at: datetime | None = None
    # Registry id of the configured source this came from (None for seed data).
    source_id: str | None = None


class PersonalRelevance(BaseModel):
    """Why a story matters to a particular reader. `level` is a coarse label;
    `reasons` are plain-language and safe to show (cf. the frontend's
    WhyRelevant). There is intentionally no numeric score.
    """

    level: RelevanceLevel = "none"
    reasons: list[str] = Field(default_factory=list)


class Article(BaseModel):
    """A Daily Signal story as served to the frontend and the chat.

    Mirrors the frontend's Article shape (src/types/index.ts). Since Module 09
    a story is usually a *cluster*: one event reported by several publications.
    `source` / `source_url` are the primary (best) source; `sources` lists all
    of them. Seed-corpus stories (Module 07) are single-source.

    Module 09 field names: the pipeline's internal candidate model uses the
    spec's names (`url`, `image`); here they stay `source_url` / `image_url`
    so the existing frontend/chat contracts don't change.
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

    # ---- Module 09 ----
    # The story body in Daily Signal's own words (generated from, or extracted
    # out of, the underlying sources). Never a republished article.
    content: str | None = None
    entities: list[str] = Field(default_factory=list)
    importance: Importance = "standard"
    personal_relevance: PersonalRelevance = Field(default_factory=PersonalRelevance)
    sources: list[SourceAttribution] = Field(default_factory=list)
    related_ids: list[str] = Field(default_factory=list)
    region: str | None = None
    # True when `summary`/`what_happened`/`key_facts` were written by a model
    # (always from retrieved evidence and verified - see pipeline/grounding.py).
    ai_generated: bool = False

    @model_validator(mode="after")
    def _ensure_primary_source_listed(self) -> "Article":
        if not self.sources and self.source_url:
            self.sources = [
                SourceAttribution(
                    publisher=self.source,
                    url=self.source_url,
                    title=self.title,
                    published_at=self.published_at,
                )
            ]
        return self
