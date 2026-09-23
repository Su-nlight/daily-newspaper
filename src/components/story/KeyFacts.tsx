interface KeyFactsProps {
  facts: string[];
}

export function KeyFacts({ facts }: KeyFactsProps) {
  if (facts.length === 0) return null;

  return (
    <section className="border-t border-border pt-6">
      <h2 className="text-section-title mb-3 text-accent">Key Facts</h2>
      <ul className="flex flex-col gap-2.5">
        {facts.map((fact) => (
          <li key={fact} className="text-body flex gap-3 text-foreground">
            <span aria-hidden="true" className="mt-1 text-accent">
              ▪
            </span>
            <span>{fact}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
