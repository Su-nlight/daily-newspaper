"use client";

import { useRouter } from "next/navigation";

interface RetryButtonProps {
  label?: string;
}

export function RetryButton({ label = "Retry" }: RetryButtonProps) {
  const router = useRouter();

  return (
    <button
      type="button"
      onClick={() => router.refresh()}
      className="text-metadata inline-flex w-fit items-center gap-2 border border-border-strong px-4 py-2 text-foreground transition-colors hover:bg-background-elevated"
    >
      {label}
    </button>
  );
}
