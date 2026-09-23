import Link from "next/link";

import type { StoryDetail } from "@/types";
import { formatCategoryLabel } from "@/lib/utils/category";
import { formatDisplayDateTime } from "@/lib/utils/date";

interface StoryHeaderProps {
  story: StoryDetail;
}

export function StoryHeader({ story }: StoryHeaderProps) {
  return (
    <div className="flex flex-col gap-5">
      <Link href="/" className="text-caption inline-flex w-fit items-center gap-1.5 text-accent hover:underline">
        <span aria-hidden="true">←</span>
        Back to today&apos;s edition
      </Link>

      <div className="flex flex-col gap-3">
        <Link
          href={`/category/${story.category}`}
          className="text-metadata w-fit text-accent hover:underline"
        >
          {formatCategoryLabel(story.category)}
        </Link>
        <h1 className="text-display">{story.title}</h1>
        <p className="text-subheadline text-muted">{story.dek}</p>
        <p className="text-caption">
          {formatDisplayDateTime(story.publishedAt)} · {story.source}
        </p>
      </div>
    </div>
  );
}
