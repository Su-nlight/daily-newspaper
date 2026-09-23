import {
  mockArticles,
  mockCategories,
  mockConversation,
  mockSavedStories,
  mockTodayEdition,
  mockTopics,
} from "@/data/mock-newspaper";
import type {
  Article,
  BriefItem,
  Category,
  CategoryEditionFeed,
  ChatConversation,
  Edition,
  HomepageFeed,
  SavedStory,
  StorySourceItem,
  Topic,
} from "@/types";

export async function getTodayEdition(): Promise<Edition> {
  return mockTodayEdition;
}

export async function getStory(id: string): Promise<Article | null> {
  return mockArticles.find((article) => article.id === id) ?? null;
}

export async function getRelatedStories(story: Article, limit = 4): Promise<Article[]> {
  return mockArticles
    .filter((candidate) => candidate.id !== story.id)
    .map((candidate) => ({
      article: candidate,
      score: relatedScore(story, candidate),
    }))
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map((item) => item.article);
}

export async function getCategory(
  slug: string,
): Promise<{ category: Category | null; stories: Article[] }> {
  const category = mockCategories.find((item) => item.slug === slug) ?? null;
  const stories = mockArticles.filter((article) => article.category === slug);
  return { category, stories };
}

export async function getCategoryEdition(slug: string): Promise<CategoryEditionFeed | null> {
  const { category, stories } = await getCategory(slug);

  if (!category || stories.length === 0) {
    return null;
  }

  const sortedStories = [...stories].sort(
    (a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime(),
  );
  const featuredStory = sortedStories[0];
  const secondaryStories = sortedStories.slice(1, 3);
  const latestStories = sortedStories.slice(1);

  return {
    category,
    featuredStory,
    secondaryStories,
    latestStories,
    trendingTopics: categoryTrendingTopics(stories),
  };
}

export async function getStorySources(story: Article): Promise<StorySourceItem[]> {
  if (story.sources && story.sources.length > 0) {
    return story.sources;
  }

  return [
    {
      id: `${story.id}-source-primary`,
      publisher: story.source,
      publishedAt: story.publishedAt,
      link: story.sourceUrl,
    },
  ];
}

export async function searchStories(query: string): Promise<Article[]> {
  if (!query.trim()) {
    return mockArticles;
  }

  const normalizedQuery = query.toLowerCase();

  return mockArticles.filter((article) =>
    [article.title, article.summary, article.category, article.topics.join(" ")]
      .join(" ")
      .toLowerCase()
      .includes(normalizedQuery),
  );
}

export async function getSavedStories(): Promise<SavedStory[]> {
  return mockSavedStories;
}

export async function getTopics(): Promise<Topic[]> {
  return mockTopics;
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
      stories: byCategorySlugs(["technology"], featuredIds),
      href: "/category/technology",
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

  const personalized = [...mockArticles]
    .filter((article) => typeof article.relevanceScore === "number")
    .sort((a, b) => (b.relevanceScore ?? 0) - (a.relevanceScore ?? 0))
    .slice(0, 4);

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

function relatedScore(base: Article, candidate: Article): number {
  const baseTopics = new Set(base.topics);
  const baseEntities = new Set(base.entities ?? []);
  const topicMatches = candidate.topics.filter((topic) => baseTopics.has(topic)).length;
  const entityMatches = (candidate.entities ?? []).filter((entity) =>
    baseEntities.has(entity),
  ).length;
  const sameCategory = base.category === candidate.category ? 1 : 0;

  return topicMatches * 3 + entityMatches * 2 + sameCategory;
}

function categoryTrendingTopics(stories: Article[]): string[] {
  const scores = new Map<string, number>();

  stories.forEach((story) => {
    story.topics.forEach((topic) => {
      scores.set(topic, (scores.get(topic) ?? 0) + 1);
    });
  });

  return [...scores.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([topic]) => topic);
}
