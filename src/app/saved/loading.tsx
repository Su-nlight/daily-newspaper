function Bar({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-sm bg-border ${className}`.trim()} />;
}

export default function Loading() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-2 border-b border-border pb-4">
        <Bar className="h-3 w-16" />
        <Bar className="h-8 w-56" />
        <Bar className="h-4 w-72 max-w-full" />
      </div>
      <div className="flex flex-col">
        {[0, 1, 2].map((key) => (
          <div key={key} className="flex flex-col gap-3 border-b border-border py-6 first:pt-0">
            <Bar className="h-3 w-20" />
            <Bar className="h-5 w-full" />
            <Bar className="h-3 w-64 max-w-full" />
            <div className="flex gap-3">
              <Bar className="h-7 w-20" />
              <Bar className="h-7 w-20" />
              <Bar className="h-7 w-24" />
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
