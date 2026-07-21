/**
 * The designed absence (Design System §5). Empty is a state with a voice —
 * the empty week reads as integrity, not failure — never a blank div.
 */
import type { ReactNode } from "react";

export function EmptyState({
  title,
  children,
  testId,
}: {
  title: string;
  children: ReactNode;
  testId?: string;
}) {
  return (
    <div data-testid={testId} className="animate-settle-in max-w-prose py-8">
      <h2 className="text-ink font-display text-xl">{title}</h2>
      <div className="text-ink-muted mt-2 text-sm leading-relaxed">{children}</div>
    </div>
  );
}
