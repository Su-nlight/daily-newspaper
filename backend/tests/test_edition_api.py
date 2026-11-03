"""Module 09 read side: /api/edition/* over pipeline-generated content."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app
from app.pipeline.store import Store, get_store
from tests.pipeline import fixtures as fx

client = TestClient(app)

SEED_STORY = "story-ai-policy-2026"
SEED_DATE = "2026-09-22"


@pytest.fixture
def pipeline_db(tmp_path, monkeypatch):
    """A database holding a real pipeline-built edition (fixtures, no network)."""
    path = tmp_path / "pipeline.db"
    settings = Settings(database_path=str(path), newsapi_key="k", pipeline_use_llm=False)
    store = Store(path)
    fx.run_pipeline_sync(settings, store)
    monkeypatch.setenv("DATABASE_PATH", str(path))
    get_settings.cache_clear()
    get_store.cache_clear()
    return store


def keys_anywhere(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from keys_anywhere(value)
    elif isinstance(node, list):
        for item in node:
            yield from keys_anywhere(item)


# --------------------------------------------------------------------- contract
def test_today_returns_the_full_edition_contract(pipeline_db):
    body = client.get("/api/edition/today").json()
    assert set(body) >= {
        "id", "date", "headline", "summary", "stories",
        "metadata", "top_story_ids", "sections", "brief", "personalized",
    }  # fmt: skip
    assert body["id"] == "edition-2026-11-03" and body["date"] == "2026-11-03"
    meta = body["metadata"]
    assert meta["status"] == "complete" and meta["story_count"] == len(body["stories"]) == 9
    assert meta["source_count"] == 11 and meta["pipeline_version"] and meta["generated_at"]
    assert meta["personalization_applied"] is False and body["personalized"] == []


def test_edition_references_resolve_to_stories(pipeline_db):
    body = client.get("/api/edition/today").json()
    ids = {s["id"] for s in body["stories"]}
    assert set(body["top_story_ids"]) <= ids
    assert body["stories"][0]["id"] == body["top_story_ids"][0]
    assert all(set(sec["story_ids"]) <= ids for sec in body["sections"])
    assert {b["id"] for b in body["brief"]} <= ids
    for story in body["stories"]:
        assert set(story["related_ids"]) <= ids and story["id"] not in story["related_ids"]


def test_every_story_exposes_the_spec_article_fields_and_its_sources(pipeline_db):
    for s in client.get("/api/edition/today").json()["stories"]:
        for field in ("id", "title", "summary", "content", "source", "source_url", "published_at",
                      "category", "topics", "entities", "image_url", "importance",
                      "personal_relevance", "sources"):  # fmt: skip
            assert field in s, field
        assert s["importance"] in {"lead", "major", "standard", "minor"}
        assert s["sources"] and s["source_url"] in {x["url"] for x in s["sources"]}
        assert all(x["url"].startswith("https://") for x in s["sources"])


def test_no_raw_scores_are_exposed_anywhere(pipeline_db):
    body = client.get(
        "/api/edition/today?topics=topic-agents:0.9&regions=india&sources=source-inc42"
    ).json()
    for key in keys_anywhere(body):
        assert "score" not in key.lower() and "weight" not in key.lower(), key
    numeric = [
        v
        for s in body["stories"]
        for k, v in s.items()
        if isinstance(v, int | float) and not isinstance(v, bool)
    ]
    assert numeric == []  # nothing numeric on a story: tiers and reasons only


def test_multi_source_story_lists_every_publisher(pipeline_db):
    nvidia = next(
        s
        for s in client.get("/api/edition/today").json()["stories"]
        if s["title"].startswith("Nvidia")
    )
    assert {x["publisher"] for x in nvidia["sources"]} == {"TechCrunch", "The Verge", "Reuters"}


def test_edition_by_date(pipeline_db):
    assert client.get("/api/edition/2026-11-03").json()["id"] == "edition-2026-11-03"
    assert client.get("/api/edition/1999-01-01").status_code == 404


# -------------------------------------------------------------- personalization
def test_preferences_add_personalized_stories_with_reasons(pipeline_db):
    body = client.get("/api/edition/today?topics=topic-india-tech:0.9&regions=india").json()
    assert body["metadata"]["personalization_applied"] is True
    (first, *_) = body["personalized"]
    story = next(s for s in body["stories"] if s["id"] == first["story_id"])
    assert story["title"].startswith("India proposes")
    assert first["level"] in {"medium", "high"}
    assert "Matches your interest in India Tech" in first["reasons"]
    assert "Relevant to India" in first["reasons"]
    assert story["personal_relevance"]["reasons"] == first["reasons"]
    others = [s for s in body["stories"] if s["id"] != story["id"]]
    assert all(s["personal_relevance"]["level"] == "none" for s in others)


def test_personalization_never_changes_the_shared_edition(pipeline_db):
    plain = client.get("/api/edition/today").json()
    client.get("/api/edition/today?topics=topic-rag:1.0")
    assert client.get("/api/edition/today").json() == plain


def test_garbage_preferences_are_ignored_not_errors(pipeline_db):
    body = client.get("/api/edition/today?topics=:::,x:notanumber&regions=").json()
    assert body["metadata"]["personalization_applied"] is False


def test_personalized_list_is_capped(pipeline_db):
    body = client.get(
        "/api/edition/today?topics=topic-semiconductors,topic-cybersecurity,topic-research,"
        "topic-agents,topic-india-tech"
    ).json()
    assert 1 <= len(body["personalized"]) <= 4


# --------------------------------------------------------- content_source modes
def test_auto_mode_without_a_pipeline_serves_seed(monkeypatch):
    body = client.get("/api/edition/today").json()
    assert body["metadata"]["status"] == "seed" and body["stories"]


def test_auto_mode_prefers_pipeline_but_resolves_seed_ids_and_dates(pipeline_db):
    assert client.get("/api/edition/today").json()["metadata"]["status"] == "complete"
    assert client.get(f"/api/edition/{SEED_DATE}").status_code == 200  # frontend mock archive
    assert client.get(f"/api/stories/{SEED_STORY}").status_code == 200  # mock story ids in chat


def test_listing_and_search_never_mix_seed_into_real_results(pipeline_db):
    ids = {s["id"] for s in client.get("/api/stories").json()}
    assert SEED_STORY not in ids and len(ids) == 9
    hits = client.get("/api/search", params={"q": "Nvidia chip"}).json()
    assert hits and all(
        h["source_url"].startswith("https://") and "example.com" not in h["source_url"]
        for h in hits
    )


def test_pipeline_mode_never_falls_back_to_seed(pipeline_db, monkeypatch):
    monkeypatch.setenv("CONTENT_SOURCE", "pipeline")
    get_settings.cache_clear()
    assert client.get(f"/api/edition/{SEED_DATE}").status_code == 404
    assert client.get(f"/api/stories/{SEED_STORY}").status_code == 404
    assert client.get("/api/edition/today").json()["metadata"]["status"] == "complete"


def test_pipeline_mode_before_first_run_is_a_clear_404(monkeypatch):
    monkeypatch.setenv("CONTENT_SOURCE", "pipeline")
    get_settings.cache_clear()
    response = client.get("/api/edition/today")
    assert response.status_code == 404 and "No edition" in response.json()["detail"]
    assert client.get("/api/stories").json() == []


def test_seed_mode_ignores_an_existing_pipeline(pipeline_db, monkeypatch):
    monkeypatch.setenv("CONTENT_SOURCE", "seed")
    get_settings.cache_clear()
    assert client.get("/api/edition/today").json()["metadata"]["status"] == "seed"
    assert client.get(f"/api/stories/{SEED_STORY}").status_code == 200


def test_reading_never_creates_a_database_file(tmp_path, monkeypatch):
    path = tmp_path / "should-not-appear.db"
    monkeypatch.setenv("DATABASE_PATH", str(path))
    get_settings.cache_clear()
    client.get("/api/edition/today")
    client.get("/api/stories")
    assert not path.exists()


def test_latest_edition_is_served_even_if_todays_run_has_not_happened(pipeline_db):
    # "today" means the most recent edition; its date tells the client how fresh it is.
    assert client.get("/api/edition/today").json()["date"] == "2026-11-03"


def test_editions_list_includes_pipeline_and_seed_dates(pipeline_db):
    from app.services import sources

    dates = [e.date for e in sources.list_editions()]
    assert dates[0] == "2026-11-03" and SEED_DATE in dates and len(dates) == len(set(dates))


# ------------------------------------------------------------ chat compatibility
def test_chat_is_grounded_in_pipeline_stories_and_cites_their_primary_source(pipeline_db):
    story = next(
        s
        for s in client.get("/api/edition/today").json()["stories"]
        if s["title"].startswith("Nvidia")
    )
    with patch("app.services.llm.generate_completion", return_value="It is 40% faster [1]."):
        body = client.post(
            "/api/chat",
            json={"message": "summarize this story", "context": {"story_id": story["id"]}},
        ).json()
    assert body["sources"][0]["url"] == story["source_url"]
    assert body["sources"][0]["publisher"] == story["source"]


def test_chat_context_still_resolves_frontend_mock_story_ids(pipeline_db):
    with patch("app.services.llm.generate_completion", return_value="It matters [1]."):
        body = client.post(
            "/api/chat",
            json={"message": "why does this matter", "context": {"story_id": SEED_STORY}},
        ).json()
    assert body["sources"] and body["sources"][0]["url"].startswith("https://")
