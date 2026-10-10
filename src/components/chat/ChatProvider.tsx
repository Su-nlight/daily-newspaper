"use client";

import { usePathname } from "next/navigation";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

import { ChatRequestError, streamChatMessage, type ChatHistoryTurn } from "@/lib/api/chat";
import { getSuggestedQuestions } from "@/lib/chat/suggestions";
import type { ChatPageContext, ChatStoryContext, ChatUiMessage } from "@/types";

export const FULL_CHAT_PATH = "/chat";
const MAX_HISTORY_TURNS = 8;

export type ChatStatus = "idle" | "streaming";

interface ChatContextValue {
  /** Compact panel open state. Always false on the full-chat page. */
  isOpen: boolean;
  /** Opens the compact panel. Pass a story to pin it as the conversation's context. */
  openChat: (story?: ChatStoryContext) => void;
  closeChat: () => void;

  conversationId: string | null;
  messages: ChatUiMessage[];
  status: ChatStatus;
  /** What the next question will be asked about: a pinned story, else the current page. */
  activeContext: ChatPageContext | null;
  /** True when activeContext is a story pinned via "Ask AI" (and can be cleared). */
  isPinned: boolean;
  suggestions: string[];

  sendMessage: (text: string) => Promise<void>;
  /** Re-sends the question behind the most recent failed answer. */
  retry: () => void;
  resetConversation: () => void;
  clearStoryContext: () => void;
  /** Called by pages (via ChatPageContextSetter) to say what they show. */
  registerPageContext: (context: ChatPageContext | null) => void;
}

const ChatContext = createContext<ChatContextValue | null>(null);

function newId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function storyToContext(story: ChatStoryContext): ChatPageContext {
  return { kind: "story", label: story.title, storyId: story.storyId };
}

function toHistory(messages: ChatUiMessage[]): ChatHistoryTurn[] {
  return messages
    .filter((message) => message.status === "done" && message.content.trim())
    .slice(-MAX_HISTORY_TURNS)
    .map((message) => ({ role: message.role, content: message.content }));
}

export function ChatProvider({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const onFullChat = pathname === FULL_CHAT_PATH;

  const [isOpen, setIsOpen] = useState(false);
  const [pinned, setPinned] = useState<{ story: ChatStoryContext; path: string } | null>(null);
  const [pageContext, setPageContext] = useState<ChatPageContext | null>(null);
  // The last context a content page registered. The full-chat page has none
  // of its own, so it continues with whatever the user was just looking at.
  const [lastContext, setLastContext] = useState<ChatPageContext | null>(null);
  const [messages, setMessages] = useState<ChatUiMessage[]>([]);
  const [status, setStatus] = useState<ChatStatus>("idle");
  const [conversationId, setConversationId] = useState<string | null>(null);

  const messagesRef = useRef<ChatUiMessage[]>([]);
  const statusRef = useRef<ChatStatus>("idle");
  const conversationIdRef = useRef<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  // A pinned story applies on the page it was pinned from, and on the full
  // chat page; elsewhere the page's own context takes over again.
  const pinnedContext =
    pinned && (pinned.path === pathname || onFullChat) ? storyToContext(pinned.story) : null;
  const activeContext = pinnedContext ?? pageContext ?? (onFullChat ? lastContext : null);

  const runRequest = useCallback(
    async (
      userMessage: ChatUiMessage,
      assistantId: string,
      history: ChatHistoryTurn[],
      id: string,
    ) => {
      const controller = new AbortController();
      abortRef.current = controller;
      statusRef.current = "streaming";
      setStatus("streaming");

      try {
        const result = await streamChatMessage({
          message: userMessage.content,
          conversationId: id,
          context: userMessage.context ?? null,
          history,
          signal: controller.signal,
          onToken: (text) =>
            setMessages((prev) =>
              prev.map((m) => (m.id === assistantId ? { ...m, content: m.content + text } : m)),
            ),
        });
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, status: "done", sources: result.sources } : m,
          ),
        );
      } catch (error) {
        if (controller.signal.aborted) return;
        const detail = error instanceof ChatRequestError ? error.message : undefined;
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, status: "error", errorDetail: detail } : m,
          ),
        );
      } finally {
        if (abortRef.current === controller) {
          abortRef.current = null;
          statusRef.current = "idle";
          setStatus("idle");
        }
      }
    },
    [],
  );

  const sendMessage = useCallback(
    async (text: string) => {
      const content = text.trim();
      if (!content || statusRef.current === "streaming") return;

      const id = conversationIdRef.current ?? newId();
      conversationIdRef.current = id;
      setConversationId(id);

      const history = toHistory(messagesRef.current);
      const now = new Date().toISOString();
      const userMessage: ChatUiMessage = {
        id: newId(),
        role: "user",
        content,
        status: "done",
        createdAt: now,
        context: activeContext,
      };
      const assistantId = newId();
      const assistantMessage: ChatUiMessage = {
        id: assistantId,
        role: "assistant",
        content: "",
        status: "streaming",
        createdAt: now,
      };

      statusRef.current = "streaming";
      setMessages((prev) => [...prev, userMessage, assistantMessage]);
      await runRequest(userMessage, assistantId, history, id);
    },
    [activeContext, runRequest],
  );

  const retry = useCallback(() => {
    if (statusRef.current === "streaming") return;

    const list = messagesRef.current;
    let errorIndex = -1;
    for (let i = list.length - 1; i >= 0; i--) {
      if (list[i].role === "assistant" && list[i].status === "error") {
        errorIndex = i;
        break;
      }
    }
    const userMessage = errorIndex > 0 ? list[errorIndex - 1] : undefined;
    if (!userMessage || userMessage.role !== "user") return;

    const id = conversationIdRef.current ?? newId();
    conversationIdRef.current = id;
    setConversationId(id);

    const assistantId = newId();
    const fresh: ChatUiMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
      status: "streaming",
      createdAt: new Date().toISOString(),
    };

    statusRef.current = "streaming";
    setMessages([...list.slice(0, errorIndex), fresh]);
    void runRequest(userMessage, assistantId, toHistory(list.slice(0, errorIndex - 1)), id);
  }, [runRequest]);

  const resetConversation = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    statusRef.current = "idle";
    conversationIdRef.current = null;
    messagesRef.current = [];
    setStatus("idle");
    setMessages([]);
    setConversationId(null);
  }, []);

  const openChat = useCallback(
    (story?: ChatStoryContext) => {
      if (story) setPinned({ story, path: pathname });
      if (pathname !== FULL_CHAT_PATH) setIsOpen(true);
    },
    [pathname],
  );

  const closeChat = useCallback(() => setIsOpen(false), []);
  const clearStoryContext = useCallback(() => setPinned(null), []);

  const registerPageContext = useCallback((context: ChatPageContext | null) => {
    setPageContext(context);
    if (context) setLastContext(context);
  }, []);

  const value = useMemo<ChatContextValue>(
    () => ({
      isOpen: isOpen && !onFullChat,
      openChat,
      closeChat,
      conversationId,
      messages,
      status,
      activeContext,
      isPinned: pinnedContext !== null,
      suggestions: getSuggestedQuestions(activeContext?.kind),
      sendMessage,
      retry,
      resetConversation,
      clearStoryContext,
      registerPageContext,
    }),
    [
      isOpen,
      onFullChat,
      openChat,
      closeChat,
      conversationId,
      messages,
      status,
      activeContext,
      pinnedContext,
      sendMessage,
      retry,
      resetConversation,
      clearStoryContext,
      registerPageContext,
    ],
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
