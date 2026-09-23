# Module 01 — Project Foundation

## Objective

Establish the technical foundation for the Daily Signal personalized newspaper website.

Do NOT build the complete UI yet.

The goal is to create a clean, scalable project structure that later modules can extend without major refactoring.

---

## Product

Daily Signal is a personalized digital newspaper.

It provides:

- Daily news editions
- Personalized stories
- Research/news monitoring
- Career intelligence
- Search
- Saved stories
- Historical editions
- AI conversational assistant

The frontend will eventually communicate with a backend powered by:

- LangGraph
- Groq API
- Python/FastAPI

---

## Frontend

Use:

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui where useful

Use the App Router.

Prefer Server Components by default.

Only use Client Components where interactivity requires them.

---

## Initial Routes

Create the route structure:

/
 /story/[id]
 /category/[slug]
 /search
 /saved
 /topics
 /archive
 /research
 /career
 /chat
 /about

At this stage, routes can contain simple placeholder content.

---

## Project Structure

Use a structure similar to:

src/
  app/
    page.tsx
    story/[id]/
    category/[slug]/
    search/
    saved/
    topics/
    archive/
    research/
    career/
    chat/
    about/

  components/
    layout/
    navigation/
    newspaper/
    story/
    chat/
    search/
    personalization/

  lib/
    api/
    utils/
    constants/

  types/

  hooks/

  data/

Do not create unnecessary abstractions.

---

## Data Types

Create shared TypeScript types for:

Article
Edition
Category
Source
Topic
SavedStory
UserPreferences
ChatMessage
ChatConversation

Example Article shape:

{
  id: string
  title: string
  summary: string
  category: string
  source: string
  sourceUrl: string
  publishedAt: string
  imageUrl?: string
  topics: string[]
  relevanceScore?: number
  whyRelevant?: string
}

Do not hardcode these types into individual components.

---

## API Layer

Create a centralized API client.

Example:

lib/api/client.ts

Future functions:

getTodayEdition()
getStory(id)
getCategory(slug)
searchStories(query)
getSavedStories()
getTopics()
sendChatMessage()

For now these can return mock data.

Do not scatter fetch() calls throughout UI components.

---

## Mock Data

Create realistic mock newspaper data.

Do NOT use lorem ipsum.

Use realistic example stories involving:

- AI
- cybersecurity
- software engineering
- research
- technology
- India
- world news

Clearly separate mock data from production API code.

---

## Requirements

The project must:

- compile successfully
- have no TypeScript errors
- have no console errors
- support responsive layouts
- support light/dark theme infrastructure
- have clean imports
- use reusable types
- be easy for future modules to extend

---

## Do NOT implement yet

Do not implement:

- LangGraph
- Groq
- authentication
- database
- real news ingestion
- advanced personalization
- complex animations
- final visual design

This module is only the foundation.