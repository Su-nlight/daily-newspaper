function Bar({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-sm bg-border ${className}`.trim()} />;
}

export default function Loading() {
  return (
    <main className="mx-auto flex w-full max-w-content flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-4 border-b border-border pb-8">
        <Bar className="h-3 w-28" />
        <div className="flex flex-col gap-2">
          <Bar className="h-3 w-32" />
          <Bar className="h-8 w-full max-w-xl" />
          <Bar className="h-4 w-96 max-w-full" />
        </div>
        <Bar className="h-4 w-64" />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.1fr_1fr] lg:items-center lg:gap-10">
        <div className="order-2 flex flex-col gap-4 lg:order-1">
          <Bar className="h-3 w-16" />
          <Bar className="h-10 w-full" />
          <Bar className="h-4 w-full max-w-md" />
        </div>
        <Bar className="order-1 aspect-video w-full lg:order-2" />
      </div>
    </main>
  );
}
