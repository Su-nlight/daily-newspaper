function Bar({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-sm bg-border ${className}`.trim()} />;
}

export default function Loading() {
  return (
    <main className="mx-auto flex w-full max-w-content flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      {/* Masthead */}
      <div className="flex flex-col items-center gap-3 border-b-4 border-double border-border pb-6">
        <Bar className="h-3 w-40" />
        <Bar className="h-10 w-72" />
        <Bar className="h-4 w-56" />
      </div>

      {/* Edition meta */}
      <div className="flex flex-col items-center gap-2 border-b border-border pb-8">
        <Bar className="h-3 w-48" />
        <Bar className="h-6 w-96 max-w-full" />
      </div>

      {/* Hero */}
      <div className="grid gap-6 lg:grid-cols-[1.1fr_1fr] lg:items-center lg:gap-10">
        <div className="order-2 flex flex-col gap-4 lg:order-1">
          <Bar className="h-3 w-16" />
          <Bar className="h-12 w-full" />
          <Bar className="h-12 w-4/5" />
          <Bar className="h-4 w-full max-w-md" />
          <Bar className="h-4 w-3/5 max-w-md" />
        </div>
        <Bar className="order-1 aspect-video w-full lg:order-2" />
      </div>

      {/* Secondary stories */}
      <div className="grid gap-8 border-t border-border pt-8 lg:grid-cols-[1.3fr_1fr]">
        <div className="flex flex-col gap-3">
          <Bar className="aspect-[4/3] w-full" />
          <Bar className="h-3 w-20" />
          <Bar className="h-6 w-full" />
          <Bar className="h-4 w-3/4" />
        </div>
        <div className="flex flex-col gap-4">
          <Bar className="h-4 w-full" />
          <Bar className="h-4 w-5/6" />
          <Bar className="h-4 w-full" />
        </div>
      </div>

      {/* A section grid */}
      <div className="flex flex-col gap-6">
        <Bar className="h-6 w-40" />
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {[0, 1, 2].map((key) => (
            <div key={key} className="flex flex-col gap-3">
              <Bar className="aspect-[4/3] w-full" />
              <Bar className="h-3 w-16" />
              <Bar className="h-5 w-full" />
              <Bar className="h-4 w-2/3" />
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
