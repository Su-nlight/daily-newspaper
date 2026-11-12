"""A small fictional news universe for pipeline tests.

Deliberately contains the hard cases: one event covered by three publications
in three formats; a *lookalike* event that must not merge with it; two CVEs
with near-identical text; tracking-URL duplicates; a `javascript:` link; a
stale item; and the same publisher posting twice about similar things.
"""

import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from email.utils import format_datetime
from typing import Any
from xml.sax.saxutils import escape

import httpx

from app.pipeline.schemas import SourceConfig

NOW = datetime(2026, 11, 3, 8, 0, tzinfo=UTC)


def ago(**kwargs: float) -> datetime:
    return NOW - timedelta(**kwargs)


# --------------------------------------------------------------------- builders
def rss(items: list[dict[str, Any]]) -> str:
    out = [
        '<?xml version="1.0"?><rss version="2.0" '
        'xmlns:content="http://purl.org/rss/1.0/modules/content/" '
        'xmlns:media="http://search.yahoo.com/mrss/"><channel><title>Feed</title>'
    ]
    for it in items:
        out.append("<item>")
        out.append(f"<title>{escape(it['title'])}</title>")
        out.append(f"<link>{escape(it['link'])}</link>")
        if "description" in it:
            out.append(f"<description>{escape(it['description'])}</description>")
        if "content" in it:
            out.append(f"<content:encoded>{escape(it['content'])}</content:encoded>")
        if "published" in it:
            out.append(f"<pubDate>{format_datetime(it['published'])}</pubDate>")
        if "image" in it:
            out.append(f'<media:thumbnail url="{escape(it["image"])}"/>')
        for cat in it.get("categories", []):
            out.append(f"<category>{escape(cat)}</category>")
        out.append("</item>")
    out.append("</channel></rss>")
    return "".join(out)


def atom(entries: list[dict[str, Any]]) -> str:
    out = ['<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">']
    for e in entries:
        out.append("<entry>")
        out.append(f"<title>{escape(e['title'])}</title>")
        out.append(f'<link rel="alternate" href="{escape(e["link"])}"/>')
        out.append(f"<summary>{escape(e.get('summary', ''))}</summary>")
        out.append(f"<published>{e['published'].isoformat()}</published>")
        out.append("</entry>")
    out.append("</feed>")
    return "".join(out)


def arxiv_feed(entries: list[dict[str, Any]]) -> str:
    out = [
        '<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom" '
        'xmlns:arxiv="http://arxiv.org/schemas/atom">'
    ]
    for e in entries:
        out.append("<entry>")
        out.append(f"<id>http://arxiv.org/abs/{e['id']}v2</id>")
        out.append(f"<published>{e['published'].isoformat()}</published>")
        out.append(f"<title>{escape(e['title'])}</title>")
        out.append(f"<summary>{escape(e['summary'])}</summary>")
        for a in e.get("authors", ["A. Author"]):
            out.append(f"<author><name>{escape(a)}</name></author>")
        out.append(f'<arxiv:primary_category term="{e.get("cat", "cs.CL")}"/>')
        out.append(f'<category term="{e.get("cat", "cs.CL")}"/>')
        out.append("</entry>")
    out.append("</feed>")
    return "".join(out)


def github_releases(items: list[dict[str, Any]]) -> str:
    return json.dumps(
        [
            {
                "tag_name": i["tag"],
                "name": i.get("name", i["tag"]),
                "html_url": i["url"],
                "body": i.get("body", ""),
                "draft": i.get("draft", False),
                "prerelease": i.get("prerelease", False),
                "published_at": i["published"].isoformat().replace("+00:00", "Z"),
            }
            for i in items
        ]
    )


def nvd_payload(items: list[dict[str, Any]]) -> str:
    vulns = []
    for i in items:
        cve: dict[str, Any] = {
            "id": i["id"],
            "published": i["published"].strftime("%Y-%m-%dT%H:%M:%S.000"),
            "descriptions": [
                {"lang": "es", "value": "ignorar"},
                {"lang": "en", "value": i["description"]},
            ],
        }
        if "score" in i:
            cve["metrics"] = {
                "cvssMetricV31": [
                    {
                        "cvssData": {
                            "baseScore": i["score"],
                            "baseSeverity": i.get("severity", "HIGH"),
                        }
                    }
                ]
            }
        vulns.append({"cve": cve})
    return json.dumps({"vulnerabilities": vulns})


def newsapi_payload(items: list[dict[str, Any]]) -> str:
    return json.dumps(
        {
            "status": "ok",
            "articles": [
                {
                    "source": {"id": None, "name": i["publisher"]},
                    "title": i["title"],
                    "description": i.get("description", ""),
                    "url": i["url"],
                    "urlToImage": i.get("image"),
                    "publishedAt": i["published"].isoformat().replace("+00:00", "Z"),
                    "content": i.get("content", ""),
                }
                for i in items
            ],
        }
    )


# --------------------------------------------------------------------- transport
Route = str | bytes | tuple[int, str] | Exception | Callable[[httpx.Request], httpx.Response]


def transport(
    routes: dict[str, Route], calls: list[httpx.Request] | None = None
) -> httpx.MockTransport:
    """Routes are matched on `host/path`. A str/bytes body is a 200; a tuple is
    (status, body); an Exception is raised (simulating a network failure)."""

    def handler(request: httpx.Request) -> httpx.Response:
        if calls is not None:
            calls.append(request)
        key = f"{request.url.host}{request.url.path}"
        route = routes.get(key)
        if route is None:
            return httpx.Response(404, text="not found")
        if isinstance(route, Exception):
            raise route
        if callable(route):
            return route(request)
        if isinstance(route, tuple):
            return httpx.Response(route[0], text=route[1])
        return httpx.Response(200, content=route if isinstance(route, bytes) else route.encode())

    return httpx.MockTransport(handler)


# ------------------------------------------------------------------- the universe
SOURCES: list[SourceConfig] = [
    SourceConfig(
        id="techcrunch",
        name="TechCrunch",
        kind="rss",
        url="https://techcrunch.com/feed/",
        quality=0.8,
        default_category="software-engineering",
    ),
    SourceConfig(
        id="verge",
        name="The Verge",
        kind="rss",
        url="https://www.theverge.com/rss/index.xml",
        quality=0.8,
    ),
    SourceConfig(
        id="newsapi",
        name="NewsAPI",
        kind="news_api",
        url="https://newsapi.org/v2/top-headlines",
        quality=0.75,
        api_key_setting="newsapi_key",
        params={"category": "technology"},
    ),
    SourceConfig(
        id="ars",
        name="Ars Technica",
        kind="rss",
        url="https://feeds.arstechnica.com/arstechnica/index",
        quality=0.8,
    ),
    SourceConfig(
        id="bleeping",
        name="BleepingComputer",
        kind="rss",
        url="https://www.bleepingcomputer.com/feed/",
        quality=0.7,
        default_category="cybersecurity",
    ),
    SourceConfig(
        id="thn",
        name="The Hacker News",
        kind="rss",
        url="https://feeds.feedburner.com/TheHackersNews",
        quality=0.65,
        default_category="cybersecurity",
    ),
    SourceConfig(
        id="nvd",
        name="NIST NVD",
        kind="nvd",
        url="https://services.nvd.nist.gov/rest/json/cves/2.0",
        quality=0.95,
        default_category="cybersecurity",
        api_key_setting="nvd_api_key",
        api_key_required=False,
        params={"min_cvss": 7.0},
    ),
    SourceConfig(
        id="arxiv",
        name="arXiv",
        kind="arxiv",
        url="https://export.arxiv.org/api/query",
        quality=0.7,
        default_category="research",
        params={"search_query": "cat:cs.CL"},
    ),
    SourceConfig(
        id="github",
        name="GitHub",
        kind="github",
        url="https://api.github.com",
        quality=0.7,
        default_category="software-engineering",
        params={"repos": ["langchain-ai/langgraph"]},
        api_key_setting="github_token",
        api_key_required=False,
    ),
    SourceConfig(
        id="inc42",
        name="Inc42",
        kind="rss",
        url="https://inc42.com/feed/",
        quality=0.6,
        region="india",
    ),
    SourceConfig(
        id="cfblog",
        name="Cloudflare Blog",
        kind="blog",
        url="https://blog.cloudflare.com/rss/",
        quality=0.85,
        default_category="software-engineering",
    ),
]

NVIDIA_TC = "https://techcrunch.com/2026/11/03/nvidia-unveils-faster-ai-inference-chip/"

TECHCRUNCH_ITEMS = [
    {  # Event A (1/3): the multi-publication story
        "title": "Nvidia unveils new AI chip promising 40% faster inference",
        "link": NVIDIA_TC + "?utm_source=rss&utm_medium=feed",
        "description": "<p>Nvidia on Monday announced a new data-center chip it says delivers 40% faster "
        "inference than its previous generation, with shipments planned for early 2027.</p>",
        "published": ago(hours=5),
        "image": "https://techcrunch.com/wp-content/uploads/nvidia-chip.jpg",
        "categories": ["AI", "Hardware"],
    },
    {  # Same publisher, different story on a similar theme (must stay separate)
        "title": "Startup raises $30 million for inference chip design software",
        "link": "https://techcrunch.com/2026/11/03/startup-raises-30m-chip-design-software/",
        "description": "A chip design software startup closed a $30 million Series A round.",
        "published": ago(hours=4),
    },
    {  # javascript: link -> must be rejected
        "title": "Totally normal looking article title here",
        "link": "javascript:alert(1)",
        "description": "Nope.",
        "published": ago(hours=2),
    },
    {  # stale
        "title": "A very old article about an old topic from long ago",
        "link": "https://techcrunch.com/2026/10/20/old-article/",
        "description": "Old news.",
        "published": ago(days=14),
    },
]

VERGE_ENTRIES = [
    {  # Event A (2/3)
        "title": "Nvidia's new AI chip is 40 percent faster at inference",
        "link": "https://www.theverge.com/2026/11/3/nvidia-new-ai-chip-faster-inference",
        "summary": "Nvidia says its newly announced chip runs inference workloads 40 percent faster "
        "than the previous generation and will ship in early 2027.",
        "published": ago(hours=4, minutes=20),
    },
]

NEWSAPI_ITEMS = [
    {  # Event A (3/3), via an aggregator crediting Reuters
        "publisher": "Reuters",
        "title": "Nvidia launches faster AI chip aimed at inference workloads",
        "url": "https://www.reuters.com/technology/nvidia-launches-faster-ai-chip-2026-11-03/",
        "description": "Nvidia introduced a data-center chip it said is 40% faster at inference, "
        "targeting a surge in demand for AI services.",
        "published": ago(hours=4, minutes=40),
        "content": "Nvidia introduced a data-center chip it said is 40% faster at inference… [+2100 chars]",
        "image": "https://www.reuters.com/img/nvidia.jpg",
    },
    {
        "publisher": "Reuters",
        "title": "[Removed]",
        "url": "https://removed.example.com/x",
        "published": ago(hours=3),
    },
]

ARS_ITEMS = [
    {  # Lookalike: shares "unveils new AI chip" with Event A but is a different event
        "title": "AMD unveils new AI chip for low-power edge devices",
        "link": "https://arstechnica.com/gadgets/2026/11/amd-unveils-new-ai-chip-edge-devices/",
        "description": "AMD announced an AI accelerator aimed at battery-powered edge devices such as "
        "cameras and robots, with samples available to partners next quarter.",
        "published": ago(hours=6),
    },
]

BLEEPING_ITEMS = [
    {  # Event C (1/3)
        "title": "Critical OpenSSL flaw CVE-2026-12345 allows remote code execution",
        "link": "https://www.bleepingcomputer.com/news/security/critical-openssl-flaw-cve-2026-12345/",
        "description": "A critical memory corruption bug in OpenSSL, tracked as CVE-2026-12345, lets "
        "attackers run code remotely on servers using affected versions.",
        "published": ago(hours=7),
    },
    {  # Event D: near-identical wording, DIFFERENT CVE (must not merge with C)
        "title": "Critical OpenSSL flaw CVE-2026-99999 allows denial of service",
        "link": "https://www.bleepingcomputer.com/news/security/critical-openssl-flaw-cve-2026-99999/",
        "description": "A critical bug in OpenSSL, tracked as CVE-2026-99999, lets attackers crash "
        "servers using affected versions.",
        "published": ago(hours=6, minutes=30),
    },
]

THN_ITEMS = [
    {  # Event C (2/3)
        "title": "OpenSSL patches critical remote code execution bug (CVE-2026-12345)",
        "link": "https://thehackernews.com/2026/11/openssl-patches-critical-rce-cve-2026-12345.html",
        "description": "OpenSSL maintainers shipped fixes for CVE-2026-12345, a critical flaw enabling "
        "remote code execution.",
        "published": ago(hours=6, minutes=45),
    },
]

NVD_ITEMS = [
    {  # Event C (3/3): the authoritative record
        "id": "CVE-2026-12345",
        "description": "A memory corruption vulnerability in OpenSSL allows remote attackers to execute "
        "arbitrary code via a crafted TLS handshake message. Versions before 3.4.2 are affected.",
        "published": ago(hours=8),
        "score": 9.8,
        "severity": "CRITICAL",
    },
    {  # below min_cvss -> dropped by the adapter
        "id": "CVE-2026-00001",
        "description": "A minor information disclosure in a rarely used debug endpoint.",
        "published": ago(hours=9),
        "score": 3.1,
        "severity": "LOW",
    },
]

ARXIV_ENTRIES = [
    {
        "id": "2611.01234",
        "title": "A New Benchmark for Evaluating Retrieval-Augmented Generation",
        "summary": "We introduce RAGBench-X, a benchmark of 12,000 questions for evaluating "
        "retrieval-augmented generation systems across five domains.",
        "published": ago(hours=10),
        "authors": ["Ada Researcher", "Bo Scientist"],
        "cat": "cs.CL",
    },
]

GITHUB_ITEMS = [
    {
        "tag": "v0.9.0",
        "name": "0.9.0",
        "url": "https://github.com/langchain-ai/langgraph/releases/tag/v0.9.0",
        "body": "## What's Changed\n- Added durable execution\n- Fixed streaming bug",
        "published": ago(hours=12),
    },
    {
        "tag": "v0.9.0rc1",
        "url": "https://github.com/langchain-ai/langgraph/releases/tag/v0.9.0rc1",
        "prerelease": True,
        "published": ago(hours=30),
    },
]

INC42_ITEMS = [
    {
        "title": "India proposes audit rules for enterprise AI used in banking and healthcare",
        "link": "https://inc42.com/buzz/india-proposes-ai-audit-rules-banking-healthcare/",
        "description": "India's technology ministry released a draft framework requiring audits of AI "
        "systems in banking and healthcare. A 60-day public comment window is open.",
        "published": ago(hours=9),
    },
]

CFBLOG_ITEMS = [
    {
        "title": "How we rebuilt our edge network to cut tail latency",
        "link": "https://blog.cloudflare.com/rebuilt-edge-network-tail-latency/",
        "description": "Our engineering team describes the architecture changes behind lower p99 latency.",
        "published": ago(hours=20),
    },
]


def universe_routes() -> dict[str, Route]:
    return {
        "techcrunch.com/feed/": rss(TECHCRUNCH_ITEMS),
        "www.theverge.com/rss/index.xml": atom(VERGE_ENTRIES),
        "newsapi.org/v2/top-headlines": newsapi_payload(NEWSAPI_ITEMS),
        "feeds.arstechnica.com/arstechnica/index": rss(ARS_ITEMS),
        "www.bleepingcomputer.com/feed/": rss(BLEEPING_ITEMS),
        "feeds.feedburner.com/TheHackersNews": rss(THN_ITEMS),
        "services.nvd.nist.gov/rest/json/cves/2.0": nvd_payload(NVD_ITEMS),
        "export.arxiv.org/api/query": arxiv_feed(ARXIV_ENTRIES),
        "api.github.com/repos/langchain-ai/langgraph/releases": github_releases(GITHUB_ITEMS),
        "inc42.com/feed/": rss(INC42_ITEMS),
        "blog.cloudflare.com/rss/": rss(CFBLOG_ITEMS),
    }


# ------------------------------------------------------------------- helpers
def candidates(now=NOW, max_age_hours: int = 72):
    """Fetch + normalize the whole universe (synchronously) -> candidates."""
    import asyncio

    from app.config import Settings
    from app.pipeline.fetch import fetch_all
    from app.pipeline.normalize import normalize_items

    async def go():
        async with httpx.AsyncClient(transport=transport(universe_routes())) as client:
            return await fetch_all(
                SOURCES,
                settings=Settings(),
                client=client,
                since=now - timedelta(hours=max_age_hours),
                now=now,
                retry_delay=0,
            )

    raw, _ = asyncio.run(go())
    cands, stats = normalize_items(
        raw, {s.id: s for s in SOURCES}, now=now, max_age=timedelta(hours=max_age_hours)
    )
    return cands, stats


def by_title(cands, prefix: str):
    return next(c for c in cands if c.title.startswith(prefix))


def run_pipeline_sync(settings, store, routes=None, now=NOW, sources=None, **kwargs):
    import asyncio

    from app.pipeline.runner import run_pipeline

    async def go():
        async with httpx.AsyncClient(
            transport=transport(universe_routes() if routes is None else routes)
        ) as client:
            return await run_pipeline(
                settings=settings,
                store=store,
                client=client,
                sources=sources or SOURCES,
                now=now,
                retry_delay=0,
                **kwargs,
            )

    return asyncio.run(go())
