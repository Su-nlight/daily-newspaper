"""Deterministic query classification — no LLM call. The module spec
explicitly prefers deterministic routing where possible; a keyword/context
heuristic is fast, free, and predictable for the five query types this
graph needs to distinguish.
"""

from app.graph.state import GraphState, QueryType

_STORY_HINTS = ("this story", "this article", "the article", "this piece")
_RESEARCH_KEYWORDS = ("research", "paper", "study", "benchmark", "dataset", "arxiv")
_CAREER_KEYWORDS = ("job", "career", "hiring", "resume", "salary", "interview", "skill")
_NEWS_KEYWORDS = ("today", "latest", "news", "happening", "headline", "edition", "brief")


def classify_query(state: GraphState) -> GraphState:
    query = state.get("query", "").lower()

    query_type: QueryType
    if state.get("story_id") or any(hint in query for hint in _STORY_HINTS):
        query_type = "story"
    elif any(keyword in query for keyword in _RESEARCH_KEYWORDS):
        query_type = "research"
    elif any(keyword in query for keyword in _CAREER_KEYWORDS):
        query_type = "career"
    elif any(keyword in query for keyword in _NEWS_KEYWORDS):
        query_type = "news"
    else:
        query_type = "general"

    return {"query_type": query_type}
