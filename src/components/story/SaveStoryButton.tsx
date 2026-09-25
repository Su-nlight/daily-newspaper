"use client";

import { useState } from "react";

import { recordSignal } from "@/lib/analytics/signals";

interface SaveStoryButtonProps {
  storyId: string;
  title: string;
}

export function SaveStoryButton({ storyId, title }: SaveStoryButtonProps) {
  const [saved, setSaved] = useState(false);

  function handleClick() {
    setSaved((prev) => {
      const next = !prev;
      if (next) recordSignal("article_saved", { storyId, title });
      return next;
    });
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      aria-pressed={saved}
      className="text-metadata flex items-center gap-1.5 border border-border-strong px-3 py-1.5 text-foreground transition-colors hover:bg-background-elevated"
    >
      <span aria-hidden="true">{saved ? "★" : "☆"}</span>
      {saved ? "Saved" : "Save"}
    </button>
  );
}
