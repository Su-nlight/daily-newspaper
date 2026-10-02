from app.graph.state import GraphState
from app.services import llm, summarization

SYSTEM_PROMPT = """You are the Daily Signal assistant, a concise newsroom AI.

Rules:
- Only use facts from the CONTEXT block you're given. Never invent facts, \
sources, or URLs.
- If the context doesn't contain enough information to answer, say so \
honestly instead of guessing.
- When you use a fact from a numbered context entry, cite it inline like [1].
- Keep answers conversational and to the point — a few sentences, not an essay.
- Do not claim to have real-time access to the internet beyond the context provided.
"""


def generate_answer(state: GraphState) -> GraphState:
    query = state.get("query", "")
    query_type = state.get("query_type", "general")
    documents = state.get("retrieved_documents", [])

    if query_type == "general":
        user_prompt = query
    elif not documents:
        # Empty retrieval for a grounded query type: say so honestly rather
        # than asking the model to answer from nothing (which invites
        # hallucination). No LLM call needed for this branch.
        return {
            "answer": (
                "I couldn't find any Daily Signal coverage matching that — try "
                "rephrasing, or ask about a specific story you're reading."
            ),
        }
    else:
        context_block = summarization.format_context(documents)
        user_prompt = (
            f"CONTEXT:\n{context_block}\n\n"
            f"QUESTION: {query}\n\n"
            "Answer using only the context above, citing sources like [1]."
        )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

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
