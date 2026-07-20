/**
 * The plain-voice error (Doc 06 §9): what happened, whose fault it isn't,
 * what to do next. Never a stack trace, never a shrug.
 */

export function ErrorNotice({ message, testId }: { message: string; testId?: string }) {
  return (
    <div
      data-testid={testId ?? "error-notice"}
      role="alert"
      className="animate-settle-in rounded-card border-hairline bg-danger-surface max-w-prose border p-4"
    >
      <p className="text-danger-ink text-sm leading-relaxed">{message}</p>
    </div>
  );
}
