"""arXiv adapter (Atom API). One item per paper; the abstract is the summary.

`source.params`: `search_query` (default "cat:cs.AI"), `sort_by`.
"""

import re
from typing import Any

from app.pipeline.adapters.base import FetchContext, http_get, register_adapter
from app.pipeline.adapters.feeds import child_text, children, local_name, parse_xml
from app.pipeline.schemas import RawItem, SourceConfig
from app.pipeline.textutil import collapse_ws, parse_datetime

_VERSION_RE = re.compile(r"v\d+$")


class ArxivAdapter:
    async def fetch(self, source: SourceConfig, ctx: FetchContext) -> list[RawItem]:
        params = {
            "search_query": source.params.get("search_query", "cat:cs.AI"),
            "sortBy": source.params.get("sort_by", "submittedDate"),
            "sortOrder": "descending",
            "start": 0,
            "max_results": source.max_items,
        }
        body = await http_get(ctx, source.url, params=params)
        return parse_arxiv(body, source)


def parse_arxiv(body: bytes, source: SourceConfig) -> list[RawItem]:
    root = parse_xml(body)
    items: list[RawItem] = []
    for entry in children(root, "entry"):
        title = collapse_ws(child_text(entry, "title"))
        raw_id = child_text(entry, "id")
        if not title or "arxiv.org/abs/" not in raw_id:
            continue
        arxiv_id = _VERSION_RE.sub("", raw_id.rsplit("/abs/", 1)[1])

        authors = [collapse_ws(child_text(author, "name")) for author in children(entry, "author")]
        categories = [c.get("term", "") for c in children(entry, "category") if c.get("term")]
        primary = next(
            (c.get("term") for c in entry if local_name(c.tag) == "primary_category"), None
        )
        extra: dict[str, Any] = {
            "arxiv_id": arxiv_id,
            "authors": [a for a in authors if a][:12],
            "primary_category": primary or (categories[0] if categories else None),
        }
        items.append(
            RawItem(
                source_id=source.id,
                source_name=source.name,
                kind="arxiv",
                title=title,
                url=f"https://arxiv.org/abs/{arxiv_id}",
                summary=collapse_ws(child_text(entry, "summary")),
                # `published` is the first version's date; `updated` moves on revisions.
                published_at=parse_datetime(child_text(entry, "published")),
                tags=categories[:8],
                extra=extra,
            )
        )
    return items


register_adapter("arxiv", ArxivAdapter())
