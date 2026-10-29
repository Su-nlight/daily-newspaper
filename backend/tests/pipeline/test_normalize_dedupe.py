from datetime import timedelta

from app.pipeline.dedupe import (
    DedupeConfig,
    TfidfSimilarity,
    cluster_articles,
    normalize_title,
)
from app.pipeline.normalize import article_id, clean_title, normalize_item
from app.pipeline.schemas import RawItem
from app.pipeline.textutil import canonicalize_url, is_public_http_url, strip_markdown
from tests.pipeline import fixtures as fx


# ------------------------------------------------------------------ urls/text
def test_canonicalize_strips_tracking_fragment_www_and_sorts_query():
    url = "HTTP://www.Example.com:80/a//b/?utm_source=x&b=2&a=1&fbclid=z#frag"
    assert canonicalize_url(url) == "https://example.com/a/b?a=1&b=2"


def test_unsafe_or_internal_urls_are_not_public():
    for bad in (
        "javascript:alert(1)",
        "file:///etc/passwd",
        "ftp://x.com/a",
        "http://localhost/x",
        "http://127.0.0.1/x",
        "http://10.0.0.5/x",
        "https://intranet/x",
        "https://printer.local/x",
        "",
        None,
    ):
        assert not is_public_http_url(bad), bad
        assert canonicalize_url(bad) is None


def test_strip_markdown_keeps_link_labels():
    text = "## Fixes\n- Fixed [the bug](https://x.com/1) in `parser`\n- **Faster** startup"
    assert strip_markdown(text) == "Fixes Fixed the bug in parser Faster startup"


# ------------------------------------------------------------------ normalize
def test_universe_normalization_drops_bad_and_stale_items():
    cands, stats = fx.candidates()
    titles = [c.title for c in cands]
    assert stats.dropped_invalid == 1  # the javascript: link ("[Removed]" dies in the adapter)
    assert stats.dropped_stale == 1
    assert not any("Totally normal" in t or "very old article" in t for t in titles)


def test_normalized_candidate_has_spec_fields_and_clean_url():
    cands, _ = fx.candidates()
    c = fx.by_title(cands, "Nvidia unveils")
    assert c.url.endswith("utm_medium=feed")  # as published
    assert (
        c.canonical_url
        == "https://techcrunch.com/2026/11/03/nvidia-unveils-faster-ai-inference-chip"
    )
    assert c.id == article_id(c.canonical_url)
    assert "<p>" not in c.summary
    assert c.image == "https://techcrunch.com/wp-content/uploads/nvidia-chip.jpg"
    assert c.source == "TechCrunch" and c.source_id == "techcrunch"


def test_reuters_credited_via_aggregator():
    cands, _ = fx.candidates()
    c = fx.by_title(cands, "Nvidia launches")
    assert c.source == "Reuters" and c.source_id == "newsapi"


def _raw(**kw):
    base = dict(
        source_id="techcrunch",
        source_name="TechCrunch",
        kind="rss",
        title="A reasonable headline",
        url="https://techcrunch.com/a",
        summary="",
    )
    return RawItem(**{**base, **kw})


def test_missing_date_is_inferred_and_future_date_clamped():
    src = fx.SOURCES[0]
    undated = normalize_item(_raw(), src, now=fx.NOW)
    assert undated and undated.published_at == fx.NOW and undated.extra["date_inferred"]
    future = normalize_item(_raw(published_at=fx.NOW + timedelta(days=30)), src, now=fx.NOW)
    assert future and future.published_at == fx.NOW and future.extra["date_clamped"]


def test_title_suffix_only_stripped_when_it_is_the_publisher():
    assert clean_title("Big news - TechCrunch", "TechCrunch") == "Big news"
    assert clean_title("Foo - A New Hope", "TechCrunch") == "Foo - A New Hope"


def test_wordpress_boilerplate_removed_and_summary_not_equal_to_title():
    src = fx.SOURCES[0]
    c = normalize_item(
        _raw(summary="Real text here. The post Big thing appeared first on TechCrunch."),
        src,
        now=fx.NOW,
    )
    assert c and c.summary == "Real text here."
    same = normalize_item(
        _raw(title="A reasonable headline", summary="A reasonable headline"), src, now=fx.NOW
    )
    assert same and same.summary == ""


# --------------------------------------------------------------------- dedupe
def test_normalize_title_ignores_decoration():
    a = normalize_title("BREAKING: Nvidia Unveils New AI Chip - Reuters")
    b = normalize_title("Nvidia unveils new AI chip!")
    assert a == b == "nvidia unveils new ai chip"


def _clusters():
    cands, _ = fx.candidates()
    return cands, cluster_articles(cands)


def _find(clusters, prefix):
    return next(c for c in clusters if any(m.title.startswith(prefix) for m in c.members))


def test_same_event_in_three_publications_becomes_one_cluster():
    _, clusters = _clusters()
    event = _find(clusters, "Nvidia unveils")
    assert {m.source for m in event.members} == {"TechCrunch", "The Verge", "Reuters"}
    assert event.reasons == {"semantic"}


def test_lookalike_event_from_another_company_is_not_merged():
    _, clusters = _clusters()
    amd = _find(clusters, "AMD unveils")
    assert [m.source for m in amd.members] == ["Ars Technica"]


def test_same_publisher_similar_story_not_merged():
    _, clusters = _clusters()
    startup = _find(clusters, "Startup raises")
    assert len(startup.members) == 1


def test_cve_ids_merge_matching_and_separate_conflicting():
    _, clusters = _clusters()
    c1 = _find(clusters, "CVE-2026-12345")
    assert {m.source for m in c1.members} == {"NIST NVD", "BleepingComputer", "The Hacker News"}
    assert "cve" in c1.reasons
    c2 = _find(clusters, "Critical OpenSSL flaw CVE-2026-99999")
    assert len(c2.members) == 1  # near-identical prose, different CVE


def test_every_unrelated_item_is_its_own_story():
    cands, clusters = _clusters()
    assert sum(len(c.members) for c in clusters) == len(cands)
    assert len(clusters) == len(cands) - 4  # 3-way event + 3-way CVE merge


def test_identical_normalized_title_merges_across_sources_and_urls():
    cands, _ = fx.candidates()
    base = fx.by_title(cands, "Nvidia unveils")
    twin = base.model_copy(
        update={
            "id": "art-twin",
            "canonical_url": "https://other.com/x",
            "source": "Other Wire",
            "title": "BREAKING: Nvidia unveils new AI chip promising 40% faster inference - Other Wire",
            "summary": "different words entirely",
            "source_id": "ars",
        }
    )
    (cluster,) = cluster_articles([base, twin])
    assert cluster.reasons == {"title"}


def test_short_generic_titles_are_not_equated():
    cands, _ = fx.candidates()
    a = cands[0].model_copy(
        update={
            "id": "a",
            "canonical_url": "https://a.com/1",
            "title": "Weekly roundup",
            "summary": "alpha beta",
        }
    )
    b = cands[1].model_copy(
        update={
            "id": "b",
            "canonical_url": "https://b.com/1",
            "title": "Weekly roundup",
            "source": "Other",
            "summary": "gamma delta",
        }
    )
    assert len(cluster_articles([a, b])) == 2


def test_items_outside_the_time_window_do_not_merge_semantically():
    cands, _ = fx.candidates()
    tc = fx.by_title(cands, "Nvidia unveils")
    verge = fx.by_title(cands, "Nvidia's new").model_copy(
        update={"published_at": tc.published_at - timedelta(days=5)}
    )
    assert len(cluster_articles([tc, verge])) == 2
    assert len(cluster_articles([tc, verge], config=DedupeConfig(window_hours=24 * 10))) == 1


def test_chain_of_pairwise_similar_items_is_not_collapsed():
    """A~B and B~C but A!~C: average-link must stop the chain from merging."""
    cands, _ = fx.candidates()
    mk = lambda i, src, text: cands[0].model_copy(
        update={  # noqa: E731
            "id": f"c{i}",
            "canonical_url": f"https://x{i}.com/p",
            "source": src,
            "title": text,
            "summary": text,
        }
    )
    a = mk(1, "A", "quantum battery prototype lithium anode cathode")
    b = mk(2, "B", "quantum battery prototype solar panel efficiency record")
    c = mk(3, "C", "solar panel efficiency record perovskite tandem cell")
    d = mk(4, "D", "perovskite tandem cell commercial production plant")
    clusters = cluster_articles([a, b, c, d])
    assert max(len(c.members) for c in clusters) < 4


def test_clustering_is_deterministic_regardless_of_input_order():
    cands, _ = fx.candidates()
    forward = cluster_articles(cands)
    backward = cluster_articles(list(reversed(cands)))
    sig = lambda cl: sorted(tuple(sorted(m.id for m in c.members)) for c in cl)  # noqa: E731
    assert sig(forward) == sig(backward)


def test_pluggable_similarity_model():
    """The embedding seam: any object with similarity()/candidate_pairs() works."""
    cands, _ = fx.candidates()
    a, b = cands[0], cands[3]

    class AlwaysSame:
        def __init__(self, items):
            self.n = len(items)  # noqa: E704

        def similarity(self, i, j):
            return 0.99  # noqa: E704

        def candidate_pairs(self):
            return [(0, 1)]  # noqa: E704

    assert len(cluster_articles([a, b], model_factory=AlwaysSame)) == 1
    assert len(cluster_articles([a, b], model_factory=TfidfSimilarity)) == 2
