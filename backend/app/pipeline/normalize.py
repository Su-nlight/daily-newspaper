"""Stage: normalize. RawItem -> CandidateArticle (the Module 09 article model).

Everything here is deterministic and offline. The id is a hash of the
canonical URL, which is what makes re-ingesting the same article a no-op.
"""

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.pipeline.schemas import CandidateArticle, RawItem, SourceConfig
from app.pipeline.textutil import (
    canonicalize_url,
    collapse_ws,
    is_public_http_url,
    lead_sentences,
    strip_html,
    truncate,
)

MAX_TITLE_CHARS = 220
MAX_SUMMARY_CHARS = 600
MAX_CONTENT_CHARS = 4000
_FUTURE_SKEW = timedelta(hours=1)

# WordPress-style footer: "The post X appeared first on Y."
_BOILERPLATE_RE = re.compile(r"\s*The post .{0,200}? appeared first on .{0,100}?\.?\s*$", re.I)
_TITLE_SUFFIX_RE = re.compile(r"\s+[-–—|·]\s+([^-–—|·]{2,40})$")


@dataclass
class NormalizeStats:
    kept: int = 0
    dropped_invalid: int = 0
    dropped_stale: int = 0


def article_id(canonical_url: str) -> str:
    return "art-" + hashlib.sha1(canonical_url.encode()).hexdigest()[:16]


def clean_title(title: str, publisher: str) -> str:
    """Strips a trailing " - Publisher" (common in aggregated feeds) but only
    when it really is the publisher, so "Foo - A New Hope" is untouched."""
    title = collapse_ws(strip_html(title))
    match = _TITLE_SUFFIX_RE.search(title)
    if match and match.group(1).strip().lower() == publisher.strip().lower():
        title = title[: match.start()]
    return truncate(title, MAX_TITLE_CHARS)


def normalize_item(
    raw: RawItem,
    source: SourceConfig,
    *,
    now: datetime,
) -> CandidateArticle | None:
    canonical = canonicalize_url(raw.url)
    if canonical is None:
        return None

    title = clean_title(raw.title, raw.source_name)
    if len(title) < 8:
        return None

    content = truncate(strip_html(raw.content), MAX_CONTENT_CHARS)
    summary = _BOILERPLATE_RE.sub("", strip_html(raw.summary))
    if not summary and content:
        summary = lead_sentences(content, max_sentences=2, max_chars=MAX_SUMMARY_CHARS)
    summary = truncate(summary, MAX_SUMMARY_CHARS)
    if summary.strip().lower() == title.strip().lower():
        summary = ""

    published = raw.published_at
    extra = dict(raw.extra)
    if raw.tags:
        extra["tags"] = raw.tags
    if published is None:
        published = now
        extra["date_inferred"] = True
    elif published > now + _FUTURE_SKEW:
        published = now
        extra["date_clamped"] = True

    return CandidateArticle(
        id=article_id(canonical),
        title=title,
        summary=summary,
        content=content,
        url=raw.url.strip(),
        source=collapse_ws(raw.source_name),
        published_at=published,
        category=source.default_category or "world",
        image=raw.image.strip() if raw.image and is_public_http_url(raw.image) else None,
        canonical_url=canonical,
        source_id=source.id,
        kind=raw.kind,
        source_quality=source.quality,
        region=source.region,
        fetched_at=now,
        extra=extra,
    )


def normalize_items(
    raw_items: list[RawItem],
    sources: dict[str, SourceConfig],
    *,
    now: datetime,
    max_age: timedelta,
) -> tuple[list[CandidateArticle], NormalizeStats]:
    stats = NormalizeStats()
    seen: set[str] = set()
    candidates: list[CandidateArticle] = []

    for raw in raw_items:
        source = sources.get(raw.source_id)
        candidate = normalize_item(raw, source, now=now) if source else None
        if candidate is None:
            stats.dropped_invalid += 1
            continue
        if candidate.published_at < now - max_age:
            stats.dropped_stale += 1
            continue
        if candidate.id in seen:  # same canonical URL twice within one fetch
            continue
        seen.add(candidate.id)
        candidates.append(candidate)

    stats.kept = len(candidates)
    return candidates, stats
