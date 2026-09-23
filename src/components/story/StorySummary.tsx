interface StorySummaryProps {
  summary: string;
}

export function StorySummary({ summary }: StorySummaryProps) {
  return (
    <section className="space-y-2">
      <h2 className="text-section-title">Summary</h2>
      <p className="text-body text-foreground">{summary}</p>
    </section>
  );
}
