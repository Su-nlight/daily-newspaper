"""The backend's article/edition store - a facade over two content origins.

* **pipeline** (Module 09): stories and editions generated from real sources
  by `app.pipeline`, kept in SQLite.
* **seed**: `app/data/corpus.json`, exported from the frontend's mock
  newsroom (`npm run export:corpus`), kept so a fresh checkout works and the
  frontend's mock story ids still resolve in chat during the migration.

`CONTENT_SOURCE` picks the behaviour (see app/config.py):
  auto      pipeline content once any edition exists, else seed. Lookups of an
            explicit id/date that the pipeline doesn't know fall back to seed.
  pipeline  never seed.
  seed      never pipeline (the pre-Module-09 behaviour).

Listing and searching never mix the two: real results are not diluted with
fictional example.com stories.
"""

import json
from functools import lru_cache
from pathlib import Path

from app.config import get_settings
from app.models.article import Article
from app.models.edition import Edition
from app.pipeline.store import Store, get_store

_CORPUS_PATH = Path(__file__).resolve().parent.parent / "data" / "corpus.json"


class EditionNotAvailable(Exception):
    """No edition exists yet (pipeline mode, before the first run)."""


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


def _mode() -> str:
    return get_settings().content_source


def _pipeline() -> Store | None:
    """The pipeline store, if it should be (and can be) used right now."""
    settings = get_settings()
    if settings.content_source == "seed":
        return None
    path = settings.resolved_database_path
    if not path.exists():  # don't create an empty database just by reading
        return None
    store = get_store(str(path))
    return store if store.has_editions() else None


def _seed_allowed() -> bool:
    return _mode() != "pipeline"


def list_articles(category: str | None = None) -> list[Article]:
    store = _pipeline()
    if store is not None:
        return store.list_stories(category)
    if not _seed_allowed():
        return []
    articles, _ = _load()
    if category:
        return [a for a in articles if a.category == category]
    return list(articles)


def get_article(article_id: str) -> Article | None:
    store = _pipeline()
    if store is not None:
        found = store.get_story(article_id)
        if found is not None:
            return found
    if _seed_allowed():
        return next((a for a in _load()[0] if a.id == article_id), None)
    return None


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
        wanted = source.lower()
        results = [
            a
            for a in results
            if a.source.lower() == wanted or any(s.publisher.lower() == wanted for s in a.sources)
        ]
    if topic:
        results = [a for a in results if topic.lower() in (t.lower() for t in a.topics)]
    if query:
        from app.services.ranking import rank_articles

        results = rank_articles(results, query, limit=len(results))

    return list(results)


def list_editions() -> list[Edition]:
    store = _pipeline()
    generated = store.list_editions() if store is not None else []
    if not _seed_allowed():
        return generated
    taken = {e.date for e in generated}
    return [*generated, *(e for e in _load()[1] if e.date not in taken)]


def get_today_edition() -> Edition:
    """The most recent edition. Deliberately "latest", not "calendar today": if
    a scheduled run is late or failed, yesterday's edition (its date and
    `metadata.generated_at` say so) beats a 404."""
    editions = list_editions()
    if not editions:
        raise EditionNotAvailable("No edition has been generated yet.")
    return max(editions, key=lambda e: e.date)


def get_edition_by_date(date: str) -> Edition | None:
    store = _pipeline()
    if store is not None:
        found = store.get_edition_by_date(date)
        if found is not None:
            return found
    if _seed_allowed():
        return next((e for e in _load()[1] if e.date == date), None)
    return None


def get_edition_by_id(edition_id: str) -> Edition | None:
    store = _pipeline()
    if store is not None:
        found = store.get_edition_by_id(edition_id)
        if found is not None:
            return found
    if _seed_allowed():
        return next((e for e in _load()[1] if e.id == edition_id), None)
    return None
