import type { BehavioralSignal, BehavioralSignalType } from "@/types";

const STORAGE_KEY = "daily-signal:behavioral-signals";
const MAX_STORED_SIGNALS = 200;

/**
 * Records a behavioral signal (article_opened, article_saved, etc.) for a
 * future recommendation backend to consume. No ML/recommendation logic
 * reads this yet — this module is intentionally just plumbing:
 *
 *   1. Logs to the console in development, so the signal is visible while
 *      building the UI that triggers it.
 *   2. Appends to a capped, best-effort localStorage log, so signals
 *      recorded across a session can be inspected or eventually flushed to
 *      a real endpoint.
 *
 * Call sites: components/story/ArticleViewTracker.tsx (article_opened),
 * SaveStoryButton (article_saved), ShareStoryButton (article_shared),
 * ArticleCompletionTracker (article_completed), and the topic weight
 * sliders on /topics (topic_followed / topic_ignored).
 */
export function recordSignal(type: BehavioralSignalType, payload: Record<string, unknown> = {}): void {
  const signal: BehavioralSignal = {
    type,
    payload,
    occurredAt: new Date().toISOString(),
  };

  if (process.env.NODE_ENV !== "production") {
    console.info("[behavioral-signal]", signal);
  }

  if (typeof window === "undefined") return;

  try {
    const existingRaw = window.localStorage.getItem(STORAGE_KEY);
    const existing: BehavioralSignal[] = existingRaw ? JSON.parse(existingRaw) : [];
    const next = [...existing, signal].slice(-MAX_STORED_SIGNALS);
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  } catch {
    // Signal recording is best-effort — private browsing, storage quota, or
    // a malformed existing value should never break the page.
  }
}
