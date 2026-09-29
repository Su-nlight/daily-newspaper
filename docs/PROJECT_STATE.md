# Daily Signal Project State

## Completed

- Module 01 Foundation
- Module 02 Design System
- Module 03 Daily Newspaper Homepage
- Module 04 Story and Category Pages
- Module 05 Personalization and Topics
- Module 06 Search, Saved Stories and Archive

## Current

Module 06 is complete and merged. Awaiting Module 07.

## Routes

| Route                | Status                                                                    |
| --------------------- | -------------------------------------------------------------------------- |
| `/`                   | Built (Module 03/05). Unchanged in Module 06.                            |
| `/story/[id]`         | Built (Module 04/05). **`SaveStoryButton` now does a real save** — see API contracts below. |
| `/category/[slug]`    | Built (Module 04). Unchanged in Module 06.                               |
| `/search`             | **Rebuilt in Module 06.** URL-driven (`?q=&date=&category=&source=&topic=&region=`) via `next/form` — no client React state for the core search flow. Covers all 5 spec states: initial (no params), searching (`loading.tsx`, shown during the client-side transition `next/form` provides), results, no results, error (`error.tsx`). |
| `/saved`              | **Rebuilt in Module 06** as "Your Library." Shows real saved stories (pre-seeded with 2 from Module 01's `mockSavedStories`), each with Open / Ask AI / Remove. Empty state ("Your reading list is empty.") only shows once all seeded + saved stories are removed. |
| `/topics`             | Built (Module 05). Unchanged in Module 06.                               |
| `/archive`            | **Rebuilt in Module 06** as an editorial timeline (vertical, dot-marker list grouped by month) — not a calendar grid. Links to `/archive/[date]`. |
| `/archive/[date]`     | **New route, added in Module 06.** Shows edition date, headline/summary, story count + estimated reading time, a category chip list, a featured story, and the rest of that edition's stories. Has `loading.tsx`, `not-found.tsx`, and `error.tsx`. |
| `/research`           | Placeholder, restyled. No research monitoring feed yet.                  |
| `/career`             | Placeholder, restyled. No career intelligence content yet.               |
| `/chat`               | Placeholder, restyled. Persistent `ChatBubble` shares state with `AskAboutStory` via `ChatProvider` (Module 04).                                                              |
| `/about`              | Placeholder, restyled.                                                   |

## API contracts

All in `src/lib/api/client.ts`, backed by `src/data/mock-newspaper.ts`. Functions are still `async` even where trivial, so a real backend can replace the body without changing call sites.

**Added in Module 06:**

- `getCategories(): Promise<Category[]>` — full category list, for the search filter dropdown.
- `getArchive(): Promise<ArchiveMonthGroup[]>` — groups `mockEditions` by month, most recent first, computing each entry's `dayLabel` ("22 — Today" / "21 — Monday") and `storyCount`.
- `getEditionByDate(date): Promise<Edition | null>` — looks up `mockEditions` by exact date.
- `saveStory(articleId): Promise<SavedStory>` / `removeSavedStory(articleId): Promise<void>` / `isStorySaved(articleId): Promise<boolean>` — **see "real mutation" note below.**

**Changed in Module 06:**

- `searchStories()` signature changed from `(query: string)` to `(filters: SearchFilters)` — `{ query?, date?, category?, source?, topic?, region? }`. Reuses the same `regionForArticle()` / `sourceIdForArticle()` helpers built for Module 05's personalization engine, so "region" and "source" mean the same thing in search as they do in Relevant to You.
- `getSavedStories()` return type changed from `SavedStory[]` to `SavedStoryWithArticle[]` (`{ saved, article }`) — the join the `/saved` page actually needs, done once in the API layer rather than in the page.

**Real mutation, not mock-only:** Unlike every other `get*` function, `saveStory()` / `removeSavedStory()` write to a **module-level in-memory array** (`savedStoryStore` in `client.ts`), seeded from `mockSavedStories`. They're called from **Server Actions** in `src/lib/actions/saved-stories.ts` (`saveStoryAction`, `removeSavedStoryAction`), which also call `revalidatePath("/saved")`. This is a genuine change in kind from every prior module's mock data — it's the first real (if temporary) write path in the app. See Known issues for what this does and doesn't mean.

## Components

`src/components/`, grouped by folder as established in Module 01:

**layout/**, **navigation/**, **newspaper/** (existing) — unchanged except **`ArchiveTimeline`** added to `newspaper/` (Module 06).

**story/** — unchanged from Module 05 except:
- **`SaveStoryButton` rewritten** — now takes an `initialSaved: boolean` prop (computed server-side via `isStorySaved()`), does optimistic UI + `useTransition`, and calls the real `saveStoryAction`/`removeSavedStoryAction` Server Actions instead of only flipping local state.
- **`AskAboutStory` generalized** — prop changed from `story: StoryDetail` to a minimal `{ id, title, context }` shape, plus a new `compact?: boolean` variant (small inline button) for reuse in the saved-stories list. Call sites updated: the story page now passes `{ id: story.id, title: story.title, context: story.dek }` explicitly.
- **Added:** `RemoveSavedButton` (client, calls `removeSavedStoryAction`), `SavedStoryCard` (composes Open link + compact `AskAboutStory` + `RemoveSavedButton`).

**personalization/**, **chat/** — unchanged (Module 05/04)

**search/** — **first components in this folder.** `SearchForm` (server-rendered `next/form`, all filter state lives in the URL), `SearchResultCard` (reuses `SaveStoryButton`).

## Known issues

- **Saved stories are in-memory only — not a real database, and not per-user.** `savedStoryStore` lives in the Node process's memory. It resets on every server restart/redeploy, and because there's still no auth/session (Module 01's stated non-goal, still true), **every visitor shares the same saved-stories list.** This is real mutation (unlike Modules 03–05's static mock data), which is a meaningful step up from Module 05's `SaveStoryButton` that didn't persist at all — but "real" here means "real for this running server process," not "real for this user."
- **Archive editions are 4 fixed dates (Sept 19–22, 2026).** `mockEditions` (in `mock-newspaper.ts`) is a short hand-authored list, not derived from some larger date range. Adding a 5th historical day means adding both new dated `mockArticles` entries and a new `mockEditions` entry — `getArchive()`/`getEditionByDate()` will pick it up automatically once that's done.
- **Search's region/source filters inherit Module 05's known simplifications** — `regionForArticle()` maps a US-based source to "Global" (no North America option exists in the region list), and Japan/South Korea/Singapore currently match zero mock sources, so filtering search by those three regions always returns no results. Same caveat as documented in Module 05.
- **`next/form`'s client-side transition is what powers the "searching" loading state**, not a custom fetch/spinner. On a very fast local mock response this transition may be too quick to visibly notice `loading.tsx` — this is expected and will become more visible once `searchStories()` does real (slower) work.
- **Estimated reading time (`estimateReadingTime()`) is a simple word-count heuristic** (summary word count ÷ 200wpm + 0.5 min/story overhead), not based on full article body text (which doesn't exist for most fields outside `StoryDetail`). Treat it as illustrative, not precise.
- **The `/archive/[date]` "Also in this edition" grid can render 0 stories** for a date with only 1 story (nothing after the featured slot) — handled gracefully by `NewspaperSection`'s existing empty-return behavior, not a bug, but worth knowing if an edition looks sparse.

## Decisions that must not be changed

- **`saveStory()` / `removeSavedStory()` are only ever called from Server Actions (`lib/actions/saved-stories.ts`), never directly from a Client Component.** A Client Component importing and calling them directly would mutate a *separate, client-side copy* of the module and silently do nothing useful — this is a real Next.js footgun, not a style preference. New save/remove UI should call the existing actions, not add new ones, unless the mutation is genuinely different.
- **Search state lives in the URL, not React state.** `SearchForm` is a Server Component using `next/form`; don't convert it to a client-side controlled-input component with `fetch`-on-change — that would lose shareable search URLs and the free `loading.tsx` integration for no benefit at mock-data scale.
- **`searchStories(filters)` takes a `SearchFilters` object, not a bare query string.** Don't revert to a single-string signature; every existing call site (the search page) depends on the object shape now.
- **`getSavedStories()` returns the article join (`SavedStoryWithArticle[]`), not bare `SavedStory[]`.** If a future module needs just the bookmarks without article data, add a separate function rather than changing this one's return shape again.
- **Design tokens, dark mode, `PageContainer`, and the "one composing API function per page" pattern** — unchanged from Modules 02–05, still binding.
- **Route structure and the Module 01 API function list are unchanged, only extended.** The breaking changes in this module (`searchStories()`'s parameter, `getSavedStories()`'s return type) are called out explicitly above rather than silently introduced.
