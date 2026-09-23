import type {
  Article,
  Category,
  ChatConversation,
  Edition,
  SavedStory,
  Source,
  StoryDetail,
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
    category: "software-engineering",
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
    category: "software-engineering",
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

/**
 * Hand-authored long-form detail content for the story-detail page
 * (Module 04). Keyed by Article.id. Not every article has an entry — see
 * `deriveStoryDetail` in lib/api/client.ts for the fallback used for the
 * rest, so /story/[id] never has an empty section for a real article id.
 */
export const mockStoryDetails: Record<
  string,
  Pick<StoryDetail, "dek" | "whatHappened" | "whyItMatters" | "keyFacts" | "citations">
> = {
  "story-ai-policy-2026": {
    dek: "Quarterly audits would apply to AI systems used in lending, diagnostics, and other high-impact decisions.",
    whatHappened:
      "India's technology ministry published a draft framework requiring enterprises to submit quarterly audits for AI systems used in finance and healthcare decision-making. The draft covers model documentation, bias testing thresholds, and incident-reporting timelines, with a 60-day public comment window before rules are finalized.",
    whyItMatters:
      "This is the first sector-specific AI audit regime proposed by an Indian regulator rather than a general-purpose AI law, and it mirrors approaches already emerging in the EU and Singapore. Teams shipping AI features into regulated Indian markets should expect documentation and testing requirements to become a procurement checklist item well before enforcement begins.",
    keyFacts: [
      "Applies to AI systems used in lending, insurance underwriting, and clinical decision support.",
      "Quarterly audit submissions would be required, with a named accountable officer per deployment.",
      "Public comment period runs 60 days from the draft's publication date.",
      "No penalty structure has been proposed yet; that is expected in a follow-up draft.",
    ],
    citations: [
      {
        publisher: "Tech Ledger",
        publishedAt: "2026-09-22T07:30:00Z",
        url: "https://techledger.example.com/ai-policy-audits",
      },
      {
        publisher: "Ministry of Electronics and IT (press note)",
        publishedAt: "2026-09-22T06:00:00Z",
        url: "https://globalwire.example.com/meity-ai-draft-framework",
      },
    ],
  },
  "story-ransomware-shift": {
    dek: "Attackers are increasingly targeting build pipelines and package registries instead of production databases.",
    whatHappened:
      "Security researchers tracking a cluster of ransomware operators found a marked shift toward compromising CI/CD infrastructure and public package registries, then timing extortion demands to coincide with scheduled release windows to maximize pressure on engineering teams.",
    whyItMatters:
      "Traditional ransomware defenses focus on endpoint and database protection; this shift means build systems — often treated as internal infrastructure with looser access controls — are now a primary target. Teams that haven't extended zero-trust practices to CI runners and artifact registries are more exposed than they may realize.",
    keyFacts: [
      "Attacks cluster around scheduled release windows to increase extortion leverage.",
      "Compromised build credentials were the most common initial access vector observed.",
      "Analysts recommend short-lived, scoped credentials for CI runners as a primary mitigation.",
    ],
    citations: [
      {
        publisher: "Security Post",
        publishedAt: "2026-09-22T09:10:00Z",
        url: "https://securitypost.example.com/supply-chain-extortion",
      },
    ],
  },
  "story-rust-backend-scale": {
    dek: "The migration cut ingestion-tier compute spend while keeping the same throughput under peak load.",
    whatHappened:
      "The team behind a widely used open-source observability platform published benchmarks comparing their Go-based ingestion service to a Rust rewrite completed over two quarters, reporting lower per-node CPU usage and reduced garbage-collection-related latency spikes under sustained write load.",
    whyItMatters:
      "The benchmarks add to a growing body of public evidence from infrastructure teams evaluating Rust for latency-sensitive, high-throughput services, an area where garbage-collected languages can hit predictability limits. The published methodology also gives other teams a reference to replicate the comparison against their own workloads.",
    keyFacts: [
      "Migration was scoped to the ingestion tier only, not the full platform.",
      "Benchmarks report lower peak memory and fewer GC-related latency spikes under sustained load.",
      "The team published its benchmark harness alongside the results.",
    ],
    citations: [
      {
        publisher: "Global Wire",
        publishedAt: "2026-09-21T19:45:00Z",
        url: "https://globalwire.example.com/rust-backend-scale",
      },
    ],
  },
  "story-semiconductor-alliance": {
    dek: "The corridor pairs Japanese chip-packaging expertise with Indian university research capacity.",
    whatHappened:
      "Japan and India signed a joint funding agreement establishing a semiconductor research corridor focused on advanced chip packaging techniques, pairing Japanese industrial partners with Indian university research groups and committing multi-year funding to shared facilities.",
    whyItMatters:
      "Advanced packaging — rather than leading-edge fabrication — is where much of the next wave of semiconductor performance gains is expected to come from, and this corridor positions both countries to build research capacity in that specific niche rather than competing directly with existing fabrication hubs.",
    keyFacts: [
      "Focus is on advanced chip packaging, not fabrication.",
      "Funding is structured as a multi-year joint program between government and university partners.",
      "Initial shared research facilities are planned in both countries.",
    ],
    citations: [
      {
        publisher: "Global Wire",
        publishedAt: "2026-09-21T13:20:00Z",
        url: "https://globalwire.example.com/semiconductor-corridor",
      },
    ],
  },
  "story-rag-benchmark": {
    dek: "Accuracy drops sharply once retrieval-augmented systems have to search past roughly 50 pages of source material.",
    whatHappened:
      "A new open benchmark testing retrieval-augmented generation systems across long-document question answering found that most evaluated pipelines lost significant answer accuracy once the source corpus exceeded roughly 50 pages, even when the underlying language model supported a much longer context window.",
    whyItMatters:
      "The results suggest the bottleneck for long-context RAG is increasingly the retrieval step rather than the model's context window, which has implications for teams that assumed larger context windows alone would solve long-document accuracy. Hybrid retrieval strategies — combining dense retrieval with structured indexing — outperformed single-method approaches in the benchmark.",
    keyFacts: [
      "Accuracy drop-off begins around the 50-page mark for most evaluated pipelines.",
      "Hybrid retrieval (dense + structured indexing) outperformed single-method retrieval.",
      "Benchmark dataset and evaluation harness were released publicly alongside the paper.",
    ],
    citations: [
      {
        publisher: "Tech Ledger",
        publishedAt: "2026-09-21T08:15:00Z",
        url: "https://techledger.example.com/rag-benchmark",
      },
    ],
  },
  "story-cloud-breach-disclosure": {
    dek: "The provider says the exposure window was limited but has not yet disclosed how many accounts were affected.",
    whatHappened:
      "A major cloud provider disclosed that a storage-service misconfiguration left some enterprise storage buckets exposed for a limited window. The company has not yet published an affected-account count but confirmed the exposure predates its recently rolled out default encryption-at-rest policy for new accounts.",
    whyItMatters:
      "Default encryption-at-rest closes one specific gap, but the disclosure is a reminder that misconfiguration — not just unpatched vulnerabilities — remains one of the most common root causes of cloud data exposure. Teams relying on the provider's default security posture rather than auditing their own bucket policies were more exposed.",
    keyFacts: [
      "Root cause was a storage-service misconfiguration, not an external breach.",
      "Default encryption-at-rest for new accounts was enabled following the incident.",
      "The provider has not yet disclosed the number of affected accounts.",
    ],
    citations: [
      {
        publisher: "Security Post",
        publishedAt: "2026-09-22T06:05:00Z",
        url: "https://securitypost.example.com/cloud-breach-disclosure",
      },
    ],
  },
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
