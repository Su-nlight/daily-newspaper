from app.services import ranking, sources


def test_rank_articles_returns_relevant_first():
    articles = sources.list_articles()
    ranked = ranking.rank_articles(articles, "AI audit framework India")
    assert ranked
    assert ranked[0].id == "story-ai-policy-2026"


def test_rank_articles_empty_query_returns_empty():
    articles = sources.list_articles()
    assert ranking.rank_articles(articles, "") == []


def test_rank_articles_no_match_returns_empty():
    articles = sources.list_articles()
    assert ranking.rank_articles(articles, "zzqqxxnonsense") == []


def test_rank_articles_respects_limit():
    articles = sources.list_articles()
    ranked = ranking.rank_articles(articles, "research AI cloud security", limit=2)
    assert len(ranked) <= 2
