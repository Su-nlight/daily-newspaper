# Module 08 — AI Chat Integration

## Objective

Connect the global Daily Signal chat interface to the LangGraph backend.

---

# Global Chat

Every page should contain:

ChatBubble

The bubble is bottom-left.

---

# Compact Chat

Clicking the bubble opens:

header
conversation
input
send button

---

# Full Chat

Route:

/chat

This should provide a larger conversational interface.

---

# Context Awareness

The chat must understand where the user is.

Examples:

Homepage:

context = today's edition

Story page:

context = current story

Category page:

context = current category

Search page:

context = current search results

---

# Example

User is reading:

"New RAG evaluation benchmark released"

They click:

Ask AI about this story

Then ask:

"How could this affect my research?"

The backend should receive the story context automatically.

The user should NOT need to paste the article.

---

# Conversation State

Maintain:

conversationId

messages

context

Do not lose conversation when the compact chat panel is expanded.

---

# Message UI

User messages:

right aligned

AI messages:

left aligned

Sources:

shown below AI response.

---

# AI Response

Support:

markdown
code blocks
lists
links
citations

Avoid excessive UI decoration.

---

# Suggested Questions

For story pages provide suggestions such as:

"Why does this matter?"

"Explain this simply."

"What are the implications?"

"Show me the sources."

---

# Loading

Show a subtle typing/loading state.

Do not use a huge loading animation.

---

# Error

If the backend fails:

"Something went wrong. Try again."

Provide retry.

---

# Accessibility

Chat must support:

keyboard navigation
Enter to send
Shift+Enter for newline
screen-reader labels
focus management

---

# Acceptance Criteria

User can:

open chat
ask question
receive LangGraph/Groq response
see sources
continue conversation
ask about current story
navigate to full chat
return to newspaper without losing conversation.