"use client";

import { useEffect, useRef } from "react";

import { recordSignal } from "@/lib/analytics/signals";

interface ArticleCompletionTrackerProps {
  storyId: string;
  title: string;
}

/**
 * Invisible sentinel placed near the bottom of a story. Fires
 * `article_completed` once, the first time it scrolls into view — a
 * lightweight stand-in for "the reader reached the end of the article."
 */
export function ArticleCompletionTracker({ storyId, title }: ArticleCompletionTrackerProps) {
  const sentinelRef = useRef<HTMLDivElement>(null);
  const firedRef = useRef(false);

  useEffect(() => {
    const node = sentinelRef.current;
    if (!node || typeof IntersectionObserver === "undefined") return;

    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (entry?.isIntersecting && !firedRef.current) {
          firedRef.current = true;
          recordSignal("article_completed", { storyId, title });
        }
      },
      { threshold: 0.5 },
    );

    observer.observe(node);
    return () => observer.disconnect();
  }, [storyId, title]);

  return <div ref={sentinelRef} aria-hidden="true" className="h-px" />;
}
