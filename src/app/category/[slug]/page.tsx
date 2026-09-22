import Link from "next/link";

import { getCategory } from "@/lib/api/client";

export default async function CategoryPage({ params }: PageProps<"/category/[slug]">) {
  const { slug } = await params;
  const { category, stories } = await getCategory(slug);

  return (
    <main className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">{category?.name ?? "Category"}</h1>
        <p className="text-zinc-700 dark:text-zinc-300">
          {category?.description ?? "Category placeholder route for upcoming modules."}
        </p>
      </header>
      <ul className="space-y-3">
        {stories.map((story) => (
          <li key={story.id} className="rounded border border-zinc-200 p-4 dark:border-zinc-800">
            <h2 className="font-semibold">{story.title}</h2>
            <p className="text-sm text-zinc-600 dark:text-zinc-400">{story.summary}</p>
            <Link
              href={`/story/${story.id}`}
              className="mt-2 inline-block text-sm font-medium text-blue-600 hover:underline dark:text-blue-400"
            >
              Open story placeholder
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
