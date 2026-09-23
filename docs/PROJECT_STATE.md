# Daily Signal Project State

## Completed

- Module 01 Foundation
- Module 02 Design System
- Module 03 Daily Newspaper Homepage
- Module 04 Story and Category Pages

## Current

Module 04 is complete and merged. Awaiting Module 05.

## Routes

| Route                | Status                                                                    |
| --------------------- | -------------------------------------------------------------------------- |
| `/`                   | Built (Module 03) — full front page: masthead, edition meta, hero, secondary stories, World/Technology/AI & Research/Cybersecurity sections, Relevant to You, 60-Second Brief. `loading.tsx` + empty-edition state with retry. |
| `/story/[id]`         | **Built (Module 04)** — full premium-journalism layout: back-to-edition, category, headline, dek, date/time, source, hero, summary, What Happened, Why It Matters, Key Facts, Sources, Related Stories, Ask AI About This Story. Has `loading.tsx`, `not-found.tsx`, and `error.tsx`. |
| `/category/[slug]`    | **Built (Module 04)** — featured story, two-column secondary area, vertical latest feed, trending topics. Has `loading.tsx`, `not-found.tsx`, and `error.tsx`. |
| `/search`             | Placeholder, restyled. No real search UI yet.                            |
| `/saved`              | Placeholder, restyled. No save/unsave interaction yet.                   |
| `/topics`             | Placeholder, restyled. Lists mock topics.                                |
| `/archive`            | Placeholder, restyled. No historical edition browsing yet.               |
| `/research`           | Placeholder, restyled. No research monitoring feed yet.                  |
| `/career`             | Placeholder, restyled. No career intelligence content yet.               |
| `/chat`               | Placeholder, restyled. Persistent `ChatBubble` (bottom-left, every page) is UI-shell only — no backend wired. Now shares state with `AskAboutStory` via `ChatProvider` (see Decisions below). |
| `/about`              | Placeholder, restyled.                                                   |

Also added in Module 04: a global `src/app/not-found.tsx` (unmatched routes) and a global `src/app/error.tsx` (root-segment error boundary), both using the design system, so every page — not just story/category — has a styled fallback instead of Next's default.

## API contracts

All in `src/lib/api/client.ts`, returning mock data from `src/data/mock-newspaper.ts`. No network calls yet — every function is `async` so a real backend can replace the body without changing call sites.

- `getTodayEdition(): Promise<Edition>`
- `getHomepageFeed(): Promise<HomepageFeed>` — composes the full "/" data contract (Module 03).
- `getStory(id): Promise<StoryDetail | null>` — **changed in Module 04.** Previously returned `Article | null`; now returns the richer `StoryDetail` (adds `dek`, `whatHappened`, `whyItMatters`, `keyFacts`, `citations`). Looks up hand-authored content in `mockStoryDetails` first, falling back to `deriveStoryDetail()` (templated from the base `Article`, not lorem ipsum) so **any** valid article id renders a complete story page, not just the 6 curated ones.
- `getRelatedStories(story, limit = 3): Promise<Article[]>` — **added in Module 04.** Ranks other articles by shared topics (weighted 2×) plus same-category (weighted 1×); entity-level matching isn't modeled yet (see Known issues).
- `getCategory(slug): Promise<{ category: Category | null; stories: Article[] }>` — unchanged, now used internally by `getCategoryFeed`.
- `getCategoryFeed(slug): Promise<CategoryFeed>` — **added in Module 04.** Composes the full "/category/[slug]" data contract: `featuredStory` (most recent), `secondaryStories` (next 2), `latestStories` (the rest), and `trendingTopics` (topic frequency within the category, top 6). Returns `category: null` for an unknown slug — the page turns that into `notFound()`, not an empty shell.
- `searchStories(query): Promise<Article[]>`
- `getSavedStories(): Promise<SavedStory[]>`
- `getTopics(): Promise<Topic[]>`
- `sendChatMessage(message): Promise<ChatConversation>`

**Breaking change to note:** `getStory`'s return type changed from `Article | null` to `StoryDetail | null`. `StoryDetail extends Article`, so any code treating the result as a plain `Article` still compiles, but anything relying on the *absence* of `dek`/`whatHappened`/etc. should be checked if added later.

## Components

`src/components/`, grouped by folder as established in Module 01:

**layout/** — `Header`, `Footer`, `PageContainer`, `SectionHeading` (Module 02)

**navigation/** — `ThemeToggle`, `MobileNavigation` (Module 02)

**newspaper/** — `Masthead` (Module 02); `HeroStory`, `EditionMeta`, `SecondaryStories`, `NewspaperSection` (Module 03, **extended in Module 04** with a `columns?: 2 | 3` prop for the category page's two-up secondary area), `SixtySecondBrief`, `EmptyEditionState`, `RetryButton` (Module 03); `TrendingTopics` — **added in Module 04**

**story/** — `StandardStory`, `CompactStory`, `HorizontalStory`, `StoryImagePlaceholder` (Module 03); `StoryHeader`, `StoryHero`, `StorySummary`, `StorySection` (reusable title+body wrapper, used for What Happened / Why It Matters), `KeyFacts`, `SourceList`, `RelatedStories`, `AskAboutStory` (client) — **all added in Module 04**

**personalization/** — `RelevantToYou` (Module 03)

**chat/** — `ChatBubble`, `ChatPanelShell` (Module 02); `ChatProvider` — **added in Module 04.** React context (`useChat()`) shared between `ChatBubble` and `AskAboutStory` so a story page can open the global chat panel pre-loaded with `{ storyId, title, context }`, shown as a "Discussing: …" banner in the panel with a Clear action. `ChatBubble` no longer owns its own open/closed state — it reads it from context. Wrapping `<ChatProvider>` was added around `{children}` + `Header` + `Footer` + `ChatBubble` in `app/layout.tsx`.

**search/** — empty, not yet built

## Known issues

- **Not-found pages return HTTP 200, not 404.** Confirmed this is current, documented Next.js App Router behavior (see https://nextjs.org/docs/app/api-reference/functions/not-found — "Because the check runs inside the `<Suspense>` boundary, the response has already begun streaming as a 200, and the status can't change once streaming has started"), not a bug in this codebase — reproduced identically with `loading.tsx` removed. Next automatically injects `<meta name="robots" content="noindex">` on these responses to protect SEO. If a real 404 status is ever a hard requirement (e.g. for uptime monitoring or crawler contracts), the article-existence check needs to happen before any streaming starts (e.g. in middleware), which is a bigger structural change than this module's scope.
- **No real images**, unchanged from Module 03 — `StoryImagePlaceholder` is still the only story visual.
- **Fonts are system stacks**, unchanged from Module 03 — see that entry below for the swap-back path.
- **`category` field is a loose string, not a foreign key** — unchanged from Module 03. Now also affects `getCategoryFeed`: a category with 0 matching articles renders `category` details with an empty featured/secondary/latest state (handled gracefully — "No stories in this category yet." — but worth knowing).
- **Only 5 of the 9 categories named in the Module 04 spec (World, India, Technology, AI, Cybersecurity, Business, Science, Research, Career) exist in `mockCategories`** (`ai`, `research`, `cybersecurity`, `software-engineering`, `world`). Visiting `/category/india`, `/category/business`, `/category/science`, or `/category/career` correctly renders the "Category not found" state rather than crashing — this is the intended behavior for an unimplemented category, not a bug, but a future module should either add these categories with real mock content or map them onto existing ones.
- **`getRelatedStories` doesn't model entities**, only topics + category. The spec mentions "entities" (e.g. companies, people) as a related-stories signal; `Article` has no entity field yet.
- **`EmptyEditionState` is still unreachable with current mock data** — unchanged from Module 03.
- **`/chat` page and the persistent `ChatBubble` are still separate UIs** — unchanged from Module 03. Note `AskAboutStory` opens the *bubble*, not the `/chat` page — that's intentional per the Module 04 spec ("Clicking this should open the global chat UI").

## Decisions that must not be changed

- **Design tokens live only in `globals.css`.** Colors and the type scale (`.text-display` … `.text-metadata`) are the only source of color and typography. No component should hardcode a hex value, a raw Tailwind color utility, or a one-off `font-size`.
- **Dark mode is class-based (`.dark` on `<html>`)**, driven by `components/navigation/ThemeToggle.tsx` + the `beforeInteractive` script in `app/layout.tsx`. Don't add a second dark-mode mechanism.
- **`PageContainer` is the only page-level width/padding wrapper**, with exactly two widths (`narrow` / default).
- **The homepage only calls `getHomepageFeed()`; the category page only calls `getCategoryFeed()`.** Section/feed composition logic belongs in `lib/api/client.ts`, never in `page.tsx` or components. This is what lets a real backend replace mock data without touching the UI layer.
- **`StoryImagePlaceholder` replaces `<img src={article.imageUrl}>` everywhere** until real images exist. Update the placeholder component once, in one place, rather than wiring raw `<img>`/`next/image` tags piecemeal.
- **Global chat state lives in `ChatProvider` (`components/chat/ChatProvider.tsx`), not in `ChatBubble`'s own state.** Anything that needs to open the chat panel or set its story context — `AskAboutStory` today, possibly other entry points later — should call `useChat().openChat(...)`, not duplicate open/close state locally.
- **`getStory` returns `StoryDetail`, not `Article`.** If a future module needs a lighter-weight story lookup that skips the detail composition, add a separate function rather than changing `getStory`'s return shape again — other code (the story page) depends on the full shape.
- **Route structure and the API function list from Module 01 are unchanged**, only extended — every addition in Modules 02–04 has been additive, not a replacement of an established contract, except the one explicitly noted breaking change above (`getStory`'s return type).
