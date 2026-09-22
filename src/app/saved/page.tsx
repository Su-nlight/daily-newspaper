import { getSavedStories } from "@/lib/api/client";

export default async function SavedPage() {
  const savedStories = await getSavedStories();

  return (
    <main className="mx-auto flex w-full max-w-4xl flex-col gap-4 px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold tracking-tight">Saved Stories</h1>
      <p className="text-zinc-700 dark:text-zinc-300">Placeholder route for saved stories management.</p>
      <p className="text-sm text-zinc-600 dark:text-zinc-400">Mock saved stories: {savedStories.length}</p>
    </main>
  );
}
