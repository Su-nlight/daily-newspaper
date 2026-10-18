from fastapi import APIRouter, HTTPException, Query

from app.models.edition import Edition
from app.models.preferences import UserPreferences
from app.pipeline.personalize import parse_preferences, personal_relevance, personalize_stories
from app.services import sources as content

router = APIRouter(prefix="/api", tags=["edition"])

PERSONALIZED_LIMIT = 4

_TOPICS = Query(
    default=None,
    description="Comma-separated topic ids, optionally weighted: `topic-agents:0.9,topic-rag`.",
)
_REGIONS = Query(default=None, description="Comma-separated region ids: `india,europe`.")
_SOURCES = Query(default=None, description="Comma-separated source ids/names the reader follows.")
_CONTENT_TYPES = Query(default=None, description="Comma-separated, e.g. `research-monitoring`.")


def personalize_edition(edition: Edition, prefs: UserPreferences | None) -> Edition:
    """Adds the reader-specific parts of an edition. The stored edition is
    shared by everyone; this runs per request, is deterministic, and exposes
    reasons and a coarse level - never a numeric score."""
    if prefs is None:
        return edition
    stories = [
        story.model_copy(update={"personal_relevance": personal_relevance(story, prefs)})
        for story in edition.stories
    ]
    return edition.model_copy(
        update={
            "stories": stories,
            "personalized": personalize_stories(stories, prefs, limit=PERSONALIZED_LIMIT),
            "metadata": edition.metadata.model_copy(update={"personalization_applied": True}),
        }
    )


@router.get("/edition/today", response_model=Edition)
async def get_today_edition(
    topics: str | None = _TOPICS,
    regions: str | None = _REGIONS,
    sources: str | None = _SOURCES,
    content_types: str | None = _CONTENT_TYPES,
) -> Edition:
    """The latest edition: metadata, ranked `stories`, `top_story_ids`,
    `sections`, the 60-second `brief` and - when preferences are supplied -
    `personalized` stories. Stories are referenced by id; join on `stories[].id`."""
    try:
        edition = content.get_today_edition()
    except content.EditionNotAvailable as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return personalize_edition(
        edition,
        parse_preferences(
            topics=topics, regions=regions, sources=sources, content_types=content_types
        ),
    )


@router.get("/edition/{date}", response_model=Edition)
async def get_edition_by_date(
    date: str,
    topics: str | None = _TOPICS,
    regions: str | None = _REGIONS,
    sources: str | None = _SOURCES,
    content_types: str | None = _CONTENT_TYPES,
) -> Edition:
    edition = content.get_edition_by_date(date)
    if edition is None:
        raise HTTPException(status_code=404, detail="Edition not found")
    return personalize_edition(
        edition,
        parse_preferences(
            topics=topics, regions=regions, sources=sources, content_types=content_types
        ),
    )
