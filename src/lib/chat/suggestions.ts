import type { ChatContextKind } from "@/types";

const BY_KIND: Record<ChatContextKind | "none", string[]> = {
  story: [
    "Why does this matter?",
    "Explain this simply.",
    "What are the implications?",
    "Show me the sources.",
  ],
  edition: [
    "What are the top stories in this edition?",
    "Which story is most important, and why?",
    "Summarize this edition in three bullets.",
  ],
  category: [
    "What's the most important development here?",
    "Summarize the latest stories in this category.",
  ],
  search: [
    "Summarize these results.",
    "Which result is most relevant?",
    "What do these stories have in common?",
  ],
  none: ["What are the latest AI developments?", "Any new cybersecurity news?"],
};

export function getSuggestedQuestions(kind: ChatContextKind | undefined): string[] {
  return BY_KIND[kind ?? "none"];
}
