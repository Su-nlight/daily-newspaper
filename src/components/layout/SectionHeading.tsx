import type { ReactNode } from "react";

interface SectionHeadingProps {
  title: string;
  description?: string;
  eyebrow?: string;
  action?: ReactNode;
}

export function SectionHeading({ title, description, eyebrow, action }: SectionHeadingProps) {
  return (
    <div className="flex flex-col gap-2 border-b border-border pb-4 sm:flex-row sm:items-end sm:justify-between">
      <div className="space-y-1.5">
        {eyebrow ? <p className="text-metadata text-accent">{eyebrow}</p> : null}
        <h2 className="text-headline">{title}</h2>
        {description ? <p className="text-body max-w-2xl text-muted">{description}</p> : null}
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div>
  );
}
