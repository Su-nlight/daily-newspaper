import type { StoryCitation } from "@/types";
import { formatDisplayDate } from "@/lib/utils/date";

interface SourceListProps {
  citations: StoryCitation[];
}

export function SourceList({ citations }: SourceListProps) {
  if (citations.length === 0) return null;

  return (
    <section className="border-t border-border pt-6">
      <h2 className="text-section-title mb-3 text-accent">Sources</h2>
      <ul className="flex flex-col divide-y divide-border">
        {citations.map((citation) => (
          <li
            key={citation.url}
            className="flex flex-col gap-1 py-3 first:pt-0 sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <p className="text-body font-medium text-foreground">{citation.publisher}</p>
              <p className="text-caption">{formatDisplayDate(citation.publishedAt)}</p>
            </div>
            <a
              href={citation.url}
              target="_blank"
              rel="noreferrer noopener"
              className="text-metadata w-fit text-accent hover:underline"
            >
              View source →
            </a>
          </li>
        ))}
      </ul>
    </section>
  );
}
