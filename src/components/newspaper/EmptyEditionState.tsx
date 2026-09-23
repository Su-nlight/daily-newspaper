import { RetryButton } from "@/components/newspaper/RetryButton";

export function EmptyEditionState() {
  return (
    <div className="flex flex-col items-center gap-4 border border-dashed border-border-strong px-6 py-20 text-center">
      <p className="text-headline">No edition is available yet.</p>
      <p className="text-body max-w-md text-muted">
        Today&apos;s edition hasn&apos;t been published. This usually resolves within a few
        minutes — try again shortly.
      </p>
      <RetryButton label="Retry" />
    </div>
  );
}
