import Link from "next/link";

import type { BriefItem } from "@/types";

interface SixtySecondBriefProps {
  items: BriefItem[];
  /** Route to the full edition, e.g. a future /archive/[date] page. Defaults to "/". */
  fullEditionHref?: string;
}

export function SixtySecondBrief({ items, fullEditionHref = "/" }: SixtySecondBriefProps) {
  if (items.length === 0) return null;

  return (
    <section className="border-t border-border pt-8">
      <div className="border border-border-strong bg-background-elevated p-6 sm:p-8">
        <p className="text-section-title text-accent">The 60-Second Brief</p>
        <ol className="mt-5 flex flex-col divide-y divide-border">
          {items.map((item, index) => (
            <li key={item.id} className="flex gap-4 py-3">
              <span className="text-metadata shrink-0 pt-0.5 text-muted">
                {String(index + 1).padStart(2, "0")}
              </span>
              <p className="text-body">
                <span className="font-medium">{item.headline}</span>
                <span className="text-muted"> — {item.summary}</span>
              </p>
            </li>
          ))}
        </ol>
        <Link
          href={fullEditionHref}
          className="text-metadata mt-5 inline-flex items-center gap-2 border-b border-accent pb-0.5 text-accent"
        >
          Read full edition
          <span aria-hidden="true">→</span>
        </Link>
      </div>
    </section>
  );
}
