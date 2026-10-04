import json
import uuid
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.graph.graph import get_graph
from app.graph.nodes.classify_query import classify_query
from app.graph.nodes.generate_answer import SYSTEM_PROMPT
from app.graph.nodes.retrieve_context import retrieve_context
from app.graph.nodes.validate_format import validate_format
from app.graph.state import GraphState
from app.models.chat import ChatRequest, ChatResponse
from app.services import llm, summarization

router = APIRouter(prefix="/api", tags=["chat"])


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    if not payload.message.strip():
        raise HTTPException(status_code=422, detail="message must not be empty")

    conversation_id = payload.conversation_id or str(uuid.uuid4())

    initial_state: GraphState = {
        "messages": [{"role": "user", "content": payload.message}],
        "query": payload.message,
        "story_id": payload.context.story_id,
        "edition_id": payload.context.edition_id,
        "category": payload.context.category,
    }

    graph = get_graph()
    result = await graph.ainvoke(initial_state)

    return ChatResponse(
        message=result.get("answer", ""),
        sources=result.get("sources", []),
        conversation_id=conversation_id,
    )


@router.post("/chat/stream")
async def chat_stream(payload: ChatRequest) -> StreamingResponse:
    """SSE variant of /api/chat. Reuses the same deterministic nodes
    (classify_query, retrieve_context, validate_format — all plain sync
    functions, safe to call outside the compiled graph) and streams tokens
    from Groq directly rather than waiting for a full single-shot answer.
    """
    if not payload.message.strip():
        raise HTTPException(status_code=422, detail="message must not be empty")

    async def event_generator() -> AsyncGenerator[str, None]:
        state: GraphState = {
            "query": payload.message,
            "story_id": payload.context.story_id,
            "edition_id": payload.context.edition_id,
            "category": payload.context.category,
        }
        state.update(classify_query(state))
        state.update(retrieve_context(state))

        query_type = state.get("query_type", "general")
        documents = state.get("retrieved_documents", [])

        if query_type != "general" and not documents:
            message = (
                "I couldn't find any Daily Signal coverage matching that — try "
                "rephrasing, or ask about a specific story you're reading."
            )
            yield _sse({"type": "token", "content": message})
            yield _sse({"type": "done", "sources": []})
            return

        if query_type == "general":
            user_prompt = payload.message
        else:
            context_block = summarization.format_context(documents)
            user_prompt = (
                f"CONTEXT:\n{context_block}\n\n"
                f"QUESTION: {payload.message}\n\n"
                "Answer using only the context above, citing sources like [1]."
            )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        full_text = ""
        try:
            for chunk in llm.stream_completion(messages):
                full_text += chunk
                yield _sse({"type": "token", "content": chunk})
        except llm.LLMConfigurationError:
            yield _sse(
                {
                    "type": "token",
                    "content": "The AI assistant isn't configured yet — GROQ_API_KEY is missing.",
                }
            )
            yield _sse({"type": "done", "sources": []})
            return
        except llm.LLMRequestError as exc:
            yield _sse({"type": "error", "message": str(exc)})
            return

        state["answer"] = full_text
        state.update(validate_format(state))
        sources = [source.model_dump() for source in state.get("sources", [])]
        yield _sse({"type": "done", "sources": sources})

    return StreamingResponse(event_generator(), media_type="text/event-stream")
