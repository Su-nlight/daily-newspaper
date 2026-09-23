# Module 04 — Story and Category Pages

## Objective

Build the individual story experience and category editions.

Routes:

/story/[id]

/category/[slug]

---

# Story Page

The story page should feel like premium journalism.

Structure:

Back to edition

Category

Large headline

Subheadline/dek

Publication date/time

Source

Hero image

Summary

What Happened

Why It Matters

Key Facts

Sources

Related Stories

Ask AI About This Story

---

# Story Components

Create:

StoryHeader
StoryHero
StorySummary
StorySection
KeyFacts
SourceList
RelatedStories
AskAboutStory

---

# Source Presentation

Sources must be clearly visible.

Each source should contain:

publisher
publication date
link

Do not hide source information inside menus.

---

# Ask About This Story

Create a prominent button:

"Ask AI about this story"

Clicking this should open the global chat UI.

Pass:

storyId

story title

story context

to the chat state.

Do not implement LangGraph yet.

---

# Category Page

Route:

/category/[slug]

Example:

/category/technology

Categories:

World
India
Technology
AI
Cybersecurity
Business
Science
Research
Career

---

# Category Layout

Category title

description

featured story

secondary stories

latest stories

trending topics

---

# Editorial Layout

Do not render the category page as a grid of identical cards.

Use:

featured story
two-column secondary area
vertical latest feed

---

# Related Stories

At the bottom of story pages show:

Related Stories

These should share:

topics
entities
category

---

# Loading and Error States

Implement:

story loading
story not found
category loading
category not found
API failure

---

# Acceptance Criteria

A user should be able to:

Homepage
→ open story
→ read story
→ open related story
→ navigate back to category
→ navigate back to today's edition.