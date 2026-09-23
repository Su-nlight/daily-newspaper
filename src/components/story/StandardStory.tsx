import Link from "next/link";

import { StoryImagePlaceholder } from "@/components/story/StoryImagePlaceholder";
import type { Article } from "@/types";
import { formatCategoryLabel } from "@/lib/utils/category";
import { formatDisplayDate } from "@/lib/utils/date";

interface StandardStoryProps {
  story: Article;
  /** Larger headline treatment for a section's lead item. */
  emphasized?: boolean;
}

export function StandardStory({ story, emphasized = false }: StandardStoryProps) {
  return (
    <article className="flex flex-col gap-3">
      <StoryImagePlaceholder category={formatCategoryLabel(story.category)} size="standard" />
      <div className="flex flex-col gap-2">
        <p className="text-metadata text-accent">{formatCategoryLabel(story.category)}</p>
        <h3 className={emphasized ? "text-headline" : "text-subheadline"}>
          <Link href={`/story/${story.id}`} className="hover:underline">
            {story.title}
          </Link>
        </h3>
        <p className="text-body text-muted">{story.summary}</p>
        <p className="text-caption">
          {story.source} · {formatDisplayDate(story.publishedAt)}
        </p>
      </div>
    </article>
  );
}
