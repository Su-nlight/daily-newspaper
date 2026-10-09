"""The backend's article/edition store. Loaded from app/data/corpus.json,
which is exported from the frontend's mock newsroom
(`npm run export:corpus` at the repo root) so chat answers are grounded in
exactly the stories the UI shows. No real news ingestion yet, per Module
01's stated scope.
"""

import json
from functools import lru_cache
from pathlib import Path

from app.models.article import Article
from app.models.edition import Edition

_CORPUS_PATH = Path(__file__).resolve().parent.parent / "data" / "corpus.json"


@lru_cache
def _load() -> tuple[list[Article], list[Edition]]:
    raw = json.loads(_CORPUS_PATH.read_text(encoding="utf-8"))
    articles = [Article(**item) for item in raw["articles"]]
    by_id = {article.id: article for article in articles}
    editions = [
        Edition(
            id=item["id"],
            date=item["date"],
            headline=item["headline"],
            summary=item["summary"],
            stories=[by_id[story_id] for story_id in item["story_ids"] if story_id in by_id],
        )
        for item in raw["editions"]
    ]
    return articles, editions


def list_articles(category: str | None = None) -> list[Article]:
    articles, _ = _load()
    if category:
        return [a for a in articles if a.category == category]
    return list(articles)


def get_article(article_id: str) -> Article | None:
    return next((a for a in list_articles() if a.id == article_id), None)


def get_articles(article_ids: list[str]) -> list[Article]:
    """Articles for the given ids, in the order given; unknown ids skipped."""
    return [a for a in (get_article(i) for i in article_ids) if a is not None]


def search_articles(
    *,
    query: str | None = None,
    category: str | None = None,
    source: str | None = None,
    topic: str | None = None,
) -> list[Article]:
    results = list_articles()

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


def list_editions() -> list[Edition]:
    _, editions = _load()
    return list(editions)


def get_today_edition() -> Edition:
    return max(list_editions(), key=lambda e: e.date)


def get_edition_by_date(date: str) -> Edition | None:
    return next((e for e in list_editions() if e.date == date), None)


def get_edition_by_id(edition_id: str) -> Edition | None:
    return next((e for e in list_editions() if e.id == edition_id), None)
