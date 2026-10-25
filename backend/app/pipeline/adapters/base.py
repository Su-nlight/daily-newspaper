"""The seam that keeps the pipeline provider-agnostic.

An adapter turns one configured source into `RawItem`s. It does parsing only:
no cleaning, ranking or dedupe. Everything downstream sees `RawItem`, so
adding a provider means writing one class and registering it - nothing else
in the pipeline changes.
"""

import asyncio
import logging
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

import httpx

from app.pipeline.schemas import RawItem, SourceConfig, SourceKind

logger = logging.getLogger("daily_signal.pipeline")


class FetchError(Exception):
    """A source could not be fetched or parsed. The message is safe to log and
    to show in a run report (it never contains credentials)."""


@dataclass(frozen=True)
class FetchContext:
    client: httpx.AsyncClient
    since: datetime
    now: datetime
    max_bytes: int = 5_000_000
    # This source's credential, already resolved from Settings (or None).
    secret: str | None = None
    retry_delay: float = 0.5


class SourceAdapter(Protocol):
    async def fetch(self, source: SourceConfig, ctx: FetchContext) -> list[RawItem]: ...


_ADAPTERS: dict[SourceKind, SourceAdapter] = {}


def register_adapter(kind: SourceKind, adapter: SourceAdapter) -> None:
    _ADAPTERS[kind] = adapter


def get_adapter(kind: SourceKind) -> SourceAdapter:
    try:
        return _ADAPTERS[kind]
    except KeyError:
        raise FetchError(f"No adapter registered for source kind '{kind}'.") from None


def registered_kinds() -> list[str]:
    return sorted(_ADAPTERS)


_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


async def http_get(
    ctx: FetchContext,
    url: str,
    *,
    params: Mapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
    attempts: int = 2,
) -> bytes:
    """GET with a hard size cap, one retry for transient failures, and errors
    normalized to FetchError. Credentials belong in `headers`, never in the
    URL, so they can't leak into an error message."""
    last_error = "unknown error"
    for attempt in range(1, attempts + 1):
        try:
            async with ctx.client.stream("GET", url, params=params, headers=headers) as response:
                if response.status_code >= 400:
                    if response.status_code in _RETRYABLE_STATUS and attempt < attempts:
                        last_error = f"HTTP {response.status_code}"
                        await asyncio.sleep(ctx.retry_delay)
                        continue
                    raise FetchError(f"HTTP {response.status_code} from {_host(url)}")

                chunks: list[bytes] = []
                total = 0
                async for chunk in response.aiter_bytes():
                    total += len(chunk)
                    if total > ctx.max_bytes:
                        raise FetchError(
                            f"Response from {_host(url)} exceeds {ctx.max_bytes} bytes."
                        )
                    chunks.append(chunk)
                return b"".join(chunks)
        except FetchError:
            raise
        except httpx.TimeoutException:
            last_error = "timed out"
        except httpx.HTTPError as exc:
            last_error = f"network error ({type(exc).__name__})"
        if attempt < attempts:
            await asyncio.sleep(ctx.retry_delay)
    raise FetchError(f"{_host(url)}: {last_error}")


def _host(url: str) -> str:
    return httpx.URL(url).host or url
