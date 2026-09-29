import Link from "next/link";

import { PageContainer } from "@/components/layout/PageContainer";

export default function EditionNotFound() {
  return (
    <PageContainer>
      <div className="flex flex-col items-center gap-4 border border-dashed border-border-strong px-6 py-20 text-center">
        <p className="text-headline">No edition for this date.</p>
        <p className="text-body max-w-md text-muted">
          Daily Signal doesn&apos;t have a published edition for that date yet.
        </p>
        <Link
          href="/archive"
          className="text-metadata inline-flex w-fit items-center gap-2 border border-border-strong px-4 py-2 text-foreground transition-colors hover:bg-background-elevated"
        >
          Browse the archive
        </Link>
      </div>
    </PageContainer>
  );
}
