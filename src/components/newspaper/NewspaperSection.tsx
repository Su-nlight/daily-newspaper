import Link from "next/link";

import { SectionHeading } from "@/components/layout/SectionHeading";
import { CompactStory } from "@/components/story/CompactStory";
import { HorizontalStory } from "@/components/story/HorizontalStory";
import { StandardStory } from "@/components/story/StandardStory";
import type { Article } from "@/types";

export type NewspaperSectionLayout = "grid" | "list" | "compact";

interface NewspaperSectionProps {
  title: string;
  description?: string;
  stories: Article[];
  layout?: NewspaperSectionLayout;
  /** Optional link to a full category page, shown as a section-level action. */
  href?: string;
}

export function NewspaperSection({
  title,
  description,
  stories,
  layout = "grid",
  href,
}: NewspaperSectionProps) {
  if (stories.length === 0) return null;

  return (
    <section className="flex flex-col gap-6">
      <SectionHeading
        title={title}
        description={description}
        action={
          href ? (
            <Link href={href} className="text-metadata text-accent hover:underline">
              View all →
            </Link>
          ) : undefined
        }
      />

      {layout === "grid" ? (
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {stories.map((story) => (
            <StandardStory key={story.id} story={story} />
          ))}
        </div>
      ) : null}

      {layout === "list" ? (
        <div className="flex flex-col divide-y divide-border">
          {stories.map((story) => (
            <HorizontalStory key={story.id} story={story} />
          ))}
        </div>
      ) : null}

      {layout === "compact" ? (
        <div className="grid divide-y divide-border sm:grid-cols-2 sm:divide-y-0 sm:gap-x-8">
          {stories.map((story) => (
            <CompactStory key={story.id} story={story} />
          ))}
        </div>
      ) : null}
    </section>
  );
}
