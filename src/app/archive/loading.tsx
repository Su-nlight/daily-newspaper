function Bar({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-sm bg-border ${className}`.trim()} />;
}

export default function Loading() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-2 border-b border-border pb-4">
        <Bar className="h-3 w-24" />
        <Bar className="h-8 w-48" />
        <Bar className="h-4 w-72 max-w-full" />
      </div>
      <div className="flex flex-col gap-1">
        <Bar className="h-3 w-40" />
        <div className="flex flex-col border-l border-border pl-6">
          {[0, 1, 2, 3].map((key) => (
            <div key={key} className="flex flex-col gap-2 py-5">
              <Bar className="h-4 w-32" />
              <Bar className="h-4 w-full" />
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
