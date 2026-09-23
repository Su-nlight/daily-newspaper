import Link from "next/link";

import { PageContainer } from "@/components/layout/PageContainer";

export default function CategoryNotFound() {
  return (
    <PageContainer>
      <div className="flex flex-col items-center gap-4 border border-dashed border-border-strong px-6 py-20 text-center">
        <p className="text-headline">Category not found.</p>
        <p className="text-body max-w-md text-muted">
          This category doesn&apos;t exist yet, or hasn&apos;t been published. Try Topics for a
          full list of what Daily Signal currently tracks.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <Link
            href="/topics"
            className="text-metadata inline-flex w-fit items-center gap-2 border border-border-strong px-4 py-2 text-foreground transition-colors hover:bg-background-elevated"
          >
            Browse Topics
          </Link>
          <Link
            href="/"
            className="text-metadata inline-flex w-fit items-center gap-2 border border-border-strong px-4 py-2 text-foreground transition-colors hover:bg-background-elevated"
          >
            Back to today&apos;s edition
          </Link>
        </div>
      </div>
    </PageContainer>
  );
}
