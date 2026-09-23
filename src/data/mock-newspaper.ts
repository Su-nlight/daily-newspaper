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
    slug: "world",
    name: "World",
    description: "Global developments impacting business and technology.",
  },
  {
    slug: "india",
    name: "India",
    description: "Policy, enterprise, and startup developments across India.",
  },
  {
    slug: "technology",
    name: "Technology",
    description: "Architecture, tooling, and engineering culture updates.",
  },
  {
    slug: "ai",
    name: "AI",
    description: "Coverage of AI models, products, and policy shifts.",
  },
  {
    slug: "business",
    name: "Business",
    description: "Markets, enterprise strategy, and leadership developments.",
  },
  {
    slug: "science",
    name: "Science",
    description: "Scientific findings shaping technology and society.",
  },
  {
    slug: "research",
    name: "Research",
    description: "Academic and industrial research worth tracking.",
  },
  {
    slug: "cybersecurity",
    name: "Cybersecurity",
    description: "Threat intelligence, breaches, and defensive practices.",
  },
  {
    slug: "career",
    name: "Career",
    description: "Career signals for engineers, researchers, and operators.",
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
    category: "technology",
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
    relevanceScore: 0.88,
    whyRelevant: "Matches your interest in AI agent tooling and evaluation.",
  },
  {
    id: "story-rag-benchmark",
    title: "New benchmark exposes retrieval gaps in long-context RAG systems",
    summary:
      "Researchers found that most retrieval-augmented pipelines lose accuracy sharply past 50 pages of source context, prompting renewed interest in hybrid retrieval strategies.",
    category: "research",
    source: "Tech Ledger",
    sourceUrl: "https://techledger.example.com/rag-benchmark",
    publishedAt: "2026-09-21T08:15:00Z",
    imageUrl: "https://images.example.com/rag-benchmark.jpg",
    topics: ["AI Agents", "Research Monitoring"],
    relevanceScore: 0.89,
    whyRelevant: "Matches your interests: AI Agents · RAG · Research Monitoring",
  },
  {
    id: "story-model-router",
    title: "Startup raises Series B for open-source model routing layer",
    summary:
      "The routing engine dynamically selects between small and large models based on task complexity, cutting inference costs by up to 40% in early enterprise pilots.",
    category: "ai",
    source: "Global Wire",
    sourceUrl: "https://globalwire.example.com/model-router-series-b",
    publishedAt: "2026-09-22T05:40:00Z",
    imageUrl: "https://images.example.com/model-router.jpg",
    topics: ["AI Agents"],
  },
  {
    id: "story-cloud-breach-disclosure",
    title: "Major cloud provider discloses misconfigured storage exposure",
    summary:
      "The provider confirmed a limited exposure window affecting enterprise storage buckets and has rolled out default encryption-at-rest for new accounts.",
    category: "cybersecurity",
    source: "Security Post",
    sourceUrl: "https://securitypost.example.com/cloud-breach-disclosure",
    publishedAt: "2026-09-22T06:05:00Z",
    imageUrl: "https://images.example.com/cloud-breach.jpg",
    topics: ["Cloud Security"],
    relevanceScore: 0.93,
    whyRelevant: "Matches your interests: Cloud Security · Cybersecurity",
  },
  {
    id: "story-zero-trust-adoption",
    title: "Zero-trust adoption crosses 60% among Fortune 500 firms",
    summary:
      "A new industry survey shows zero-trust network access has overtaken VPN-based models as the default enterprise architecture for the first time.",
    category: "cybersecurity",
    source: "Security Post",
    sourceUrl: "https://securitypost.example.com/zero-trust-adoption",
    publishedAt: "2026-09-21T11:30:00Z",
    topics: ["Cloud Security", "Research Monitoring"],
  },
  {
    id: "story-webassembly-edge",
    title: "WebAssembly runtimes gain ground in edge compute deployments",
    summary:
      "Engineering teams report faster cold-start times and smaller deployment footprints after moving latency-sensitive services from containers to WASM.",
    category: "technology",
    source: "Global Wire",
    sourceUrl: "https://globalwire.example.com/webassembly-edge",
    publishedAt: "2026-09-21T16:10:00Z",
    imageUrl: "https://images.example.com/webassembly-edge.jpg",
    topics: ["Research Monitoring"],
  },
  {
    id: "story-typed-apis-survey",
    title: "Survey: teams shipping typed APIs report 30% fewer integration bugs",
    summary:
      "Engineering leaders point to end-to-end type safety across client and server boundaries as the single highest-leverage reliability investment this year.",
    category: "technology",
    source: "Tech Ledger",
    sourceUrl: "https://techledger.example.com/typed-apis-survey",
    publishedAt: "2026-09-20T09:00:00Z",
    topics: ["Research Monitoring"],
  },
  {
    id: "story-india-startup-funding",
    title: "India's enterprise SaaS startups post strongest quarter since 2022",
    summary:
      "Fresh funding data shows a rebound led by AI-infrastructure and fintech-adjacent startups based in Bengaluru and Pune.",
    category: "world",
    source: "Global Wire",
    sourceUrl: "https://globalwire.example.com/india-startup-funding",
    publishedAt: "2026-09-22T04:20:00Z",
    imageUrl: "https://images.example.com/india-startup-funding.jpg",
    topics: ["India Tech"],
    relevanceScore: 0.86,
    whyRelevant: "Matches your interests: India Tech",
  },
  {
    id: "story-eu-tech-regulation",
    title: "EU proposes unified compute-reporting rule for large model training runs",
    summary:
      "The draft rule would require disclosure of compute usage above a set threshold, aligning the bloc's approach more closely with emerging US guidance.",
    category: "world",
    source: "Global Wire",
    sourceUrl: "https://globalwire.example.com/eu-compute-reporting",
    publishedAt: "2026-09-21T20:05:00Z",
    topics: ["Research Monitoring"],
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
  preferredCategories: ["ai", "cybersecurity", "technology"],
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
