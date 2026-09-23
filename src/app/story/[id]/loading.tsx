function Bar({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-sm bg-border ${className}`.trim()} />;
}

export default function Loading() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-5">
        <Bar className="h-3 w-40" />
        <div className="flex flex-col gap-3">
          <Bar className="h-3 w-20" />
          <Bar className="h-10 w-full" />
          <Bar className="h-10 w-4/5" />
          <Bar className="h-5 w-3/5" />
          <Bar className="h-4 w-32" />
        </div>
      </div>

      <Bar className="aspect-[16/9] w-full" />

      <Bar className="h-6 w-full" />
      <Bar className="h-6 w-5/6" />

      <div className="flex flex-col gap-3 border-t border-border pt-6">
        <Bar className="h-3 w-28" />
        <Bar className="h-4 w-full" />
        <Bar className="h-4 w-full" />
        <Bar className="h-4 w-2/3" />
      </div>

      <div className="flex flex-col gap-3 border-t border-border pt-6">
        <Bar className="h-3 w-28" />
        <Bar className="h-4 w-full" />
        <Bar className="h-4 w-3/4" />
      </div>
    </main>
  );
}
