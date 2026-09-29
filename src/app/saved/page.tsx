import Link from "next/link";

import { PageContainer } from "@/components/layout/PageContainer";
import { SectionHeading } from "@/components/layout/SectionHeading";
import { SavedStoryCard } from "@/components/story/SavedStoryCard";
import { getSavedStories } from "@/lib/api/client";

export default async function SavedPage() {
  const savedStories = await getSavedStories();

  return (
    <PageContainer narrow>
      <SectionHeading
        eyebrow="Library"
        title="Your Library"
        description="Stories you've saved to read later or revisit."
      />

      {savedStories.length === 0 ? (
        <div className="flex flex-col items-center gap-3 border border-dashed border-border-strong px-6 py-20 text-center">
          <p className="text-headline">Your reading list is empty.</p>
          <p className="text-body max-w-md text-muted">
            Open any story and select <span className="font-medium">Save</span> to add it here.
            Saved stories stay in your library until you remove them.
          </p>
          <Link
            href="/"
            className="text-metadata mt-2 inline-flex w-fit items-center gap-2 border border-border-strong px-4 py-2 text-foreground transition-colors hover:bg-background-elevated"
          >
            Browse today&apos;s edition
          </Link>
        </div>
      ) : (
        <div className="flex flex-col">
          {savedStories.map((entry) => (
            <SavedStoryCard key={entry.saved.id} entry={entry} />
          ))}
        </div>
      )}
    </PageContainer>
  );
}
