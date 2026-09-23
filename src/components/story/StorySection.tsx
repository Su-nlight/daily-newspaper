interface StorySectionProps {
  title: string;
  body: string;
}

export function StorySection({ title, body }: StorySectionProps) {
  return (
    <section className="space-y-2">
      <h2 className="text-section-title">{title}</h2>
      <p className="text-body text-foreground">{body}</p>
    </section>
  );
}
