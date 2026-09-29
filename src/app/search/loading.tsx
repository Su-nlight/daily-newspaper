function Bar({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-sm bg-border ${className}`.trim()} />;
}

export default function Loading() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-2 border-b border-border pb-4">
        <Bar className="h-3 w-16" />
        <Bar className="h-8 w-64" />
      </div>

      <div className="flex flex-col gap-5">
        <Bar className="h-12 w-full" />
        <div className="flex flex-wrap gap-3">
          {[0, 1, 2, 3, 4, 5].map((key) => (
            <Bar key={key} className="h-9 w-28" />
          ))}
        </div>
      </div>

      <div className="flex flex-col border-t border-border pt-6">
        {[0, 1, 2].map((key) => (
          <div key={key} className="flex flex-col gap-2 border-b border-border py-6 first:pt-0">
            <Bar className="h-3 w-20" />
            <Bar className="h-5 w-full" />
            <Bar className="h-4 w-3/4" />
            <Bar className="h-3 w-48" />
          </div>
        ))}
      </div>
    </main>
  );
}
