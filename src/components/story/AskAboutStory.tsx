"use client";

import { useChat } from "@/components/chat/ChatProvider";

interface AskAboutStoryProps {
  story: {
    id: string;
    title: string;
    /** Short blurb passed into the chat as context — a story's dek or summary. */
    context: string;
  };
  /** Smaller inline rendering for list contexts (e.g. the /saved list), vs.
   *  the full-width prominent CTA used at the end of a story page. */
  compact?: boolean;
}

export function AskAboutStory({ story, compact = false }: AskAboutStoryProps) {
  const { openChat } = useChat();

  function handleClick() {
    openChat({ storyId: story.id, title: story.title, context: story.context });
  }

  if (compact) {
    return (
      <button
        type="button"
        onClick={handleClick}
        className="text-metadata flex items-center gap-1.5 border border-border-strong px-3 py-1.5 text-accent transition-colors hover:bg-background-elevated"
      >
        <span aria-hidden="true">💬</span>
        Ask AI
      </button>
    );
  }

  return (
    <section className="border-t border-border pt-6">
      <button
        type="button"
        onClick={handleClick}
        className="text-metadata flex w-full items-center justify-center gap-2 border border-border-strong bg-background-elevated px-5 py-3.5 text-accent transition-colors hover:bg-background sm:w-auto"
      >
        <svg
          aria-hidden="true"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.7"
          className="size-4"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M4 5.5h16a1 1 0 0 1 1 1V15a1 1 0 0 1-1 1H9l-4 4v-4H4a1 1 0 0 1-1-1V6.5a1 1 0 0 1 1-1Z"
          />
        </svg>
        Ask AI about this story
      </button>
    </section>
  );
}
