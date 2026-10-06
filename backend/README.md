# Daily Signal — AI Backend

FastAPI + LangGraph + Groq backend for Daily Signal's conversational
assistant and read-only content endpoints. Built per `docs/Module-07.md`.

**This backend is not yet wired into the Next.js frontend.** The frontend
still uses its own TypeScript mock data (`src/lib/api/client.ts`). This
module is backend-only, standalone groundwork — connecting the two is a
future module's job. See `docs/PROJECT_STATE.md`.

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt    # or requirements.txt for prod-only deps

cp .env.example .env
# edit .env and set GROQ_API_KEY
```

## Running

```bash
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive API docs (FastAPI's
auto-generated Swagger UI).

Without `GROQ_API_KEY` set, the server still starts and every endpoint
still works — `/api/chat` just returns a clear "AI assistant isn't
configured yet" message instead of a real answer. This is intentional: see
`app/services/llm.py`.

## Tests

```bash
pytest
```

Tests mock `app.services.llm` so they never make a real network call to
Groq (and can't — this environment generally won't have a Groq API key or
network access to `api.groq.com` either way).

## Architecture

```
START → classify_query → retrieve_context → generate_answer → validate_format → END
```

A single small, linear LangGraph (`app/graph/graph.py`). No branching, no
sub-agents, no multi-agent orchestration — the module spec explicitly asks
to avoid that until a real requirement forces it.

- **classify_query** — deterministic keyword/context routing into `news`,
  `story`, `research`, `career`, or `general`. No LLM call.
- **retrieve_context** — pulls from a small in-memory mock article corpus
  (`app/services/sources.py`, independent of the frontend's mock data — see
  Known issues in `docs/PROJECT_STATE.md`). Returns `[]` when nothing
  matches; that's a legitimate outcome the next node handles explicitly,
  not an error.
- **generate_answer** — the only node that calls Groq (via the centralized
  `app/services/llm.py`, the single place the Groq client is instantiated).
  General queries get a direct conversational prompt; everything else gets
  a context block built by `app/services/summarization.py` (deterministic
  formatting, not a second LLM call) and is instructed to cite sources as
  `[1]`, `[2]`, etc., and to say so honestly if the context is insufficient.
- **validate_format** — builds the response's `sources` list **only** from
  the URLs of documents that were actually retrieved — never from anything
  in the model's raw text. This is what structurally prevents the model
  from inventing a source URL, not just a prompt instruction.

## Error handling

Every Groq failure mode (missing key, rate limit, timeout, non-2xx
response) normalizes to one of two exceptions in `app/services/llm.py`
(`LLMConfigurationError`, `LLMRequestError`). `generate_answer` catches
both and degrades to a clear in-band chat message (HTTP 200, `error` set
in graph state) rather than a 500 — a chat UI can just display the message
without special-casing errors. `app/main.py` adds exception handlers for
the same two types as a safety net for anything called outside the graph,
plus a catch-all handler so no unexpected exception ever leaks a raw
traceback to the frontend.

"Invalid request" (empty message, malformed JSON body) is handled by
FastAPI/Pydantic validation automatically (422) plus an explicit empty-
message check in `app/api/chat.py`. "Missing context" and "empty
retrieval" are the same code path: `retrieve_context` returning `[]` for a
non-general query, handled explicitly in `generate_answer` without an LLM
call.

## Streaming

`POST /api/chat/stream` returns Server-Sent Events (`text/event-stream`):
`{"type": "token", "content": "..."}` per chunk, then a final
`{"type": "done", "sources": [...]}`, or `{"type": "error", "message": "..."}`
if the stream fails mid-flight. It reuses `classify_query`/
`retrieve_context`/`validate_format` directly as plain functions (they're
synchronous, non-LLM transforms — safe to call outside the compiled graph)
and streams tokens from `llm.stream_completion()` as they arrive from Groq.

## Endpoints

| Method | Path                  | Purpose                                   |
| ------ | --------------------- | ------------------------------------------ |
| POST   | `/api/chat`            | Single-shot chat (runs the full graph)    |
| POST   | `/api/chat/stream`     | SSE streaming chat                        |
| GET    | `/api/edition/today`   | Today's edition                           |
| GET    | `/api/edition/{date}`  | Edition by date (`YYYY-MM-DD`)            |
| GET    | `/api/stories`         | List stories, optional `?category=`       |
| GET    | `/api/stories/{id}`    | Single story                              |
| GET    | `/api/search`          | `?q=&category=&source=&topic=`            |
| GET    | `/api/health`          | Liveness + whether Groq is configured     |
