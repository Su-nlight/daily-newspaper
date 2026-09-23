"use client";

import { useChat } from "@/components/chat/ChatProvider";
import type { StoryDetail } from "@/types";

interface AskAboutStoryProps {
  story: StoryDetail;
}

export function AskAboutStory({ story }: AskAboutStoryProps) {
  const { openChat } = useChat();

  return (
    <section className="border-t border-border pt-6">
      <button
        type="button"
        onClick={() =>
          openChat({
            storyId: story.id,
            title: story.title,
            context: story.dek,
          })
        }
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
