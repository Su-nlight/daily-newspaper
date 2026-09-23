"use client";

import { createContext, useCallback, useContext, useMemo, useState } from "react";

import type { StoryChatContext } from "@/types";

interface ChatUiState {
  isOpen: boolean;
  activeStoryContext: StoryChatContext | null;
  openChat: (storyContext?: StoryChatContext) => void;
  closeChat: () => void;
}

const ChatUiContext = createContext<ChatUiState | null>(null);

export function ChatUiProvider({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeStoryContext, setActiveStoryContext] = useState<StoryChatContext | null>(null);

  const openChat = useCallback((storyContext?: StoryChatContext) => {
    if (storyContext) {
      setActiveStoryContext(storyContext);
    }
    setIsOpen(true);
  }, []);

  const closeChat = useCallback(() => {
    setIsOpen(false);
  }, []);

  const value = useMemo(
    () => ({
      isOpen,
      activeStoryContext,
      openChat,
      closeChat,
    }),
    [activeStoryContext, closeChat, isOpen, openChat],
  );

  return <ChatUiContext.Provider value={value}>{children}</ChatUiContext.Provider>;
}

export function useChatUiState(): ChatUiState {
  const context = useContext(ChatUiContext);

  if (!context) {
    throw new Error("useChatUiState must be used within ChatUiProvider.");
  }

  return context;
}
