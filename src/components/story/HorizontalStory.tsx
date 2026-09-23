import Link from "next/link";

import { StoryImagePlaceholder } from "@/components/story/StoryImagePlaceholder";
import type { Article } from "@/types";
import { formatCategoryLabel } from "@/lib/utils/category";
import { formatDisplayDate } from "@/lib/utils/date";

interface HorizontalStoryProps {
  story: Article;
}

export function HorizontalStory({ story }: HorizontalStoryProps) {
  return (
    <article className="grid grid-cols-[5rem_1fr] items-start gap-4 py-4 sm:grid-cols-[7rem_1fr]">
      <StoryImagePlaceholder category={formatCategoryLabel(story.category)} size="horizontal" />
      <div className="flex flex-col gap-1.5">
        <p className="text-metadata text-accent">{formatCategoryLabel(story.category)}</p>
        <h4 className="text-subheadline">
          <Link href={`/story/${story.id}`} className="hover:underline">
            {story.title}
          </Link>
        </h4>
        <p className="text-body hidden text-muted sm:block">{story.summary}</p>
        <p className="text-caption">
          {story.source} · {formatDisplayDate(story.publishedAt)}
        </p>
      </div>
    </article>
  );
}
