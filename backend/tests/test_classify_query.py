from app.graph.nodes.classify_query import classify_query


def test_story_context_takes_priority():
    result = classify_query({"query": "what happened", "story_id": "story-1"})
    assert result["query_type"] == "story"


def test_story_hint_without_context():
    result = classify_query({"query": "can you summarize this article"})
    assert result["query_type"] == "story"


def test_research_keyword():
    result = classify_query({"query": "any new research on this benchmark"})
    assert result["query_type"] == "research"


def test_career_keyword():
    result = classify_query({"query": "any hiring trends for this job"})
    assert result["query_type"] == "career"


def test_news_keyword():
    result = classify_query({"query": "what's the latest news today"})
    assert result["query_type"] == "news"


def test_general_fallback():
    result = classify_query({"query": "hello, who are you?"})
    assert result["query_type"] == "general"


def test_empty_query_is_general():
    result = classify_query({})
    assert result["query_type"] == "general"
