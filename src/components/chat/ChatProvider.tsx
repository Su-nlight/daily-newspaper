"use client";

import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

import type { ChatStoryContext } from "@/types";

interface ChatContextValue {
  isOpen: boolean;
  activeStory: ChatStoryContext | null;
  /** Opens the chat panel. Pass a story to pin it as the active context. */
  openChat: (story?: ChatStoryContext) => void;
  closeChat: () => void;
  clearStoryContext: () => void;
}

const ChatContext = createContext<ChatContextValue | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeStory, setActiveStory] = useState<ChatStoryContext | null>(null);

  const value = useMemo<ChatContextValue>(
    () => ({
      isOpen,
      activeStory,
      openChat: (story) => {
        if (story) setActiveStory(story);
        setIsOpen(true);
      },
      closeChat: () => setIsOpen(false),
      clearStoryContext: () => setActiveStory(null),
    }),
    [isOpen, activeStory],
  );

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat(): ChatContextValue {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
}
