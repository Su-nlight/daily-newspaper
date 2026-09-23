# Module 05 — Personalization and Topics

## Objective

Build the personalization experience.

Routes:

/topics

and personalized sections throughout the site.

---

# Personalization Concept

Daily Signal should learn what the user cares about.

Initial preferences are explicit.

Later preferences can be learned from behavior.

---

# Topics Page

Create:

YOUR INTERESTS

Topic list with adjustable importance.

Example:

AI
Cybersecurity
RAG
Software Engineering
Research
Cloud
SAP
Blockchain

Use a simple slider or importance control.

---

# Regions

Allow users to select regions:

India
Europe
Japan
South Korea
Singapore
Global

---

# Sources

Allow users to enable/disable preferred sources.

---

# Personalization Categories

Support:

topics
regions
sources
content types

---

# Why You're Seeing This

Create reusable component:

WhyRelevant

Example:

Why you're seeing this

✓ Matches your interest in RAG
✓ Related to cybersecurity research
✓ Published today

Do not expose internal scoring numbers.

---

# User Preference Type

Use:

UserPreferences

Example:

{
  topics: [
    {
      id: "ai",
      weight: 0.9
    }
  ],
  regions: ["india", "europe"],
  sources: [],
  readingTime: 10
}

---

# Behavioral Signals

Prepare frontend infrastructure for:

article_opened
article_saved
article_shared
article_completed
topic_followed
topic_ignored

Do not implement ML recommendation logic.

The backend will eventually consume these signals.

---

# For You Section

Add:

"For You"

or

"Relevant to You"

to the homepage.

Stories should support a personalized flag and explanation.

---

# Important

Do not claim personalization is AI-powered yet.

At this stage, implement the UI and data model.

The LangGraph personalization logic comes later.