import { ChatMarkdown } from "@/components/chat/ChatMarkdown";
import { ChatSources } from "@/components/chat/ChatSources";
import type { ChatUiMessage } from "@/types";

interface ChatMessageItemProps {
  message: ChatUiMessage;
  variant: "compact" | "full";
  /** Only the latest failed answer offers a retry. */
  onRetry?: () => void;
}

function TypingIndicator() {
  return (
    <span className="inline-flex items-center gap-1 py-1" aria-hidden="true">
      {[0, 150, 300].map((delay) => (
        <span
          key={delay}
          className="size-1.5 animate-pulse rounded-full bg-muted motion-reduce:animate-none"
          style={{ animationDelay: `${delay}ms` }}
        />
      ))}
    </span>
  );
}

export function ChatMessageItem({ message, variant, onRetry }: ChatMessageItemProps) {
  const textSize = variant === "compact" ? "text-sm leading-relaxed" : "text-body";

  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <p
          className={`${textSize} max-w-[85%] whitespace-pre-wrap break-words rounded-lg rounded-br-sm bg-accent px-3 py-2 text-accent-foreground`}
        >
          <span className="sr-only">You: </span>
          {message.content}
        </p>
      </div>
    );
  }

  const isThinking = message.status === "streaming" && message.content === "";

  return (
    <div className="flex justify-start">
      <div className={`${textSize} min-w-0 max-w-full break-words text-foreground`}>
        <span className="sr-only">Daily Signal AI: </span>
        {isThinking ? <TypingIndicator /> : null}
        {message.content ? <ChatMarkdown content={message.content} messageId={message.id} /> : null}

        {message.status === "error" ? (
          <div className="mt-2 flex flex-col items-start gap-1.5">
            <p className="text-caption text-foreground">Something went wrong. Try again.</p>
            {message.errorDetail ? <p className="text-caption">{message.errorDetail}</p> : null}
            {onRetry ? (
              <button
                type="button"
                onClick={onRetry}
                className="text-metadata border border-border-strong px-3 py-1.5 text-accent transition-colors hover:bg-background"
              >
                Retry
              </button>
            ) : null}
          </div>
        ) : null}

        {message.status === "done" && message.sources ? (
          <ChatSources sources={message.sources} messageId={message.id} />
        ) : null}
      </div>
    </div>
  );
}
