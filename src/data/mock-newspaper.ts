import type {
  Article,
  Category,
  ChatConversation,
  Edition,
  SavedStory,
  Source,
  Topic,
  UserPreferences,
} from "@/types";

export const mockSources: Source[] = [
  {
    id: "source-tech-ledger",
    name: "Tech Ledger",
    url: "https://techledger.example.com",
    country: "India",
  },
  {
    id: "source-global-wire",
    name: "Global Wire",
    url: "https://globalwire.example.com",
    country: "United Kingdom",
  },
  {
    id: "source-security-post",
    name: "Security Post",
    url: "https://securitypost.example.com",
    country: "United States",
  },
];

export const mockCategories: Category[] = [
  {
    slug: "ai",
    name: "Artificial Intelligence",
    description: "Coverage of AI models, products, and policy shifts.",
  },
  {
    slug: "cybersecurity",
    name: "Cybersecurity",
    description: "Threat intelligence, breaches, and defensive practices.",
  },
  {
    slug: "software-engineering",
    name: "Software Engineering",
    description: "Architecture, tooling, and engineering culture updates.",
  },
  {
    slug: "world",
    name: "World News",
    description: "Global developments impacting business and technology.",
  },
];

export const mockTopics: Topic[] = [
  {
    id: "topic-agents",
    name: "AI Agents",
    description: "Autonomous and semi-autonomous AI workflows.",
  },
  {
    id: "topic-cloud-security",
    name: "Cloud Security",
    description: "Security posture and zero-trust adoption in cloud systems.",
  },
  {
    id: "topic-india-tech",
    name: "India Tech",
    description: "Indian startup ecosystem, policy, and enterprise adoption.",
  },
  {
    id: "topic-research",
    name: "Research Monitoring",
    description: "Academic and industrial research worth tracking.",
  },
];

export const mockArticles: Article[] = [
  {
    id: "story-ai-policy-2026",
    title: "India releases draft framework for enterprise AI model audits",
    summary:
      "India's technology ministry proposed quarterly audit standards for high-impact enterprise AI deployments across finance and healthcare.",
    category: "ai",
    source: "Tech Ledger",
    sourceUrl: "https://techledger.example.com/ai-policy-audits",
    publishedAt: "2026-09-22T07:30:00Z",
    imageUrl: "https://images.example.com/ai-policy-audit.jpg",
    topics: ["AI Agents", "India Tech"],
    relevanceScore: 0.95,
    whyRelevant:
      "Strong policy signal for teams deploying production-grade AI features in regulated markets.",
  },
  {
    id: "story-ransomware-shift",
    title: "Ransomware groups pivot to software supply-chain extortion",
    summary:
      "Security analysts report a rise in attacks targeting build systems and package registries, with demands tied to release cycles.",
    category: "cybersecurity",
    source: "Security Post",
    sourceUrl: "https://securitypost.example.com/supply-chain-extortion",
    publishedAt: "2026-09-22T09:10:00Z",
    imageUrl: "https://images.example.com/ransomware-supply-chain.jpg",
    topics: ["Cloud Security", "Research Monitoring"],
    relevanceScore: 0.91,
    whyRelevant:
      "Highlights immediate actions for CI hardening and dependency integrity checks.",
  },
  {
    id: "story-rust-backend-scale",
    title: "Open-source observability team cuts backend costs with Rust rewrite",
    summary:
      "A high-traffic observability platform shared benchmarks showing lower compute spend after migrating ingestion services from Go to Rust.",
    category: "software-engineering",
    source: "Global Wire",
    sourceUrl: "https://globalwire.example.com/rust-backend-scale",
    publishedAt: "2026-09-21T19:45:00Z",
    imageUrl: "https://images.example.com/rust-observability.jpg",
    topics: ["Research Monitoring"],
  },
  {
    id: "story-semiconductor-alliance",
    title: "Japan and India announce semiconductor research corridor",
    summary:
      "The two governments announced a joint funding program for advanced chip packaging research and university partnerships.",
    category: "world",
    source: "Global Wire",
    sourceUrl: "https://globalwire.example.com/semiconductor-corridor",
    publishedAt: "2026-09-21T13:20:00Z",
    imageUrl: "https://images.example.com/semiconductor-corridor.jpg",
    topics: ["India Tech", "Research Monitoring"],
  },
  {
    id: "story-ai-debugger",
    title: "Research lab introduces AI debugger for multi-agent workflows",
    summary:
      "A new open-source toolkit traces decision paths across coordinated LLM agents to reduce failure rates in production pipelines.",
    category: "research",
    source: "Tech Ledger",
    sourceUrl: "https://techledger.example.com/ai-debugger-toolkit",
    publishedAt: "2026-09-20T15:00:00Z",
    topics: ["AI Agents", "Research Monitoring"],
  },
];

export const mockTodayEdition: Edition = {
  id: "edition-2026-09-22",
  date: "2026-09-22",
  headline: "AI governance and cyber resilience lead today's brief",
  summary:
    "Today's edition tracks policy momentum in AI, growing software supply-chain threats, and new research partnerships shaping global technology strategy.",
  stories: mockArticles.slice(0, 4),
};

export const mockSavedStories: SavedStory[] = [
  {
    id: "saved-1",
    articleId: "story-ransomware-shift",
    savedAt: "2026-09-22T10:20:00Z",
    notes: "Review with platform team before Friday security review.",
  },
  {
    id: "saved-2",
    articleId: "story-ai-policy-2026",
    savedAt: "2026-09-22T10:22:00Z",
  },
];

export const mockUserPreferences: UserPreferences = {
  preferredCategories: ["ai", "cybersecurity", "software-engineering"],
  preferredTopics: ["AI Agents", "Cloud Security", "India Tech"],
  mutedSources: [],
  locale: "en-IN",
};

export const mockConversation: ChatConversation = {
  id: "conversation-daily-brief",
  title: "Morning Brief Companion",
  updatedAt: "2026-09-22T10:30:00Z",
  messages: [
    {
      id: "msg-1",
      role: "user",
      content: "Summarize today's cybersecurity stories in 3 bullets.",
      createdAt: "2026-09-22T10:29:10Z",
    },
    {
      id: "msg-2",
      role: "assistant",
      content:
        "Supply-chain extortion is rising, CI pipelines are top targets, and zero-trust build isolation is the key mitigation trend.",
      createdAt: "2026-09-22T10:29:12Z",
    },
  ],
};
