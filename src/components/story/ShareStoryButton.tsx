"use client";

import { useState } from "react";

import { recordSignal } from "@/lib/analytics/signals";

interface ShareStoryButtonProps {
  storyId: string;
  title: string;
}

export function ShareStoryButton({ storyId, title }: ShareStoryButtonProps) {
  const [copied, setCopied] = useState(false);

  async function handleClick() {
    recordSignal("article_shared", { storyId, title });

    const url = window.location.href;

    if (navigator.share) {
      try {
        await navigator.share({ title, url });
        return;
      } catch {
        // User cancelled the native share sheet, or it failed — fall
        // through to the clipboard fallback below.
      }
    }

    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API unavailable — button remains harmless.
    }
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className="text-metadata flex items-center gap-1.5 border border-border-strong px-3 py-1.5 text-foreground transition-colors hover:bg-background-elevated"
    >
      <span aria-hidden="true">↗</span>
      {copied ? "Link copied" : "Share"}
    </button>
  );
}
