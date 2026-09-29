# Module 06 — Search, Saved Stories and Archive

## Objective

Build the newspaper's discovery and history functionality.

Routes:

/search
/saved
/archive

---

# Search

Search should feel like searching a newspaper archive.

Not like a generic Google clone.

---

## Search UI

Large search field:

"What are you looking for?"

Filters:

Date
Category
Source
Topic
Region

---

## Search Results

Each result:

category

headline

summary

source

date

topics

Save button

---

## Search States

Implement:

initial
searching
results
no results
error

---

# Saved Stories

Route:

/saved

Display:

Your Library

Saved stories

Each story:

headline
source
date
category
saved date

Actions:

Open
Remove
Ask AI

---

# Empty State

If there are no saved stories:

"Your reading list is empty."

Explain how to save stories.

---

# Archive

Route:

/archive

Display historical editions by date.

Example:

September 2026

22 — Today
21 — Monday
20 — Sunday
19 — Saturday

---

# Edition Archive

Clicking a date should open:

/archive/[date]

or the appropriate edition route.

Display:

edition date
top stories
section list
reading time

---

# Archive Visual Style

Use a timeline/editorial archive aesthetic.

Avoid a generic calendar dashboard.

---

# Data

Use API abstraction.

Do not hardcode search logic into UI.

Prepare:

searchStories()
getSavedStories()
saveStory()
removeSavedStory()
getArchive()
getEditionByDate()

---

# Acceptance Criteria

Users can:

search
filter
open results
save stories
remove saved stories
browse historical editions
open an old edition.