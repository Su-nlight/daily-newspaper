"use client";

import { useEffect } from "react";

import { useChat } from "@/components/chat/ChatProvider";
import type { ChatPageContext } from "@/types";

/**
 * Render one of these on a page to tell the chat what the page shows (the
 * story being read, today's edition, a category, the current search
 * results). It registers on mount and clears on unmount, so the chat always
 * knows where the user is without them pasting anything.
 */
export function ChatPageContextSetter({ context }: { context: ChatPageContext }) {
  const { registerPageContext } = useChat();
  // Key on the serialized value: server pages build a fresh object every
  // render, which would otherwise re-register on every navigation tick.
  const key = JSON.stringify(context);

  useEffect(() => {
    registerPageContext(JSON.parse(key) as ChatPageContext);
    return () => registerPageContext(null);
  }, [key, registerPageContext]);

  return null;
}
