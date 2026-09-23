interface KeyFactsProps {
  items: string[];
}

export function KeyFacts({ items }: KeyFactsProps) {
  if (items.length === 0) return null;

  return (
    <section className="space-y-3">
      <h2 className="text-section-title">Key Facts</h2>
      <ul className="space-y-2 border-l border-border pl-4">
        {items.map((fact) => (
          <li key={fact} className="text-body text-foreground">
            {fact}
          </li>
        ))}
      </ul>
    </section>
  );
}
