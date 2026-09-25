"use client";

import { useEffect } from "react";

import { recordSignal } from "@/lib/analytics/signals";

interface ArticleViewTrackerProps {
  storyId: string;
  title: string;
  category: string;
}

/** Fires an `article_opened` signal once per mount. Renders nothing. */
export function ArticleViewTracker({ storyId, title, category }: ArticleViewTrackerProps) {
  useEffect(() => {
    recordSignal("article_opened", { storyId, title, category });
  }, [storyId, title, category]);

  return null;
}
