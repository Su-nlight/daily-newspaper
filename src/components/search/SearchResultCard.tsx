import Link from "next/link";

import { SaveStoryButton } from "@/components/story/SaveStoryButton";
import type { Article } from "@/types";
import { formatCategoryLabel } from "@/lib/utils/category";
import { formatDisplayDate } from "@/lib/utils/date";

interface SearchResultCardProps {
  article: Article;
  initialSaved: boolean;
}

export function SearchResultCard({ article, initialSaved }: SearchResultCardProps) {
  return (
    <article className="flex flex-col gap-2 border-b border-border py-6 first:pt-0 last:border-b-0">
      <p className="text-metadata text-accent">{formatCategoryLabel(article.category)}</p>
      <h3 className="text-subheadline">
        <Link href={`/story/${article.id}`} className="hover:underline">
          {article.title}
        </Link>
      </h3>
      <p className="text-body text-muted">{article.summary}</p>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-caption">
          {article.source} · {formatDisplayDate(article.publishedAt)}
          {article.topics.length > 0 ? ` · ${article.topics.join(", ")}` : ""}
        </p>
        <SaveStoryButton storyId={article.id} title={article.title} initialSaved={initialSaved} />
      </div>
    </article>
  );
}
