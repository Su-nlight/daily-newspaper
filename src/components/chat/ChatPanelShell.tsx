"use client";

import Link from "next/link";
import type { KeyboardEvent } from "react";

import { ChatWindow } from "@/components/chat/ChatWindow";
import { FULL_CHAT_PATH, useChat } from "@/components/chat/ChatProvider";

interface ChatPanelShellProps {
  id?: string;
}

const headerButton =
  "text-caption flex h-7 items-center justify-center rounded-full border border-border px-2.5 text-foreground transition-colors hover:border-border-strong";

/** The compact chat panel opened from the bubble: header, conversation, input. */
export function ChatPanelShell({ id }: ChatPanelShellProps) {
  const { closeChat, messages, resetConversation } = useChat();

  function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Escape") {
      event.stopPropagation();
      closeChat();
    }
  }

  return (
    <div
      id={id}
      role="dialog"
      aria-label="Daily Signal AI assistant"
      onKeyDown={handleKeyDown}
      className="flex h-[34rem] max-h-[calc(100dvh-7rem)] w-[26rem] max-w-[calc(100vw-2.5rem)] flex-col overflow-hidden rounded-lg border border-border bg-background-elevated shadow-xl"
    >
      <div className="flex items-center justify-between gap-2 border-b border-border px-4 py-3">
        <div className="min-w-0">
          <p className="text-section-title text-accent">Daily Signal AI</p>
        </div>
        <div className="flex shrink-0 items-center gap-1.5">
          {messages.length > 0 ? (
            <button type="button" onClick={resetConversation} className={headerButton}>
              New chat
            </button>
          ) : null}
          <Link href={FULL_CHAT_PATH} onClick={closeChat} className={headerButton}>
            Open full chat
          </Link>
          <button
            type="button"
            onClick={closeChat}
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
      </div>

      <ChatWindow variant="compact" focusInputOnMount />
    </div>
  );
}
