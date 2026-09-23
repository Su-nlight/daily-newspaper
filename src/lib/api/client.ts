import {
  mockArticles,
  mockCategories,
  mockConversation,
  mockSavedStories,
  mockStoryDetails,
  mockTodayEdition,
  mockTopics,
} from "@/data/mock-newspaper";
import type {
  Article,
  BriefItem,
  Category,
  CategoryFeed,
  ChatConversation,
  Edition,
  HomepageFeed,
  SavedStory,
  StoryDetail,
  Topic,
  TrendingTopic,
} from "@/types";
import { formatCategoryLabel } from "@/lib/utils/category";
import { formatDisplayDate } from "@/lib/utils/date";

export async function getTodayEdition(): Promise<Edition> {
  return mockTodayEdition;
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
