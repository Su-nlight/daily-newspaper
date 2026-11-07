"""SQLite persistence for the pipeline (stdlib only).

Tables:
  articles       normalized candidates; UNIQUE canonical_url (idempotent ingest)
  stories        one row per story cluster, payload = public Article JSON
  story_members  article id -> story id (what keeps story ids stable)
  editions       one row per edition date; UNIQUE date
  pipeline_runs  run reports, for operators
  locks          advisory lock with expiry, so overlapping runs don't collide

A connection is opened per operation: SQLite is cheap to open, and it keeps the
store safe to use from the FastAPI server and the scheduled CLI at once (WAL
mode lets readers continue during a write).
"""

import json
import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from pathlib import Path

from app.models.article import Article
from app.models.edition import Edition
from app.pipeline.schemas import CandidateArticle, StoryDraft

_SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    canonical_url TEXT NOT NULL UNIQUE,
    source_id TEXT NOT NULL,
    published_at TEXT NOT NULL,
    first_seen_at TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at);
CREATE TABLE IF NOT EXISTS stories (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    latest_published_at TEXT NOT NULL,
    evidence_hash TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS story_members (
    article_id TEXT PRIMARY KEY,
    story_id TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_members_story ON story_members(story_id);
CREATE TABLE IF NOT EXISTS editions (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL UNIQUE,
    content_hash TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT NOT NULL,
    report TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS locks (
    name TEXT PRIMARY KEY,
    expires_at TEXT NOT NULL
);
"""


def iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat()


@dataclass
class SaveCounts:
    created: int = 0
    updated: int = 0
    unchanged: int = 0


class Store:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.transaction() as conn:
            conn.executescript(_SCHEMA)

    # ------------------------------------------------------------ plumbing
    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=15000")
        return conn

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                yield conn
            except BaseException:
                conn.rollback()
                raise
            else:
                conn.commit()

    @contextmanager
    def _read(self) -> Iterator[sqlite3.Connection]:
        with closing(self._connect()) as conn:
            yield conn

    # ------------------------------------------------------------ candidates
    def upsert_candidates(self, items: list[CandidateArticle]) -> tuple[int, int]:
        """(new, changed). Re-ingesting an identical article changes nothing;
        a feed that edited its summary updates the stored copy but keeps the
        original `first_seen_at`."""
        new = changed = 0
        with self.transaction() as conn:
            for item in items:
                row = conn.execute(
                    "SELECT payload FROM articles WHERE canonical_url = ?", (item.canonical_url,)
                ).fetchone()
                payload = item.model_dump_json()
                if row is None:
                    conn.execute(
                        "INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            item.id,
                            item.canonical_url,
                            item.source_id,
                            iso(item.published_at),
                            iso(item.fetched_at),
                            payload,
                        ),
                    )
                    new += 1
                else:
                    old = CandidateArticle.model_validate_json(row["payload"])
                    # Compare ignoring fetch time, which differs on every run.
                    if old.model_copy(update={"fetched_at": item.fetched_at}) != item:
                        conn.execute(
                            "UPDATE articles SET payload = ?, published_at = ? WHERE id = ?",
                            (payload, iso(item.published_at), item.id),
                        )
                        changed += 1
        return new, changed

    def load_candidates(self, since: datetime) -> list[CandidateArticle]:
        with self._read() as conn:
            rows = conn.execute(
                "SELECT payload FROM articles WHERE published_at >= ? "
                "ORDER BY published_at DESC, id",
                (iso(since),),
            ).fetchall()
        return [CandidateArticle.model_validate_json(r["payload"]) for r in rows]

    # --------------------------------------------------------------- stories
    def membership(self) -> dict[str, str]:
        with self._read() as conn:
            return {
                r["article_id"]: r["story_id"] for r in conn.execute("SELECT * FROM story_members")
            }

    def story_meta(self) -> dict[str, tuple[str, str]]:
        """story id -> (created_at, evidence_hash)."""
        with self._read() as conn:
            return {
                r["id"]: (r["created_at"], r["evidence_hash"])
                for r in conn.execute("SELECT id, created_at, evidence_hash FROM stories")
            }

    def get_stories(self, ids: list[str]) -> dict[str, Article]:
        if not ids:
            return {}
        marks = ",".join("?" * len(ids))
        with self._read() as conn:
            rows = conn.execute(f"SELECT id, payload FROM stories WHERE id IN ({marks})", ids)
            return {r["id"]: Article.model_validate_json(r["payload"]) for r in rows}

    def get_story(self, story_id: str) -> Article | None:
        return self.get_stories([story_id]).get(story_id)

    def list_stories(self, category: str | None = None) -> list[Article]:
        with self._read() as conn:
            rows = conn.execute(
                "SELECT payload FROM stories ORDER BY latest_published_at DESC, id"
            ).fetchall()
        stories = [Article.model_validate_json(r["payload"]) for r in rows]
        return [s for s in stories if category is None or s.category == category]

    def save_stories(self, drafts: list[StoryDraft], now: datetime) -> SaveCounts:
        counts = SaveCounts()
        stamp = iso(now)
        with self.transaction() as conn:
            for draft in drafts:
                article = draft.article
                payload = article.model_dump_json()
                latest = iso(max(m.published_at for m in draft.members))
                row = conn.execute(
                    "SELECT payload, evidence_hash FROM stories WHERE id = ?", (article.id,)
                ).fetchone()
                if row is None:
                    conn.execute(
                        "INSERT INTO stories VALUES (?, ?, ?, ?, ?, ?)",
                        (article.id, stamp, stamp, latest, draft.evidence_hash, payload),
                    )
                    counts.created += 1
                elif row["payload"] != payload:
                    conn.execute(
                        "UPDATE stories SET updated_at=?, latest_published_at=?, evidence_hash=?, "
                        "payload=? WHERE id=?",
                        (stamp, latest, draft.evidence_hash, payload, article.id),
                    )
                    counts.updated += 1
                else:
                    counts.unchanged += 1
                for member in draft.members:
                    conn.execute(
                        "INSERT OR REPLACE INTO story_members VALUES (?, ?)",
                        (member.id, article.id),
                    )
            # A merge can leave an old story with no members: retire it.
            conn.execute(
                "DELETE FROM stories WHERE id NOT IN (SELECT DISTINCT story_id FROM story_members)"
            )
        return counts

    # --------------------------------------------------------------- editions
    def save_edition(self, edition: Edition, content_hash: str) -> bool:
        """Insert or replace the edition for its date. Returns False (and
        writes nothing) when the stored one has identical content."""
        with self.transaction() as conn:
            row = conn.execute(
                "SELECT content_hash FROM editions WHERE date = ?", (edition.date,)
            ).fetchone()
            if row is not None and row["content_hash"] == content_hash:
                return False
            generated = edition.metadata.generated_at or datetime.now(UTC)
            conn.execute(
                "INSERT OR REPLACE INTO editions VALUES (?, ?, ?, ?, ?)",
                (edition.id, edition.date, content_hash, iso(generated), edition.model_dump_json()),
            )
            return True

    def _edition_from(self, row: sqlite3.Row | None) -> Edition | None:
        return Edition.model_validate_json(row["payload"]) if row else None

    def get_edition_by_date(self, date: str) -> Edition | None:
        with self._read() as conn:
            return self._edition_from(
                conn.execute("SELECT payload FROM editions WHERE date = ?", (date,)).fetchone()
            )

    def get_edition_by_id(self, edition_id: str) -> Edition | None:
        with self._read() as conn:
            return self._edition_from(
                conn.execute("SELECT payload FROM editions WHERE id = ?", (edition_id,)).fetchone()
            )

    def latest_edition(self) -> Edition | None:
        with self._read() as conn:
            return self._edition_from(
                conn.execute("SELECT payload FROM editions ORDER BY date DESC LIMIT 1").fetchone()
            )

    def list_editions(self) -> list[Edition]:
        with self._read() as conn:
            rows = conn.execute("SELECT payload FROM editions ORDER BY date DESC").fetchall()
        return [Edition.model_validate_json(r["payload"]) for r in rows]

    def has_editions(self) -> bool:
        with self._read() as conn:
            return conn.execute("SELECT 1 FROM editions LIMIT 1").fetchone() is not None

    # ------------------------------------------------------- runs and locking
    def record_run(self, started: datetime, finished: datetime, report_json: str) -> None:
        with self.transaction() as conn:
            conn.execute(
                "INSERT INTO pipeline_runs (started_at, finished_at, report) VALUES (?, ?, ?)",
                (iso(started), iso(finished), report_json),
            )

    def recent_runs(self, limit: int = 5) -> list[dict[str, object]]:
        with self._read() as conn:
            rows = conn.execute(
                "SELECT started_at, finished_at, report FROM pipeline_runs "
                "ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "started_at": r["started_at"],
                "finished_at": r["finished_at"],
                **json.loads(r["report"]),
            }
            for r in rows
        ]

    def acquire_lock(self, name: str, now: datetime, ttl: timedelta) -> bool:
        """Take the named lock unless someone holds an unexpired one."""
        with self.transaction() as conn:
            row = conn.execute("SELECT expires_at FROM locks WHERE name = ?", (name,)).fetchone()
            if row is not None and row["expires_at"] > iso(now):
                return False
            conn.execute("INSERT OR REPLACE INTO locks VALUES (?, ?)", (name, iso(now + ttl)))
            return True

    def release_lock(self, name: str) -> None:
        with self.transaction() as conn:
            conn.execute("DELETE FROM locks WHERE name = ?", (name,))

    # -------------------------------------------------------------- retention
    def prune(self, older_than: datetime) -> int:
        """Drop articles and stories last published before the cutoff.
        Editions are kept (each carries its own story snapshot)."""
        cutoff = iso(older_than)
        with self.transaction() as conn:
            conn.execute(
                "DELETE FROM story_members WHERE story_id IN "
                "(SELECT id FROM stories WHERE latest_published_at < ?)",
                (cutoff,),
            )
            removed = conn.execute(
                "DELETE FROM stories WHERE latest_published_at < ?", (cutoff,)
            ).rowcount
            conn.execute(
                "DELETE FROM articles WHERE published_at < ? "
                "AND id NOT IN (SELECT article_id FROM story_members)",
                (cutoff,),
            )
            return removed


@lru_cache(maxsize=8)
def get_store(path: str) -> Store:
    """One Store per database path (the server asks for it on every request)."""
    return Store(path)
