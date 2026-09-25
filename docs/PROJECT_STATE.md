# Daily Signal Project State

## Completed

- Module 01 Foundation
- Module 02 Design System
- Module 03 Daily Newspaper Homepage
- Module 04 Story and Category Pages
- Module 05 Personalization and Topics

## Current

Module 05 is complete and merged. Awaiting Module 06.

## Routes

| Route                | Status                                                                    |
| --------------------- | -------------------------------------------------------------------------- |
| `/`                   | Built (Module 03). "Relevant to You" **changed in Module 05** — now driven by `getPersonalizedStories()` against the mock user's actual preferences instead of static per-article `relevanceScore`/`whyRelevant` fields. |
| `/story/[id]`         | Built (Module 04). **Extended in Module 05** with `ArticleViewTracker` (fires `article_opened` on mount), `SaveStoryButton` / `ShareStoryButton` (fire `article_saved` / `article_shared`), and `ArticleCompletionTracker` (fires `article_completed` via `IntersectionObserver` near the bottom of the article). |
| `/category/[slug]`    | Built (Module 04). Unchanged in Module 05.                               |
| `/search`             | Placeholder, restyled. No real search UI yet.                            |
| `/saved`              | Placeholder, restyled. No save/unsave interaction yet — note `SaveStoryButton` on the story page is a local UI toggle only (see Known issues); it does not write into `getSavedStories()`. |
| `/topics`             | **Rebuilt in Module 05** as the personalization preferences center: topic-importance sliders ("Your Interests"), region toggles, source toggles, content-type toggles, and a reading-time slider, via `PreferencesEditor`. Previously a static list of topic names. |
| `/archive`            | Placeholder, restyled. No historical edition browsing yet.               |
| `/research`           | Placeholder, restyled. No research monitoring feed yet.                  |
| `/career`             | Placeholder, restyled. No career intelligence content yet.               |
| `/chat`               | Placeholder, restyled. Persistent `ChatBubble` shares state with `AskAboutStory` via `ChatProvider` (Module 04).                                                              |
| `/about`              | Placeholder, restyled.                                                   |

## API contracts

All in `src/lib/api/client.ts`, returning mock data from `src/data/mock-newspaper.ts`. No network calls, no persistence — every function is `async` so a real backend can replace the body without changing call sites.

**Added in Module 05:**

- `getRegions(): Promise<Region[]>` — the 6 regions from the spec (India, Europe, Japan, South Korea, Singapore, Global).
- `getSources(): Promise<Source[]>` — previously unused `mockSources`, now surfaced for the Sources preference toggles.
- `getContentTypes(): Promise<ContentType[]>` — 4 content types tied to the product areas from Module 01 (Daily Edition, Research Monitoring, Career Intelligence, 60-Second Brief).
- `getUserPreferences(): Promise<UserPreferences>` — returns `mockUserPreferences`, standing in for "the current signed-in user." **There is still no auth/session** — this is a single hardcoded preferences object, not per-user data.
- `getPersonalizedStories(preferences = mockUserPreferences, limit = 4): Promise<PersonalizedStory[]>` — **the personalization engine.** Deterministic, explainable, rule-based scoring (not ML): sums the user's own topic weights for matching topics, +0.3 for a followed region (derived from the article's source's country — see Known issues), +0.2 for a followed source, +0.1 if published today. Returns each article paired with plain-language `reasons: string[]`; **the numeric score itself is never returned**, matching the spec's "do not expose internal scoring numbers" requirement.

**Changed in Module 05:**

- `getHomepageFeed()`'s `personalized` field is now computed by calling `getPersonalizedStories()` instead of filtering `mockArticles` by a static `relevanceScore` field. Its type changed from `Article[]` to `PersonalizedStory[]` (breaking change to `HomepageFeed`, see Decisions below).
- `UserPreferences` **type shape changed completely** — see Decisions below.

**Unchanged:** `getTodayEdition`, `getStory`, `getRelatedStories`, `getCategory`, `getCategoryFeed`, `searchStories`, `getSavedStories`, `getTopics` (now returns 10 topics instead of 4 — see Decisions), `sendChatMessage`.

## Components

`src/components/`, grouped by folder as established in Module 01:

**layout/**, **navigation/** — unchanged (Module 02)

**newspaper/** — unchanged (Modules 02–04)

**story/** — unchanged from Module 04 plus, **added in Module 05:** `ArticleViewTracker`, `ArticleCompletionTracker`, `SaveStoryButton`, `ShareStoryButton` (all client, all call `lib/analytics/signals.ts`)

**personalization/** — `RelevantToYou` (Module 03, **rewritten in Module 05** to consume `PersonalizedStory[]` and render `WhyRelevant` instead of inlining a single `whyRelevant` string); **added in Module 05:** `WhyRelevant` (reusable, spec-required), `PreferencesEditor` (client, owns all preference state for the session), `TopicPreferenceSlider`, `ToggleChip` (shared by regions/sources/content-types), `ReadingTimeSlider`

**chat/** — unchanged (Module 04)

**search/** — empty, not yet built

## Known issues

- **No persistence for preferences.** `PreferencesEditor` holds state in a plain `useState`, seeded from `mockUserPreferences` on the server. Reloading the page resets every slider/toggle to the mock defaults. This was a deliberate simplification to avoid a `useEffect` + `localStorage`-on-mount pattern, which would trip the same `react-hooks/set-state-in-effect` lint issue already worked around in `ThemeToggle` (Module 02) and would need a `useSyncExternalStore` rewrite to do properly — left as a clearly-scoped follow-up rather than adding that complexity now. The homepage's `getPersonalizedStories()` always reads from `mockUserPreferences` server-side, **not** from whatever a visitor has changed on `/topics` in their own browser — the two are not wired together yet.
- **Behavioral signals are logged, not sent anywhere.** `lib/analytics/signals.ts` console-logs (dev only) and appends to a capped `localStorage` array (`daily-signal:behavioral-signals`). No backend endpoint exists yet — this is exactly the "prepare frontend infrastructure" scope the module asked for, not a working analytics pipeline.
- **`SaveStoryButton` is a local visual toggle only.** Clicking it fires an `article_saved` signal and flips the button's own state, but does **not** add the story to `getSavedStories()` / the `/saved` page. Wiring real save persistence is `/saved`'s job in a future module.
- **Region matching is approximate.** `Article` has no `region` field, so `getPersonalizedStories()` infers it from the article's source's `country` (`Source.country`) via a small `COUNTRY_TO_REGION` map. India → india, United Kingdom → europe, United States → global (the spec's region list has no North America option, so US-sourced coverage is treated as "Global" — a pragmatic choice, not a precise mapping). Japan, South Korea, and Singapore currently match no mock sources at all, so selecting those regions has no visible effect on `/` yet.
- **`Article.relevanceScore` and `Article.whyRelevant` are now legacy/unused fields.** They're still on the `Article` type and still set on 6 mock articles (from Module 03), but `getPersonalizedStories()` no longer reads them — personalization is now fully preference-driven. Left in place rather than touched in this module to avoid unnecessary diff noise; a future module should remove them from the type and mock data once nothing references them.
- **Only 5 of the 10 topics have any matching mock articles** (AI Agents, Cloud Security, Research Monitoring, India Tech, Cybersecurity — and Cybersecurity only via `Article.category`, no article currently tags the `"Cybersecurity"` topic string directly, only `"Cloud Security"`). RAG, Software Engineering, Cloud, SAP, and Blockchain exist as followable topics with zero current matches — intentional (real products let you follow an interest before matching content exists), but worth knowing when testing `/topics`.
- **`weightLabel()` (Low/Medium/High/Essential) is a presentation-only bucketing of the 0–1 weight**, chosen to keep the preferences page from reading like a numeric dashboard slider per Module 02's design direction. The underlying `TopicPreference.weight` stored in state is still the precise slider value (steps of 0.05).

## Decisions that must not be changed

- **`UserPreferences` now matches the Module 05 spec's exact shape**: `{ topics: TopicPreference[], regions: string[], sources: string[], contentTypes: string[], readingTime: number }`. This replaced the Module 01 placeholder shape (`preferredCategories` / `preferredTopics` / `mutedSources` / `locale`), which was never used by any built feature. `contentTypes` was added beyond the spec's literal JSON example because the surrounding spec prose explicitly lists "content types" as a 4th personalization category to support — don't remove it without re-reading Module 05's "Personalization Categories" section.
- **`getPersonalizedStories()` never returns a raw numeric score to its caller.** Only `{ article, reasons }`. If a future module needs the score for internal sorting elsewhere, compute it in `lib/api/client.ts` and still only expose reasons outward — never let a numeric relevance value reach a component that renders to the user, per the spec's explicit "do not expose internal scoring numbers."
- **Personalization here is rule-based and must not be described as AI-powered.** Copy on `/topics` and in `RelevantToYou`'s description explicitly says preferences are "not AI-generated yet" / "not AI-generated." Don't change this copy until a real model-driven recommendation module actually exists.
- **Design tokens, dark mode, `PageContainer`, and the homepage/category "one composing API function per page" pattern** — unchanged from Modules 02–04, still binding. `getHomepageFeed()` is still the only function `/` calls; it now happens to call `getPersonalizedStories()` internally, but `page.tsx` still doesn't know that.
- **`lib/analytics/signals.ts`'s `recordSignal()` is the single call site for every behavioral signal.** New signal-emitting UI should call it rather than writing to `localStorage` or `console` directly, so there's exactly one place to swap in a real endpoint later.
- **Route structure and the Module 01 API function list are unchanged**, only extended. The one breaking change in this module (`UserPreferences`'s shape, and `HomepageFeed.personalized`'s type) is called out explicitly above rather than silently introduced.
