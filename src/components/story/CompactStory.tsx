import Link from "next/link";

import type { Article } from "@/types";
import { formatCategoryLabel } from "@/lib/utils/category";

interface CompactStoryProps {
  story: Article;
}

export function CompactStory({ story }: CompactStoryProps) {
  return (
    <article className="flex flex-col gap-1 py-3">
      <p className="text-metadata text-accent">{formatCategoryLabel(story.category)}</p>
      <h4 className="text-body font-medium">
        <Link href={`/story/${story.id}`} className="hover:underline">
          {story.title}
        </Link>
      </h4>
    </article>
  );
}
