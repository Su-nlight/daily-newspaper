import {
  mockArticles,
  mockCategories,
  mockConversation,
  mockContentTypes,
  mockEditions,
  mockRegions,
  mockSavedStories,
  mockSources,
  mockStoryDetails,
  mockTodayEdition,
  mockTopics,
  mockUserPreferences,
} from "@/data/mock-newspaper";
import type {
  Article,
  ArchiveEntry,
  ArchiveMonthGroup,
  BriefItem,
  Category,
  CategoryFeed,
  ChatConversation,
  ContentType,
  Edition,
  HomepageFeed,
  PersonalizedStory,
  Region,
  SavedStory,
  SavedStoryWithArticle,
  SearchFilters,
  Source,
  StoryDetail,
  Topic,
  TrendingTopic,
  UserPreferences,
} from "@/types";
import { formatCategoryLabel } from "@/lib/utils/category";
import { archiveDayLabel, formatDisplayDate, monthYearLabel } from "@/lib/utils/date";

export async function getTodayEdition(): Promise<Edition> {
  return mockTodayEdition;
}

export async function getEditionByDate(date: string): Promise<Edition | null> {
  return mockEditions.find((edition) => edition.date === date) ?? null;
}

/**
 * Groups historical editions by month for the /archive timeline, most
 * recent month and date first. Adding a new entry to mockEditions is all a
 * future module needs to do to extend the archive.
 */
export async function getArchive(): Promise<ArchiveMonthGroup[]> {
  const sortedEditions = [...mockEditions].sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime(),
  );

  const groups = new Map<string, ArchiveEntry[]>();
  for (const edition of sortedEditions) {
    const monthLabel = monthYearLabel(edition.date);
    const entry: ArchiveEntry = {
      date: edition.date,
      dayLabel: archiveDayLabel(edition.date, mockTodayEdition.date),
      headline: edition.headline,
      storyCount: edition.stories.length,
    };
    groups.set(monthLabel, [...(groups.get(monthLabel) ?? []), entry]);
  }

  return [...groups.entries()].map(([monthLabel, editions]) => ({ monthLabel, editions }));
}

/**
 * Builds a full StoryDetail from an Article for ids without hand-authored
 * content in mockStoryDetails, so /story/[id] never renders an empty
 * section for an article that legitimately exists.
 */
function deriveStoryDetail(article: Article): Omit<StoryDetail, keyof Article> {
  const categoryLabel = formatCategoryLabel(article.category);
  const topicList = article.topics.join(" and ");

  return {
    dek: article.summary,
    whatHappened: article.summary,
    whyItMatters: topicList
      ? `This development is relevant to readers tracking ${topicList}, and fits into broader ${categoryLabel.toLowerCase()} coverage this edition is following.`
      : `This is part of Daily Signal's ongoing ${categoryLabel.toLowerCase()} coverage.`,
    keyFacts: [
      `Reported by ${article.source} on ${formatDisplayDate(article.publishedAt)}.`,
      ...(article.topics.length > 0 ? [`Related topics: ${article.topics.join(", ")}.`] : []),
    ],
    citations: [
      {
        publisher: article.source,
        publishedAt: article.publishedAt,
        url: article.sourceUrl,
      },
    ],
  };
}

export async function getStory(id: string): Promise<StoryDetail | null> {
  const article = mockArticles.find((item) => item.id === id) ?? null;
  if (!article) return null;

  const detail = mockStoryDetails[id] ?? deriveStoryDetail(article);
  return { ...article, ...detail };
}

/**
 * Finds other articles that share topics and/or a category with the given
 * story, ranked by relevance (shared topics weighted higher than a shared
 * category alone). Entity-level matching isn't modeled yet — see
 * docs/PROJECT_STATE.md.
 */
export async function getRelatedStories(story: Article, limit = 3): Promise<Article[]> {
  return mockArticles
    .filter((candidate) => candidate.id !== story.id)
    .map((candidate) => {
      const sharedTopics = candidate.topics.filter((topic) => story.topics.includes(topic)).length;
      const sameCategory = candidate.category === story.category ? 1 : 0;
      return { candidate, score: sharedTopics * 2 + sameCategory };
    })
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(({ candidate }) => candidate);
}

export async function getCategory(
  slug: string,
): Promise<{ category: Category | null; stories: Article[] }> {
  const category = mockCategories.find((item) => item.slug === slug) ?? null;
  const stories = mockArticles.filter((article) => article.category === slug);
  return { category, stories };
}

export async function getCategories(): Promise<Category[]> {
  return mockCategories;
}

/**
 * Composes the "/category/[slug]" data contract: a featured story, a
 * secondary two-up area, a vertical latest feed, and trending topics
 * computed from the category's own stories. Returns category: null when the
 * slug doesn't match a known category, which the page treats as "category
 * not found" rather than rendering an empty shell.
 */
export async function getCategoryFeed(slug: string): Promise<CategoryFeed> {
  const { category, stories } = await getCategory(slug);

  if (!category) {
    return {
      category: null,
      featuredStory: null,
      secondaryStories: [],
      latestStories: [],
      trendingTopics: [],
    };
  }

  const sorted = [...stories].sort(
    (a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime(),
  );
  const [featuredStory = null, ...rest] = sorted;
  const secondaryStories = rest.slice(0, 2);
  const latestStories = rest.slice(2);

  const topicCounts = new Map<string, number>();
  for (const story of stories) {
    for (const topic of story.topics) {
      topicCounts.set(topic, (topicCounts.get(topic) ?? 0) + 1);
    }
  }
  const trendingTopics: TrendingTopic[] = [...topicCounts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map(([name, count]) => ({ name, count }));

  return { category, featuredStory, secondaryStories, latestStories, trendingTopics };
}

/**
 * Filters mock articles by free-text query plus optional date/category/
 * source/topic/region facets. Reuses the same region/source resolution
 * helpers as getPersonalizedStories, so "region" here means the same thing
 * it means there.
 */
export async function searchStories(filters: SearchFilters): Promise<Article[]> {
  const { query, date, category, source, topic, region } = filters;
  const normalizedQuery = query?.trim().toLowerCase();

  return mockArticles.filter((article) => {
    if (normalizedQuery) {
      const haystack = [article.title, article.summary, article.category, article.topics.join(" ")]
        .join(" ")
        .toLowerCase();
      if (!haystack.includes(normalizedQuery)) return false;
    }

    if (date && !article.publishedAt.startsWith(date)) return false;
    if (category && article.category !== category) return false;

    if (source) {
      if (sourceIdForArticle(article) !== source) return false;
    }

    if (topic) {
      const topicMeta = mockTopics.find((candidate) => candidate.id === topic);
      if (!topicMeta || !article.topics.includes(topicMeta.name)) return false;
    }

    if (region) {
      if (regionForArticle(article) !== region) return false;
    }

    return true;
  });
}

/**
 * In-memory store, seeded from mockSavedStories and mutated only through
 * saveStory()/removeSavedStory() (called from Server Actions — see
 * lib/actions/saved-stories.ts). This resets on server restart; there's no
 * database yet, see docs/PROJECT_STATE.md. It's also shared across all
 * visitors, since there's still no per-user auth/session.
 */
const savedStoryStore: SavedStory[] = [...mockSavedStories];

export async function getSavedStories(): Promise<SavedStoryWithArticle[]> {
  return savedStoryStore
    .map((saved) => {
      const article = mockArticles.find((candidate) => candidate.id === saved.articleId);
      return article ? { saved, article } : null;
    })
    .filter((entry): entry is SavedStoryWithArticle => entry !== null)
    .sort((a, b) => new Date(b.saved.savedAt).getTime() - new Date(a.saved.savedAt).getTime());
}

export async function isStorySaved(articleId: string): Promise<boolean> {
  return savedStoryStore.some((saved) => saved.articleId === articleId);
}

export async function saveStory(articleId: string): Promise<SavedStory> {
  const existing = savedStoryStore.find((saved) => saved.articleId === articleId);
  if (existing) return existing;

  const entry: SavedStory = {
    id: `saved-${articleId}`,
    articleId,
    savedAt: new Date().toISOString(),
  };
  savedStoryStore.push(entry);
  return entry;
}

export async function removeSavedStory(articleId: string): Promise<void> {
  const index = savedStoryStore.findIndex((saved) => saved.articleId === articleId);
  if (index !== -1) savedStoryStore.splice(index, 1);
}

export async function getTopics(): Promise<Topic[]> {
  return mockTopics;
}

export async function getRegions(): Promise<Region[]> {
  return mockRegions;
}

export async function getSources(): Promise<Source[]> {
  return mockSources;
}

export async function getContentTypes(): Promise<ContentType[]> {
  return mockContentTypes;
}

export async function getUserPreferences(): Promise<UserPreferences> {
  return mockUserPreferences;
}

const COUNTRY_TO_REGION: Record<string, string> = {
  India: "india",
  "United Kingdom": "europe",
  "United States": "global",
};

function regionForArticle(article: Article): string | null {
  const source = mockSources.find((candidate) => candidate.name === article.source);
  if (!source) return null;
  return COUNTRY_TO_REGION[source.country] ?? null;
}

function sourceIdForArticle(article: Article): string | null {
  return mockSources.find((candidate) => candidate.name === article.source)?.id ?? null;
}

function isPublishedToday(publishedAt: string): boolean {
  return publishedAt.slice(0, 10) === mockTodayEdition.date;
}

/**
 * Deterministic, explainable scoring — not ML. Weighs topic-preference
 * matches (using the user's own slider weights), a followed region, a
 * followed source, and same-day recency. Every contributing factor is
 * surfaced as a plain-language reason in `reasons`, and the underlying
 * numeric score is never returned to the caller — see WhyRelevant, which
 * intentionally has no numeric prop to render.
 */
function scoreArticle(
  article: Article,
  preferences: UserPreferences,
): { score: number; reasons: string[] } {
  let score = 0;
  const reasons: string[] = [];

  for (const topicPreference of preferences.topics) {
    if (topicPreference.weight <= 0) continue;
    const topic = mockTopics.find((candidate) => candidate.id === topicPreference.id);
    if (topic && article.topics.includes(topic.name)) {
      score += topicPreference.weight;
      reasons.push(`Matches your interest in ${topic.name}`);
    }
  }

  const articleRegion = regionForArticle(article);
  if (articleRegion && preferences.regions.includes(articleRegion)) {
    score += 0.3;
    const regionName = mockRegions.find((region) => region.id === articleRegion)?.name;
    reasons.push(`Relevant to ${regionName ?? articleRegion}`);
  }

  const sourceId = sourceIdForArticle(article);
  if (sourceId && preferences.sources.includes(sourceId)) {
    score += 0.2;
    reasons.push(`From ${article.source}, a source you follow`);
  }

  if (isPublishedToday(article.publishedAt)) {
    score += 0.1;
    reasons.push("Published today");
  }

  return { score, reasons };
}

/**
 * Ranks mock articles against a user's stated preferences and returns each
 * with a short list of plain-language reasons (never a raw score) — the
 * data source for RelevantToYou / WhyRelevant. Deterministic rule-based
 * scoring only; no ML/recommendation model is involved yet, and the
 * homepage should never describe this section as "AI-powered."
 */
export async function getPersonalizedStories(
  preferences: UserPreferences = mockUserPreferences,
  limit = 4,
): Promise<PersonalizedStory[]> {
  return mockArticles
    .map((article) => ({ article, ...scoreArticle(article, preferences) }))
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(({ article, reasons }) => ({ article, reasons }));
}

export async function sendChatMessage(message: string): Promise<ChatConversation> {
  const trimmedMessage = message.trim();
  const now = new Date().toISOString();

  if (!trimmedMessage) {
    return mockConversation;
  }

  return {
    ...mockConversation,
    updatedAt: now,
    messages: [
      ...mockConversation.messages,
      {
        id: `msg-${mockConversation.messages.length + 1}`,
        role: "user",
        content: trimmedMessage,
        createdAt: now,
      },
      {
        id: `msg-${mockConversation.messages.length + 2}`,
        role: "assistant",
        content:
          "Thanks — this is a mock response for Module 01. Backend chat orchestration will be added in a later module.",
        createdAt: now,
      },
    ],
  };
}

function byCategorySlugs(slugs: string[], excludeIds: string[] = [], limit = 4): Article[] {
  return mockArticles
    .filter((article) => slugs.includes(article.category) && !excludeIds.includes(article.id))
    .slice(0, limit);
}

function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength - 1).trimEnd()}…`;
}

/**
 * Composes the full front-page data contract for the "/" route from mock
 * data. This is the only function the homepage should call — it keeps
 * section logic (which categories map to which front-page section, what
 * counts as "personalized", how the brief is derived) out of page.tsx so a
 * future real backend can implement this one function without the UI
 * changing.
 */
export async function getHomepageFeed(): Promise<HomepageFeed> {
  const edition = mockTodayEdition;
  const heroStory = edition.stories[0] ?? null;
  const secondaryStories = edition.stories.slice(1);
  const featuredIds = edition.stories.map((story) => story.id);

  const sections = [
    {
      slug: "world",
      title: "World",
      description: "Global developments shaping technology and business.",
      stories: byCategorySlugs(["world"], featuredIds),
      href: "/category/world",
    },
    {
      slug: "technology",
      title: "Technology",
      description: "Engineering, infrastructure, and product updates.",
      stories: byCategorySlugs(["software-engineering"], featuredIds),
      href: "/category/software-engineering",
    },
    {
      slug: "ai-research",
      title: "AI & Research",
      description: "Models, agent systems, and the research behind them.",
      stories: byCategorySlugs(["ai", "research"], featuredIds),
    },
    {
      slug: "cybersecurity",
      title: "Cybersecurity",
      description: "Threats, breaches, and defensive practice.",
      stories: byCategorySlugs(["cybersecurity"], featuredIds),
      href: "/category/cybersecurity",
    },
  ].filter((section) => section.stories.length > 0);

  const personalized = await getPersonalizedStories(mockUserPreferences, 4);

  const brief: BriefItem[] = [...mockArticles]
    .sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime())
    .slice(0, 6)
    .map((article) => ({
      id: article.id,
      headline: article.title,
      summary: truncate(article.summary, 130),
    }));

  return {
    edition,
    heroStory,
    secondaryStories,
    sections,
    personalized,
    brief,
  };
}
