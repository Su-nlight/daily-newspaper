"""START -> classify_query -> retrieve_context -> generate_answer ->
validate_format -> END

A single small, linear state graph — no branching, no sub-agents. Expand
only when a real requirement appears (per the module spec's explicit
instruction not to build a multi-agent system just because LangGraph is
available).
"""

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.graph.nodes.classify_query import classify_query
from app.graph.nodes.generate_answer import generate_answer
from app.graph.nodes.retrieve_context import retrieve_context
from app.graph.nodes.validate_format import validate_format
from app.graph.state import GraphState


def build_graph() -> CompiledStateGraph:
    graph = StateGraph(GraphState)

    graph.add_node("classify_query", classify_query)
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("generate_answer", generate_answer)
    graph.add_node("validate_format", validate_format)

    graph.add_edge(START, "classify_query")
    graph.add_edge("classify_query", "retrieve_context")
    graph.add_edge("retrieve_context", "generate_answer")
    graph.add_edge("generate_answer", "validate_format")
    graph.add_edge("validate_format", END)

    return graph.compile()


_compiled_graph: CompiledStateGraph | None = None


def get_graph() -> CompiledStateGraph:
    """Lazily compiles and caches the graph. Compiling doesn't require
    GROQ_API_KEY — only actually invoking generate_answer does — so this is
    safe to call at import time or in tests without any credentials."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph
