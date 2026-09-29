import Link from "next/link";

import { AskAboutStory } from "@/components/story/AskAboutStory";
import { RemoveSavedButton } from "@/components/story/RemoveSavedButton";
import type { SavedStoryWithArticle } from "@/types";
import { formatCategoryLabel } from "@/lib/utils/category";
import { formatDisplayDate } from "@/lib/utils/date";

interface SavedStoryCardProps {
  entry: SavedStoryWithArticle;
}

export function SavedStoryCard({ entry }: SavedStoryCardProps) {
  const { saved, article } = entry;

  return (
    <article className="flex flex-col gap-3 border-b border-border py-6 first:pt-0 last:border-b-0">
      <div className="flex flex-col gap-1.5">
        <p className="text-metadata text-accent">{formatCategoryLabel(article.category)}</p>
        <h3 className="text-subheadline">
          <Link href={`/story/${article.id}`} className="hover:underline">
            {article.title}
          </Link>
        </h3>
        <p className="text-caption">
          {article.source} · Published {formatDisplayDate(article.publishedAt)} · Saved{" "}
          {formatDisplayDate(saved.savedAt)}
        </p>
      </div>

      <div className="flex flex-wrap gap-3">
        <Link
          href={`/story/${article.id}`}
          className="text-metadata flex items-center gap-1.5 border border-border-strong px-3 py-1.5 text-foreground transition-colors hover:bg-background-elevated"
        >
          Open
        </Link>
        <AskAboutStory
          story={{ id: article.id, title: article.title, context: article.summary }}
          compact
        />
        <RemoveSavedButton storyId={article.id} />
      </div>
    </article>
  );
}
