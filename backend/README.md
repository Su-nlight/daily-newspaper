# Daily Signal — AI Backend

FastAPI + LangGraph + Groq backend for Daily Signal's conversational
assistant and read-only content endpoints. Built per `docs/Module-07.md`.

The Next.js chat (Module 08) calls `POST /api/chat/stream` from the browser
(`src/lib/api/chat.ts`). The rest of the frontend still uses its own mock data
(`src/lib/api/client.ts`). See `docs/PROJECT_STATE.md`.

**Corpus:** answers are grounded in `app/data/corpus.json`, generated from the
frontend's mock data. After changing `src/data/mock-newspaper.ts`, run
`npm run export:corpus` from the repo root.

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

(52 tests.) Tests mock `app.services.llm` so they never make a real network call to
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
| GET    | `/api/edition/today`   | Latest edition (+ optional preferences)   |
| GET    | `/api/edition/{date}`  | Edition by date (`YYYY-MM-DD`)            |
| GET    | `/api/stories`         | List stories, optional `?category=`       |
| GET    | `/api/stories/{id}`    | Single story                              |
| GET    | `/api/search`          | `?q=&category=&source=&topic=`            |
| GET    | `/api/health`          | Liveness + whether Groq is configured     |

## Chat request

```json
{
  "message": "How could this affect my research?",
  "conversation_id": "optional, echoed back",
  "history": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}],
  "context": {
    "story_id": "story the user is reading",
    "edition_id": "edition being viewed",
    "category": "category page being viewed",
    "search_query": "current search",
    "search_result_ids": ["ids of the current search results"]
  }
}
```

Everything except `message` is optional. `history` (last 8 turns are used)
makes follow-ups work; the `context` fields scope retrieval (a story id wins,
then search results, then category, then edition). Each returned source has an
`index` matching the `[n]` citation marker in the answer text.

## News and daily edition pipeline (Module 09)

Real content replaces the mock corpus. Until the first run the API serves the
seed corpus (`CONTENT_SOURCE=auto`); afterwards it serves generated editions.

```bash
python -m app.pipeline sources          # configured sources, active/inactive
python -m app.pipeline run              # fetch -> process -> publish today's edition
python -m app.pipeline run --no-llm     # extractive summaries only (no Groq calls)
python -m app.pipeline run --no-fetch   # rebuild from already-stored articles
python -m app.pipeline run --date 2026-11-03 --json
python -m app.pipeline status           # latest edition and recent runs
```

`run` exits 0 for ok/degraded/skipped and 1 when no edition could be produced.
It prints a per-source health report - **read it on the first run**: the feed
URLs in `app/data/pipeline_sources.json` are unverified, and it is where you
add, remove or disable sources (no code change needed).

### Scheduling

The pipeline is idempotent, so scheduling is "run the CLI once a day" - running
it more often is harmless (unchanged stories reuse their summaries, an
identical edition writes nothing, and an advisory lock stops overlapping runs).
Set `EDITION_TIMEZONE` first, and make sure the server and the job share
`DATABASE_PATH`.

```cron
# 06:30 every day, from the backend directory
30 6 * * *  cd /path/to/backend && .venv/bin/python -m app.pipeline run >> pipeline.log 2>&1
```

systemd timers, a GitHub Actions `schedule:` job or a cloud scheduler work the
same way. There is intentionally no HTTP endpoint to trigger a run: the backend
has no auth, and a run spends Groq budget.

### Output

`GET /api/edition/today` returns `metadata`, the ranked `stories` (each with its
full `sources` list, `importance` tier, `entities`, `related_ids`), `top_story_ids`,
`sections`, the 60-second `brief` and - when preferences are supplied -
`personalized`:

```
/api/edition/today?topics=topic-agents:0.9,topic-rag&regions=india&sources=source-tech-ledger
```

Stories, sections, the brief and personalized entries reference each other by
story id. No numeric scores are ever returned.

### Content source

`CONTENT_SOURCE=auto|pipeline|seed` (see `.env.example`). Use `pipeline` once the
frontend reads real editions; `seed` reproduces pre-Module-09 behaviour.

### How summaries stay honest

The model only sees each story's own source excerpts, and its output is
*verified* before use: any number, quote, URL or proper noun that is not in the
evidence rejects the summary, and the story falls back to extractive text taken
directly from the sources. Source links and attribution are never taken from
model output. The run report's `summary_fallback_reasons` shows how often that
happens.
