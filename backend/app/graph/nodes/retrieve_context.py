from app.graph.state import GraphState
from app.services import retrieval


def retrieve_context(state: GraphState) -> GraphState:
    query_type = state.get("query_type", "general")

    # General queries (greetings, meta questions about the assistant) don't
    # need grounding — skipping retrieval here isn't the empty-retrieval
    # error case, it's simply not applicable.
    if query_type == "general":
        return {"retrieved_documents": []}

    documents = retrieval.retrieve_for_query(
        query=state.get("query", ""),
        story_id=state.get("story_id"),
        category=state.get("category"),
    )
    return {"retrieved_documents": documents}
