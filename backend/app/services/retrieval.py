from app.models.article import Article
from app.services import ranking, sources


def retrieve_for_query(
    *,
    query: str,
    story_id: str | None = None,
    category: str | None = None,
    limit: int = 4,
) -> list[Article]:
    """Resolves the documents a chat answer may be grounded in.

    If story_id is set (the frontend says "the user is reading this
    story"), that article is always included first, followed by related
    articles ranked by shared topics. Otherwise, ranks the full corpus
    (optionally scoped to a category) against the free-text query.

    Returns [] when nothing relevant is found — this is a legitimate,
    expected outcome (see ranking.rank_articles), not a failure.
    """
    if story_id:
        anchor = sources.get_article(story_id)
        if anchor is None:
            return []

        candidates = [a for a in sources.list_articles() if a.id != story_id]
        related_query = " ".join(anchor.topics) or anchor.title
        related = ranking.rank_articles(candidates, related_query, limit=max(limit - 1, 0))
        return [anchor, *related]

    pool = sources.list_articles(category=category) if category else sources.list_articles()
    return ranking.rank_articles(pool, query, limit=limit)
