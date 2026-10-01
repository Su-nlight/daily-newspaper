from typing import Literal, TypedDict

from app.models.article import Article
from app.models.chat import ChatSourceRef

QueryType = Literal["news", "story", "research", "career", "general"]


class GraphState(TypedDict, total=False):
    """The state threaded through every node. Extends the module spec's
    example ({messages, query_type, query, story_id, retrieved_documents,
    sources, answer}) with edition_id/category, since the "Context" section
    of the spec requires the graph to use more than just story_id.

    total=False: every node returns only the keys it sets; LangGraph merges
    partial updates into the running state (see graph.py), so no node needs
    to know or preserve the full state shape.
    """

    messages: list[dict[str, str]]
    query: str
    query_type: QueryType

    # Frontend-provided context (all optional — a homepage chat has none).
    story_id: str | None
    edition_id: str | None
    category: str | None

    retrieved_documents: list[Article]
    sources: list[ChatSourceRef]
    answer: str

    # Set by a node when something recoverable went wrong (missing API key,
    # Groq request failure). Never raised as an uncaught exception through
    # the graph — see generate_answer.py.
    error: str | None
