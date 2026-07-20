/**
 * Shape-true loading placeholders (Design System §5). No spinners anywhere:
 * a skeleton promises the shape of what's coming; a spinner promises
 * nothing. Waits that are genuinely long are voiced, not animated.
 */

export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div
      aria-hidden="true"
      className={`animate-skeleton rounded-control bg-hairline ${className}`}
    />
  );
}

export function TextSkeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div data-testid="skeleton" role="status" aria-label="loading" className="space-y-2">
      {Array.from({ length: lines }, (_, index) => (
        <Skeleton key={index} className={index === lines - 1 ? "h-4 w-2/3" : "h-4 w-full"} />
      ))}
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div
      data-testid="skeleton"
      role="status"
      aria-label="loading"
      className="rounded-card border-hairline bg-surface shadow-card border p-4"
    >
      <div className="flex items-baseline justify-between">
        <Skeleton className="h-5 w-40" />
        <Skeleton className="h-5 w-16 rounded-full" />
      </div>
      <div className="mt-3 space-y-2">
        <Skeleton className="h-3.5 w-full" />
        <Skeleton className="h-3.5 w-4/5" />
      </div>
    </div>
  );
}
