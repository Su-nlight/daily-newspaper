import type { ReactNode } from "react";

interface PageContainerProps {
  children: ReactNode;
  /** Narrower measure for long-form / single-column pages (story, about, chat). */
  narrow?: boolean;
  className?: string;
}

export function PageContainer({ children, narrow = false, className = "" }: PageContainerProps) {
  return (
    <main
      className={`mx-auto flex w-full flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8 ${
        narrow ? "max-w-3xl" : "max-w-content"
      } ${className}`.trim()}
    >
      {children}
    </main>
  );
}
