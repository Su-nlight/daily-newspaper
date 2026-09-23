import { formatCategoryLabel } from "@/lib/utils/category";
import { formatDisplayDate } from "@/lib/utils/date";
import type { Article } from "@/types";

interface StoryHeaderProps {
  story: Article;
}

export function StoryHeader({ story }: StoryHeaderProps) {
  return (
    <header className="space-y-3 border-b border-border pb-6">
      <p className="text-metadata text-accent">{formatCategoryLabel(story.category)}</p>
      <h1 className="text-headline">{story.title}</h1>
      <p className="text-subheadline text-muted">{story.dek ?? story.summary}</p>
      <p className="text-caption">
        {formatDisplayDate(story.publishedAt)} · {story.source}
      </p>
    </header>
  );
}
