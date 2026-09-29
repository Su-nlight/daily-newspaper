import Link from "next/link";
import { notFound } from "next/navigation";

import { PageContainer } from "@/components/layout/PageContainer";
import { HeroStory } from "@/components/newspaper/HeroStory";
import { NewspaperSection } from "@/components/newspaper/NewspaperSection";
import { getEditionByDate } from "@/lib/api/client";
import { formatCategoryLabel } from "@/lib/utils/category";
import { formatDisplayDate } from "@/lib/utils/date";
import { estimateReadingTime } from "@/lib/utils/reading-time";

export default async function EditionArchivePage({ params }: PageProps<"/archive/[date]">) {
  const { date } = await params;
  const edition = await getEditionByDate(date);

  if (!edition) {
    notFound();
  }

  const [featuredStory, ...restStories] = edition.stories;
  const readingTime = estimateReadingTime(edition.stories);
  const sections = [...new Set(edition.stories.map((story) => story.category))];

  return (
    <PageContainer>
      <div className="flex flex-col gap-4 border-b border-border pb-8">
        <Link href="/archive" className="text-caption inline-flex w-fit items-center gap-1.5 text-accent hover:underline">
          <span aria-hidden="true">←</span>
          Back to archive
        </Link>
        <div className="flex flex-col gap-2">
          <p className="text-metadata">{formatDisplayDate(edition.date)}</p>
          <h1 className="text-headline">{edition.headline}</h1>
          <p className="text-body max-w-2xl text-muted">{edition.summary}</p>
        </div>
        <div className="flex flex-wrap items-center gap-4">
          <span className="text-caption">
            {edition.stories.length} {edition.stories.length === 1 ? "story" : "stories"} ·{" "}
            {readingTime} min read
          </span>
          {sections.length > 0 ? (
            <span className="flex flex-wrap gap-2">
              {sections.map((slug) => (
                <Link
                  key={slug}
                  href={`/category/${slug}`}
                  className="text-metadata border border-border px-2.5 py-1 text-foreground transition-colors hover:border-border-strong hover:bg-background-elevated"
                >
                  {formatCategoryLabel(slug)}
                </Link>
              ))}
            </span>
          ) : null}
        </div>
      </div>

      {featuredStory ? <HeroStory story={featuredStory} /> : null}

      <NewspaperSection title="Also in this edition" stories={restStories} layout="grid" />
    </PageContainer>
  );
}
