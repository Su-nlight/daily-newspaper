import json
import sqlite3
from datetime import timedelta

import httpx
import pytest

from app.config import Settings
from app.pipeline.__main__ import main
from app.pipeline.runner import LOCK_NAME
from app.pipeline.store import Store
from tests.pipeline import fixtures as fx
from tests.pipeline.test_grounding_summarize import GOOD, FakeLLM


@pytest.fixture
def env(tmp_path):
    settings = Settings(
        database_path=str(tmp_path / "p.db"), newsapi_key="k", pipeline_use_llm=False
    )
    return settings, Store(settings.resolved_database_path)


def counts(store: Store) -> dict[str, int]:
    with sqlite3.connect(store.path) as conn:
        return {
            t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in ("articles", "stories", "story_members", "editions")
        }


# ----------------------------------------------------------------- happy path
def test_first_run_builds_a_complete_edition(env):
    settings, store = env
    r = fx.run_pipeline_sync(settings, store)
    assert r.status == "ok" and r.edition_written and r.edition_id == "edition-2026-11-03"
    assert r.new_articles == 13 and r.stories_created == 9 and r.multi_source_stories == 2
    assert (r.dropped_invalid, r.dropped_stale) == (1, 1)
    assert all(s.ok for s in r.sources) and len(r.sources) == 11
    ed = store.latest_edition()
    assert ed and ed.metadata.status == "complete" and len(ed.stories) == 9
    assert counts(store) == {"articles": 13, "stories": 9, "story_members": 13, "editions": 1}


def test_every_story_in_the_edition_retains_its_sources(env):
    settings, store = env
    fx.run_pipeline_sync(settings, store)
    ed = store.latest_edition()
    for s in ed.stories:
        assert s.sources and s.source_url in {x.url for x in s.sources}
        assert all(x.url.startswith("https://") and x.publisher for x in s.sources)
    nvidia = next(s for s in ed.stories if s.title.startswith("Nvidia"))
    assert {x.publisher for x in nvidia.sources} == {"TechCrunch", "The Verge", "Reuters"}
    # canonical (tracking-free) URL is stored for dedupe; the article link is kept as published
    assert "techcrunch.com/2026/11/03/nvidia-unveils" in nvidia.source_url


# ----------------------------------------------------------------- idempotency
def test_running_twice_creates_no_duplicates_and_changes_nothing(env):
    settings, store = env
    first = fx.run_pipeline_sync(settings, store)
    snapshot = counts(store)
    stories_before = {s.id: s.model_dump_json() for s in store.list_stories()}
    edition_before = store.latest_edition().model_dump_json()

    second = fx.run_pipeline_sync(settings, store)
    assert second.new_articles == 0 and second.changed_articles == 0
    assert (second.stories_created, second.stories_updated) == (0, 0)
    assert second.stories_unchanged == first.stories_created
    assert second.edition_written is False
    assert counts(store) == snapshot
    assert {s.id: s.model_dump_json() for s in store.list_stories()} == stories_before
    assert store.latest_edition().model_dump_json() == edition_before


def test_many_reruns_stay_stable(env):
    settings, store = env
    fx.run_pipeline_sync(settings, store)
    ids = {s.id for s in store.list_stories()}
    for minutes in (5, 30, 90):  # later runs of the same day: fresher `now`
        fx.run_pipeline_sync(settings, store, now=fx.NOW + timedelta(minutes=minutes))
    assert {s.id for s in store.list_stories()} == ids
    assert counts(store)["editions"] == 1


def test_story_gains_a_source_on_a_later_run_keeping_its_id(env):
    settings, store = env
    early = fx.universe_routes()
    early["newsapi.org/v2/top-headlines"] = fx.newsapi_payload([])  # Reuters hasn't published yet
    fx.run_pipeline_sync(settings, store, routes=early)
    before = next(s for s in store.list_stories() if s.title.startswith("Nvidia"))
    assert {x.publisher for x in before.sources} == {"TechCrunch", "The Verge"}
    n_stories = counts(store)["stories"]

    later = fx.run_pipeline_sync(settings, store, now=fx.NOW + timedelta(hours=1))
    after = next(s for s in store.list_stories() if s.title.startswith("Nvidia"))
    assert after.id == before.id  # same story, not a new one
    assert {x.publisher for x in after.sources} == {"TechCrunch", "The Verge", "Reuters"}
    assert counts(store)["stories"] == n_stories
    assert later.stories_updated >= 1 and later.edition_written


def test_merging_two_existing_stories_retires_the_younger_id(env):
    """If two clusters later turn out to be one event, one story id survives."""
    settings, store = env
    split = fx.universe_routes()
    # Run 1: the Verge piece is unrelated wording, so it stands alone.
    split["www.theverge.com/rss/index.xml"] = fx.atom(
        [
            {
                "title": "Chipmaker reveals silicon for datacenter inference",
                "link": "https://www.theverge.com/2026/11/3/chipmaker-reveals-silicon",
                "summary": "A new accelerator for datacenter inference workloads.",
                "published": fx.ago(hours=4),
            }
        ]
    )
    fx.run_pipeline_sync(settings, store, routes=split)
    fx.run_pipeline_sync(
        settings, store, now=fx.NOW + timedelta(minutes=10)
    )  # universe: bridging item
    ids = [s.id for s in store.list_stories()]
    assert len(ids) == len(set(ids))
    with sqlite3.connect(store.path) as conn:
        orphans = conn.execute(
            "SELECT COUNT(*) FROM stories WHERE id NOT IN (SELECT story_id FROM story_members)"
        ).fetchone()[0]
    assert orphans == 0


# -------------------------------------------------------------------- failures
def test_one_failing_source_degrades_but_does_not_stop_the_run(env):
    settings, store = env
    routes = fx.universe_routes()
    routes["www.theverge.com/rss/index.xml"] = httpx.ConnectError("down")
    r = fx.run_pipeline_sync(settings, store, routes=routes)
    assert r.status == "degraded" and r.edition_written
    assert any("1 of 11 sources" in w for w in r.warnings)
    ed = store.latest_edition()
    assert ed.metadata.status == "degraded" and "1 of 11" in ed.metadata.warnings[0]
    nvidia = next(s for s in ed.stories if s.title.startswith("Nvidia"))
    assert {x.publisher for x in nvidia.sources} == {"TechCrunch", "Reuters"}


def test_all_sources_failing_with_empty_store_is_a_clean_failure(env):
    settings, store = env
    r = fx.run_pipeline_sync(settings, store, routes={})
    assert r.status == "failed" and not r.edition_written
    assert store.latest_edition() is None
    assert any("No articles" in w for w in r.warnings)


def test_all_sources_failing_still_serves_from_stored_articles(env):
    settings, store = env
    fx.run_pipeline_sync(settings, store)
    r = fx.run_pipeline_sync(settings, store, routes={}, now=fx.NOW + timedelta(hours=1))
    assert r.status == "degraded" and r.edition_id
    assert len(store.latest_edition().stories) >= 9


def test_a_much_thinner_edition_never_replaces_a_healthy_one(env):
    """E.g. a sources file accidentally trimmed to one entry: the rebuilt
    edition would be a fraction of the size, so the healthy one is kept."""
    settings, store = env
    fx.run_pipeline_sync(settings, store)
    healthy = store.latest_edition().model_dump_json()
    only_inc42 = [s for s in fx.SOURCES if s.id == "inc42"]
    r = fx.run_pipeline_sync(
        settings, store, sources=only_inc42, fetch=False, now=fx.NOW + timedelta(minutes=5)
    )
    assert r.status == "degraded" and not r.edition_written
    assert any("much smaller" in w for w in r.warnings)
    assert store.get_edition_by_date("2026-11-03").model_dump_json() == healthy


def test_sources_missing_credentials_are_skipped_not_fetched(tmp_path):
    settings = Settings(
        database_path=str(tmp_path / "p.db"), pipeline_use_llm=False
    )  # no newsapi key
    store = Store(settings.resolved_database_path)
    calls: list[httpx.Request] = []
    import asyncio

    from app.pipeline.runner import run_pipeline

    async def go():
        async with httpx.AsyncClient(transport=fx.transport(fx.universe_routes(), calls)) as c:
            return await run_pipeline(
                settings=settings,
                store=store,
                client=c,
                sources=fx.SOURCES,
                now=fx.NOW,
                retry_delay=0,
            )

    r = asyncio.run(go())
    assert any("NEWSAPI_KEY" in s for s in r.skipped_sources)
    assert not any("newsapi.org" in str(c.url) for c in calls)
    assert all(s.source_id != "newsapi" for s in r.sources)


def test_a_source_removed_from_config_stops_contributing_stored_articles(env):
    settings, store = env
    fx.run_pipeline_sync(settings, store)
    fewer = [s for s in fx.SOURCES if s.id != "verge"]
    fx.run_pipeline_sync(
        settings, store, sources=fewer, fetch=False, now=fx.NOW + timedelta(minutes=5)
    )
    nvidia = next(s for s in store.latest_edition().stories if s.title.startswith("Nvidia"))
    assert "The Verge" not in {x.publisher for x in nvidia.sources}


def test_overlapping_runs_are_prevented_by_the_lock(env):
    settings, store = env
    assert store.acquire_lock(LOCK_NAME, fx.NOW, timedelta(minutes=30))
    r = fx.run_pipeline_sync(settings, store)
    assert r.status == "skipped" and store.latest_edition() is None
    # an expired lock (crashed run) does not block forever
    r2 = fx.run_pipeline_sync(settings, store, now=fx.NOW + timedelta(hours=1))
    assert r2.status == "ok"
    assert store.acquire_lock(LOCK_NAME, fx.NOW + timedelta(hours=2), timedelta(minutes=30))


def test_lock_is_released_even_if_a_stage_crashes(env, monkeypatch):
    settings, store = env
    import app.pipeline.runner as runner

    monkeypatch.setattr(
        runner, "cluster_articles", lambda *_: (_ for _ in ()).throw(RuntimeError("x"))
    )
    with pytest.raises(RuntimeError):
        fx.run_pipeline_sync(settings, store)
    assert store.acquire_lock(LOCK_NAME, fx.NOW, timedelta(minutes=1))


# ------------------------------------------------------------------------ LLM
def test_llm_summaries_are_used_only_where_grounded_and_reused_on_rerun(env):
    settings, store = env
    fake = FakeLLM(GOOD)
    r = fx.run_pipeline_sync(settings, store, llm_fn=fake)
    assert r.summaries_llm == 1 and r.summaries_extractive == 8  # GOOD only fits the Nvidia story
    assert r.summary_fallback_reasons.get("ungrounded") == 8
    ed = store.latest_edition()
    ai = [s for s in ed.stories if s.ai_generated]
    assert (
        len(ai) == 1 and ai[0].title.startswith("Nvidia") and ed.metadata.ai_summarized_count == 1
    )

    calls_after_first = len(fake.calls)
    r2 = fx.run_pipeline_sync(settings, store, llm_fn=fake)
    assert r2.summaries_reused >= 1 and r2.stories_updated == 0
    # the 8 extractive stories are retried (a model is available) but the grounded one is reused
    assert len(fake.calls) == calls_after_first + 8


def test_llm_budget_is_respected(env):
    settings, store = env
    settings = settings.model_copy(update={"pipeline_max_llm_stories": 2})
    fake = FakeLLM(GOOD)
    r = fx.run_pipeline_sync(settings, store, llm_fn=fake)
    assert len(fake.calls) == 2 and r.summary_fallback_reasons.get("llm_budget_exhausted") == 7


def test_pipeline_without_groq_key_still_produces_a_full_edition(env):
    settings, store = env
    r = fx.run_pipeline_sync(settings.model_copy(update={"pipeline_use_llm": True}), store)
    assert r.summaries_llm == 0 and r.summaries_extractive == 9 and r.status == "ok"


# ------------------------------------------------------------------ date logic
def test_regenerating_a_past_edition_only_uses_articles_published_by_then(env):
    settings, store = env
    fx.run_pipeline_sync(settings, store)
    r = fx.run_pipeline_sync(settings, store, edition_date="2026-11-02", fetch=False)
    past = store.get_edition_by_date("2026-11-02")
    assert past and r.edition_id == "edition-2026-11-02"
    assert max(s.published_at for s in past.stories) <= fx.NOW.replace(hour=0)
    assert len(past.stories) < len(store.get_edition_by_date("2026-11-03").stories)


def test_edition_date_follows_the_configured_timezone(env):
    settings, store = env
    ist = settings.model_copy(update={"edition_timezone": "Asia/Kolkata"})
    late = fx.NOW.replace(hour=20)  # 20:00 UTC == 01:30 next day in IST
    fx.run_pipeline_sync(ist, store, now=late)
    assert store.latest_edition().date == "2026-11-04"


# ----------------------------------------------------------------------- store
def test_candidate_upsert_is_idempotent_and_detects_edits(env):
    _, store = env
    cands, _ = fx.candidates()
    assert store.upsert_candidates(cands) == (13, 0)
    again = [c.model_copy(update={"fetched_at": fx.NOW + timedelta(hours=1)}) for c in cands]
    assert store.upsert_candidates(again) == (0, 0)  # only fetch time differs
    edited = [cands[0].model_copy(update={"summary": "A materially edited summary."})]
    assert store.upsert_candidates(edited) == (0, 1)
    assert counts(store)["articles"] == 13


def test_canonical_url_uniqueness_is_enforced_by_the_database(env):
    _, store = env
    cands, _ = fx.candidates()
    store.upsert_candidates(cands[:1])
    with sqlite3.connect(store.path) as conn, pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO articles VALUES ('other-id', ?, 's', 't', 't', '{}')",
            (cands[0].canonical_url,),
        )


def test_prune_removes_old_stories_but_keeps_editions(env):
    settings, store = env
    fx.run_pipeline_sync(settings, store)
    removed = store.prune(fx.NOW + timedelta(days=1))
    assert removed == 9 and counts(store)["stories"] == 0 and counts(store)["articles"] == 0
    assert counts(store)["editions"] == 1


def test_run_reports_are_recorded(env):
    settings, store = env
    fx.run_pipeline_sync(settings, store)
    (run,) = store.recent_runs()
    assert run["status"] == "ok" and run["edition_id"] == "edition-2026-11-03"


def test_the_report_never_contains_secrets(env):
    settings, store = env
    settings = settings.model_copy(update={"newsapi_key": "TOP-SECRET-KEY"})
    r = fx.run_pipeline_sync(settings, store)
    assert "TOP-SECRET-KEY" not in r.model_dump_json()
    assert "TOP-SECRET-KEY" not in json.dumps(store.recent_runs())


# ------------------------------------------------------------------------- CLI
def test_cli_sources_and_status(capsys, monkeypatch):
    assert main(["sources"]) == 0
    out = capsys.readouterr().out
    assert "techcrunch" in out and "arxiv" in out and "nvd-critical" in out
    assert "newsapi-tech" in out and "inactive" in out
    assert main(["status"]) == 0
    assert "latest edition: none" in capsys.readouterr().out


def test_cli_run_with_nothing_to_build_exits_nonzero(capsys):
    assert main(["run", "--no-fetch", "--no-llm"]) == 1
    assert "failed" in capsys.readouterr().out


def test_bundled_sources_file_is_valid():
    from app.pipeline.registry import load_sources

    sources = load_sources()
    assert len({s.id for s in sources}) == len(sources) >= 15
    kinds = {s.kind for s in sources}
    assert {"rss", "blog", "arxiv", "github", "nvd", "news_api"} <= kinds
    for s in sources:
        assert s.url.startswith("https://")
        assert s.api_key_setting is None or hasattr(Settings(), s.api_key_setting)
