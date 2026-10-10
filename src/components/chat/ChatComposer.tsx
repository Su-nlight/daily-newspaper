"use client";

import { useEffect, useId, useRef, useState, type KeyboardEvent } from "react";

interface ChatComposerProps {
  onSend: (text: string) => void;
  /** Disables sending (not typing) while an answer is streaming. */
  busy: boolean;
  /** DOM id for the textarea, so other UI can focus it. */
  inputId?: string;
  focusOnMount?: boolean;
}

export function ChatComposer({ onSend, busy, inputId, focusOnMount = false }: ChatComposerProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const hintId = useId();

  useEffect(() => {
    if (focusOnMount) textareaRef.current?.focus();
  }, [focusOnMount]);

  // Grow with the content up to a cap, then scroll.
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [value]);

  function submit() {
    const text = value.trim();
    if (!text || busy) return;
    onSend(text);
    setValue("");
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    // Enter sends; Shift+Enter inserts a newline. Ignore Enter while an IME
    // composition is being confirmed.
    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault();
      submit();
    }
  }

  return (
    <div className="border-t border-border p-3">
      <div className="flex items-end gap-2 rounded-lg border border-border bg-background px-3 py-2 focus-within:border-accent">
        <textarea
          ref={textareaRef}
          id={inputId}
          rows={1}
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={handleKeyDown}
          aria-label="Message Daily Signal AI"
          aria-describedby={hintId}
          placeholder="Ask Daily Signal AI…"
          className="text-body max-h-40 w-full resize-none bg-transparent text-foreground placeholder:text-muted focus:outline-none"
        />
        <button
          type="button"
          onClick={submit}
          disabled={busy || !value.trim()}
          aria-label="Send message"
          className="flex size-8 shrink-0 items-center justify-center rounded-full bg-accent text-accent-foreground transition-opacity disabled:opacity-40"
        >
          <svg
            aria-hidden="true"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            className="size-4"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 19V5M5 12l7-7 7 7" />
          </svg>
        </button>
      </div>
      <p id={hintId} className="text-caption mt-1.5 px-1">
        Enter to send · Shift+Enter for a new line
      </p>
    </div>
  );
}
