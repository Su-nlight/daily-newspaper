"""Stage: fetch. Runs every active source concurrently and in isolation - a
failing source is recorded in the run report, never raised."""

import asyncio
import logging
import time
from datetime import datetime

import httpx
from pydantic import BaseModel

from app.config import Settings
from app.pipeline import adapters
from app.pipeline.adapters.base import FetchContext, FetchError, get_adapter
from app.pipeline.registry import source_secret
from app.pipeline.schemas import RawItem, SourceConfig

logger = logging.getLogger("daily_signal.pipeline")

# Hard ceiling for one source (an adapter may make several requests).
_PER_SOURCE_TIMEOUT_SECONDS = 90


class SourceReport(BaseModel):
    source_id: str
    kind: str
    ok: bool
    item_count: int = 0
    error: str | None = None
    duration_ms: int = 0


async def fetch_all(
    sources: list[SourceConfig],
    *,
    settings: Settings,
    client: httpx.AsyncClient,
    since: datetime,
    now: datetime,
    retry_delay: float = 0.5,
) -> tuple[list[RawItem], list[SourceReport]]:
    assert adapters  # importing the package registers the built-in adapters
    semaphore = asyncio.Semaphore(max(1, settings.pipeline_fetch_concurrency))

    async def run_one(source: SourceConfig) -> tuple[list[RawItem], SourceReport]:
        started = time.monotonic()
        async with semaphore:
            try:
                ctx = FetchContext(
                    client=client,
                    since=since,
                    now=now,
                    max_bytes=settings.pipeline_max_response_bytes,
                    secret=source_secret(source, settings),
                    retry_delay=retry_delay,
                )
                async with asyncio.timeout(_PER_SOURCE_TIMEOUT_SECONDS):
                    items = await get_adapter(source.kind).fetch(source, ctx)
                items = _newest_first(items)[: source.max_items]
                return items, _report(source, started, ok=True, count=len(items))
            except FetchError as exc:
                logger.warning("Source %s failed: %s", source.id, exc)
                return [], _report(source, started, ok=False, error=str(exc))
            except TimeoutError:
                return [], _report(source, started, ok=False, error="timed out")
            except Exception as exc:  # an adapter bug must not abort the run
                logger.exception("Source %s crashed", source.id)
                return [], _report(
                    source, started, ok=False, error=f"unexpected error ({type(exc).__name__})"
                )

    results = await asyncio.gather(*(run_one(source) for source in sources))
    items = [item for batch, _ in results for item in batch]
    return items, [report for _, report in results]


def _newest_first(items: list[RawItem]) -> list[RawItem]:
    dated = [i for i in items if i.published_at]
    undated = [i for i in items if not i.published_at]
    dated.sort(key=lambda i: i.published_at, reverse=True)  # type: ignore[arg-type, return-value]
    return dated + undated


def _report(
    source: SourceConfig,
    started: float,
    *,
    ok: bool,
    count: int = 0,
    error: str | None = None,
) -> SourceReport:
    return SourceReport(
        source_id=source.id,
        kind=source.kind,
        ok=ok,
        item_count=count,
        error=error,
        duration_ms=int((time.monotonic() - started) * 1000),
    )
