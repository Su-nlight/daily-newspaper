"use client";

import { useState, useTransition } from "react";

import { removeSavedStoryAction, saveStoryAction } from "@/lib/actions/saved-stories";
import { recordSignal } from "@/lib/analytics/signals";

interface SaveStoryButtonProps {
  storyId: string;
  title: string;
  initialSaved: boolean;
}

export function SaveStoryButton({ storyId, title, initialSaved }: SaveStoryButtonProps) {
  const [saved, setSaved] = useState(initialSaved);
  const [isPending, startTransition] = useTransition();

  function handleClick() {
    const next = !saved;
    setSaved(next); // optimistic

    startTransition(async () => {
      if (next) {
        await saveStoryAction(storyId);
        recordSignal("article_saved", { storyId, title });
      } else {
        await removeSavedStoryAction(storyId);
      }
    });
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={isPending}
      aria-pressed={saved}
      className="text-metadata flex items-center gap-1.5 border border-border-strong px-3 py-1.5 text-foreground transition-colors hover:bg-background-elevated disabled:opacity-60"
    >
      <span aria-hidden="true">{saved ? "★" : "☆"}</span>
      {saved ? "Saved" : "Save"}
    </button>
  );
}
