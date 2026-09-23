import Link from "next/link";

import { PageContainer } from "@/components/layout/PageContainer";

export default function StoryNotFound() {
  return (
    <PageContainer narrow>
      <div className="flex flex-col items-center gap-4 border border-dashed border-border-strong px-6 py-20 text-center">
        <p className="text-headline">Story not found.</p>
        <p className="text-body max-w-md text-muted">
          This story may have been moved, retired from the current edition, or the link is
          incorrect.
        </p>
        <Link
          href="/"
          className="text-metadata inline-flex w-fit items-center gap-2 border border-border-strong px-4 py-2 text-foreground transition-colors hover:bg-background-elevated"
        >
          Back to today&apos;s edition
        </Link>
      </div>
    </PageContainer>
  );
}
