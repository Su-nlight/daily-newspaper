"""Deterministic keyword-overlap ranking — no embeddings, no ML model.
Mirrors the frontend's stance (Module 05: rule-based, explainable
personalization, not ML) applied here to retrieval instead of preferences.
"""

import re

from app.models.article import Article

_WORD_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> set[str]:
    return set(_WORD_RE.findall(text.lower()))


def score_article(article: Article, query_terms: set[str]) -> int:
    haystack = _tokenize(
        f"{article.title} {article.summary} {' '.join(article.topics)} {article.category}"
    )
    return len(query_terms & haystack)


def rank_articles(
    articles: list[Article],
    query: str,
    *,
    limit: int | None = None,
) -> list[Article]:
    """Ranks articles by keyword overlap with `query`. Returns [] (not a
    fallback list) when the query has no term overlap with anything —
    empty retrieval is a real, expected outcome the graph must handle, not
    an error to paper over here."""
    query_terms = _tokenize(query)
    if not query_terms:
        return []

    scored = [(score_article(article, query_terms), article) for article in articles]
    scored = [(score, article) for score, article in scored if score > 0]
    scored.sort(key=lambda pair: pair[0], reverse=True)

    ranked = [article for _, article in scored]
    return ranked[:limit] if limit is not None else ranked
