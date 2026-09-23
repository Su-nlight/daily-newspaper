import Link from "next/link";

import { StoryImagePlaceholder } from "@/components/story/StoryImagePlaceholder";
import type { Article } from "@/types";
import { formatCategoryLabel } from "@/lib/utils/category";
import { formatDisplayDate } from "@/lib/utils/date";

interface HeroStoryProps {
  story: Article;
}

export function HeroStory({ story }: HeroStoryProps) {
  return (
    <article className="grid gap-6 lg:grid-cols-[1.1fr_1fr] lg:items-center lg:gap-10">
      <div className="order-2 flex flex-col gap-4 lg:order-1">
        <p className="text-metadata text-accent">{formatCategoryLabel(story.category)}</p>
        <h2 className="text-display">
          <Link href={`/story/${story.id}`} className="hover:underline">
            {story.title}
          </Link>
        </h2>
        <p className="text-body max-w-xl text-muted">{story.summary}</p>
        <p className="text-caption">
          {story.source} · {formatDisplayDate(story.publishedAt)}
        </p>
        <Link
          href={`/story/${story.id}`}
          className="text-metadata mt-1 inline-flex w-fit items-center gap-2 border-b border-accent pb-0.5 text-accent"
        >
          Read story
          <span aria-hidden="true">→</span>
        </Link>
      </div>

      <div className="order-1 lg:order-2">
        <StoryImagePlaceholder category={formatCategoryLabel(story.category)} size="hero" />
      </div>
    </article>
  );
}
