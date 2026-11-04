from datetime import timedelta

import pytest

from app.models.article import Article
from app.models.preferences import TopicPreference, UserPreferences
from app.pipeline import rank
from app.pipeline.classify import aggregate
from app.pipeline.dedupe import cluster_articles
from app.pipeline.metadata import extract_entities
from app.pipeline.personalize import (
    parse_preferences,
    personal_relevance,
    personalize_stories,
    relevance_level,
)
from app.pipeline.stories import build_drafts
from tests.pipeline import fixtures as fx


def drafts():
    cands, _ = fx.candidates()
    clusters = cluster_articles(cands)
    return build_drafts(clusters, {}, {}), clusters


def by_prefix(ds, prefix):
    return next(d for d in ds if d.article.title.startswith(prefix))


# --------------------------------------------------------------- classification
def test_categories_topics_and_regions_for_the_universe():
    ds, _ = drafts()
    a = by_prefix(ds, "Nvidia unveils").article
    assert (a.category, a.topics, a.region) == ("ai", ["Semiconductors"], "global")

    paper = by_prefix(ds, "A New Benchmark").article
    assert paper.category == "research"
    assert {"Research Monitoring", "RAG"} <= set(paper.topics)

    india = by_prefix(ds, "India proposes").article
    assert india.category == "ai" and india.region == "india"
    assert {"AI Policy", "India Tech"} <= set(india.topics)

    release = by_prefix(ds, "langgraph").article
    assert "Open Source" in release.topics and "AI Agents" in release.topics


def test_cve_story_is_cybersecurity_and_not_mistagged_as_india():
    """Regression: an un-grouped regex alternation made `rbi` match inside
    'a-rbi-trary', tagging an OpenSSL CVE as India."""
    ds, _ = drafts()
    cve = by_prefix(ds, "Critical OpenSSL flaw CVE-2026-12345").article
    assert cve.category == "cybersecurity" and cve.region == "global"
    assert cve.topics == ["Cybersecurity"]


def test_policy_topic_requires_ai_context():
    cands, _ = fx.candidates()
    c = fx.by_title(cands, "India proposes").model_copy(
        update={
            "title": "Government proposes audit rules for banks",
            "summary": "A regulator published a draft framework for banking audits.",
        }
    )
    assert "AI Policy" not in aggregate([c]).topics


def test_only_known_topic_names_are_emitted():
    from app.pipeline.taxonomy import TOPIC_NAMES

    ds, _ = drafts()
    for d in ds:
        assert set(d.article.topics) <= set(TOPIC_NAMES.values())


def test_taxonomy_matches_frontend_topic_ids_and_categories():
    from app.pipeline.taxonomy import CATEGORY_ORDER, TOPIC_NAMES

    assert CATEGORY_ORDER == ["ai", "research", "cybersecurity", "software-engineering", "world"]
    for tid, name in {
        "topic-agents": "AI Agents",
        "topic-cloud-security": "Cloud Security",
        "topic-india-tech": "India Tech",
        "topic-research": "Research Monitoring",
        "topic-cybersecurity": "Cybersecurity",
        "topic-rag": "RAG",
        "topic-software-engineering": "Software Engineering",
        "topic-cloud": "Cloud",
        "topic-sap": "SAP",
        "topic-blockchain": "Blockchain",
    }.items():
        assert TOPIC_NAMES[tid] == name


# -------------------------------------------------------------------- entities
def test_entities_found_and_noise_excluded():
    ds, _ = drafts()
    assert "Nvidia" in by_prefix(ds, "Nvidia unveils").article.entities
    cve = by_prefix(ds, "Critical OpenSSL flaw CVE-2026-12345").article.entities
    assert cve[0] == "CVE-2026-12345" and "OpenSSL" in cve
    for d in ds:
        assert not {"AI", "Series", "Changed Added", "The", "Monday"} & set(d.article.entities)


def test_markdown_release_notes_yield_no_phrase_entities():
    ds, _ = drafts()
    assert by_prefix(ds, "langgraph").article.entities == []


def test_entities_are_capped():
    cands, _ = fx.candidates()
    big = cands[0].model_copy(
        update={"summary": " ".join(f"Then Acme{i}Corp bought Foo{i}Labs." for i in range(30))}
    )
    assert len(extract_entities([big])) <= 8


# ------------------------------------------------------------------------ rank
def test_freshness_halves_every_half_life():
    ds, _ = drafts()
    d = ds[0]
    latest = rank.latest_published(d)
    assert rank.freshness(d, latest) == pytest.approx(1.0)
    assert rank.freshness(
        d, latest + timedelta(hours=rank.FRESHNESS_HALF_LIFE_HOURS)
    ) == pytest.approx(0.5)


def test_corroboration_and_severity_raise_importance():
    ds, _ = drafts()
    multi = by_prefix(ds, "Nvidia unveils")
    single = by_prefix(ds, "AMD unveils")
    assert rank.importance_signal(multi) > rank.importance_signal(single)
    cve = by_prefix(ds, "Critical OpenSSL flaw CVE-2026-12345")
    quiet = by_prefix(ds, "How we rebuilt")
    assert rank.importance_signal(cve) > rank.importance_signal(quiet)


def test_ranking_is_deterministic_and_orders_sensibly():
    ds, _ = drafts()
    once = rank.rank_stories(ds, now=fx.NOW, regions=["global"])
    twice = rank.rank_stories(list(reversed(ds)), now=fx.NOW, regions=["global"])
    assert [r.draft.article.id for r in once] == [r.draft.article.id for r in twice]
    top_titles = [r.draft.article.title for r in once[:2]]
    assert any("CVE-2026-12345" in t for t in top_titles)  # corroborated + critical
    assert all(0 <= part <= 1 for r in once for part in r.parts.values())


def test_geographic_signal_prefers_matching_region():
    ds, _ = drafts()
    india = by_prefix(ds, "India proposes")
    assert rank.geographic_signal(india, ["india"]) == 1.0
    assert rank.geographic_signal(india, ["global"]) == 0.3
    assert rank.geographic_signal(by_prefix(ds, "AMD"), ["india"]) == 0.6


def test_personal_preferences_change_the_ranking():
    ds, _ = drafts()
    base = rank.rank_stories(ds, now=fx.NOW, regions=["global"])
    prefs = UserPreferences(
        topics=[TopicPreference(id="topic-india-tech", weight=1.0)], regions=["india"]
    )
    mine = rank.rank_stories(ds, now=fx.NOW, regions=["global"], preferences=prefs)
    pos = lambda r: [x.draft.article.title for x in r].index(  # noqa: E731
        next(x.draft.article.title for x in r if x.draft.article.title.startswith("India proposes"))
    )
    assert pos(mine) < pos(base)


def test_importance_tiers():
    assert rank.importance_tiers(0) == []
    assert rank.importance_tiers(1) == ["lead"]
    assert rank.importance_tiers(2) == ["lead", "standard"]
    tiers = rank.importance_tiers(12)
    assert tiers[0] == "lead" and tiers.count("lead") == 1
    assert tiers[1:4] == ["major"] * 3 and tiers[-3:] == ["minor"] * 3
    assert set(tiers) == {"lead", "major", "standard", "minor"}


# ---------------------------------------------------------------- personalize
def _article(**kw):
    base = dict(
        id="s1",
        title="t",
        summary="s",
        category="ai",
        source="Tech Ledger",
        source_url="https://x.com/a",
        published_at=fx.NOW,
        topics=["AI Agents", "RAG"],
        region="india",
    )
    return Article(**{**base, **kw})


def test_reasons_mirror_frontend_wording_and_include_region_and_source():
    prefs = UserPreferences(
        topics=[
            TopicPreference(id="topic-agents", weight=0.9),
            TopicPreference(id="topic-rag", weight=0.8),
        ],
        regions=["india"],
        sources=["source-tech-ledger"],
    )
    rel = personal_relevance(_article(), prefs)
    assert rel.level == "high"
    assert rel.reasons == [
        "Matches your interest in AI Agents",
        "Matches your interest in RAG",
        "Relevant to India",
        "From Tech Ledger, a source you follow",
    ]


def test_no_match_means_none_and_no_prefs_means_none():
    prefs = UserPreferences(topics=[TopicPreference(id="topic-sap", weight=1.0)])
    assert personal_relevance(_article(), prefs).level == "none"
    assert personal_relevance(_article(), None).level == "none"


def test_zero_weight_topics_are_ignored_and_levels_are_banded():
    prefs = UserPreferences(topics=[TopicPreference(id="topic-agents", weight=0.0)])
    assert personal_relevance(_article(region=None), prefs).level == "none"
    assert [relevance_level(x) for x in (0, 0.2, 0.5, 0.9)] == ["none", "low", "medium", "high"]


def test_personalized_selection_orders_by_fit_and_drops_non_matches():
    a = _article(id="a", topics=["RAG"], region=None)
    b = _article(id="b", topics=["AI Agents"], region=None)
    c = _article(id="c", topics=["SAP"], region=None)
    prefs = UserPreferences(
        topics=[
            TopicPreference(id="topic-agents", weight=0.9),
            TopicPreference(id="topic-rag", weight=0.4),
        ]
    )
    picked = personalize_stories([a, b, c], prefs, limit=4)
    assert [p.story_id for p in picked] == ["b", "a"]
    assert not hasattr(picked[0], "score")


def test_parse_preferences_is_lenient_and_validates():
    prefs = parse_preferences(
        topics="topic-agents:0.9, topic-rag, bad:xyz, big:7",
        regions="india, europe",
        sources="source-a",
    )
    assert prefs is not None
    assert [(t.id, t.weight) for t in prefs.topics] == [("topic-agents", 0.9), ("topic-rag", 0.7)]
    assert prefs.regions == ["india", "europe"] and prefs.sources == ["source-a"]
    assert parse_preferences(topics="", regions=None) is None
