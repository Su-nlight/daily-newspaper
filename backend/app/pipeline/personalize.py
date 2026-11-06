"""Personal relevance: how well a story fits one reader's stated preferences.

Rule-based and explainable, mirroring the frontend's `scoreArticle` (Module 05)
including its reason wording. Produces a coarse `level` and plain-language
`reasons` for the API; the numeric score stays internal.
"""

import re

from app.models.article import Article, PersonalRelevance, RelevanceLevel
from app.models.edition import PersonalizedStory
from app.models.preferences import TopicPreference, UserPreferences
from app.pipeline import taxonomy as tx

DEFAULT_TOPIC_WEIGHT = 0.7
_REGION_BONUS = 0.25
_SOURCE_BONUS = 0.15
_CONTENT_TYPE_BONUS = 0.2
_EXTRA_TOPIC_BONUS = 0.1


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _source_keys(article: Article) -> set[str]:
    keys = {_slug(article.source)}
    for attribution in article.sources:
        keys.add(_slug(attribution.publisher))
        if attribution.source_id:
            keys.add(_slug(attribution.source_id))
    return keys


def score_article(article: Article, prefs: UserPreferences) -> tuple[float, list[str]]:
    reasons: list[str] = []
    matched_weights: list[float] = []

    topic_names = {t.lower() for t in article.topics}
    for pref in sorted(prefs.topics, key=lambda p: -p.weight):
        name = tx.TOPIC_NAMES.get(pref.id)
        if pref.weight > 0 and name and name.lower() in topic_names:
            matched_weights.append(pref.weight)
            reasons.append(f"Matches your interest in {name}")

    score = 0.0
    if matched_weights:
        # The strongest interest sets the base; extra matches add a little.
        score = matched_weights[0] + _EXTRA_TOPIC_BONUS * (len(matched_weights) - 1)

    if article.region and article.region in prefs.regions:
        score += _REGION_BONUS
        reasons.append(f"Relevant to {tx.REGION_NAMES.get(article.region, article.region)}")

    wanted_sources = {_slug(s.removeprefix("source-")) for s in prefs.sources}
    if wanted_sources & _source_keys(article):
        score += _SOURCE_BONUS
        reasons.append(f"From {article.source}, a source you follow")

    if "research-monitoring" in prefs.content_types and article.category == "research":
        score += _CONTENT_TYPE_BONUS
        reasons.append("Matches your Research Monitoring preference")

    return min(score, 1.0), reasons


def relevance_level(score: float) -> RelevanceLevel:
    if score <= 0:
        return "none"
    if score < 0.35:
        return "low"
    if score < 0.7:
        return "medium"
    return "high"


def personal_relevance(article: Article, prefs: UserPreferences | None) -> PersonalRelevance:
    if prefs is None:
        return PersonalRelevance()
    score, reasons = score_article(article, prefs)
    return PersonalRelevance(level=relevance_level(score), reasons=reasons)


def personalize_stories(
    stories: list[Article], prefs: UserPreferences, *, limit: int = 4
) -> list[PersonalizedStory]:
    """The "Relevant to You" selection: stories with any match, best first
    (ties keep edition order). Never returns a numeric score."""
    scored = [(score_article(story, prefs), story) for story in stories]
    ranked = sorted(
        (item for item in scored if item[0][0] > 0),
        key=lambda item: -item[0][0],  # sorted() is stable: ties stay in edition order
    )
    return [
        PersonalizedStory(story_id=story.id, level=relevance_level(score), reasons=reasons)
        for (score, reasons), story in ranked[:limit]
    ]


def parse_preferences(
    *,
    topics: str | None = None,
    regions: str | None = None,
    sources: str | None = None,
    content_types: str | None = None,
) -> UserPreferences | None:
    """Builds preferences from the edition endpoint's comma-separated query
    parameters. `topics` entries are `id` or `id:weight` (weight 0-1).
    Returns None when nothing usable was supplied."""

    def split(value: str | None) -> list[str]:
        return [part.strip() for part in (value or "").split(",") if part.strip()]

    topic_prefs: list[TopicPreference] = []
    for entry in split(topics):
        topic_id, _, raw_weight = entry.partition(":")
        try:
            weight = float(raw_weight) if raw_weight else DEFAULT_TOPIC_WEIGHT
        except ValueError:
            continue
        if topic_id and 0 <= weight <= 1:
            topic_prefs.append(TopicPreference(id=topic_id, weight=weight))

    prefs = UserPreferences(
        topics=topic_prefs,
        regions=split(regions),
        sources=split(sources),
        content_types=split(content_types),
    )
    if not (prefs.topics or prefs.regions or prefs.sources or prefs.content_types):
        return None
    return prefs
