"""Stage: edition generation.

From ranked stories, build the day's edition: top stories (hero first, with
category diversity), section stories, the 60-second brief and related-story
links. Personalized content is *not* baked in - it depends on the reader and is
computed per request from the edition's stories (see api/edition.py).
"""

import hashlib
from datetime import datetime

from app.models.article import Article
from app.models.edition import BriefItem, Edition, EditionMetadata, EditionSection
from app.pipeline import PIPELINE_VERSION
from app.pipeline.rank import RankedStory, importance_tiers
from app.pipeline.taxonomy import CATEGORY_LABELS
from app.pipeline.textutil import lead_sentences, truncate

TOP_STORY_COUNT = 5
MAX_PER_CATEGORY_IN_TOP = 2
SECTION_STORY_LIMIT = 4
RELATED_LIMIT = 3
# ~200 words read aloud at a normal pace is about a minute.
BRIEF_WORD_BUDGET = 190
BRIEF_MIN_ITEMS = 3
BRIEF_MAX_ITEMS = 6

# Same front-page sections the frontend composes today (Module 03).
SECTION_DEFS: list[tuple[str, str, str, list[str]]] = [
    ("world", "World", "Global developments shaping technology and business.", ["world"]),
    (
        "technology",
        "Technology",
        "Engineering, infrastructure, and product updates.",
        ["software-engineering"],
    ),
    (
        "ai-research",
        "AI & Research",
        "Models, agent systems, and the research behind them.",
        ["ai", "research"],
    ),
    (
        "cybersecurity",
        "Cybersecurity",
        "Threats, breaches, and defensive practice.",
        ["cybersecurity"],
    ),
]


def pick_top_stories(ranked: list[Article], count: int = TOP_STORY_COUNT) -> list[Article]:
    """Best-first, but no more than two from one category while others remain,
    so a front page full of one beat doesn't read as an edition."""
    chosen: list[Article] = []
    per_category: dict[str, int] = {}
    for story in ranked:
        if len(chosen) == count:
            break
        if per_category.get(story.category, 0) < MAX_PER_CATEGORY_IN_TOP:
            chosen.append(story)
            per_category[story.category] = per_category.get(story.category, 0) + 1
    for story in ranked:  # not enough variety available: fill by rank
        if len(chosen) == count:
            break
        if story not in chosen:
            chosen.append(story)
    return chosen


def build_brief(stories: list[Article]) -> list[BriefItem]:
    items: list[BriefItem] = []
    words = 0
    for story in stories:
        line = lead_sentences(story.summary or story.title, max_sentences=1, max_chars=130)
        cost = len(story.title.split()) + len(line.split())
        if len(items) >= BRIEF_MAX_ITEMS or (
            len(items) >= BRIEF_MIN_ITEMS and words + cost > BRIEF_WORD_BUDGET
        ):
            break
        items.append(BriefItem(id=story.id, headline=story.title, summary=line))
        words += cost
    return items


def related_ids(story: Article, pool: list[Article]) -> list[str]:
    topics, entities = set(story.topics), set(story.entities)
    scored: list[tuple[float, int, str]] = []
    for index, other in enumerate(pool):
        if other.id == story.id:
            continue
        score = (
            2.0 * len(topics & set(other.topics))
            + 1.5 * len(entities & set(other.entities))
            + (1.0 if other.category == story.category else 0.0)
        )
        if score >= 2.0:
            scored.append((-score, index, other.id))
    return [story_id for _, _, story_id in sorted(scored)[:RELATED_LIMIT]]


def _headline_and_summary(top: list[Article], stories: list[Article]) -> tuple[str, str]:
    if not top:
        return "No stories today", "No stories were available for this edition."
    publishers = {s.publisher for story in stories for s in story.sources}
    categories: dict[str, int] = {}
    for story in stories:
        categories[story.category] = categories.get(story.category, 0) + 1
    leading = [
        CATEGORY_LABELS.get(c, c)
        for c, _ in sorted(categories.items(), key=lambda kv: (-kv[1], kv[0]))
    ][:3]
    led_by = leading[0] if len(leading) == 1 else ", ".join(leading[:-1]) + " and " + leading[-1]
    summary = f"{len(stories)} stories from {len(publishers)} publications, led by {led_by}."
    return truncate(top[0].title, 200), summary


def edition_hash(edition: Edition) -> str:
    """Content fingerprint that ignores *when* it was generated, so a re-run
    that changes nothing is recognisably a no-op."""
    payload = edition.model_copy(
        update={"metadata": edition.metadata.model_copy(update={"generated_at": None})}
    )
    return hashlib.sha256(payload.model_dump_json().encode()).hexdigest()[:24]


def build_edition(
    ranked: list[RankedStory],
    *,
    date: str,
    now: datetime,
    timezone: str,
    max_stories: int,
    warnings: list[str],
) -> Edition:
    chosen = ranked[:max_stories]
    tiers = importance_tiers(len(chosen))
    articles = [
        r.draft.article.model_copy(update={"importance": tier})
        for r, tier in zip(chosen, tiers, strict=True)
    ]

    top = pick_top_stories(articles)
    top_ids = {s.id for s in top}
    ordered = [*top, *(s for s in articles if s.id not in top_ids)]
    ordered = [s.model_copy(update={"related_ids": related_ids(s, ordered)}) for s in ordered]

    by_id = {s.id: s for s in ordered}
    sections: list[EditionSection] = []
    for slug, title, description, categories in SECTION_DEFS:
        ids = [s.id for s in ordered if s.category in categories and s.id not in top_ids][
            :SECTION_STORY_LIMIT
        ]
        if ids:
            sections.append(
                EditionSection(
                    slug=slug,
                    title=title,
                    description=description,
                    categories=categories,
                    story_ids=ids,
                )
            )

    headline, summary = _headline_and_summary([by_id[s.id] for s in top], ordered)
    publishers = {src.publisher for s in ordered for src in s.sources}
    metadata = EditionMetadata(
        generated_at=now,
        timezone=timezone,
        pipeline_version=PIPELINE_VERSION,
        story_count=len(ordered),
        source_count=len(publishers),
        ai_summarized_count=sum(1 for s in ordered if s.ai_generated),
        status="degraded" if warnings else "complete",
        warnings=warnings,
    )
    return Edition(
        id=f"edition-{date}",
        date=date,
        headline=headline,
        summary=summary,
        stories=ordered,
        metadata=metadata,
        top_story_ids=[s.id for s in top],
        sections=sections,
        brief=build_brief(ordered),
    )
