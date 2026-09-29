import Link from "next/link";

import type { ArchiveMonthGroup } from "@/types";

interface ArchiveTimelineProps {
  months: ArchiveMonthGroup[];
}

export function ArchiveTimeline({ months }: ArchiveTimelineProps) {
  if (months.length === 0) {
    return (
      <p className="text-body border-t border-border pt-8 text-muted">
        No past editions are available yet.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-10">
      {months.map((month) => (
        <section key={month.monthLabel} className="flex flex-col gap-1">
          <p className="text-section-title mb-4 text-accent">{month.monthLabel}</p>
          <ol className="flex flex-col border-l border-border pl-6">
            {month.editions.map((entry) => (
              <li key={entry.date} className="relative py-5">
                <span
                  aria-hidden="true"
                  className="absolute top-6 -left-[1.6rem] size-2.5 rounded-full border-2 border-background bg-accent"
                />
                <Link
                  href={`/archive/${entry.date}`}
                  className="group flex flex-col gap-1 sm:flex-row sm:items-baseline sm:gap-4"
                >
                  <span className="text-subheadline shrink-0 sm:w-40">{entry.dayLabel}</span>
                  <span className="flex flex-col gap-0.5">
                    <span className="text-body text-foreground group-hover:underline">
                      {entry.headline}
                    </span>
                    <span className="text-caption">{entry.storyCount} stories</span>
                  </span>
                </Link>
              </li>
            ))}
          </ol>
        </section>
      ))}
    </div>
  );
}
