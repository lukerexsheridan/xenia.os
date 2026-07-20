/**
 * The four-word confidence vocabulary as design tokens (Doc 06 §5;
 * Design System §1). The word arrives from the API (AP5) — this component
 * only styles it. Colour underlines meaning; the word carries it.
 */

const TOKENS: Record<string, string> = {
  confident: "bg-confident-surface text-confident-ink",
  likely: "bg-likely-surface text-likely-ink",
  possible: "bg-possible-surface text-possible-ink",
  uncertain: "bg-uncertain-surface text-uncertain-ink",
};

export function ConfidenceWord({ word }: { word: string }) {
  const token = TOKENS[word] ?? TOKENS.uncertain;
  return (
    <span
      data-testid="confidence-word"
      role="status"
      aria-label={`confidence: ${word}`}
      className={`border-hairline inline-block rounded-full border px-2.5 py-0.5 text-xs font-medium lowercase ${token}`}
    >
      {word}
    </span>
  );
}
