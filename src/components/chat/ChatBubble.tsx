"use client";

import { usePathname } from "next/navigation";
import { useEffect, useId, useRef } from "react";

import { ChatPanelShell } from "@/components/chat/ChatPanelShell";
import { FULL_CHAT_PATH, useChat } from "@/components/chat/ChatProvider";
import { FULL_CHAT_INPUT_ID } from "@/components/chat/ChatWindow";

export function ChatBubble() {
  const { isOpen, openChat, closeChat } = useChat();
  const pathname = usePathname();
  const onFullChat = pathname === FULL_CHAT_PATH;

  const buttonRef = useRef<HTMLButtonElement>(null);
  const wasOpenRef = useRef(false);
  const panelId = useId();

  // Give focus back to the bubble when the panel closes, so keyboard users
  // land where they started instead of at the top of the page.
  useEffect(() => {
    if (wasOpenRef.current && !isOpen) buttonRef.current?.focus();
    wasOpenRef.current = isOpen;
  }, [isOpen]);

  function handleClick() {
    if (onFullChat) {
      // The full chat is already on screen — just jump to its input.
      document.getElementById(FULL_CHAT_INPUT_ID)?.focus();
      return;
    }
    if (isOpen) closeChat();
    else openChat();
  }

  return (
    <div className="fixed bottom-5 left-5 z-50 flex flex-col items-start gap-3">
      {isOpen ? <ChatPanelShell id={panelId} /> : null}

      <div className="group relative">
        {!isOpen ? (
          <span
            className="text-caption pointer-events-none absolute bottom-1/2 left-full ml-3 translate-y-1/2 whitespace-nowrap rounded-full border border-border bg-background-elevated px-3 py-1.5 opacity-0 shadow-sm transition-opacity duration-150 group-hover:opacity-100 group-focus-within:opacity-100"
            aria-hidden="true"
          >
            Ask Daily Signal AI
          </span>
        ) : null}
        <button
          ref={buttonRef}
          type="button"
          onClick={handleClick}
          aria-label={isOpen ? "Close Daily Signal AI chat" : "Ask Daily Signal AI"}
          aria-expanded={onFullChat ? undefined : isOpen}
          aria-controls={isOpen ? panelId : undefined}
          className="flex size-13 items-center justify-center rounded-full border border-border bg-accent text-accent-foreground shadow-lg transition-transform hover:scale-105"
        >
          {isOpen ? (
            <svg
              aria-hidden="true"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.7"
              className="size-5"
            >
              <path strokeLinecap="round" d="M6 6l12 12M18 6L6 18" />
            </svg>
          ) : (
            <svg
              aria-hidden="true"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.7"
              className="size-5"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4 5.5h16a1 1 0 0 1 1 1V15a1 1 0 0 1-1 1H9l-4 4v-4H4a1 1 0 0 1-1-1V6.5a1 1 0 0 1 1-1Z"
              />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}
