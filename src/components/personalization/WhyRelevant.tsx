interface WhyRelevantProps {
  reasons: string[];
}

/**
 * Renders the plain-language reasons a story was personalized for this
 * user. Intentionally has no numeric/score prop — callers should never
 * pass a raw relevance number here.
 */
export function WhyRelevant({ reasons }: WhyRelevantProps) {
  if (reasons.length === 0) return null;

  return (
    <div className="flex flex-col gap-1.5">
      <p className="text-metadata text-muted">Why you&apos;re seeing this</p>
      <ul className="flex flex-col gap-1">
        {reasons.map((reason) => (
          <li key={reason} className="text-caption flex items-start gap-2">
            <span aria-hidden="true" className="text-accent">
              ✓
            </span>
            <span>{reason}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
