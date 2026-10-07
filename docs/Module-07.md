# Module 07 — LangGraph + Groq Backend

## Objective

Build the AI backend for Daily Signal using LangGraph and Groq.

The backend must expose a clean API to the frontend.

---

# Stack

Python
FastAPI
LangGraph
Groq API
Pydantic

Use environment variables for secrets.

Never expose the Groq API key to the browser.

---

# Backend Structure

backend/

  app/
    main.py

    api/
      chat.py
      edition.py
      stories.py
      search.py

    graph/
      state.py
      graph.py
      nodes/

    models/
      article.py
      edition.py
      chat.py
      preferences.py

    services/
      retrieval.py
      ranking.py
      summarization.py
      sources.py

    config.py

---

# LangGraph

The graph should initially support:

START
 ↓
Classify Query
 ↓
Retrieve Context
 ↓
Generate Answer
 ↓
Validate / Format
 ↓
END

---

# Query Classification

Classify user messages into:

news
story
research
career
general

Do not create unnecessary agents.

Prefer deterministic routing where possible.

---

# State

Create typed graph state.

Example:

{
  messages,
  query_type,
  query,
  story_id,
  retrieved_documents,
  sources,
  answer
}

---

# Context

The frontend may provide:

current story
current edition
current category

The graph should use that context when appropriate.

---

# Groq

Create a centralized LLM service.

Do not instantiate the Groq client independently in every node.

Use environment variables.

Example:

GROQ_API_KEY=

Model should be configurable.

Do not hardcode a model name throughout the codebase.

---

# API

POST /api/chat

Request:

{
  "message": "...",
  "conversation_id": "...",
  "context": {
    "story_id": "...",
    "edition_id": "..."
  }
}

Response:

{
  "message": "...",
  "sources": [],
  "conversation_id": "..."
}

---

# Streaming

Prepare the architecture for streaming responses.

If implemented, use Server-Sent Events or an appropriate streaming mechanism.

The frontend should progressively display the answer.

---

# Citations

Every factual answer based on retrieved news should retain source references.

The LLM must not invent source URLs.

---

# Error Handling

Handle:

Groq API failure
timeout
invalid request
missing context
empty retrieval
rate limits

Return useful errors to the frontend.

---

# Important

Do not build a multi-agent system just because LangGraph is being used.

Start with a small state graph.

Expand only when a real requirement appears.