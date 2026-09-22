import { getTopics } from "@/lib/api/client";

export default async function TopicsPage() {
  const topics = await getTopics();

  return (
    <main className="mx-auto flex w-full max-w-4xl flex-col gap-4 px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold tracking-tight">Topics</h1>
      <p className="text-zinc-700 dark:text-zinc-300">Placeholder topic discovery route.</p>
      <ul className="list-disc space-y-1 pl-6 text-sm text-zinc-600 dark:text-zinc-400">
        {topics.map((topic) => (
          <li key={topic.id}>{topic.name}</li>
        ))}
      </ul>
    </main>
  );
}
