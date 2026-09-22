import {
  mockArticles,
  mockCategories,
  mockConversation,
  mockSavedStories,
  mockTodayEdition,
  mockTopics,
} from "@/data/mock-newspaper";
import type { Article, Category, ChatConversation, Edition, SavedStory, Topic } from "@/types";

export async function getTodayEdition(): Promise<Edition> {
  return mockTodayEdition;
}

export async function getStory(id: string): Promise<Article | null> {
  return mockArticles.find((article) => article.id === id) ?? null;
}

export async function getCategory(
  slug: string,
): Promise<{ category: Category | null; stories: Article[] }> {
  const category = mockCategories.find((item) => item.slug === slug) ?? null;
  const stories = mockArticles.filter((article) => article.category === slug);
  return { category, stories };
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
