import Link from "next/link";
import { notFound } from "next/navigation";

import { PageContainer } from "@/components/layout/PageContainer";
import { getStory } from "@/lib/api/client";
import { formatDisplayDate } from "@/lib/utils/date";

export default async function StoryPage({ params }: PageProps<"/story/[id]">) {
  const { id } = await params;
  const story = await getStory(id);

  if (!story) {
    notFound();
  }

  return (
    <PageContainer narrow>
      <div className="space-y-4">
        <p className="text-metadata text-accent">
          {story.category} · {formatDisplayDate(story.publishedAt)}
        </p>
        <h1 className="text-headline">{story.title}</h1>
        <p className="text-body text-muted">{story.summary}</p>
        <p className="text-caption">
          Source:{" "}
          <a href={story.sourceUrl} className="text-accent hover:underline">
            {story.source}
          </a>
        </p>
      </div>

      <Link href="/" className="text-caption text-accent hover:underline">
        ← Back to today&apos;s edition
      </Link>
    </PageContainer>
  );
}
