import type { ChatSource } from "@/types";

interface ChatSourcesProps {
  sources: ChatSource[];
  messageId: string;
}

export function ChatSources({ sources, messageId }: ChatSourcesProps) {
  if (sources.length === 0) return null;

  return (
    <div className="mt-3 border-t border-border pt-2">
      <p className="text-metadata">Sources</p>
      <ul className="mt-1.5 flex flex-col gap-1">
        {sources.map((source, position) => {
          const number = source.index ?? position + 1;
          return (
            <li
              key={`${source.url}-${number}`}
              id={`source-${messageId}-${number}`}
              className="text-caption flex gap-2 scroll-mt-2"
            >
              <span className="shrink-0 text-muted">[{number}]</span>
              <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-accent hover:underline"
              >
                {source.publisher}
                {source.title ? ` — ${source.title}` : ""}
                <span className="sr-only"> (opens in a new tab)</span>
              </a>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
