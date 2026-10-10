import json
import uuid
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.graph.graph import get_graph
from app.graph.nodes.classify_query import classify_query
from app.graph.nodes.generate_answer import build_messages, no_coverage_message
from app.graph.nodes.retrieve_context import retrieve_context
from app.graph.nodes.validate_format import validate_format
from app.graph.state import GraphState
from app.models.chat import ChatRequest, ChatResponse
from app.services import llm

router = APIRouter(prefix="/api", tags=["chat"])


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


def _initial_state(payload: ChatRequest) -> GraphState:
    return {
        "messages": [{"role": "user", "content": payload.message}],
        "query": payload.message,
        "story_id": payload.context.story_id,
        "edition_id": payload.context.edition_id,
        "category": payload.context.category,
        "search_query": payload.context.search_query,
        "search_result_ids": payload.context.search_result_ids,
        "history": [turn.model_dump() for turn in payload.history],
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    if not payload.message.strip():
        raise HTTPException(status_code=422, detail="message must not be empty")

    conversation_id = payload.conversation_id or str(uuid.uuid4())

    graph = get_graph()
    result = await graph.ainvoke(_initial_state(payload))

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

    Events: {"type": "token", "content"}, then {"type": "done", "sources",
    "conversation_id"}; or {"type": "error", "message"} if the stream fails.
    """
    if not payload.message.strip():
        raise HTTPException(status_code=422, detail="message must not be empty")

    conversation_id = payload.conversation_id or str(uuid.uuid4())

    async def event_generator() -> AsyncGenerator[str, None]:
        state = _initial_state(payload)
        state.update(classify_query(state))
        state.update(retrieve_context(state))

        query_type = state.get("query_type", "general")
        documents = state.get("retrieved_documents", [])

        if query_type != "general" and not documents:
            yield _sse({"type": "token", "content": no_coverage_message()})
            yield _sse({"type": "done", "sources": [], "conversation_id": conversation_id})
            return

        messages = build_messages(
            query=payload.message,
            query_type=query_type,
            documents=documents,
            history=state.get("history"),
        )

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
            yield _sse({"type": "done", "sources": [], "conversation_id": conversation_id})
            return
        except llm.LLMRequestError as exc:
            yield _sse({"type": "error", "message": str(exc)})
            return

        state["answer"] = full_text
        state.update(validate_format(state))
        sources = [source.model_dump() for source in state.get("sources", [])]
        yield _sse({"type": "done", "sources": sources, "conversation_id": conversation_id})

    return StreamingResponse(event_generator(), media_type="text/event-stream")
