import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";

import { linkifyCitations } from "@/lib/utils/citations";

interface ChatMarkdownProps {
  content: string;
  /** Used to point inline [n] markers at the matching entry in this message's source list. */
  messageId: string;
}

/**
 * Renders an AI answer: Markdown (lists, links, code blocks, tables) with
 * inline [n] citations as small superscript links to the sources below.
 * react-markdown never renders raw HTML, and unsafe link protocols are
 * stripped by its default URL transform, so model output can't inject markup.
 */
export function ChatMarkdown({ content, messageId }: ChatMarkdownProps) {
  const components: Components = {
    a: ({ href, children }) => {
      if (href?.startsWith("#cite-")) {
        const n = href.slice("#cite-".length);
        return (
          <sup>
            <a
              href={`#source-${messageId}-${n}`}
              aria-label={`Source ${n}`}
              className="text-accent hover:underline"
            >
              [{n}]
            </a>
          </sup>
        );
      }
      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-accent underline underline-offset-2"
        >
          {children}
        </a>
      );
    },
    p: ({ children }) => <p className="[&:not(:first-child)]:mt-2">{children}</p>,
    ul: ({ children }) => <ul className="mt-2 list-disc space-y-1 pl-5">{children}</ul>,
    ol: ({ children }) => <ol className="mt-2 list-decimal space-y-1 pl-5">{children}</ol>,
    li: ({ children }) => <li>{children}</li>,
    strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
    blockquote: ({ children }) => (
      <blockquote className="mt-2 border-l-2 border-border-strong pl-3 text-muted">
        {children}
      </blockquote>
    ),
    h1: ({ children }) => <p className="mt-3 font-semibold">{children}</p>,
    h2: ({ children }) => <p className="mt-3 font-semibold">{children}</p>,
    h3: ({ children }) => <p className="mt-3 font-semibold">{children}</p>,
    h4: ({ children }) => <p className="mt-3 font-semibold">{children}</p>,
    hr: () => <hr className="my-3 border-border" />,
    pre: ({ children }) => (
      <pre className="mt-2 overflow-x-auto rounded-md border border-border bg-background p-3 font-mono text-[0.8125rem] leading-relaxed [&_code]:bg-transparent [&_code]:p-0">
        {children}
      </pre>
    ),
    code: ({ children }) => (
      <code className="rounded bg-background px-1 py-0.5 font-mono text-[0.85em]">{children}</code>
    ),
    table: ({ children }) => (
      <div className="mt-2 overflow-x-auto">
        <table className="w-full border-collapse text-left">{children}</table>
      </div>
    ),
    th: ({ children }) => (
      <th className="border-b border-border-strong px-2 py-1 font-semibold">{children}</th>
    ),
    td: ({ children }) => <td className="border-b border-border px-2 py-1">{children}</td>,
  };

  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {linkifyCitations(content)}
    </ReactMarkdown>
  );
}
