import type { Article } from "@/types";

const WORDS_PER_MINUTE = 200;

/** Rough reading-time estimate for a set of stories, based on summary word
 *  counts plus a small fixed overhead per story for headline scanning. */
export function estimateReadingTime(articles: Article[]): number {
  const totalWords = articles.reduce((sum, article) => sum + article.summary.split(/\s+/).length, 0);
  const minutes = totalWords / WORDS_PER_MINUTE + articles.length * 0.5;
  return Math.max(1, Math.round(minutes));
}
