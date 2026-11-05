"""Stage: relevance ranking.

    freshness · importance · topic relevance · personal relevance ·
    source quality · geographic relevance

Every component is 0-1 and the weights are explicit (`RankWeights`). Scores
exist only inside the backend: the API exposes an `importance` *tier* and
`personal_relevance` *reasons*, never a number (Module 09).
"""

import math
import re
from dataclasses import dataclass
from datetime import datetime

from app.models.preferences import UserPreferences
from app.pipeline.personalize import score_article
from app.pipeline.schemas import StoryDraft

FRESHNESS_HALF_LIFE_HOURS = 18.0

# How much the front page cares about each category, independent of any user.
CATEGORY_PRIORITY = {
    "ai": 1.0,
    "cybersecurity": 0.9,
    "software-engineering": 0.8,
    "research": 0.75,
    "world": 0.6,
}

_NEWSWORTHY_RE = re.compile(
    r"\b(breach|outage|zero-day|actively exploited|acquires?|acquisition|launch(es|ed)?|unveils?|"
    r"announces?|record|ban(s|ned)?|shutdown|layoffs?|critical|recall|lawsuit|raises)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class RankWeights:
    freshness: float = 0.26
    importance: float = 0.24
    topic: float = 0.14
    personal: float = 0.16
    source_quality: float = 0.12
    geographic: float = 0.08

    def without_personal(self) -> "RankWeights":
        return RankWeights(
            self.freshness, self.importance, self.topic, 0.0, self.source_quality, self.geographic
        )

    def total(self) -> float:
        return (
            self.freshness + self.importance + self.topic + self.personal
            + self.source_quality + self.geographic
        )  # fmt: skip


@dataclass(frozen=True)
class RankedStory:
    draft: StoryDraft
    score: float  # internal only
    parts: dict[str, float]  # internal only (debugging / tests)


def latest_published(draft: StoryDraft) -> datetime:
    return max(m.published_at for m in draft.members)


def freshness(draft: StoryDraft, now: datetime) -> float:
    age_hours = max(0.0, (now - latest_published(draft)).total_seconds() / 3600)
    return math.pow(0.5, age_hours / FRESHNESS_HALF_LIFE_HOURS)


def importance_signal(draft: StoryDraft) -> float:
    publishers = {m.source.lower() for m in draft.members}
    corroboration = min(1.0, (len(publishers) - 1) / 3)

    cvss = max((float(m.extra.get("cvss") or 0) for m in draft.members), default=0.0)
    severity = 1.0 if cvss >= 9.0 else 0.7 if cvss >= 7.0 else 0.0

    headline = " ".join(m.title for m in draft.members[:3])
    newsworthy = min(1.0, len(_NEWSWORTHY_RE.findall(headline)) / 2)

    return min(1.0, 0.45 * corroboration + 0.25 * severity + 0.30 * newsworthy)


def topic_signal(draft: StoryDraft) -> float:
    article = draft.article
    priority = CATEGORY_PRIORITY.get(article.category, 0.5)
    return 0.7 * priority + 0.3 * min(1.0, len(article.topics) / 3)


def source_quality_signal(draft: StoryDraft) -> float:
    qualities = sorted((m.source_quality for m in draft.members), reverse=True)
    return 0.7 * qualities[0] + 0.3 * (sum(qualities[:3]) / len(qualities[:3]))


def geographic_signal(draft: StoryDraft, regions: list[str]) -> float:
    region = draft.article.region or "global"
    if region in regions:
        return 1.0
    return 0.6 if region == "global" else 0.3


def rank_stories(
    drafts: list[StoryDraft],
    *,
    now: datetime,
    regions: list[str],
    preferences: UserPreferences | None = None,
    weights: RankWeights | None = None,
) -> list[RankedStory]:
    weights = weights or RankWeights()
    if preferences is None:
        weights = weights.without_personal()
    norm = weights.total() or 1.0

    ranked: list[RankedStory] = []
    for draft in drafts:
        parts = {
            "freshness": freshness(draft, now),
            "importance": importance_signal(draft),
            "topic": topic_signal(draft),
            "personal": score_article(draft.article, preferences)[0] if preferences else 0.0,
            "source_quality": source_quality_signal(draft),
            "geographic": geographic_signal(draft, regions),
        }
        score = (
            weights.freshness * parts["freshness"]
            + weights.importance * parts["importance"]
            + weights.topic * parts["topic"]
            + weights.personal * parts["personal"]
            + weights.source_quality * parts["source_quality"]
            + weights.geographic * parts["geographic"]
        ) / norm
        ranked.append(RankedStory(draft=draft, score=score, parts=parts))

    ranked.sort(
        key=lambda r: (
            -round(r.score, 9),
            -latest_published(r.draft).timestamp(),
            r.draft.article.id,
        )
    )
    return ranked


def importance_tiers(count: int) -> list[str]:
    """Tier labels by rank position: one lead, the next ~quarter major, the
    last ~quarter minor, the rest standard."""
    if count == 0:
        return []
    major = max(1, math.ceil(count * 0.25)) if count > 2 else 0
    minor = math.floor(count * 0.25)
    tiers = ["standard"] * count
    tiers[0] = "lead"
    for i in range(1, min(count, 1 + major)):
        tiers[i] = "major"
    for i in range(count - minor, count):
        if tiers[i] == "standard":
            tiers[i] = "minor"
    return tiers
