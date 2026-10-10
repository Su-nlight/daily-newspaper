"use client";

import { ChatWindow } from "@/components/chat/ChatWindow";
import { useChat } from "@/components/chat/ChatProvider";

/** The /chat page body: the same conversation as the bubble, in a larger layout. */
export function FullChat() {
  const { messages, resetConversation } = useChat();

  return (
    <section
      aria-label="Daily Signal AI conversation"
      className="flex h-[calc(100dvh-14rem)] min-h-[28rem] flex-col overflow-hidden rounded-lg border border-border bg-background-elevated"
    >
      <div className="flex items-center justify-between gap-3 border-b border-border px-4 py-3">
        <p className="text-section-title text-accent">Daily Signal AI</p>
        {messages.length > 0 ? (
          <button
            type="button"
            onClick={resetConversation}
            className="text-caption flex h-7 items-center rounded-full border border-border px-2.5 text-foreground transition-colors hover:border-border-strong"
          >
            New conversation
          </button>
        ) : null}
      </div>
      <ChatWindow variant="full" />
    </section>
  );
}
