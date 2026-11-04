"""Stage: topic classification, plus region detection.

`classify_article` scores one article; `aggregate` combines a story's members
(weighting by source quality, so a trusted outlet's framing counts for more).
Scores here are internal and never leave the backend.
"""

from dataclasses import dataclass, field

from app.pipeline import taxonomy as tx
from app.pipeline.schemas import CandidateArticle
from app.pipeline.textutil import collapse_ws

_TITLE_MULTIPLIER = 3
_BODY_HIT_CAP = 2  # a keyword repeated 10 times is not 10x as relevant
TOPIC_THRESHOLD = 3.0
MAX_TOPICS = 4
CATEGORY_MIN_SCORE = 2.0
REGION_THRESHOLD = 3.0


@dataclass
class Classification:
    category_scores: dict[str, float] = field(default_factory=dict)
    topic_scores: dict[str, float] = field(default_factory=dict)  # keyed by topic id
    region_scores: dict[str, float] = field(default_factory=dict)


def _score_rules(rules: tuple[tx.Rule, ...], title: str, body: str) -> float:
    total = 0.0
    for rule in rules:
        if rule.pattern.search(title):
            total += rule.weight * _TITLE_MULTIPLIER
        hits = len(rule.pattern.findall(body))
        total += rule.weight * min(hits, _BODY_HIT_CAP)
    return total


def classify_article(article: CandidateArticle) -> Classification:
    title = article.title
    body = collapse_ws(f"{article.summary} {article.content[:1500]}")
    haystack = f"{title} {body}"
    result = Classification()

    for category, rules in tx.CATEGORY_RULES.items():
        result.category_scores[category] = _score_rules(rules, title, body)
    if article.category in result.category_scores:  # the source's own default
        result.category_scores[article.category] += 2.0
    prior = tx.KIND_CATEGORY_PRIOR.get(article.kind)
    if prior:
        result.category_scores[prior[0]] += prior[1]

    for topic in tx.TOPICS:
        if topic.requires and not topic.requires.search(haystack):
            continue
        score = _score_rules(topic.rules, title, body)
        if score:
            result.topic_scores[topic.id] = score
    topic_prior = tx.KIND_TOPIC_PRIOR.get(article.kind)
    if topic_prior:
        result.topic_scores[topic_prior[0]] = (
            result.topic_scores.get(topic_prior[0], 0) + topic_prior[1]
        )

    for region, rules in tx.REGION_RULES.items():
        score = _score_rules(rules, title, body)
        if score:
            result.region_scores[region] = score
    return result


@dataclass
class StoryClassification:
    category: str
    topics: list[str]  # display names, strongest first
    region: str


def aggregate(articles: list[CandidateArticle]) -> StoryClassification:
    category_scores: dict[str, float] = {c: 0.0 for c in tx.CATEGORY_ORDER}
    topic_scores: dict[str, float] = {}
    region_scores: dict[str, float] = {}

    for article in articles:
        weight = 0.5 + article.source_quality  # 0.5-1.5: trusted sources count more
        result = classify_article(article)
        for key, score in result.category_scores.items():
            category_scores[key] += score * weight
        for key, score in result.topic_scores.items():
            topic_scores[key] = topic_scores.get(key, 0.0) + score * weight
        for key, score in result.region_scores.items():
            region_scores[key] = region_scores.get(key, 0.0) + score * weight

    best = max(tx.CATEGORY_ORDER, key=lambda c: (category_scores[c], -tx.CATEGORY_ORDER.index(c)))
    if category_scores[best] < CATEGORY_MIN_SCORE:
        best = articles[0].category if articles[0].category in category_scores else "world"

    # A topic must clear the bar on the story's *average* article, so one
    # off-topic outlier among five doesn't tag the story.
    n = len(articles)
    topics = sorted(
        (
            (tid, score)
            for tid, score in topic_scores.items()
            if score / n >= TOPIC_THRESHOLD and tid in tx.TOPIC_NAMES
        ),
        key=lambda pair: (-pair[1], pair[0]),
    )[:MAX_TOPICS]

    source_region = next((a.region for a in articles if a.region != "global"), "global")
    region_best = max(region_scores, key=lambda r: (region_scores[r], r), default=None)
    if region_best and region_scores[region_best] / n >= REGION_THRESHOLD:
        region = region_best
    else:
        region = source_region
    return StoryClassification(
        category=best, topics=[tx.TOPIC_NAMES[tid] for tid, _ in topics], region=region
    )
