function Bar({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-sm bg-border ${className}`.trim()} />;
}

export default function Loading() {
  return (
    <main className="mx-auto flex w-full max-w-content flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-2 border-b border-border pb-4">
        <Bar className="h-3 w-24" />
        <Bar className="h-8 w-64" />
        <Bar className="h-4 w-96 max-w-full" />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.1fr_1fr] lg:items-center lg:gap-10">
        <div className="order-2 flex flex-col gap-4 lg:order-1">
          <Bar className="h-3 w-16" />
          <Bar className="h-10 w-full" />
          <Bar className="h-4 w-full max-w-md" />
        </div>
        <Bar className="order-1 aspect-video w-full lg:order-2" />
      </div>

      <div className="flex flex-col gap-6 border-t border-border pt-8">
        <Bar className="h-6 w-48" />
        <div className="grid gap-8 sm:grid-cols-2">
          {[0, 1].map((key) => (
            <div key={key} className="flex flex-col gap-3">
              <Bar className="aspect-[4/3] w-full" />
              <Bar className="h-5 w-full" />
              <Bar className="h-4 w-2/3" />
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
