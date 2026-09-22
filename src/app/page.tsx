import Link from "next/link";

import { getTodayEdition } from "@/lib/api/client";
import { siteConfig } from "@/lib/constants/site";
import { formatDisplayDate } from "@/lib/utils/date";

export default async function Home() {
  const edition = await getTodayEdition();

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-4 py-8 sm:px-6 lg:px-8">
      <header className="space-y-3">
        <p className="text-sm font-medium uppercase tracking-wide text-zinc-600 dark:text-zinc-400">
          {formatDisplayDate(edition.date)} Edition
        </p>
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">{siteConfig.name}</h1>
        <p className="max-w-3xl text-base text-zinc-700 dark:text-zinc-300">{edition.summary}</p>
      </header>

      <section className="grid gap-4 sm:grid-cols-2">
        {edition.stories.map((story) => (
          <article
            key={story.id}
            className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950"
          >
            <p className="text-xs font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
              {story.category}
            </p>
            <h2 className="mt-2 text-lg font-semibold">{story.title}</h2>
            <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-300">{story.summary}</p>
            <Link
              href={`/story/${story.id}`}
              className="mt-3 inline-block text-sm font-medium text-blue-600 hover:underline dark:text-blue-400"
            >
              Read placeholder story page
            </Link>
          </article>
        ))}
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Route foundation</h2>
        <ul className="grid gap-2 sm:grid-cols-2">
          {siteConfig.routes.map((route) => (
            <li key={route} className="rounded border border-zinc-200 px-3 py-2 dark:border-zinc-800">
              {route}
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
