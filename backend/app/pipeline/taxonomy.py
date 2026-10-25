"""The editorial taxonomy: categories, topics and regions.

Category slugs, topic ids/names and region ids intentionally match the
frontend's (src/data/mock-newspaper.ts) so personalization and category pages
work unchanged. A few topics are new (marked below); the frontend's topic
picker can adopt them when it moves off mock data.

Rules are plain keyword patterns - deterministic, free and explainable, in the
spirit of the repo's rule-based stance (no classifier model in the loop).
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    pattern: re.Pattern[str]
    weight: int = 1


def _rules(*specs: tuple[str, int]) -> tuple[Rule, ...]:
    # The (?:...) group matters: without it "a|b" would bind the word-boundary
    # guards to the first/last alternative only ("rbi" would match "arbitrary").
    return tuple(Rule(re.compile(rf"(?<![a-z0-9])(?:{p})(?![a-z0-9])", re.I), w) for p, w in specs)


@dataclass(frozen=True)
class TopicDef:
    id: str
    name: str
    rules: tuple[Rule, ...]
    # Only counts when this also appears (e.g. "regulation" is only AI Policy
    # when the text is about AI).
    requires: re.Pattern[str] | None = None
    new_in_module_09: bool = False


CATEGORY_ORDER = ["ai", "research", "cybersecurity", "software-engineering", "world"]

CATEGORY_LABELS = {
    "ai": "AI",
    "research": "Research",
    "cybersecurity": "Cybersecurity",
    "software-engineering": "Technology",
    "world": "World",
}

CATEGORY_RULES: dict[str, tuple[Rule, ...]] = {
    "ai": _rules(
        (r"ai", 2),
        (r"artificial intelligence", 3),
        (r"llms?", 3),
        (r"machine learning", 3),
        (r"generative", 2),
        (r"chatbots?", 2),
        (r"neural", 2),
        (r"inference", 2),
        (r"openai", 3),
        (r"anthropic", 3),
        (r"gemini", 2),
        (r"chatgpt", 3),
        (r"agents?", 1),
        (r"agentic", 3),
        (r"foundation models?", 3),
        (r"gpus?", 1),
    ),
    "research": _rules(
        (r"arxiv", 3),
        (r"papers?", 2),
        (r"preprints?", 3),
        (r"benchmarks?", 3),
        (r"datasets?", 2),
        (r"researchers?", 2),
        (r"study", 1),
        (r"we (introduce|propose|present)", 3),
    ),
    "cybersecurity": _rules(
        (r"cve-\d{4}-\d+", 4),
        (r"ransomware", 3),
        (r"malware", 3),
        (r"vulnerabilit(y|ies)", 3),
        (r"exploit(s|ed|ation)?", 2),
        (r"breach(es)?", 3),
        (r"phishing", 3),
        (r"zero-days?", 3),
        (r"remote code execution", 4),
        (r"cyber\w*", 3),
        (r"botnets?", 3),
        (r"security", 1),
        (r"patch(es|ed)?", 1),
        (r"hackers?", 2),
        (r"data leak", 3),
    ),
    "software-engineering": _rules(
        (r"software", 2),
        (r"developers?", 2),
        (r"open[- ]source", 2),
        (r"framework", 1),
        (r"kubernetes", 2),
        (r"rust", 2),
        (r"typescript", 2),
        (r"python", 1),
        (r"apis?", 1),
        (r"databases?", 2),
        (r"compiler", 3),
        (r"latency", 2),
        (r"infrastructure", 1),
        (r"devops", 3),
        (r"github", 1),
        (r"release[sd]?", 1),
        (r"cloud", 1),
        (r"chips?", 1),
        (r"semiconductors?", 1),
        (r"startups?", 1),
    ),
    "world": _rules(
        (r"government", 2),
        (r"regulators?", 2),
        (r"regulations?", 2),
        (r"ministry", 2),
        (r"tariffs?", 3),
        (r"sanctions?", 3),
        (r"export controls?", 3),
        (r"economy", 3),
        (r"elections?", 3),
        (r"lawsuit", 2),
        (r"antitrust", 3),
        (r"merger", 2),
        (r"acquisitions?", 2),
        (r"layoffs?", 3),
        (r"trade (war|deal)", 3),
        (r"geopolit\w+", 3),
    ),
}

_AI_CONTEXT = re.compile(
    r"(?<![a-z0-9])(ai|artificial intelligence|machine learning|llms?)(?![a-z0-9])", re.I
)

TOPICS: tuple[TopicDef, ...] = (
    TopicDef(
        "topic-agents",
        "AI Agents",
        _rules(
            (r"agents?", 2),
            (r"agentic", 3),
            (r"multi-agent", 3),
            (r"langgraph", 3),
            (r"langchain", 3),
            (r"tool use", 3),
            (r"model context protocol", 3),
            (r"mcp", 2),
        ),
    ),
    TopicDef(
        "topic-cloud-security",
        "Cloud Security",
        _rules(
            (r"cloud security", 3),
            (r"zero[- ]trust", 3),
            (r"iam", 2),
            (r"misconfigur\w+", 3),
            (r"cspm", 3),
            (r"container escape", 3),
            (r"s3 bucket", 3),
            (r"cloud (breach|leak)", 3),
        ),
    ),
    TopicDef(
        "topic-india-tech",
        "India Tech",
        _rules(
            (r"india", 3),
            (r"indian", 3),
            (r"bengaluru|bangalore", 3),
            (r"mumbai", 2),
            (r"delhi", 2),
            (r"hyderabad", 2),
            (r"meity", 3),
            (r"infosys|tcs|wipro|flipkart|zomato", 3),
        ),
    ),
    TopicDef(
        "topic-research",
        "Research Monitoring",
        _rules(
            (r"arxiv", 3),
            (r"preprints?", 3),
            (r"benchmarks?", 3),
            (r"papers?", 2),
            (r"researchers?", 2),
            (r"we (introduce|propose|present)", 3),
        ),
    ),
    TopicDef(
        "topic-cybersecurity",
        "Cybersecurity",
        _rules(
            (r"cve-\d{4}-\d+", 3),
            (r"ransomware", 3),
            (r"malware", 3),
            (r"vulnerabilit(y|ies)", 3),
            (r"breach(es)?", 3),
            (r"phishing", 3),
            (r"zero-days?", 3),
            (r"remote code execution", 3),
            (r"cyber\w*", 3),
            (r"botnets?", 3),
        ),
    ),
    TopicDef(
        "topic-rag",
        "RAG",
        _rules(
            (r"rag", 3),
            (r"retrieval[- ]augmented( generation)?", 3),
            (r"vector (database|search|store)s?", 3),
            (r"rerank\w*", 3),
            (r"embeddings?", 2),
        ),
    ),
    TopicDef(
        "topic-software-engineering",
        "Software Engineering",
        _rules(
            (r"software engineering", 3),
            (r"developers?", 2),
            (r"devops", 3),
            (r"compiler", 3),
            (r"microservices?", 3),
            (r"refactor\w*", 3),
            (r"latency", 2),
            (r"architecture", 2),
            (r"rust", 2),
            (r"typescript", 2),
            (r"release[sd]?", 1),
        ),
    ),
    TopicDef(
        "topic-cloud",
        "Cloud",
        _rules(
            (r"cloud", 2),
            (r"aws|azure|google cloud|gcp", 3),
            (r"kubernetes", 3),
            (r"serverless", 3),
            (r"data ?centers?", 2),
            (r"cdn", 3),
            (r"edge network", 3),
            (r"cloudflare", 3),
        ),
    ),
    TopicDef(
        "topic-sap",
        "SAP",
        _rules(
            (r"sap", 3),
            (r"s/4hana", 3),
            (r"abap", 3),
            (r"erp", 2),
        ),
    ),
    TopicDef(
        "topic-blockchain",
        "Blockchain",
        _rules(
            (r"blockchains?", 3),
            (r"bitcoin", 3),
            (r"ethereum", 3),
            (r"smart contracts?", 3),
            (r"crypto(currency|currencies)?", 3),
            (r"stablecoins?", 3),
            (r"defi", 3),
            (r"web3", 3),
        ),
    ),
    # --- new in Module 09 --------------------------------------------------
    TopicDef(
        "topic-llm",
        "LLMs",
        _rules(
            (r"llms?", 3),
            (r"large language models?", 3),
            (r"gpt-?\d\S*", 3),
            (r"claude", 3),
            (r"gemini", 3),
            (r"llama", 3),
            (r"foundation models?", 3),
            (r"chatgpt", 3),
        ),
        new_in_module_09=True,
    ),
    TopicDef(
        "topic-ai-policy",
        "AI Policy",
        _rules(
            (r"regulat\w+", 2),
            (r"governance", 2),
            (r"draft framework", 3),
            (r"legislation", 2),
            (r"public comment", 2),
            (r"audits?", 2),
            (r"ai act", 3),
            (r"compliance", 1),
        ),
        requires=_AI_CONTEXT,
        new_in_module_09=True,
    ),
    TopicDef(
        "topic-semiconductors",
        "Semiconductors",
        _rules(
            (r"semiconductors?", 3),
            (r"chips?", 2),
            (r"gpus?", 2),
            (r"tsmc", 3),
            (r"nvidia", 3),
            (r"amd", 2),
            (r"intel", 2),
            (r"foundr(y|ies)", 3),
            (r"wafers?", 3),
        ),
        new_in_module_09=True,
    ),
    TopicDef(
        "topic-open-source",
        "Open Source",
        _rules(
            (r"open[- ]source", 3),
            (r"maintainers?", 2),
            (r"open[- ]weights?", 3),
        ),
        new_in_module_09=True,
    ),
)

TOPIC_NAMES: dict[str, str] = {t.id: t.name for t in TOPICS}
TOPIC_IDS_BY_NAME: dict[str, str] = {t.name: t.id for t in TOPICS}

# Priors applied by what the *source* is, before any text is read.
KIND_CATEGORY_PRIOR = {
    "arxiv": ("research", 6),
    "nvd": ("cybersecurity", 6),
    "github": ("software-engineering", 2),
}
KIND_TOPIC_PRIOR = {
    "arxiv": ("topic-research", 3),
    "nvd": ("topic-cybersecurity", 3),
    "github": ("topic-open-source", 3),
}

REGION_NAMES = {
    "india": "India",
    "europe": "Europe",
    "japan": "Japan",
    "south-korea": "South Korea",
    "singapore": "Singapore",
    "global": "Global",
}

REGION_RULES: dict[str, tuple[Rule, ...]] = {
    "india": _rules(
        (r"india", 3),
        (r"indian", 3),
        (r"bengaluru|bangalore|mumbai|delhi|hyderabad|chennai|pune", 2),
        (r"meity|rbi|sebi", 3),
    ),
    "europe": _rules(
        (r"europe", 3),
        (r"european", 3),
        (r"eu", 2),
        (r"brussels", 2),
        (r"gdpr", 3),
        (r"germany|france|spain|italy|netherlands|ireland", 2),
        (r"united kingdom|britain|british", 2),
    ),
    "japan": _rules((r"japan", 3), (r"japanese", 3), (r"tokyo", 2)),
    "south-korea": _rules((r"south korea", 3), (r"korean?", 3), (r"seoul", 2)),
    "singapore": _rules((r"singapore", 3)),
}

# Well-known organisations/products, matched case-sensitively as whole words.
KNOWN_ENTITIES: tuple[str, ...] = tuple(
    name.replace("_", " ")
    for name in """
    OpenAI Anthropic Google Microsoft Meta Nvidia AMD Intel TSMC Apple Amazon AWS Azure
    Cloudflare GitHub GitLab Mozilla Linux Kubernetes Docker Rust Python TypeScript JavaScript
    Next.js React PostgreSQL MySQL MongoDB Redis OpenSSL OpenSSH Android iOS Windows macOS
    Chrome Firefox Samsung Qualcomm Broadcom Oracle IBM SAP Salesforce Infosys TCS Wipro
    Flipkart Zomato Reliance Tesla Cisco Fortinet Palo_Alto Okta Crowdstrike Hugging_Face
    LangChain LangGraph Groq DeepMind NIST CISA NVD ArXiv
    """.split()
)
