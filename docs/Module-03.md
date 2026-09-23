# Module 03 — Daily Newspaper Homepage

## Objective

Build the main Daily Signal homepage.

Route:

/

This is the most important page in the product.

---

# Concept

The homepage should look like the front page of a premium digital newspaper.

It should NOT look like a news dashboard.

Use:

- editorial columns
- large headlines
- variable story sizes
- thin dividers
- whitespace
- typography

Avoid making every story an identical card.

---

# Page Structure

1. Masthead
2. Today's edition metadata
3. Main story
4. Secondary stories
5. World
6. Technology
7. AI & Research
8. Cybersecurity
9. Relevant to You
10. 60-Second Brief
11. Footer

---

# Hero Story

Create HeroStory component.

Structure:

category

large headline

short summary

publication information

large image

Read story button

---

# Secondary Stories

Use a mixture of:

StandardStory
CompactStory
HorizontalStory

The visual hierarchy should make clear which stories are most important.

---

# Sections

Create reusable:

NewspaperSection

Props:

title
description
stories
layout

Example:

<NewspaperSection
  title="Technology"
  stories={...}
/>

---

# Relevant To You

Create a personalized section.

Each story should optionally show:

"Why you're seeing this"

Example:

Matches your interests:
AI · RAG · Cybersecurity

Keep this subtle.

---

# 60-Second Brief

Create a compact summary section.

Example:

THE 60-SECOND BRIEF

01 — Major event...

02 — Important technology development...

03 — Research development...

Allow "Read full edition".

---

# Loading State

Create newspaper skeletons.

Do not use generic rectangular dashboard skeletons everywhere.

Maintain the editorial structure.

---

# Empty State

If no edition exists:

"No edition is available yet."

Include a retry action.

---

# Data

Use the API abstraction created in Module 01.

Initially use mock data.

Do not directly hardcode stories inside page.tsx.

---

# Responsive

Desktop:
multi-column editorial layout.

Tablet:
two-column layout.

Mobile:
single-column layout with preserved hierarchy.

---

# Acceptance Criteria

The homepage should immediately communicate:

"This is today's personalized newspaper."

It should not communicate:

"This is an AI SaaS dashboard."