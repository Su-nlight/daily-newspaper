# Daily Signal Project State

## Completed

- Module 01 Foundation
- Module 02 Design System
- Module 03 Daily Newspaper Homepage
- Module 04 Story and Category Pages
- Module 05 Personalization and Topics
- Module 06 Search, Saved Stories and Archive
- Module 07 LangGraph + Groq Backend
- Module 08 AI Chat Integration
- Module 09 News and Daily Edition Pipeline (**backend only** — see Known issues)

## Current

Module 09 is complete **on the backend**: a real ingestion → edition pipeline
(`backend/app/pipeline/`), an enriched `GET /api/edition/today`, and a CLI for
the scheduler. **Verified with fixtures and a scripted stand-in for Groq — never
against real feeds, real APIs or a real Groq key** (no network in the build
sandbox) — see Known issues. **The frontend is untouched and still mock-backed;
cutting it over to the Edition API is the natural next step.** Awaiting Module 10.

## Running it

Two processes. Backend (needs `backend/.env`, see `backend/.env.example`):

```bash
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000
```

Frontend (optional `.env.local`, see `.env.example`; defaults to
`http://localhost:8000`):

```bash
npm run dev
```

Checks: `npm run lint`, `npx tsc --noEmit`, `npm test` (vitest), `npm run build`;
backend: `cd backend && pytest && ruff check . && mypy app --ignore-missing-imports`.

## Routes

| Route | Status |
| --- | --- |
| `/` | Homepage (M3). Registers an **edition** chat context. "Relevant to You" is rule-based personalization (M5). |
| `/story/[id]` | Full story page (M4) with save/share/tracking (M5/M6). Registers a **story** chat context. `Ask AI about this story` pins the story and opens the chat. |
| `/category/[slug]` | Category edition (M4). Registers a **category** context. |
| `/search` | URL-driven search via `next/form` (M6). Registers a **search** context (first 20 result ids) when there are results. |
| `/saved` | "Your Library" (M6) — Open / Ask AI / Remove. |
| `/topics` | Preferences center (M5). |
| `/archive`, `/archive/[date]` | Timeline + historical editions (M6). `/archive/[date]` registers an **edition** context. |
| `/chat` | **Full chat (M8)** — the same conversation as the bubble in a larger layout. |
| `/research`, `/career`, `/about` | Placeholders, restyled. |

Every route has styled `loading.tsx` / `not-found.tsx` / `error.tsx` where it
is dynamic or can fail (M4/M6), plus global `not-found.tsx` and `error.tsx`.

## API contracts

### Frontend (`src/lib/api/client.ts`, mock data in `src/data/mock-newspaper.ts`)

All `async`, mock-backed, so a real backend can replace bodies without
changing call sites. Pages call one composing function each.

- Editions: `getTodayEdition`, `getEditionByDate(date)`, `getArchive()`, `getHomepageFeed()` (the only call `/` makes)
- Stories: `getStory(id) → StoryDetail | null`, `getRelatedStories(story, limit)`
- Categories: `getCategory(slug)`, `getCategories()`, `getCategoryFeed(slug)` (the only call the category page makes)
- Search: `searchStories(filters: SearchFilters)` — `{ query?, date?, category?, source?, topic?, region? }`
- Saved: `getSavedStories() → SavedStoryWithArticle[]`, `isStorySaved`, `saveStory`, `removeSavedStory` (real mutation against an in-memory array; only ever called from Server Actions in `src/lib/actions/saved-stories.ts`)
- Personalization: `getTopics`, `getRegions`, `getSources`, `getContentTypes`, `getUserPreferences`, `getPersonalizedStories(preferences, limit) → PersonalizedStory[]` (rule-based; never returns a numeric score)
- **Removed in M8:** the mock `sendChatMessage()` (and its `/chat` placeholder usage). `mockConversation` is now unused.

### Frontend → backend chat (`src/lib/api/chat.ts`, new in M8)

The **only** file that talks to the FastAPI backend. Base URL
`NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`) — a public value;
the Groq key lives only in `backend/.env` and never reaches the browser.

- `streamChatMessage({ message, conversationId, context, history, signal, onToken }) → { sources }` — POSTs to `/api/chat/stream`, parses Server-Sent Events, calls `onToken` per chunk, resolves on the `done` event, rejects with `ChatRequestError` for network/HTTP/server-reported errors or a stream that ends without `done`.
- `toRequestContext(pageContext)` maps the UI's `ChatPageContext` onto the backend's `context` object. `parseSseBuffer` is exported for tests.

### Backend (`backend/`, see `backend/README.md`)

```
POST /api/chat          single-shot, runs the full LangGraph
POST /api/chat/stream   SSE: {"type":"token","content"} ... {"type":"done","sources","conversation_id"} | {"type":"error","message"}
GET  /api/edition/today | /api/edition/{date}   (+ optional preference query params, below)
GET  /api/stories | /api/stories/{id}
GET  /api/search?q=&category=&source=&topic=
GET  /api/health

request: { message, conversation_id?, history: [{role: user|assistant, content}],
           context: { story_id?, edition_id?, category?, search_query?, search_result_ids? } }
source:  { publisher, url, title, index }   # index = the [n] marker used in the answer text
```

`history` and `search_*` context were added in M8 (backwards compatible).

**Edition API (M9).** `Edition` keeps its M7 fields (`id, date, headline, summary,
stories`) and adds `metadata`, `top_story_ids`, `sections`, `brief`,
`personalized`. `stories` is the single master list in rank order (hero first);
everything else **references stories by id** — clients join on `stories[].id`
(this is where `getHomepageFeed`-style composition belongs).

```
metadata:     { generated_at, timezone, pipeline_version, story_count, source_count,
                ai_summarized_count, status: complete|degraded|seed, warnings[],
                personalization_applied }
sections:     [{ slug, title, description, categories[], story_ids[] }]   # top stories excluded
brief:        [{ id, headline, summary }]            # ~60 seconds of reading
personalized: [{ story_id, level: low|medium|high, reasons[] }]   # only when preferences are sent
Article (+M9): content, entities[], importance: lead|major|standard|minor,
               personal_relevance: { level, reasons[] }, sources: [{publisher,url,title,
               published_at,source_id}], related_ids[], region, ai_generated
               (`source`/`source_url` = the primary source; `sources` = all of them)
preferences:  ?topics=topic-agents:0.9,topic-rag &regions=india &sources=… &content_types=research-monitoring
```
There are **no numeric scores anywhere** in the response (a test enforces it).
`/api/edition/today` means "the latest edition", not "calendar today": if a
scheduled run is late, yesterday's edition (see `date`, `metadata.generated_at`)
beats a 404.

## Chat architecture (Module 08)

- **State lives in `ChatProvider`** (`components/chat/ChatProvider.tsx`), mounted in the root layout, so the conversation survives client-side navigation: `conversationId`, `messages` (with per-message `status`: streaming/done/error and `sources`), `status`, the active context, and the compact panel's open state. The compact panel and `/chat` both render `ChatWindow` from this same state — expanding to full chat or returning to the newspaper loses nothing. **A full page reload does lose the conversation** (in-memory only).
- **Context awareness is automatic.** Pages render `<ChatPageContextSetter context={...} />` (registers on mount, clears on unmount). The provider derives `activeContext` = pinned story (from `openChat(story)` / "Ask AI") → else the page's context → else, on `/chat` only, the last registered page context. A pin applies on the page it was made on and on `/chat`; elsewhere the page's own context takes over. Each user message stores the context it was asked in (used for retries, and for "Now discussing: …" dividers when it changes mid-conversation).
- **Multi-turn:** the frontend sends the last 8 completed turns as `history`; the backend replays them to the model.
- **UI:** user messages right-aligned (accent bubble), AI messages left-aligned (plain, Markdown via `react-markdown` + `remark-gfm`, no raw HTML), `[n]` citations become superscript links to the matching entry in the **Sources** list under the answer. Subtle three-dot typing state; failure shows "Something went wrong. Try again." + **Retry** (re-sends the same question with its original context, without duplicating it). Suggested questions are context-specific (`lib/chat/suggestions.ts`; story pages get the four from the spec).
- **Accessibility:** Enter sends, Shift+Enter newline (ignored during IME composition); labelled textarea/buttons; message log is `role="log"` with `aria-live="off"` plus a separate `role="status"` region that announces only transitions (thinking / responding / complete / error) so streaming doesn't spam screen readers; compact panel is a non-modal `dialog`, focuses the input on open, **Escape closes and returns focus to the bubble**; the bubble toggles open/close with `aria-expanded`; on `/chat` the bubble stays but jumps to the full chat input.

## Components

`src/components/`:

- **layout/** `Header`, `Footer`, `PageContainer`, `SectionHeading` · **navigation/** `ThemeToggle`, `MobileNavigation` (M2)
- **newspaper/** `Masthead`; `HeroStory`, `EditionMeta`, `SecondaryStories`, `NewspaperSection` (`layout`, `columns`), `SixtySecondBrief`, `EmptyEditionState`, `RetryButton`, `TrendingTopics`, `ArchiveTimeline` (M2–M6)
- **story/** `StandardStory`, `CompactStory`, `HorizontalStory`, `StoryImagePlaceholder`; `StoryHeader`, `StoryHero`, `StorySummary`, `StorySection`, `KeyFacts`, `SourceList`, `RelatedStories`; `AskAboutStory` (`{id,title,context}`, `compact?`), `SaveStoryButton` (real save via Server Action), `ShareStoryButton`, `RemoveSavedButton`, `SavedStoryCard`, `ArticleViewTracker`, `ArticleCompletionTracker`
- **personalization/** `RelevantToYou`, `WhyRelevant`, `PreferencesEditor`, `TopicPreferenceSlider`, `ToggleChip`, `ReadingTimeSlider`
- **search/** `SearchForm`, `SearchResultCard`
- **chat/** (M8) `ChatProvider` (+ `useChat`), `ChatPageContextSetter`, `ChatBubble`, `ChatPanelShell` (compact container), `FullChat`, `ChatWindow` (shared conversation UI), `ChatMessageItem`, `ChatMarkdown`, `ChatSources`, `ChatComposer`

Tests (new tooling in M8): `npm test` runs vitest + Testing Library in jsdom — `src/lib/api/__tests__`, `src/lib/utils/__tests__`, `src/components/chat/__tests__` (26 tests).

## Backend (Module 07, extended in 08)

`backend/` — Python 3.12, FastAPI, LangGraph, Groq, Pydantic. Graph:
`START → classify_query → retrieve_context → generate_answer → validate_format → END`
(linear, 4 nodes, no agents).

- `classify_query` — deterministic (no LLM): `story` if a story id/“this story” is present; else research/career/news keywords or page-scope phrases (“these results”, “this edition”, “top stories”…) → `news`; else `general`.
- `retrieve_context` — keyword-overlap ranking over the corpus. With a **story id**: that story first + related by topic. With a **page scope** (search result ids > category > edition): ranks within the scope, and if no keyword matches still returns the scope's own articles ("summarize these results"). With no scope and no match: `[]`.
- `generate_answer` — only node that calls Groq (via `services/llm.py`). `build_messages()` (shared with the stream endpoint) = system prompt + last 8 history turns + the question with a numbered context block (summary plus long-form detail where available). Skips the LLM entirely for empty retrieval on a grounded query.
- `validate_format` — builds `sources` only from retrieved documents' own URLs, keeping each source's original `[n]` index.
- Errors: all Groq failures normalize to `LLMConfigurationError` / `LLMRequestError`; the graph path degrades to an in-band 200 message, the stream path emits an `error` event (the frontend shows "Something went wrong. Try again." + Retry).
- **Corpus:** `backend/app/data/corpus.json` is **generated from the frontend mock data** by `npm run export:corpus` (`scripts/export-corpus.mjs`) so chat is grounded in exactly the stories the UI shows (15 articles, 4 editions, plus long-form detail for the 6 stories that have it). Re-run it whenever `src/data/mock-newspaper.ts` changes.
- Default model is `openai/gpt-oss-20b` (the previous default, `llama-3.3-70b-versatile`, is Enterprise-only on Groq and returns 404 for standard keys).

## Pipeline architecture (Module 09)

`backend/app/pipeline/` — one small module per stage, plain functions, no framework:

```
registry (sources JSON) → adapters/* → fetch → normalize → [SQLite store] → dedupe/cluster
  → stories (stable ids, metadata, classify) → rank → summarize(+grounding) → validate_sources
  → edition → store ; CLI: python -m app.pipeline run|sources|status
```

- **Adapters** (`adapters/`): `rss` (+`blog`), `arxiv`, `github` (releases), `nvd` (CVEs ≥ `min_cvss`), `news_api` (NewsAPI-style). Each emits `RawItem`; register a new provider with `register_adapter(kind, adapter)` — nothing else changes. Sources live in `app/data/pipeline_sources.json` (no code to add a feed); credentials are Settings fields referenced by name, never in the file.
- **Fetch** runs sources concurrently and in isolation; a failing source lands in the run report, never aborts the run. Responses are size-capped, retried once, XML is parsed with `defusedxml`, and URLs must be public http(s) (no `javascript:`, `file:`, localhost/private IPs).
- **Dedupe** (`dedupe.py`): canonical URL, normalized title and CVE-id set merge outright; otherwise TF-IDF cosine over title + lead summary. Guards: 48 h window, different CVE ids never merge, a publisher never merges with itself on similarity, average-link (no A~B~C chaining), minimum distinctive text. `SimilarityModel` is the seam for real embeddings.
- **Story ids are assigned once and persisted** (`stories.assign_story_ids`): a cluster containing an already-known article inherits that story's id; only all-new clusters mint one. That is what makes reruns update instead of duplicate while stories gain sources.
- **Classify / metadata**: rule-based (`taxonomy.py`) — category slugs, topic ids/names and region ids match the frontend; 4 topics are new (LLMs, AI Policy, Semiconductors, Open Source). Entities: CVE ids, a gazetteer, acronyms, body proper nouns.
- **Rank** (`rank.py`): freshness · importance · topic · personal · source quality · geographic, explicit `RankWeights`. Scores stay in the backend; the API gets an `importance` tier and `personal_relevance` reasons (wording mirrors the frontend's `scoreArticle`). Personalization is applied per request in `api/edition.py`; the stored edition is shared.
- **Summarize** (`summarize.py` + `grounding.py`): the LLM only sees the story's own source excerpts. Its JSON output is *verified* — any number, quote, URL, domain or proper noun not in the evidence rejects the output and the story gets deterministic **extractive** text; key facts are checked against the single source they cite. Headlines, URLs and attribution always come from metadata. Structured facts (CVSS, release tag, arXiv authors) come straight from metadata. Budgeted (`PIPELINE_MAX_LLM_STORIES`, best stories first); unchanged stories reuse their summary.
- **Validate sources**: ≥1 valid, configured, attributable source per story; no URLs inside generated text.
- **Idempotent**: `articles.canonical_url` UNIQUE, stable story ids, editions keyed by date with a content hash (identical rebuild writes nothing), an advisory lock against overlapping runs, and a guard that never replaces a healthy edition with one under half its size.
- **Read side** (`services/sources.py`): `CONTENT_SOURCE=auto|pipeline|seed`. In `auto`, pipeline content is served once an edition exists; listing/search never mix in seed stories, but explicit id/date lookups fall back to the seed corpus so the frontend's mock story ids keep working in chat during the migration.

## Known issues

**News pipeline (M9)**
- **Never run against real feeds, APIs or Groq.** The build sandbox has no outbound network. Everything is tested with fixtures (`httpx.MockTransport`) and a scripted fake LLM. The feed URLs in `pipeline_sources.json` were written from memory and are **unverified** — run `python -m app.pipeline run` and read the per-source report; fix or disable what fails. Real feeds will expose parsing edge cases the fixtures don't.
- **Thresholds are tuned on a small fixture set.** Dedupe thresholds (0.40 / 0.28), classification keyword weights, ranking weights and the grounding verifier's strictness need tuning on real data. Watch `summary_fallback_reasons` in the run report: a high `ungrounded` share means the verifier is stricter than it needs to be (or the prompt needs work).
- Similarity is lexical (TF-IDF), so paraphrases with little shared vocabulary won't cluster; English only.
- `why_it_matters` is **not generated** (implications aren't facts in the evidence), so pipeline stories have it `null`; the story page must tolerate that.
- Only feed-provided summaries/excerpts are stored — no full-article scraping. A story's `content` is Daily Signal's own text (generated or a ≤2-sentence extract), not a republished article.
- No link-liveness check; no image fetching/validation beyond URL shape; no ads/paywall detection.
- **The frontend still reads mock data.** Chat resolves the mock story ids via the seed fallback, but until `getHomepageFeed` etc. consume `/api/edition/today`, the UI and the pipeline show different stories. Field mapping: backend is snake_case (`source_url`, `published_at`, `image_url`); `Article.importance` is a tier string; see "Edition API" above.
- The chat context block cites a story's *primary* source only; `validate_format` doesn't yet list a cluster's other publications.
- SQLite is single-node (WAL, per-call connections). `Store` is the seam if you need Postgres. Stories/articles are pruned after `PIPELINE_RETENTION_DAYS` (90); editions are kept with their own story snapshot.
- `EDITION_TIMEZONE` defaults to UTC, so "today" rolls over at 00:00 UTC. Set it (e.g. `Asia/Kolkata`) before scheduling.
- There is deliberately **no HTTP endpoint to trigger a run** (the backend has no auth and a run spends LLM budget). Scheduling = run the CLI.


**Chat / backend (M7–M8)**
- **Never exercised against real Groq or a real browser.** `api.groq.com` isn't reachable from the build sandbox. The frontend was verified (a) in jsdom with a mocked network (26 tests) and (b) by driving the real `streamChatMessage` against the real FastAPI server with a stand-in for `llm.stream_completion`. Real model output, latency and rate limits are untested, and **no one has looked at the chat UI in an actual browser** — layout, spacing, dark mode and the compact panel's size on small screens are unverified visually.
- **Conversation is lost on a full page reload** (provider state is in memory). Navigating client-side, including to `/chat` and back, keeps it.
- **No auth, rate limiting or request-size limits** on the backend; CORS allows only `http://localhost:3000` by default (`CORS_ALLOW_ORIGINS`).
- The corpus is a **generated copy** of the frontend mock data, not a shared source — it goes stale until `npm run export:corpus` is re-run. `corpus.json` is committed.
- Only the streaming endpoint is used by the UI; `POST /api/chat` (non-streaming) is kept for API consumers/tests.
- Search context sends at most the first 20 result ids. "General" questions (greetings, anything with no news/story/research/career keyword and no scope phrase) are not grounded — the model answers without retrieved context.
- Vitest is pinned to v3 because v5 requires `@types/node` ≥ 22 and the project is on 20.
- `backend/.env.example` was never actually committed before M8 (the root `.gitignore` had `.env*`); `.env.example` files are now whitelisted.

**Frontend (M3–M6)**
- No real images: every story visual is `StoryImagePlaceholder` (`Article.imageUrl` values are fake).
- Fonts are system stacks (a `next/font/google` attempt failed in the build sandbox); components read `var(--font-display)` / `var(--font-sans)` only, so swapping is a two-line change.
- `Article.category` is a loose string matched to `Category.slug`; only 5 of the 9 spec'd categories exist (others render "Category not found").
- `notFound()` on streamed dynamic routes returns HTTP 200 (documented Next behavior, with an automatic `noindex`).
- Preferences on `/topics` aren't persisted and aren't wired into the homepage (which reads the mock user's preferences server-side). Behavioral signals are only logged (console + capped localStorage).
- Region matching is approximate (US sources → "Global"; Japan/South Korea/Singapore match nothing).
- `Article.relevanceScore` / `whyRelevant` are legacy and unused.
- Saved stories are an in-memory server array: reset on restart, shared by all visitors (no auth).
- Archive has 4 fixed dates; `getRelatedStories` doesn't model entities; reading time is a word-count heuristic.

## Decisions that must not be changed

**Chat / backend**
- `services/llm.py` is the only place that imports `groq` or builds a client; the model name lives only in `config.py` / `GROQ_MODEL`.
- `src/lib/api/chat.ts` is the only frontend code that calls the backend; **the Groq key never goes in any `NEXT_PUBLIC_*` variable or the browser bundle.**
- `validate_format` builds `sources` only from retrieved documents' URLs — never from model text. Frontend source links come only from the `sources` field; the markdown renderer must keep rejecting raw HTML.
- `classify_query` stays deterministic; the graph stays linear/4 nodes; add nodes only for a concrete requirement.
- Retrieval returns `[]` when nothing matches **and no page scope was given** (generate_answer relies on that to answer honestly without an LLM call). With an explicit page scope it returns the scope's articles — don't extend that fallback to unscoped queries.
- Conversation state lives in `ChatProvider` in the root layout. New entry points call `useChat()`; pages describe themselves with `ChatPageContextSetter` — don't add per-page chat state or let a page send its own context to the backend.
- The compact panel and `/chat` must keep rendering the same `ChatWindow` over the same provider state.
- Backend stays free of Next.js imports; the corpus is regenerated via `npm run export:corpus`, not edited by hand.

**Frontend (M2–M6)**
- Design tokens and the type scale live only in `globals.css`; dark mode is class-based (`ThemeToggle` + the `beforeInteractive` script); `PageContainer` is the only page width wrapper (`narrow` or default).
- Pages call one composing API function each (`getHomepageFeed`, `getCategoryFeed`, …); composition logic belongs in `lib/api/client.ts`, not pages or components.
- `StoryImagePlaceholder` is the single point to swap when real images exist.
- `saveStory`/`removeSavedStory` are only called from Server Actions, never from Client Components.
- Search state lives in the URL (`next/form`), and `searchStories` takes a `SearchFilters` object.
- `getStory` returns `StoryDetail`; `getSavedStories` returns the article join; `getPersonalizedStories` never exposes a numeric score; personalization copy must not claim to be AI-powered.
- `recordSignal()` is the single call site for behavioral signals.
- `UserPreferences` keeps the Module 05 shape (`topics`, `regions`, `sources`, `contentTypes`, `readingTime`).

**News pipeline (M9)**
- The pipeline stays provider-agnostic: providers enter only through `adapters/` + the sources JSON. Credentials are Settings fields referenced by name; never put a key in the JSON or in a URL.
- **Generated text must pass `grounding.check_text`** against the evidence the model was given; source URLs and attribution come only from metadata. Don't loosen the verifier without adding tests for what it will now let through.
- **Story ids are assigned once and persisted.** Never derive a story's id from its current cluster membership alone — that would duplicate stories each time one gains a source.
- Reruns must stay idempotent (`tests/pipeline/test_runner_store.py` pins it). The API never exposes numeric scores (`test_no_raw_scores_are_exposed_anywhere`).
- No unauthenticated endpoint that triggers a pipeline run.
- Listing/search must not mix the seed corpus into real pipeline results.
