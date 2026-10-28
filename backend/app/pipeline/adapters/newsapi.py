"""Adapter for NewsAPI.org-style aggregators (`articles[]` with a per-article
publisher). Other providers with a similar shape (GNews, Currents...) need only
a different `url`/params; a structurally different API gets its own adapter
registered under its own kind.

The key is sent as a header (never in the URL) and read from Settings via the
source's `api_key_setting`.

`source.params`: `query` (q), `category`, `country`, `language`, `domains`.
"""

import json
import re
from typing import Any

from app.pipeline.adapters.base import FetchContext, FetchError, http_get, register_adapter
from app.pipeline.schemas import RawItem, SourceConfig
from app.pipeline.textutil import collapse_ws, parse_datetime

# NewsAPI truncates `content` with a marker like "… [+1234 chars]".
_TRUNCATION_RE = re.compile(r"\s*…?\s*\[\+\d+ chars\]\s*$")


class NewsApiAdapter:
    async def fetch(self, source: SourceConfig, ctx: FetchContext) -> list[RawItem]:
        params: dict[str, Any] = {"pageSize": min(source.max_items, 100)}
        for key, param in (
            ("query", "q"),
            ("category", "category"),
            ("country", "country"),
            ("language", "language"),
            ("domains", "domains"),
        ):
            if source.params.get(key):
                params[param] = source.params[key]
        headers = {"X-Api-Key": ctx.secret} if ctx.secret else None
        body = await http_get(ctx, source.url, params=params, headers=headers)
        return parse_news_api(body, source)


def parse_news_api(body: bytes, source: SourceConfig) -> list[RawItem]:
    try:
        payload: Any = json.loads(body)
    except json.JSONDecodeError as exc:
        raise FetchError("News API returned invalid JSON.") from exc
    if not isinstance(payload, dict) or payload.get("status") not in (None, "ok"):
        message = payload.get("message") if isinstance(payload, dict) else None
        raise FetchError(f"News API error: {str(message or 'unexpected response')[:120]}")

    items: list[RawItem] = []
    for article in payload.get("articles") or []:
        if not isinstance(article, dict):
            continue
        title = collapse_ws(str(article.get("title") or ""))
        url = article.get("url")
        publisher = collapse_ws(str((article.get("source") or {}).get("name") or ""))
        # NewsAPI uses this placeholder for removed articles.
        if not title or not url or not publisher or title == "[Removed]":
            continue
        content = _TRUNCATION_RE.sub("", str(article.get("content") or ""))
        items.append(
            RawItem(
                source_id=source.id,
                source_name=publisher,
                kind="news_api",
                title=title,
                url=url,
                summary=str(article.get("description") or ""),
                content=content,
                published_at=parse_datetime(article.get("publishedAt")),
                image=article.get("urlToImage"),
                extra={"via": source.name},
            )
        )
    return items


register_adapter("news_api", NewsApiAdapter())
