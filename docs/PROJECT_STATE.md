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

## Current

Module 08 is complete. **Verified with a real FastAPI server and a stand-in for
Groq, not with a real Groq key or a real browser** — see Known issues.
Awaiting Module 09.

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
GET  /api/edition/today | /api/edition/{date}
GET  /api/stories | /api/stories/{id}
GET  /api/search?q=&category=&source=&topic=
GET  /api/health

request: { message, conversation_id?, history: [{role: user|assistant, content}],
           context: { story_id?, edition_id?, category?, search_query?, search_result_ids? } }
source:  { publisher, url, title, index }   # index = the [n] marker used in the answer text
```

`history` and `search_*` context were added in M8 (backwards compatible).

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

## Known issues

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
