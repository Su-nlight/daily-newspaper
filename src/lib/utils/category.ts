const CATEGORY_LABELS: Record<string, string> = {
  ai: "AI",
  research: "Research",
  cybersecurity: "Cybersecurity",
  technology: "Technology",
  world: "World",
  india: "India",
  business: "Business",
  science: "Science",
  career: "Career",
};

/** Formats a category slug (e.g. "software-engineering") for display without
 *  components needing to import mock category data directly. */
export function formatCategoryLabel(slug: string): string {
  if (CATEGORY_LABELS[slug]) return CATEGORY_LABELS[slug];

  return slug
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}
