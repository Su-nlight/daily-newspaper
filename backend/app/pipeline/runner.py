"""The orchestrator: runs every stage in order and reports what happened.

    lock -> fetch -> normalize -> store -> cluster -> assemble -> summarize
         -> validate -> rank -> edition -> save -> prune

Idempotent by construction (Module 09: "Running it twice should not create
duplicate stories"):
* articles are keyed by canonical URL (a DB UNIQUE constraint);
* stories keep the id of the first run that saw any of their articles
  (`stories.assign_story_ids`), so a story that gains a source is *updated*;
* an edition is keyed by its date, and an identical rebuild writes nothing;
* unchanged stories reuse their summaries, so reruns don't re-spend LLM calls;
* an advisory lock stops two overlapping scheduled runs from colliding.
"""

import logging
import time
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import httpx
from pydantic import BaseModel, Field

from app.config import Settings, get_settings
from app.pipeline import summarize
from app.pipeline.dedupe import cluster_articles
from app.pipeline.edition import build_edition, edition_hash
from app.pipeline.fetch import SourceReport, fetch_all
from app.pipeline.normalize import normalize_items
from app.pipeline.rank import rank_stories
from app.pipeline.registry import active_sources, load_sources
from app.pipeline.schemas import SourceConfig
from app.pipeline.store import Store, get_store
from app.pipeline.stories import build_drafts
from app.pipeline.validate_sources import validate_drafts

logger = logging.getLogger("daily_signal.pipeline")

LOCK_NAME = "pipeline"
LOCK_TTL = timedelta(minutes=30)


class PipelineReport(BaseModel):
    status: str = "ok"  # ok | degraded | failed | skipped
    edition_id: str | None = None
    edition_date: str | None = None
    edition_written: bool = False

    sources: list[SourceReport] = Field(default_factory=list)
    skipped_sources: list[str] = Field(default_factory=list)

    fetched: int = 0
    normalized: int = 0
    dropped_invalid: int = 0
    dropped_stale: int = 0
    new_articles: int = 0
    changed_articles: int = 0

    stories_total: int = 0
    multi_source_stories: int = 0
    stories_created: int = 0
    stories_updated: int = 0
    stories_unchanged: int = 0

    summaries_llm: int = 0
    summaries_reused: int = 0
    summaries_extractive: int = 0
    summary_fallback_reasons: dict[str, int] = Field(default_factory=dict)

    validation_dropped: int = 0
    validation_removed_sources: int = 0
    validation_reverted_text: int = 0

    pruned_stories: int = 0
    warnings: list[str] = Field(default_factory=list)
    duration_ms: int = 0


def _resolve_llm(settings: Settings, use_llm: bool | None, llm_fn: summarize.LlmFn | None):
    """The model callable to use, or None for extractive-only."""
    if llm_fn is not None:
        return llm_fn
    wanted = settings.pipeline_use_llm if use_llm is None else use_llm
    if wanted and settings.groq_configured:
        return summarize._default_llm
    return None


async def run_pipeline(
    *,
    settings: Settings | None = None,
    store: Store | None = None,
    client: httpx.AsyncClient | None = None,
    sources: list[SourceConfig] | None = None,
    now: datetime | None = None,
    use_llm: bool | None = None,
    llm_fn: summarize.LlmFn | None = None,
    edition_date: str | None = None,
    fetch: bool = True,
    retry_delay: float = 0.5,
) -> PipelineReport:
    started = time.monotonic()
    settings = settings or get_settings()
    store = store or get_store(str(settings.resolved_database_path))
    now = (now or datetime.now(UTC)).astimezone(UTC)
    report = PipelineReport()

    if not store.acquire_lock(LOCK_NAME, now, LOCK_TTL):
        report.status = "skipped"
        report.warnings.append("Another pipeline run is in progress; nothing was done.")
        return report
    try:
        await _run(
            report, settings, store, client, sources, now, use_llm, llm_fn, edition_date, fetch,
            retry_delay,
        )  # fmt: skip
    finally:
        store.release_lock(LOCK_NAME)
        report.duration_ms = int((time.monotonic() - started) * 1000)
        store.record_run(now, datetime.now(UTC), report.model_dump_json())
    return report


async def _run(
    report: PipelineReport,
    settings: Settings,
    store: Store,
    client: httpx.AsyncClient | None,
    sources: list[SourceConfig] | None,
    now: datetime,
    use_llm: bool | None,
    llm_fn: summarize.LlmFn | None,
    edition_date: str | None,
    fetch: bool,
    retry_delay: float,
) -> None:
    tz = ZoneInfo(settings.edition_timezone)
    local_today = now.astimezone(tz).date().isoformat()
    date = edition_date or local_today
    as_of = now
    if date < local_today:  # regenerating a past edition: as of the end of that day
        end_of_day = datetime.fromisoformat(date).replace(tzinfo=tz) + timedelta(days=1)
        as_of = min(now, end_of_day.astimezone(UTC))
    lookback = timedelta(hours=settings.pipeline_lookback_hours)

    all_sources = sources if sources is not None else load_sources(settings.pipeline_sources_file)
    active, skipped = active_sources(all_sources, settings)
    report.skipped_sources = skipped
    registry = {s.id: s for s in active}

    # ---- fetch + normalize + store ---------------------------------------
    if fetch and active:
        owns_client = client is None
        http = client or httpx.AsyncClient(
            timeout=settings.pipeline_fetch_timeout_seconds,
            headers={"User-Agent": settings.pipeline_user_agent},
            follow_redirects=True,
        )
        try:
            raw_items, report.sources = await fetch_all(
                active, settings=settings, client=http, since=as_of - lookback, now=as_of,
                retry_delay=retry_delay,
            )  # fmt: skip
        finally:
            if owns_client:
                await http.aclose()
        report.fetched = len(raw_items)

        candidates, stats = normalize_items(raw_items, registry, now=as_of, max_age=lookback)
        report.normalized = stats.kept
        report.dropped_invalid, report.dropped_stale = stats.dropped_invalid, stats.dropped_stale
        report.new_articles, report.changed_articles = store.upsert_candidates(candidates)

        failed = [r for r in report.sources if not r.ok]
        if failed:
            report.warnings.append(
                f"{len(failed)} of {len(report.sources)} sources were unavailable."
            )
    elif fetch:
        report.warnings.append("No active sources are configured.")

    # ---- cluster -----------------------------------------------------------
    window = [
        c
        for c in store.load_candidates(as_of - lookback)
        if c.source_id in registry and c.published_at <= as_of
    ]
    if not window:
        report.status = "failed"
        report.warnings.append("No articles available to build an edition.")
        return

    clusters = cluster_articles(window)
    created_at = {sid: meta[0] for sid, meta in store.story_meta().items()}
    drafts = build_drafts(clusters, store.membership(), created_at)
    report.stories_total = len(drafts)
    report.multi_source_stories = sum(1 for d in drafts if len(d.article.sources) > 1)

    # ---- order by prominence, then summarize (best-first within the LLM budget)
    regions = settings.edition_regions
    drafts = [r.draft for r in rank_stories(drafts, now=as_of, regions=regions)]

    previous_ids = [d.article.id for d in drafts]
    summary_stats = await summarize.summarize_drafts(
        drafts,
        llm_fn=_resolve_llm(settings, use_llm, llm_fn),
        max_llm=settings.pipeline_max_llm_stories,
        previous=store.get_stories(previous_ids),
        previous_hashes={sid: meta[1] for sid, meta in store.story_meta().items()},
    )
    report.summaries_llm = summary_stats.llm_generated
    report.summaries_reused = summary_stats.reused
    report.summaries_extractive = summary_stats.extractive
    report.summary_fallback_reasons = dict(summary_stats.fallback_reasons)

    # ---- validate sources --------------------------------------------------
    drafts, validation = validate_drafts(drafts, registry_ids=set(registry), now=as_of)
    report.validation_dropped = len(validation.dropped_stories)
    report.validation_removed_sources = validation.removed_sources
    report.validation_reverted_text = len(validation.reverted_text)
    report.warnings.extend(validation.problems[:5])
    if not drafts:
        report.status = "failed"
        report.warnings.append("Every story failed validation.")
        return

    # ---- edition -----------------------------------------------------------
    ranked = rank_stories(drafts, now=as_of, regions=regions)
    edition_warnings = [w for w in report.warnings if "sources were unavailable" in w]
    edition = build_edition(
        ranked,
        date=date,
        now=now,
        timezone=settings.edition_timezone,
        max_stories=settings.edition_max_stories,
        warnings=edition_warnings,
    )

    # Persist the edition's version of each story (importance tier, related ids)
    # so /api/stories/{id} agrees with what the edition showed.
    published = {s.id: s for s in edition.stories}
    for draft in drafts:
        if draft.article.id in published:
            draft.article = published[draft.article.id]
    counts = store.save_stories(drafts, now)
    report.stories_created, report.stories_updated = counts.created, counts.updated
    report.stories_unchanged = counts.unchanged

    existing = store.get_edition_by_date(date)
    report.edition_id, report.edition_date = edition.id, date
    if existing and len(edition.stories) < max(1, len(existing.stories) // 2):
        # Never replace a healthy edition with a much thinner one (an outage).
        report.warnings.append("New edition was much smaller than the existing one; kept the old.")
        report.status = "degraded"
        return
    report.edition_written = store.save_edition(edition, edition_hash(edition))

    report.pruned_stories = store.prune(now - timedelta(days=settings.pipeline_retention_days))
    report.status = "degraded" if edition_warnings else "ok"
