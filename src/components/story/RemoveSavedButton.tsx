"use client";

import { useTransition } from "react";

import { removeSavedStoryAction } from "@/lib/actions/saved-stories";

interface RemoveSavedButtonProps {
  storyId: string;
}

export function RemoveSavedButton({ storyId }: RemoveSavedButtonProps) {
  const [isPending, startTransition] = useTransition();

  return (
    <button
      type="button"
      disabled={isPending}
      onClick={() => startTransition(() => removeSavedStoryAction(storyId))}
      className="text-metadata flex items-center gap-1.5 border border-border-strong px-3 py-1.5 text-foreground transition-colors hover:bg-background-elevated disabled:opacity-60"
    >
      Remove
    </button>
  );
}
