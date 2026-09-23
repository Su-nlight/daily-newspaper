import type { ChatStoryContext } from "@/types";

interface ChatPanelShellProps {
  onClose: () => void;
  activeStory?: ChatStoryContext | null;
  onClearContext?: () => void;
}

export function ChatPanelShell({ onClose, activeStory, onClearContext }: ChatPanelShellProps) {
  return (
    <div
      role="dialog"
      aria-label="Daily Signal AI assistant"
      className="flex h-[28rem] w-[22rem] max-w-[calc(100vw-2.5rem)] flex-col overflow-hidden rounded-lg border border-border bg-background-elevated shadow-xl"
    >
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div>
          <p className="text-section-title text-accent">Daily Signal AI</p>
          <p className="text-caption">Ask about today&apos;s stories</p>
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

      {activeStory ? (
        <div className="flex items-start justify-between gap-2 border-b border-border bg-background px-4 py-2.5">
          <p className="text-caption">
            Discussing: <span className="text-foreground">{activeStory.title}</span>
          </p>
          {onClearContext ? (
            <button
              type="button"
              onClick={onClearContext}
              className="text-caption shrink-0 text-accent hover:underline"
            >
              Clear
            </button>
          ) : null}
        </div>
      ) : null}

      <div className="flex flex-1 flex-col justify-end gap-3 overflow-y-auto px-4 py-4">
        <div className="max-w-[85%] self-start rounded-lg rounded-bl-sm bg-background px-3 py-2">
          <p className="text-caption text-foreground">
            {activeStory
              ? `Hi — I'm the Daily Signal assistant. Conversational answers about "${activeStory.title}" are coming in a later module.`
              : "Hi — I'm the Daily Signal assistant. Conversational answers over your edition are coming in a later module."}
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
