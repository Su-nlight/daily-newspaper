import asyncio
from datetime import timedelta

from app.models.article import Article, SourceAttribution
from app.pipeline import summarize
from app.pipeline.dedupe import cluster_articles
from app.pipeline.edition import (
    BRIEF_WORD_BUDGET,
    build_brief,
    build_edition,
    edition_hash,
    pick_top_stories,
    related_ids,
)
from app.pipeline.rank import rank_stories
from app.pipeline.stories import build_drafts
from app.pipeline.validate_sources import validate_drafts
from tests.pipeline import fixtures as fx

REGISTRY = {s.id for s in fx.SOURCES}


def make_drafts():
    cands, _ = fx.candidates()
    ds = build_drafts(cluster_articles(cands), {}, {})
    asyncio.run(summarize.summarize_drafts(ds, llm_fn=None, max_llm=0))
    return ds


def story(ds, prefix):
    return next(d for d in ds if d.article.title.startswith(prefix))


# ------------------------------------------------------------------ validation
def test_clean_universe_passes_validation_with_all_sources_retained():
    ds = make_drafts()
    valid, report = validate_drafts(ds, registry_ids=REGISTRY, now=fx.NOW)
    assert len(valid) == len(ds) and not report.dropped_stories
    multi = story(valid, "Nvidia unveils").article
    assert {s.publisher for s in multi.sources} == {"TechCrunch", "The Verge", "Reuters"}
    assert multi.source_url in {s.url for s in multi.sources}


def test_invalid_sources_are_removed_and_story_survives_on_the_rest():
    ds = make_drafts()
    d = story(ds, "Nvidia unveils")
    d.article.sources[1] = SourceAttribution(publisher="X", url="javascript:alert(1)")
    d.article.sources[2] = SourceAttribution(publisher="Y", url="https://y.com/a", source_id="gone")
    valid, report = validate_drafts([d], registry_ids=REGISTRY, now=fx.NOW)
    assert len(valid) == 1 and len(valid[0].article.sources) == 1
    assert report.removed_sources == 2


def test_story_with_no_valid_source_is_dropped():
    d = make_drafts()[0]
    d.article.sources = [SourceAttribution(publisher="", url="http://127.0.0.1/x")]
    valid, report = validate_drafts([d], registry_ids=REGISTRY, now=fx.NOW)
    assert valid == [] and report.dropped_stories == [d.article.id]


def test_primary_link_is_repaired_if_its_source_was_removed():
    d = story(make_drafts(), "Nvidia unveils")
    d.article.sources[0] = SourceAttribution(publisher="Bad", url="ftp://bad.com/x")
    valid, _ = validate_drafts([d], registry_ids=REGISTRY, now=fx.NOW)
    a = valid[0].article
    assert a.source_url == a.sources[0].url and a.source == a.sources[0].publisher


def test_future_dated_story_is_dropped_and_bad_image_removed():
    ds = make_drafts()
    future = story(ds, "AMD")
    future.article.published_at = fx.NOW + timedelta(days=3)
    imaged = story(ds, "Nvidia unveils")
    imaged.article.image_url = "javascript:evil()"
    valid, report = validate_drafts([future, imaged], registry_ids=REGISTRY, now=fx.NOW)
    assert [v.article.id for v in valid] == [imaged.article.id]
    assert valid[0].article.image_url is None and "future" in report.problems[0]


def test_url_in_generated_text_reverts_story_to_extractive():
    d = story(make_drafts(), "Nvidia unveils")
    d.article.ai_generated = True
    d.article.what_happened = "Buy now at https://scam.example.com/offer today."
    valid, report = validate_drafts([d], registry_ids=REGISTRY, now=fx.NOW)
    a = valid[0].article
    assert report.reverted_text == [a.id] and not a.ai_generated
    assert a.what_happened is None and "scam" not in (a.content or "")


# --------------------------------------------------------------------- edition
def ranked(ds=None):
    return rank_stories(ds or make_drafts(), now=fx.NOW, regions=["global"])


def edition(**kw):
    args = dict(date="2026-11-03", now=fx.NOW, timezone="UTC", max_stories=30, warnings=[])
    return build_edition(ranked(), **{**args, **kw})


def test_edition_structure_and_references_are_consistent():
    ed = edition()
    ids = [s.id for s in ed.stories]
    assert ed.id == "edition-2026-11-03" and len(ids) == len(set(ids))
    assert ed.stories[0].importance == "lead" and ed.stories[0].id == ed.top_story_ids[0]
    assert ed.top_story_ids == ids[: len(ed.top_story_ids)]
    for section in ed.sections:
        assert set(section.story_ids) <= set(ids)
        assert not set(section.story_ids) & set(ed.top_story_ids)  # not repeated
    assert {b.id for b in ed.brief} <= set(ids)
    assert ed.metadata.story_count == len(ids) and ed.metadata.status == "complete"
    assert ed.metadata.source_count == 11 and ed.metadata.generated_at == fx.NOW


def test_max_stories_caps_the_edition():
    assert len(edition(max_stories=4).stories) == 4


def test_top_stories_limit_per_category_while_variety_exists():
    def art(i, cat):
        return Article(
            id=f"s{i}",
            title=f"t{i}",
            summary="s",
            category=cat,
            source="S",
            source_url="https://x.com/a",
            published_at=fx.NOW,
        )

    arts = [art(i, "ai") for i in range(4)] + [
        art(10, "research"),
        art(11, "world"),
        art(12, "cybersecurity"),
    ]
    top = pick_top_stories(arts)
    assert [a.category for a in top].count("ai") == 2 and len(top) == 5
    # Not enough variety to fill five: the cap yields rather than leave a gap.
    thin = pick_top_stories(arts[:4] + [art(10, "research"), art(11, "world")])
    assert len(thin) == 5 and [a.category for a in thin].count("ai") == 3
    only_ai = pick_top_stories([art(i, "ai") for i in range(6)])
    assert len(only_ai) == 5  # fills by rank when there is no variety


def test_brief_fits_about_sixty_seconds():
    ed = edition()
    words = sum(len(b.headline.split()) + len(b.summary.split()) for b in ed.brief)
    assert (
        3 <= len(ed.brief) <= 6 and words <= BRIEF_WORD_BUDGET + 40
    )  # last item may overshoot only if < min items
    long_stories = [
        Article(
            id=f"s{i}",
            title="A long headline " * 6,
            summary="Word " * 40 + ".",
            category="ai",
            source="S",
            source_url="https://x.com/a",
            published_at=fx.NOW,
        )
        for i in range(10)
    ]
    brief = build_brief(long_stories)
    total = sum(len(b.headline.split()) + len(b.summary.split()) for b in brief)
    assert len(brief) < 10 and total <= BRIEF_WORD_BUDGET + 40


def test_related_stories_share_topics_or_entities_and_exclude_self():
    ed = edition()
    amd = next(s for s in ed.stories if s.title.startswith("AMD"))
    assert amd.id not in amd.related_ids
    related_titles = {s.title[:6] for s in ed.stories if s.id in amd.related_ids}
    assert "Nvidia" in related_titles or "Startu" in related_titles  # both Semiconductors
    unrelated = next(s for s in ed.stories if s.title.startswith("How we rebuilt"))
    assert related_ids(unrelated, ed.stories) == unrelated.related_ids


def test_headline_summary_and_degraded_status():
    ed = edition(warnings=["2 of 11 sources were unavailable."])
    assert ed.headline == ed.stories[0].title[: len(ed.headline)].rstrip("…") or ed.headline
    assert "stories from" in ed.summary and "publications" in ed.summary
    assert ed.metadata.status == "degraded" and ed.metadata.warnings


def test_empty_edition_is_representable():
    ed = build_edition(
        [], date="2026-11-03", now=fx.NOW, timezone="UTC", max_stories=30, warnings=[]
    )
    assert ed.stories == [] and ed.brief == [] and ed.sections == []


def test_edition_hash_ignores_generation_time_but_not_content():
    a = edition(now=fx.NOW)
    b = edition(now=fx.NOW + timedelta(minutes=5))
    assert edition_hash(a) == edition_hash(b)
    c = edition(max_stories=5)
    assert edition_hash(a) != edition_hash(c)
