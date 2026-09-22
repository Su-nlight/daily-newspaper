export interface Article {
  id: string;
  title: string;
  summary: string;
  category: string;
  source: string;
  sourceUrl: string;
  publishedAt: string;
  imageUrl?: string;
  topics: string[];
  relevanceScore?: number;
  whyRelevant?: string;
}

export interface Edition {
  id: string;
  date: string;
  headline: string;
  summary: string;
  stories: Article[];
}

export interface Category {
  slug: string;
  name: string;
  description: string;
}

export interface Source {
  id: string;
  name: string;
  url: string;
  country: string;
}

export interface Topic {
  id: string;
  name: string;
  description: string;
}

export interface SavedStory {
  id: string;
  articleId: string;
  savedAt: string;
  notes?: string;
}

export interface UserPreferences {
  preferredCategories: string[];
  preferredTopics: string[];
  mutedSources: string[];
  locale: string;
}

export type ChatRole = "user" | "assistant" | "system";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: string;
}

export interface ChatConversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  updatedAt: string;
}
