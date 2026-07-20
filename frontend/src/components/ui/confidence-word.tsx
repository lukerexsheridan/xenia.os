/**
 * The four-word confidence vocabulary as design tokens (Doc 06 §5).
 *
 * The word arrives from the API (AP5) — this component only styles it.
 * Semantic colour tokens, never ad-hoc styling; no percentages, ever.
 */

const TOKENS: Record<string, string> = {
  confident: "text-emerald-800 bg-emerald-50 border-emerald-200",
  likely: "text-sky-800 bg-sky-50 border-sky-200",
  possible: "text-amber-800 bg-amber-50 border-amber-200",
  uncertain: "text-stone-600 bg-stone-100 border-stone-300",
};

export function ConfidenceWord({ word }: { word: string }) {
  const token = TOKENS[word] ?? TOKENS.uncertain;
  return (
    <span
      data-testid="confidence-word"
      role="status"
      aria-label={`confidence: ${word}`}
      className={`inline-block rounded-full border px-2.5 py-0.5 text-xs font-medium lowercase ${token}`}
    >
      {word}
    </span>
  );
}
