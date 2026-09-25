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

export interface TopicPreference {
  id: string;
  /** 0–1. Set by the user via a slider; never treated as a hidden backend score. */
  weight: number;
}

export interface Region {
  id: string;
  name: string;
}

export interface ContentType {
  id: string;
  name: string;
  description: string;
}

export interface UserPreferences {
  topics: TopicPreference[];
  regions: string[];
  sources: string[];
  contentTypes: string[];
  /** Preferred daily reading time budget, in minutes. */
  readingTime: number;
}

export type BehavioralSignalType =
  | "article_opened"
  | "article_saved"
  | "article_shared"
  | "article_completed"
  | "topic_followed"
  | "topic_ignored";

/**
 * Frontend-only event shape for Module 05's behavioral-signal
 * infrastructure. No ML/recommendation logic consumes these yet — see
 * lib/analytics/signals.ts and docs/PROJECT_STATE.md.
 */
export interface BehavioralSignal {
  type: BehavioralSignalType;
  payload: Record<string, unknown>;
  occurredAt: string;
}

/** An Article paired with the (non-numeric) reasons it was personalized
 *  for this user, rendered by components/personalization/WhyRelevant.tsx. */
export interface PersonalizedStory {
  article: Article;
  reasons: string[];
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
  personalized: PersonalizedStory[];
  brief: BriefItem[];
}

export interface StoryCitation {
  publisher: string;
  publishedAt: string;
  url: string;
}

export interface StoryDetail extends Article {
  /** Short one-line subhead shown under the headline. */
  dek: string;
  whatHappened: string;
  whyItMatters: string;
  keyFacts: string[];
  citations: StoryCitation[];
}

export interface TrendingTopic {
  name: string;
  count: number;
}

export interface CategoryFeed {
  category: Category | null;
  featuredStory: Article | null;
  secondaryStories: Article[];
  latestStories: Article[];
  trendingTopics: TrendingTopic[];
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

/** Story context passed from a story page's "Ask AI about this story"
 *  button into the global chat UI (components/chat/ChatProvider.tsx). */
export interface ChatStoryContext {
  storyId: string;
  title: string;
  context: string;
}
