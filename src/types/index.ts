export interface Article {
  id: string;
  title: string;
  dek?: string;
  summary: string;
  context?: string;
  whatHappened?: string;
  whyItMatters?: string;
  keyFacts?: string[];
  entities?: string[];
  sources?: StorySourceItem[];
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

export interface StorySourceItem {
  id: string;
  publisher: string;
  publishedAt: string;
  link: string;
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

export interface HomepageSection {
  slug: string;
  title: string;
  description?: string;
  stories: Article[];
  /** Link to the matching category page, when the section maps 1:1 to a category slug. */
  href?: string;
}

export interface BriefItem {
  id: string;
  headline: string;
  summary: string;
}

export interface HomepageFeed {
  edition: Edition;
  heroStory: Article | null;
  secondaryStories: Article[];
  sections: HomepageSection[];
  personalized: Article[];
  brief: BriefItem[];
}

export interface CategoryEditionFeed {
  category: Category;
  featuredStory: Article;
  secondaryStories: Article[];
  latestStories: Article[];
  trendingTopics: string[];
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

export interface StoryChatContext {
  storyId: string;
  storyTitle: string;
  storyContext: string;
}
