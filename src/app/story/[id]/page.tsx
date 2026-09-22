import Link from "next/link";
import { notFound } from "next/navigation";

import { getStory } from "@/lib/api/client";
import { formatDisplayDate } from "@/lib/utils/date";

export default async function StoryPage({ params }: PageProps<"/story/[id]">) {
  const { id } = await params;
  const story = await getStory(id);

  if (!story) {
    notFound();
  }

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-4 px-4 py-8 sm:px-6 lg:px-8">
      <p className="text-xs font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
        {story.category} • {formatDisplayDate(story.publishedAt)}
      </p>
      <h1 className="text-3xl font-bold tracking-tight">{story.title}</h1>
      <p className="text-base text-zinc-700 dark:text-zinc-300">{story.summary}</p>
      <p className="text-sm text-zinc-600 dark:text-zinc-400">
        Source: <a href={story.sourceUrl}>{story.source}</a>
      </p>
      <Link href="/" className="text-sm font-medium text-blue-600 hover:underline dark:text-blue-400">
        Back to today&apos;s edition
      </Link>
    </main>
  );
}
