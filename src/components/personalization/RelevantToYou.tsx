import Link from "next/link";

import { SectionHeading } from "@/components/layout/SectionHeading";
import type { Article } from "@/types";
import { formatCategoryLabel } from "@/lib/utils/category";

interface RelevantToYouProps {
  stories: Article[];
}

export function RelevantToYou({ stories }: RelevantToYouProps) {
  if (stories.length === 0) return null;

  return (
    <section className="flex flex-col gap-6 border-t border-border pt-8">
      <SectionHeading
        eyebrow="For you"
        title="Relevant to You"
        description="Stories matched to your topics and reading history."
      />

      <div className="grid gap-6 sm:grid-cols-2">
        {stories.map((story) => (
          <article key={story.id} className="flex flex-col gap-2 border-l-2 border-accent/40 pl-4">
            <p className="text-metadata text-accent">{formatCategoryLabel(story.category)}</p>
            <h3 className="text-subheadline">
              <Link href={`/story/${story.id}`} className="hover:underline">
                {story.title}
              </Link>
            </h3>
            <p className="text-body text-muted">{story.summary}</p>
            {story.whyRelevant ? (
              <p className="text-caption italic">
                Why you&apos;re seeing this: {story.whyRelevant}
              </p>
            ) : null}
            {story.topics.length > 0 ? (
              <p className="text-caption">
                Matches your interests: {story.topics.join(" · ")}
              </p>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}
