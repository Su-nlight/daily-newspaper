from app.graph.state import GraphState
from app.models.article import Article
from app.services import llm, summarization

SYSTEM_PROMPT = """You are the Daily Signal assistant, a concise newsroom AI.

Rules:
- Only use facts from the CONTEXT block you're given. Never invent facts, \
sources, or URLs.
- If the context doesn't contain enough information to answer, say so \
honestly instead of guessing.
- When you use a fact from a numbered context entry, cite it inline like [1].
- Keep answers conversational and to the point — a few sentences, not an essay.
- You may use light Markdown (short lists, bold, inline code) when it helps.
- Do not claim to have real-time access to the internet beyond the context provided.
"""

# Prior turns replayed to the model. Enough for natural follow-ups without
# letting a long conversation blow the context window.
MAX_HISTORY_TURNS = 8


def no_coverage_message() -> str:
    return (
        "I couldn't find any Daily Signal coverage matching that — try "
        "rephrasing, or ask about a specific story you're reading."
    )


def build_messages(
    *,
    query: str,
    query_type: str,
    documents: list[Article],
    history: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """The chat messages sent to the model: system prompt, recent history,
    then the current question (with retrieved context for grounded types).
    Shared by the graph's generate_answer node and the streaming endpoint so
    both build prompts identically."""
    if query_type == "general":
        user_prompt = query
    else:
        context_block = summarization.format_context(documents)
        user_prompt = (
            f"CONTEXT:\n{context_block}\n\n"
            f"QUESTION: {query}\n\n"
            "Answer using only the context above, citing sources like [1]."
        )

    recent = (history or [])[-MAX_HISTORY_TURNS:]
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        *({"role": turn["role"], "content": turn["content"]} for turn in recent),
        {"role": "user", "content": user_prompt},
    ]


def generate_answer(state: GraphState) -> GraphState:
    query = state.get("query", "")
    query_type = state.get("query_type", "general")
    documents = state.get("retrieved_documents", [])

    if query_type != "general" and not documents:
        # Empty retrieval for a grounded query type: say so honestly rather
        # than asking the model to answer from nothing (which invites
        # hallucination). No LLM call needed for this branch.
        return {"answer": no_coverage_message()}

    messages = build_messages(
        query=query,
        query_type=query_type,
        documents=documents,
        history=state.get("history"),
    )

    try:
        answer = llm.generate_completion(messages)
    except llm.LLMConfigurationError:
        return {
            "answer": "The AI assistant isn't configured yet — GROQ_API_KEY is missing.",
            "error": "llm_not_configured",
        }
    except llm.LLMRequestError as exc:
        return {
            "answer": f"The AI assistant is temporarily unavailable. {exc}",
            "error": "llm_request_failed",
        }

    return {"answer": answer}
