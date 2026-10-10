"use client";

import { Fragment, useEffect, useRef } from "react";

import { ChatComposer } from "@/components/chat/ChatComposer";
import { ChatMessageItem } from "@/components/chat/ChatMessageItem";
import { useChat } from "@/components/chat/ChatProvider";
import type { ChatUiMessage } from "@/types";

export const FULL_CHAT_INPUT_ID = "chat-input-full";

interface ChatWindowProps {
  variant: "compact" | "full";
  focusInputOnMount?: boolean;
}

function announcement(messages: ChatUiMessage[]): string {
  const last = messages[messages.length - 1];
  if (!last || last.role !== "assistant") return "";
  if (last.status === "error") return "Something went wrong. Try again.";
  if (last.status === "streaming") {
    return last.content ? "Daily Signal AI is responding." : "Daily Signal AI is thinking.";
  }
  return "Response complete.";
}

/**
 * The conversation itself — context bar, message log, suggestions and
 * composer. Rendered both in the compact bubble panel and on /chat; both
 * read the same provider state, so the conversation carries across.
 */
export function ChatWindow({ variant, focusInputOnMount = false }: ChatWindowProps) {
  const { messages, status, activeContext, isPinned, clearStoryContext, suggestions, sendMessage, retry } =
    useChat();

  const listRef = useRef<HTMLDivElement>(null);
  const stickToBottomRef = useRef(true);

  useEffect(() => {
    const el = listRef.current;
    if (el && stickToBottomRef.current) el.scrollTop = el.scrollHeight;
  }, [messages]);

  function handleScroll() {
    const el = listRef.current;
    if (!el) return;
    stickToBottomRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
  }

  function handleSend(text: string) {
    stickToBottomRef.current = true;
    void sendMessage(text);
  }

  const lastErrorId = [...messages].reverse().find((m) => m.status === "error")?.id;

  // Mark where the conversation's context changes (e.g. the user moved from
  // a story to the homepage) so it's clear what each question was about.
  const contextChanges = new Map<string, string>();
  let previousLabel: string | null = null;
  for (const message of messages) {
    const label = message.role === "user" ? (message.context?.label ?? null) : null;
    if (label && label !== previousLabel) contextChanges.set(message.id, label);
    if (label) previousLabel = label;
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      {activeContext ? (
        <div className="flex items-start justify-between gap-2 border-b border-border bg-background px-4 py-2">
          <p className="text-caption">
            Discussing: <span className="text-foreground">{activeContext.label}</span>
          </p>
          {isPinned ? (
            <button
              type="button"
              onClick={clearStoryContext}
              className="text-caption shrink-0 text-accent hover:underline"
            >
              Clear
            </button>
          ) : null}
        </div>
      ) : null}

      <div
        ref={listRef}
        onScroll={handleScroll}
        role="log"
        aria-label="Conversation"
        aria-live="off"
        aria-busy={status === "streaming"}
        tabIndex={0}
        className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto px-4 py-4 focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-accent"
      >
        {messages.length === 0 ? (
          <div className="flex flex-1 flex-col justify-end gap-3">
            <p className={variant === "compact" ? "text-sm text-muted" : "text-body text-muted"}>
              {activeContext
                ? `Ask anything about “${activeContext.label}”. I'll use it as context automatically.`
                : "Ask about today's stories, a topic, or research you're following."}
            </p>
            <div className="flex flex-wrap gap-2" role="group" aria-label="Suggested questions">
              {suggestions.map((question) => (
                <button
                  key={question}
                  type="button"
                  onClick={() => handleSend(question)}
                  className="text-caption rounded-full border border-border px-3 py-1.5 text-left text-foreground transition-colors hover:border-border-strong hover:bg-background"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        ) : null}

        {messages.map((message) => {
          const divider = contextChanges.get(message.id);
          return (
            <Fragment key={message.id}>
              {divider ? (
                <p className="text-caption border-t border-border pt-2 text-center">
                  Now discussing: {divider}
                </p>
              ) : null}
              <ChatMessageItem
                message={message}
                variant={variant}
                onRetry={message.id === lastErrorId && status === "idle" ? retry : undefined}
              />
            </Fragment>
          );
        })}
      </div>

      <div role="status" aria-live="polite" className="sr-only">
        {announcement(messages)}
      </div>

      <ChatComposer
        onSend={handleSend}
        busy={status === "streaming"}
        inputId={variant === "full" ? FULL_CHAT_INPUT_ID : undefined}
        focusOnMount={focusInputOnMount}
      />
    </div>
  );
}
