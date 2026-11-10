import asyncio
import json

import httpx
import pytest

from app.config import Settings
from app.pipeline import adapters
from app.pipeline.adapters.base import FetchContext, FetchError, get_adapter
from app.pipeline.adapters.feeds import parse_feed
from app.pipeline.fetch import fetch_all
from tests.pipeline import fixtures as fx

SRC = {s.id: s for s in fx.SOURCES}


def run(coro):
    return asyncio.run(coro)


def fetch_one(source_id: str, routes=None, secret=None, max_bytes=5_000_000):
    async def go():
        transport = fx.transport(routes or fx.universe_routes())
        async with httpx.AsyncClient(transport=transport) as client:
            ctx = FetchContext(
                client=client,
                since=fx.ago(days=3),
                now=fx.NOW,
                secret=secret,
                retry_delay=0,
                max_bytes=max_bytes,
            )
            return await get_adapter(SRC[source_id].kind).fetch(SRC[source_id], ctx)

    return run(go())


def test_all_provider_kinds_are_registered():
    assert {"rss", "blog", "arxiv", "github", "nvd", "news_api"} <= set(adapters.registered_kinds())


def test_rss_parses_items_image_categories_and_keeps_tracking_url_raw():
    items = fetch_one("techcrunch")
    nvidia = next(i for i in items if i.title.startswith("Nvidia"))
    assert nvidia.source_name == "TechCrunch"
    assert nvidia.image == "https://techcrunch.com/wp-content/uploads/nvidia-chip.jpg"
    assert nvidia.tags == ["AI", "Hardware"]
    assert nvidia.published_at is not None
    assert "utm_source" in nvidia.url  # adapters don't clean; normalize does


def test_atom_feed_parses():
    (item,) = fetch_one("verge")
    assert item.url.endswith("nvidia-new-ai-chip-faster-inference")
    assert "40 percent" in item.summary


def test_blog_kind_uses_feed_parser():
    (item,) = fetch_one("cfblog")
    assert item.source_name == "Cloudflare Blog"


def test_news_api_credits_per_article_publisher_and_skips_removed():
    items = fetch_one("newsapi", secret="k")
    assert [i.source_name for i in items] == ["Reuters"]
    assert "[+2100 chars]" not in items[0].content
    assert items[0].extra["via"] == "NewsAPI"


def test_news_api_key_is_sent_in_header_not_url():
    calls: list[httpx.Request] = []

    async def go():
        t = fx.transport(fx.universe_routes(), calls)
        async with httpx.AsyncClient(transport=t) as client:
            ctx = FetchContext(
                client=client, since=fx.ago(days=3), now=fx.NOW, secret="s3cret", retry_delay=0
            )
            await get_adapter("news_api").fetch(SRC["newsapi"], ctx)

    run(go())
    assert calls[0].headers["X-Api-Key"] == "s3cret"
    assert "s3cret" not in str(calls[0].url)


def test_news_api_error_payload_becomes_fetch_error():
    error = json.dumps({"status": "error", "message": "apiKeyInvalid"})
    routes = {"newsapi.org/v2/top-headlines": error}
    with pytest.raises(FetchError, match="apiKeyInvalid"):
        fetch_one("newsapi", routes)


def test_arxiv_strips_version_and_extracts_metadata():
    (item,) = fetch_one("arxiv")
    assert item.url == "https://arxiv.org/abs/2611.01234"
    assert item.extra["arxiv_id"] == "2611.01234"
    assert item.extra["authors"] == ["Ada Researcher", "Bo Scientist"]
    assert item.extra["primary_category"] == "cs.CL"


def test_github_skips_prereleases_by_default_and_builds_title():
    (item,) = fetch_one("github")
    assert item.title == "langgraph v0.9.0 released"
    assert item.extra["repo"] == "langchain-ai/langgraph"
    assert "Added durable execution" in item.summary and "##" not in item.summary


def test_github_one_missing_repo_does_not_fail_the_source():
    repos = ["a/missing", "langchain-ai/langgraph"]
    source = SRC["github"].model_copy(update={"params": {"repos": repos}})

    async def go():
        async with httpx.AsyncClient(transport=fx.transport(fx.universe_routes())) as client:
            ctx = FetchContext(client=client, since=fx.ago(days=3), now=fx.NOW, retry_delay=0)
            return await get_adapter("github").fetch(source, ctx)

    assert len(run(go())) == 1


def test_nvd_filters_by_min_cvss_and_extracts_severity():
    (item,) = fetch_one("nvd")
    assert item.extra == {"cve_id": "CVE-2026-12345", "cvss": 9.8, "severity": "CRITICAL"}
    assert item.title.startswith("CVE-2026-12345: A memory corruption vulnerability in OpenSSL")
    assert item.url == "https://nvd.nist.gov/vuln/detail/CVE-2026-12345"


def test_nvd_sends_bounded_date_window():
    calls: list[httpx.Request] = []

    async def go():
        transport = fx.transport(fx.universe_routes(), calls)
        async with httpx.AsyncClient(transport=transport) as client:
            ctx = FetchContext(client=client, since=fx.ago(days=400), now=fx.NOW, retry_delay=0)
            await get_adapter("nvd").fetch(SRC["nvd"], ctx)

    run(go())
    q = calls[0].url.params
    assert q["pubEndDate"].startswith("2026-11-03")
    assert q["pubStartDate"] >= "2026-07-"  # clamped to NVD's 120-day max


def test_malicious_xml_entities_are_rejected():
    bomb = (
        '<?xml version="1.0"?><!DOCTYPE lol [<!ENTITY a "aaaa"><!ENTITY b "&a;&a;&a;&a;">]>'
        "<rss><channel><item><title>&b;</title><link>https://x.com/a</link></item></channel></rss>"
    )
    with pytest.raises(FetchError, match="disallowed XML"):
        parse_feed(bomb.encode(), SRC["techcrunch"])


def test_malformed_xml_and_unknown_format_raise_fetch_error():
    with pytest.raises(FetchError, match="well-formed"):
        parse_feed(b"<rss><channel>", SRC["techcrunch"])
    with pytest.raises(FetchError, match="Unrecognised"):
        parse_feed(b"<html><body/></html>", SRC["techcrunch"])


def test_oversized_response_is_rejected():
    with pytest.raises(FetchError, match="exceeds"):
        fetch_one("techcrunch", max_bytes=100)


def test_http_error_message_never_contains_secrets():
    routes = {"newsapi.org/v2/top-headlines": (401, "bad key")}
    with pytest.raises(FetchError) as exc:
        fetch_one("newsapi", routes, secret="s3cret")
    assert "s3cret" not in str(exc.value) and "401" in str(exc.value)


def test_transient_failure_is_retried_once():
    attempts = {"n": 0}

    def flaky(request):
        attempts["n"] += 1
        if attempts["n"] == 1:
            return httpx.Response(503)
        return httpx.Response(200, text=fx.rss(fx.CFBLOG_ITEMS))

    items = fetch_one("cfblog", {"blog.cloudflare.com/rss/": flaky})
    assert attempts["n"] == 2 and len(items) == 1


# --- fetch stage: isolation -------------------------------------------------
def test_fetch_all_isolates_failures_and_reports_each_source():
    routes = fx.universe_routes()
    routes["www.theverge.com/rss/index.xml"] = httpx.ConnectError("boom")
    routes["feeds.arstechnica.com/arstechnica/index"] = "<html>not a feed</html>"
    sources = [SRC[i] for i in ("techcrunch", "verge", "ars", "cfblog")]

    async def go():
        async with httpx.AsyncClient(transport=fx.transport(routes)) as client:
            return await fetch_all(
                sources,
                settings=Settings(),
                client=client,
                since=fx.ago(days=3),
                now=fx.NOW,
                retry_delay=0,
            )

    items, reports = run(go())
    by_id = {r.source_id: r for r in reports}
    assert by_id["techcrunch"].ok and by_id["cfblog"].ok
    assert not by_id["verge"].ok and "network error" in (by_id["verge"].error or "")
    assert not by_id["ars"].ok
    assert {i.source_id for i in items} == {"techcrunch", "cfblog"}


def test_fetch_all_survives_an_adapter_bug():
    class Broken:
        async def fetch(self, source, ctx):
            raise RuntimeError("kaboom with secret details")

    adapters.register_adapter("rss", Broken())  # type: ignore[arg-type]
    try:

        async def go():
            async with httpx.AsyncClient(transport=fx.transport({})) as client:
                return await fetch_all(
                    [SRC["techcrunch"]],
                    settings=Settings(),
                    client=client,
                    since=fx.ago(days=3),
                    now=fx.NOW,
                )

        items, (report,) = run(go())
    finally:
        from app.pipeline.adapters.rss import RssAdapter

        adapters.register_adapter("rss", RssAdapter())
    assert items == [] and not report.ok
    assert "secret details" not in (report.error or "")
