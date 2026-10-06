# Daily Signal Project State

## Completed

- Module 01 Foundation
- Module 02 Design System
- Module 03 Daily Newspaper Homepage
- Module 04 Story and Category Pages
- Module 05 Personalization and Topics
- Module 06 Search, Saved Stories and Archive
- Module 07 LangGraph + Groq Backend

## Current

Module 07 is complete. **Not yet merged/tested against a real Groq API key or
wired into the Next.js frontend** — see Known issues. Awaiting Module 08.

## Routes

No frontend route changes in this module — `/chat` and `ChatBubble` still
talk to nothing real (unchanged from Module 06). This module is entirely
new: a standalone `backend/` directory. See `backend/README.md` for its own
setup and endpoint docs; summarized below.

## Backend (new in Module 07)

`backend/` — Python 3.12, FastAPI, LangGraph, Groq, Pydantic. Fully
independent of the Next.js app (`src/`); nothing in `src/` was touched this
module.

**Structure** (matches the module spec's requested layout exactly):

```
backend/app/
  main.py              FastAPI app, CORS, global exception handlers
  api/chat.py           POST /api/chat, POST /api/chat/stream (SSE)
  api/edition.py         GET /api/edition/today, /api/edition/{date}
  api/stories.py          GET /api/stories, /api/stories/{id}
  api/search.py            GET /api/search
  graph/state.py          Typed LangGraph state (TypedDict)
  graph/graph.py           Compiles the 4-node linear graph
  graph/nodes/              classify_query, retrieve_context, generate_answer, validate_format
  models/article.py, edition.py, chat.py, preferences.py    Pydantic models
  services/retrieval.py, ranking.py, summarization.py, sources.py, llm.py
  config.py                Centralized settings (pydantic-settings)
```

**Graph:** `START → classify_query → retrieve_context → generate_answer →
validate_format → END`. Linear, no branching, no multi-agent orchestration
— per the module's explicit instruction not to build one until a real
requirement forces it.

- `classify_query` — **deterministic**, no LLM call. Keyword/context
  heuristic routes into `news` / `story` / `research` / `career` /
  `general`.
- `retrieve_context` — keyword-overlap ranking (`services/ranking.py`,
  `services/retrieval.py`) against a small in-memory mock corpus
  (`services/sources.py`, 8 articles). Returns `[]` on no match — a real,
  expected outcome, not an error.
- `generate_answer` — the only node that calls Groq, via the centralized
  `services/llm.py` (the single place the Groq client is instantiated —
  `@lru_cache`'d). Skips the LLM call entirely for empty retrieval on a
  grounded query type (saves a call, avoids inviting hallucination).
- `validate_format` — builds `sources` **only** from retrieved documents'
  own URLs, never from the model's raw text, structurally preventing
  invented source URLs (verified by test —
  `test_validate_format_never_trusts_a_url_from_the_answer_text`).

**Streaming:** `POST /api/chat/stream` is a real, working SSE
implementation (not just scaffolding) — reuses the three non-LLM nodes as
plain functions and streams tokens from `llm.stream_completion()`.

**Error handling:** every Groq failure mode (missing key, rate limit,
timeout, bad response) normalizes to `LLMConfigurationError` /
`LLMRequestError` in `services/llm.py`. `generate_answer` catches both and
degrades to a clear in-band chat message (HTTP 200) rather than a 500.
`main.py` adds exception handlers for the same two types as a safety net,
plus a catch-all so no unhandled exception leaks a traceback.

**Verified, not just written:**
- `pytest` — 38 tests, all passing (`backend/tests/`). Covers
  classification, ranking, retrieval, citation-filtering (including the
  "model can't inject a URL" case explicitly), and API-level behavior via
  FastAPI's `TestClient` with `app.services.llm` mocked.
- `ruff check` and `mypy app` — both clean.
- Full live-server smoke test via `uvicorn` + `curl`: every REST endpoint,
  `/api/chat` (general query, news query, story-context query, empty
  message → 422), and `/api/chat/stream` (real SSE event stream) — all
  exercised against a running server with **no GROQ_API_KEY set**,
  confirming the graceful-degradation path works for real, not just in
  mocked tests.

## API contracts (backend)

Request/response shapes match the module spec exactly:

```
POST /api/chat
{ "message": "...", "conversation_id": "...", "context": { "story_id": "...", "edition_id": "..." } }
→ { "message": "...", "sources": [{"publisher","url","title"}], "conversation_id": "..." }
```

`ChatContext` also accepts `category` (needed because the spec's own
"Context" section says the graph should use current story/edition/category
— `story_id` and `edition_id` alone weren't enough).

## Known issues

- **Not wired to the frontend.** The Next.js app's `ChatBubble`/`ChatPanelShell`/`AskAboutStory` (Modules 02–06) still show a static "not connected yet" placeholder and don't call this backend. `lib/api/client.ts` still serves mock data. This is explicitly a future module's job — Module 07's objective was "build the backend," not integrate it.
- **No real Groq API key was available in this environment**, and `api.groq.com` isn't reachable from this sandbox either way. Every Groq-calling code path (`generate_completion`, `stream_completion`) is verified only against: (a) the real, unmocked "no API key" failure path (genuinely exercised, not mocked), and (b) mocked success/failure responses in tests. **The actual Groq integration — real model output, real latency, real rate-limit behavior — has never been exercised.** Test with a real key before relying on this in any demo.
- **The backend's mock corpus (`services/sources.py`) is independent of the frontend's** (`src/data/mock-newspaper.ts`) — different language, duplicated by hand, not generated from a shared source. They currently describe a similar but not identical set of stories. A future integration module should decide whether the backend becomes the single source of truth (frontend fetches from it) or whether to formalize a shared schema — right now there are two separate "mock newsrooms."
- **No conversation history is persisted or reused.** `conversation_id` is accepted and echoed back, but each `/api/chat` call only sees the single incoming `message` — multi-turn context isn't threaded through `messages` in `GraphState` yet, even though the state shape has a `messages` field for it.
- **No rate limiting, no auth, no request size limits** on the FastAPI app itself. Fine for local development; not production-ready.
- **CORS defaults to `http://localhost:3000` only.** Set `CORS_ALLOW_ORIGINS` (comma-separated) for any other deployment target.

## Decisions that must not be changed

- **`services/llm.py` is the only file that imports `groq` or instantiates a `Groq` client.** Every node and service that needs the LLM calls `generate_completion()` / `stream_completion()` from here. Don't add a second `Groq(...)` instantiation anywhere else, even "just for one node" — this was an explicit module requirement.
- **No model name is hardcoded outside `config.py`'s `groq_model` default.** Every call site reads `get_settings().groq_model`.
- **`validate_format` is the only place `sources` gets built, and it only ever uses `retrieved_documents[i].source_url`** — never a URL parsed or guessed from the model's answer text. This is the structural guarantee against invented citations; don't "simplify" it into trusting inline markdown links from the model.
- **`classify_query` stays deterministic (no LLM call).** If a future module wants smarter classification, that's a deliberate, separately-justified change — not a default to drift into.
- **The graph stays linear and 4 nodes.** Don't add a router/supervisor node or parallel branches without a concrete requirement that the current linear flow can't satisfy — this was an explicit instruction in the module spec, not just a starting point to immediately outgrow.
- **`retrieve_for_query`/`rank_articles` return `[]` on no match — never a padded "best effort" fallback list.** `generate_answer` depends on `[]` meaning "genuinely nothing relevant" to trigger its honest "couldn't find anything" response instead of calling the LLM.
- **The backend is standalone.** Nothing in `src/` (the Next.js app) should import from or assume the existence of `backend/` until an explicit integration module says otherwise.
