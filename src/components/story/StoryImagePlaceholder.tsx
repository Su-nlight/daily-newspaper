interface StoryImagePlaceholderProps {
  category: string;
  size?: "hero" | "standard" | "horizontal";
  className?: string;
}

const aspectByFallback: Record<NonNullable<StoryImagePlaceholderProps["size"]>, string> = {
  hero: "aspect-[16/9]",
  standard: "aspect-[4/3]",
  horizontal: "aspect-square",
};

/**
 * Real photography arrives with the news-ingestion module. Until then this
 * renders a restrained, editorial placeholder (ruled paper texture + the
 * category name) instead of pointing <img> at mock URLs that would 404.
 */
export function StoryImagePlaceholder({
  category,
  size = "standard",
  className = "",
}: StoryImagePlaceholderProps) {
  return (
    <div
      className={`relative flex items-end overflow-hidden border border-border bg-background-elevated ${aspectByFallback[size]} ${className}`.trim()}
      style={{
        backgroundImage:
          "repeating-linear-gradient(135deg, var(--color-border) 0, var(--color-border) 1px, transparent 1px, transparent 14px)",
      }}
      aria-hidden="true"
    >
      <span className="text-metadata m-2 rounded-full border border-border-strong bg-background px-2 py-1">
        {category}
      </span>
    </div>
  );
}
