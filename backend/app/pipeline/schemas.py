"""Internal pipeline schemas. The public (API-facing) shapes live in app/models."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.models.article import Article

SourceKind = Literal["rss", "news_api", "arxiv", "github", "nvd", "blog"]


class SourceConfig(BaseModel):
    """One configured content source. Lives in the sources JSON file, so
    adding a feed needs no code."""

    id: str
    name: str
    kind: SourceKind
    url: str
    enabled: bool = True
    # Editorial trust tier, 0-1. Feeds source-quality ranking and nothing else.
    quality: float = Field(default=0.5, ge=0, le=1)
    # Where the source "is" (region id as used by user preferences).
    region: str = "global"
    default_category: str | None = None
    max_items: int = Field(default=30, ge=1, le=200)
    # Name of a Settings attribute holding this source's credential
    # (e.g. "newsapi_key"). The secret itself is never in the sources file.
    api_key_setting: str | None = None
    # False for sources that work anonymously but are rate-limited without a key.
    api_key_required: bool = True
    # Adapter-specific options (GitHub repos, NVD min_cvss, arXiv query...).
    params: dict[str, Any] = Field(default_factory=dict)


class RawItem(BaseModel):
    """What an adapter emits: one item exactly as the provider described it,
    before any cleaning. Adapters do parsing only - no ranking, no dedupe."""

    source_id: str
    # The publisher to credit. For aggregators (news APIs) this is the
    # per-article publisher, not the aggregator.
    source_name: str
    kind: SourceKind
    title: str
    url: str
    summary: str = ""
    content: str = ""
    published_at: datetime | None = None
    image: str | None = None
    tags: list[str] = Field(default_factory=list)
    # Provider-specific facts: cve_id, cvss, arxiv_id, repo, release tag...
    extra: dict[str, Any] = Field(default_factory=dict)


class CandidateArticle(BaseModel):
    """The normalized article model from the Module 09 spec: one item from one
    publisher, cleaned and enriched. A *story* is a cluster of these.

    `importance` / `personal_relevance` are pre-ranking placeholders in 0-1;
    final values are computed per edition and exposed only as labels.
    """

    id: str
    title: str
    summary: str
    content: str
    url: str
    source: str
    published_at: datetime
    category: str
    topics: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    image: str | None = None
    importance: float = 0.0
    personal_relevance: float = 0.0

    # Provenance / pipeline bookkeeping.
    canonical_url: str
    source_id: str
    kind: SourceKind
    source_quality: float = 0.5
    region: str = "global"
    fetched_at: datetime
    extra: dict[str, Any] = Field(default_factory=dict)


class StoryDraft(BaseModel):
    """A story under construction: the public `Article` plus what ranking and
    summarization need to know about its underlying members."""

    article: Article
    members: list[CandidateArticle]
    # Fingerprint of the evidence the text was written from; lets reruns skip
    # re-summarizing a story whose sources haven't changed.
    evidence_hash: str
    merge_reasons: list[str] = Field(default_factory=list)
