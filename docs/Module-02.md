# Module 02 — Design System + Site Shell

## Objective

Create the visual identity and global layout of Daily Signal.

This module establishes the design language that all later pages must follow.

Do not build individual newspaper content sections yet.

---

# Design Direction

Daily Signal should feel like:

- a premium digital newspaper
- an editorial magazine
- a personal intelligence briefing
- a research publication

It must NOT look like:

- a generic SaaS dashboard
- a generic AI chatbot
- a crypto website
- a neon AI landing page

Avoid excessive:

- rounded cards
- gradients
- glassmorphism
- glowing effects
- neon purple/blue
- dashboard metric cards

Typography and editorial hierarchy should dominate.

---

# Typography

Use:

- one serif/display font for major headlines
- one clean sans-serif font for UI/body

Create typography tokens:

display
headline
subheadline
section-title
body
caption
metadata

Headlines should have strong hierarchy.

---

# Colors

Light mode:

- warm paper/off-white background
- near-black text
- muted gray
- restrained warm accent

Dark mode:

- deep charcoal background
- warm off-white text
- muted gray
- restrained accent

Do not use neon colors.

---

# Global Layout

Create:

Header
Main container
Footer
Chat bubble

Desktop content width:

approximately 1200–1400px.

The website should feel like an editorial canvas rather than a dashboard.

---

# Header

Desktop:

Daily Signal

Today's Edition
Topics
Research
Career
Archive
Search

Theme toggle
Profile/settings placeholder

Mobile:

Logo
Menu button

---

# Masthead

Create reusable newspaper masthead component:

Daily Signal

Personal Daily Intelligence

Date / edition information

This should visually resemble a newspaper masthead.

---

# Chat Bubble

Every page must have a persistent AI chat bubble.

Position:

bottom-left.

Collapsed:

small circular button.

Hover:

show:

"Ask Daily Signal AI"

Expanded:

compact chat panel.

The chat functionality itself will be implemented later.

For now create the UI shell and an onClick handler.

---

# Footer

Include:

Daily Signal

About
Methodology
Sources
Privacy
Terms

---

# Components

Create:

Header
MobileNavigation
Footer
Masthead
PageContainer
SectionHeading
ThemeToggle
ChatBubble
ChatPanelShell

---

# Responsive Design

Desktop:
editorial multi-column layouts.

Tablet:
two-column layouts.

Mobile:
single-column layout.

Do not simply shrink desktop UI.

---

# Important

Every future module must use this design system.

Do not introduce independent colors, typography, buttons, spacing systems, or card styles unless absolutely necessary.