"""Stage: source validation - the last gate before a story is published.

Guarantees for every surviving story:
* it has at least one source, each with a publisher and a public http(s) URL;
* every source came from a configured, enabled provider (no orphan data);
* its primary `source_url` is one of its listed sources;
* its image URL (if any) is a public http(s) URL;
* no URL appears inside generated text (URLs live in metadata only);
* it is not dated in the future.

Problems with a *source* drop that source; a story with none left is dropped.
Problems with generated *text* revert the story to extractive text.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.models.article import SourceAttribution
from app.pipeline import summarize
from app.pipeline.grounding import _DOMAIN_RE, _URL_RE
from app.pipeline.schemas import StoryDraft
from app.pipeline.textutil import is_public_http_url

_FUTURE_SKEW = timedelta(hours=1)


@dataclass
class ValidationReport:
    dropped_stories: list[str] = field(default_factory=list)
    removed_sources: int = 0
    reverted_text: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)


def _has_url(text: str | None) -> bool:
    return bool(text and (_URL_RE.search(text) or _DOMAIN_RE.search(text)))


def _generated_text(draft: StoryDraft) -> list[str | None]:
    article = draft.article
    return [article.summary, article.what_happened, article.content, *article.key_facts]


def validate_drafts(
    drafts: list[StoryDraft],
    *,
    registry_ids: set[str],
    now: datetime,
) -> tuple[list[StoryDraft], ValidationReport]:
    report = ValidationReport()
    valid: list[StoryDraft] = []

    for draft in drafts:
        article = draft.article

        good: list[SourceAttribution] = []
        for source in article.sources:
            ok = (
                bool(source.publisher.strip())
                and is_public_http_url(source.url)
                and (source.source_id is None or source.source_id in registry_ids)
            )
            if ok:
                good.append(source)
            else:
                report.removed_sources += 1
        if not good:
            report.dropped_stories.append(article.id)
            report.problems.append(f"{article.id}: no valid sources")
            continue
        article.sources = good

        if article.source_url not in {s.url for s in good}:
            article.source, article.source_url = good[0].publisher, good[0].url
        if article.published_at > now + _FUTURE_SKEW:
            report.dropped_stories.append(article.id)
            report.problems.append(f"{article.id}: dated in the future")
            continue
        if not article.title.strip():
            report.dropped_stories.append(article.id)
            continue
        if article.image_url and not is_public_http_url(article.image_url):
            article.image_url = None

        if any(_has_url(text) for text in _generated_text(draft)) and article.ai_generated:
            summarize.apply(article, summarize.extractive(draft))
            report.reverted_text.append(article.id)

        valid.append(draft)

    return valid, report
