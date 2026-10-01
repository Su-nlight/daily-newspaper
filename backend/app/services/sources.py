"""The backend's own small mock corpus. Deliberately independent of the
frontend's src/data/mock-newspaper.ts rather than sharing it (different
languages, and there's no ingestion pipeline yet to source both from one
place) — see docs/PROJECT_STATE.md's Known Issues for this module. No real
news ingestion, per Module 01's stated scope, still holds.
"""

from datetime import datetime

from app.models.article import Article
from app.models.edition import Edition


def _dt(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


_ARTICLES: list[Article] = [
    Article(
        id="story-ai-policy-2026",
        title="India proposes AI audit framework for high-risk sectors",
        summary=(
            "A draft framework would require quarterly AI audits for systems used in lending, "
            "insurance, and healthcare decisions, with a 60-day public comment window before "
            "the rules are finalized."
        ),
        category="ai",
        source="Tech Ledger",
        source_url="https://techledger.example.com/ai-policy-audits",
        published_at=_dt("2026-09-22T07:30:00Z"),
        topics=["AI Agents", "India Tech"],
    ),
    Article(
        id="story-ransomware-shift",
        title="Ransomware groups pivot from databases to CI/CD pipelines",
        summary=(
            "Security researchers report a marked shift toward compromising build "
            "infrastructure and timing extortion demands around scheduled release windows."
        ),
        category="cybersecurity",
        source="Security Post",
        source_url="https://securitypost.example.com/supply-chain-extortion",
        published_at=_dt("2026-09-22T09:10:00Z"),
        topics=["Cloud Security"],
    ),
    Article(
        id="story-rag-benchmark",
        title="New benchmark exposes retrieval gaps in long-context RAG systems",
        summary=(
            "Most retrieval-augmented pipelines lose significant accuracy once the source "
            "corpus exceeds roughly 50 pages, even with a much larger model context window."
        ),
        category="research",
        source="Tech Ledger",
        source_url="https://techledger.example.com/rag-benchmark",
        published_at=_dt("2026-09-21T08:15:00Z"),
        topics=["AI Agents", "Research Monitoring"],
    ),
    Article(
        id="story-semiconductor-alliance",
        title="Japan and India fund a semiconductor packaging research corridor",
        summary=(
            "The multi-year program pairs Japanese industrial partners with Indian university "
            "research groups, focused on advanced chip packaging rather than fabrication."
        ),
        category="world",
        source="Global Wire",
        source_url="https://globalwire.example.com/semiconductor-corridor",
        published_at=_dt("2026-09-21T13:20:00Z"),
        topics=["India Tech"],
    ),
    Article(
        id="story-webassembly-edge",
        title="WebAssembly runtimes gain ground in edge compute deployments",
        summary=(
            "Engineering teams report faster cold starts and smaller deployment footprints "
            "after moving latency-sensitive services from containers to WASM runtimes."
        ),
        category="software-engineering",
        source="Global Wire",
        source_url="https://globalwire.example.com/webassembly-edge",
        published_at=_dt("2026-09-20T16:10:00Z"),
        topics=["Research Monitoring"],
    ),
    Article(
        id="story-ai-debugger",
        title="Research lab releases tracing tools for multi-agent AI failures",
        summary=(
            "The open-source toolkit traces decision paths across coordinated LLM agents to "
            "help teams debug failures in production agent pipelines."
        ),
        category="research",
        source="Tech Ledger",
        source_url="https://techledger.example.com/ai-debugger-toolkit",
        published_at=_dt("2026-09-20T15:00:00Z"),
        topics=["AI Agents", "Research Monitoring"],
    ),
    Article(
        id="story-cloud-breach-disclosure",
        title="Cloud provider discloses storage misconfiguration exposure",
        summary=(
            "A major cloud provider confirmed a limited exposure window from a storage "
            "misconfiguration and has since enabled default encryption-at-rest for new accounts."
        ),
        category="cybersecurity",
        source="Security Post",
        source_url="https://securitypost.example.com/cloud-breach-disclosure",
        published_at=_dt("2026-09-22T06:05:00Z"),
        topics=["Cloud Security"],
    ),
    Article(
        id="story-india-startup-funding",
        title="India's enterprise SaaS startups post strongest quarter since 2022",
        summary=(
            "Fresh funding data shows a rebound led by AI-infrastructure and fintech-adjacent "
            "startups based in Bengaluru and Pune."
        ),
        category="world",
        source="Global Wire",
        source_url="https://globalwire.example.com/india-startup-funding",
        published_at=_dt("2026-09-22T04:20:00Z"),
        topics=["India Tech"],
    ),
]

_EDITIONS: list[Edition] = [
    Edition(
        id="edition-2026-09-22",
        date="2026-09-22",
        headline="AI governance and cyber resilience lead today's brief",
        summary=(
            "Today's edition tracks policy momentum in AI, growing software supply-chain "
            "threats, and new research partnerships shaping global technology strategy."
        ),
        stories=[a for a in _ARTICLES if a.published_at.date().isoformat() == "2026-09-22"],
    ),
    Edition(
        id="edition-2026-09-21",
        date="2026-09-21",
        headline="A Japan–India chip corridor and a RAG benchmark",
        summary=(
            "Japan and India fund a semiconductor packaging corridor, and a new benchmark "
            "exposes retrieval limits in long-document RAG."
        ),
        stories=[a for a in _ARTICLES if a.published_at.date().isoformat() == "2026-09-21"],
    ),
    Edition(
        id="edition-2026-09-20",
        date="2026-09-20",
        headline="WebAssembly at the edge and a multi-agent debugger",
        summary=(
            "Engineering teams report gains moving latency-sensitive services to WebAssembly, "
            "and a research lab releases tracing tools for coordinated LLM agent failures."
        ),
        stories=[a for a in _ARTICLES if a.published_at.date().isoformat() == "2026-09-20"],
    ),
]


def list_articles(category: str | None = None) -> list[Article]:
    if category:
        return [a for a in _ARTICLES if a.category == category]
    return list(_ARTICLES)


def get_article(article_id: str) -> Article | None:
    return next((a for a in _ARTICLES if a.id == article_id), None)


def search_articles(
    *,
    query: str | None = None,
    category: str | None = None,
    source: str | None = None,
    topic: str | None = None,
) -> list[Article]:
    results = _ARTICLES

    if category:
        results = [a for a in results if a.category == category]
    if source:
        results = [a for a in results if a.source.lower() == source.lower()]
    if topic:
        results = [a for a in results if topic.lower() in (t.lower() for t in a.topics)]
    if query:
        from app.services.ranking import rank_articles

        results = rank_articles(results, query, limit=len(results))

    return list(results)


def get_today_edition() -> Edition:
    return max(_EDITIONS, key=lambda e: e.date)


def get_edition_by_date(date: str) -> Edition | None:
    return next((e for e in _EDITIONS if e.date == date), None)


def list_editions() -> list[Edition]:
    return list(_EDITIONS)
