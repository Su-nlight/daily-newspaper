"use client";

import { useEffect } from "react";

import { PageContainer } from "@/components/layout/PageContainer";

export default function StoryError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Story page failed to load:", error);
  }, [error]);

  return (
    <PageContainer narrow>
      <div className="flex flex-col items-center gap-4 border border-dashed border-border-strong px-6 py-20 text-center">
        <p className="text-headline">This story couldn&apos;t be loaded.</p>
        <p className="text-body max-w-md text-muted">
          Something went wrong while fetching this story. This is usually temporary.
        </p>
        <button
          type="button"
          onClick={reset}
          className="text-metadata inline-flex w-fit items-center gap-2 border border-border-strong px-4 py-2 text-foreground transition-colors hover:bg-background-elevated"
        >
          Try again
        </button>
      </div>
    </PageContainer>
  );
}
