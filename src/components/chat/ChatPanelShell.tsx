"use client";

import { useChatUiState } from "@/hooks/useChatUiState";

interface ChatPanelShellProps {
  onClose: () => void;
}

export function ChatPanelShell({ onClose }: ChatPanelShellProps) {
  const { activeStoryContext } = useChatUiState();

  return (
    <div
      role="dialog"
      aria-label="Daily Signal AI assistant"
      className="flex h-[28rem] w-[22rem] max-w-[calc(100vw-2.5rem)] flex-col overflow-hidden rounded-lg border border-border bg-background-elevated shadow-xl"
    >
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div>
          <p className="text-section-title text-accent">Daily Signal AI</p>
          <p className="text-caption">
            {activeStoryContext
              ? `Story context: ${activeStoryContext.storyTitle}`
              : "Ask about today&apos;s stories"}
          </p>
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close chat"
          className="flex size-7 items-center justify-center rounded-full border border-border text-foreground transition-colors hover:border-border-strong"
        >
          <svg
            aria-hidden="true"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.6"
            className="size-3.5"
          >
            <path strokeLinecap="round" d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>
      </div>

      <div className="flex flex-1 flex-col justify-end gap-3 overflow-y-auto px-4 py-4">
        {activeStoryContext ? (
          <div className="max-w-[92%] self-end rounded-lg rounded-br-sm border border-border bg-background px-3 py-2">
            <p className="text-metadata text-accent">Story context loaded</p>
            <p className="text-caption text-foreground">{activeStoryContext.storyTitle}</p>
            <p className="text-caption mt-1 text-muted">{activeStoryContext.storyContext}</p>
          </div>
        ) : null}
        <div className="max-w-[85%] self-start rounded-lg rounded-bl-sm bg-background px-3 py-2">
          <p className="text-caption text-foreground">
            Hi — I&apos;m the Daily Signal assistant. Conversational answers over your edition are
            coming in a later module.
          </p>
        </div>
      </div>

      <div className="border-t border-border p-3">
        <div className="flex items-center gap-2 rounded-full border border-border px-3 py-2">
          <input
            type="text"
            disabled
            placeholder="Chat backend not connected yet"
            className="text-body w-full bg-transparent text-foreground placeholder:text-muted focus:outline-none disabled:cursor-not-allowed"
          />
          <button
            type="button"
            disabled
            aria-label="Send message"
            className="flex size-7 shrink-0 items-center justify-center rounded-full bg-accent text-accent-foreground opacity-50"
          >
            <svg
              aria-hidden="true"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              className="size-3.5"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="m5 12 14-7-5 7 5 7-14-7Z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
