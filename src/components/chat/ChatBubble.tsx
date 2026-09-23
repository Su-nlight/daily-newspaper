"use client";

import { useState } from "react";

import { ChatPanelShell } from "@/components/chat/ChatPanelShell";

export function ChatBubble() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="fixed bottom-5 left-5 z-50 flex flex-col items-start gap-3">
      {isOpen ? <ChatPanelShell onClose={() => setIsOpen(false)} /> : null}

      {!isOpen ? (
        <div className="group relative">
          <span
            className="text-caption pointer-events-none absolute bottom-1/2 left-full ml-3 translate-y-1/2 whitespace-nowrap rounded-full border border-border bg-background-elevated px-3 py-1.5 opacity-0 shadow-sm transition-opacity duration-150 group-hover:opacity-100"
            role="tooltip"
          >
            Ask Daily Signal AI
          </span>
          <button
            type="button"
            onClick={() => setIsOpen(true)}
            aria-label="Ask Daily Signal AI"
            className="flex size-13 items-center justify-center rounded-full border border-border bg-accent text-accent-foreground shadow-lg transition-transform hover:scale-105"
          >
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
          </button>
        </div>
      ) : null}
    </div>
  );
}
