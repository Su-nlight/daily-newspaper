# Daily Signal Project State

## Completed

- Module 01 Foundation
- Module 02 Design System
- Module 03 Daily Newspaper Homepage

## Current

Module 03 is complete and merged. Awaiting Module 04.

## Routes

| Route                | Status                                                                    |
| --------------------- | -------------------------------------------------------------------------- |
| `/`                   | **Built (Module 03)** — full front page: masthead, edition meta, hero, secondary stories, World/Technology/AI & Research/Cybersecurity sections, Relevant to You, 60-Second Brief. Has `loading.tsx` (newspaper-shaped skeleton) and an empty-edition state with retry. |
| `/story/[id]`         | Placeholder (Module 01), restyled with the design system (Module 02). Not yet a full story reading experience. |
| `/category/[slug]`    | Placeholder, restyled. Lists articles matching a category slug via `getCategory()`. |
| `/search`             | Placeholder, restyled. No real search UI yet.                            |
| `/saved`              | Placeholder, restyled. No save/unsave interaction yet.                   |
| `/topics`             | Placeholder, restyled. Lists mock topics.                                |
| `/archive`            | Placeholder, restyled. No historical edition browsing yet.               |
| `/research`           | Placeholder, restyled. No research monitoring feed yet.                  |
| `/career`             | Placeholder, restyled. No career intelligence content yet.               |
| `/chat`               | Placeholder, restyled. Persistent `ChatBubble` (bottom-left, every page) is UI-shell only — no backend wired. |
| `/about`              | Placeholder, restyled.                                                   |

## API contracts

All in `src/lib/api/client.ts`, returning mock data from `src/data/mock-newspaper.ts`. No network calls yet — every function is `async` so a real backend can replace the body without changing call sites.

- `getTodayEdition(): Promise<Edition>`
- `getHomepageFeed(): Promise<HomepageFeed>` — **added in Module 03.** The single call the homepage makes. Composes `heroStory`, `secondaryStories`, category `sections` (World / Technology / AI & Research / Cybersecurity), `personalized` (articles with a `relevanceScore`, sorted desc), and `brief` (6 most recent articles, summary truncated to ~130 chars) from `mockArticles` + `mockTodayEdition`. **Any future module changing what counts as "personalized" or how sections are grouped should change this function, not `page.tsx`.**
- `getStory(id): Promise<Article | null>`
- `getCategory(slug): Promise<{ category: Category | null; stories: Article[] }>`
- `searchStories(query): Promise<Article[]>`
- `getSavedStories(): Promise<SavedStory[]>`
- `getTopics(): Promise<Topic[]>`
- `sendChatMessage(message): Promise<ChatConversation>`

## Components

`src/components/`, grouped by folder as established in Module 01:

**layout/** — `Header`, `Footer`, `PageContainer`, `SectionHeading` (Module 02)

**navigation/** — `ThemeToggle` (uses `useSyncExternalStore`, not `useEffect`+`setState`, to avoid hydration flash and a React lint violation), `MobileNavigation` (Module 02)

**newspaper/** — `Masthead` (Module 02); `HeroStory`, `EditionMeta`, `SecondaryStories`, `NewspaperSection` (props: `title`, `description`, `stories`, `layout: "grid" | "list" | "compact"`, `href`), `SixtySecondBrief`, `EmptyEditionState`, `RetryButton` (client, `router.refresh()`) — **all added in Module 03**

**story/** — `StandardStory`, `CompactStory`, `HorizontalStory`, `StoryImagePlaceholder` — **added in Module 03.** Shared by both the homepage and (eventually) `/story/[id]` and `/category/[slug]`.

**personalization/** — `RelevantToYou` — **added in Module 03**

**chat/** — `ChatBubble` (client, bottom-left, hover tooltip "Ask Daily Signal AI"), `ChatPanelShell` (UI shell only, input disabled) (Module 02)

**search/** — empty, not yet built

## Known issues

- **No real images.** `Article.imageUrl` mock values (`https://images.example.com/...`) do not resolve. Rather than render broken `<img>` tags, all story visuals use `StoryImagePlaceholder` (a ruled-paper CSS pattern + category label). `imageUrl` is currently unused by any component. Swap this out once real image ingestion/CDN exists.
- **Fonts are system stacks, not the intended custom serif/sans pairing.** `next/font/google` (Source Serif 4 + Inter) was tried first but Google Fonts fetch was blocked/flaky in the build sandbox used for this work, so `globals.css` falls back to `Georgia, "Iowan Old Style", ...` (display) and `-apple-system, "Segoe UI", ...` (sans). Every component reads type through `var(--font-display)` / `var(--font-sans)` only — re-adding `next/font/google` (or `next/font/local` with real font files) is a two-line change in `layout.tsx` plus setting those two CSS variables from the font's `variable` output. No component changes needed.
- **`category` field is a loose string, not a foreign key.** `Article.category` must match a `Category.slug` for `/category/[slug]` and homepage section filtering to work. There's no compile-time or runtime check enforcing this — a typo'd category slug on a new mock article will silently make that article invisible to its intended section/category page.
- **`EmptyEditionState` is unreachable with current mock data.** `mockTodayEdition` always has stories, so the empty-edition code path in `page.tsx` (`if (!feed.heroStory)`) is implemented but not exercised outside manual testing (temporarily emptying `mockTodayEdition.stories`).
- **`/chat` page and the persistent `ChatBubble` are unrelated UIs that both say "not connected yet."** This is intentional (one is the full chat page, one is the always-on quick-access widget) but worth knowing so a future module doesn't accidentally treat them as the same component.

## Decisions that must not be changed

- **Design tokens live only in `globals.css`.** Colors (`--background`, `--foreground`, `--muted`, `--border`, `--border-strong`, `--accent`, `--accent-foreground`, plus `-elevated`/dark variants) and the type scale (`.text-display`, `.text-headline`, `.text-subheadline`, `.text-section-title`, `.text-body`, `.text-caption`, `.text-metadata`) are the only source of color and typography. No component should hardcode a hex value, a raw Tailwind color utility (e.g. `text-zinc-500`), or a one-off `font-size`.
- **Dark mode is class-based (`.dark` on `<html>`), not just `prefers-color-scheme`.** Toggling logic lives in `components/navigation/ThemeToggle.tsx` and the no-FOUC `beforeInteractive` script in `app/layout.tsx`. Don't reintroduce a separate dark-mode mechanism (e.g. `next-themes`) without removing this one first — the two would fight.
- **`PageContainer` is the only page-level width/padding wrapper.** `narrow` (max-w-3xl, for long-form/single-column pages) vs. default (`max-w-content`, ~1360px) are the only two widths. Don't add a third ad-hoc container.
- **The homepage only calls `getHomepageFeed()`.** Section composition (which categories map to which section, what "personalized" means, how the brief is built) belongs in `lib/api/client.ts`, not in `page.tsx` or in components. This is what lets a real backend replace mock data without touching the UI layer.
- **`StoryImagePlaceholder` replaces `<img src={article.imageUrl}>` everywhere until real images exist.** Don't wire raw `<img>`/`next/image` tags to `Article.imageUrl` piecemeal in new components — update the placeholder component (or replace it) once, in one place.
- **Route structure, types, and the API function list from Module 01 are unchanged**, only extended (`getHomepageFeed` and its supporting types were additive, not replacements).
