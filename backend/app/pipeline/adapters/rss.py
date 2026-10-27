"""RSS/Atom adapter. Also serves "official technology blogs" (kind "blog"):
essentially all of them publish a feed, which is far more stable and polite
than scraping HTML."""

from app.pipeline.adapters.base import FetchContext, http_get, register_adapter
from app.pipeline.adapters.feeds import parse_feed
from app.pipeline.schemas import RawItem, SourceConfig


class RssAdapter:
    async def fetch(self, source: SourceConfig, ctx: FetchContext) -> list[RawItem]:
        body = await http_get(
            ctx,
            source.url,
            headers={"Accept": "application/rss+xml, application/atom+xml, application/xml"},
        )
        return parse_feed(body, source)


register_adapter("rss", RssAdapter())
register_adapter("blog", RssAdapter())
