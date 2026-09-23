import Link from "next/link";

import type { TrendingTopic } from "@/types";

interface TrendingTopicsProps {
  topics: TrendingTopic[];
}

export function TrendingTopics({ topics }: TrendingTopicsProps) {
  if (topics.length === 0) return null;

  return (
    <section className="border-t border-border pt-6">
      <h2 className="text-section-title mb-3 text-accent">Trending Topics</h2>
      <ul className="flex flex-wrap gap-2">
        {topics.map((topic) => (
          <li key={topic.name}>
            <Link
              href="/topics"
              className="text-metadata flex items-center gap-1.5 rounded-full border border-border px-3 py-1.5 text-foreground transition-colors hover:border-border-strong hover:bg-background-elevated"
            >
              {topic.name}
              <span className="text-muted">{topic.count}</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
