import type { ReactNode } from "react";

interface StorySectionProps {
  title: string;
  children: ReactNode;
}

export function StorySection({ title, children }: StorySectionProps) {
  return (
    <section className="flex flex-col gap-3 border-t border-border pt-6">
      <h2 className="text-section-title text-accent">{title}</h2>
      <div className="text-body flex flex-col gap-3 text-foreground">{children}</div>
    </section>
  );
}
