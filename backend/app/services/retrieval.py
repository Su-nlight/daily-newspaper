from app.models.article import Article
from app.services import ranking, sources


def _scope_pool(
    category: str | None,
    edition_id: str | None,
    search_result_ids: list[str] | None,
) -> list[Article] | None:
    """The set of articles the user's current page puts "in scope", or None
    when the page provides no scope. Search results win over a category,
    which wins over an edition — each page sends only its own context, so
    in practice at most one is set."""
    if search_result_ids is not None:
        return sources.get_articles(search_result_ids)
    if category:
        return sources.list_articles(category=category)
    if edition_id:
        edition = sources.get_edition_by_id(edition_id)
        return list(edition.stories) if edition else None
    return None


def retrieve_for_query(
    *,
    query: str,
    story_id: str | None = None,
    category: str | None = None,
    edition_id: str | None = None,
    search_result_ids: list[str] | None = None,
    limit: int = 4,
) -> list[Article]:
    """Resolves the documents a chat answer may be grounded in.

    If story_id is set (the user is reading this story), that article is
    always included first, followed by related articles ranked by shared
    topics. Otherwise the query is ranked against the user's page scope
    (search results, a category, or an edition) or, with no scope, the
    whole corpus.

    With no keyword match, a page scope still returns its own articles —
    "summarize these results" has no keywords in common with them, but the
    user plainly means the stories in front of them. Without a scope, no
    match returns [] — a legitimate outcome, not a failure.
    """
    if story_id:
        anchor = sources.get_article(story_id)
        if anchor is None:
            return []

        candidates = [a for a in sources.list_articles() if a.id != story_id]
        related_query = " ".join(anchor.topics) or anchor.title
        related = ranking.rank_articles(candidates, related_query, limit=max(limit - 1, 0))
        return [anchor, *related]

    scope = _scope_pool(category, edition_id, search_result_ids)
    pool = scope if scope is not None else sources.list_articles()

    ranked = ranking.rank_articles(pool, query, limit=limit)
    if ranked:
        return ranked
    if scope:
        return scope[:limit]
    return []
