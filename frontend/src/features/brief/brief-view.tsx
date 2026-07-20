/**
 * The brief is a document, not a dashboard (Doc 06 §7): a typeset memo in
 * the B1–B8 reading order, receipts and couldn't-see at the end, the
 * confidence word above the fold. Scrolling is the disclosure.
 */
import { useQuery } from "@tanstack/react-query";

import { ConfidenceWord } from "@/components/ui/confidence-word";
import { api } from "@/lib/api/client";

export function BriefView({ prospectId }: { prospectId: string }) {
  const brief = useQuery({
    queryKey: ["brief", prospectId],
    queryFn: () => api.brief(prospectId),
    retry: false,
  });

  if (brief.isPending) return <p className="text-sm text-stone-500">Opening the brief…</p>;
  if (brief.isError)
    return (
      <p data-testid="no-brief" className="max-w-prose text-sm text-stone-600">
        No approved brief here yet. Briefs reach you only after review — when this one clears, it
        appears.
      </p>
    );

  const data = brief.data;
  return (
    <article data-testid="brief" className="max-w-prose">
      <header className="flex items-baseline justify-between">
        <p className="text-xs tracking-wide text-stone-500 uppercase">Research brief</p>
        <ConfidenceWord word={data.confidence_word} />
      </header>
      {data.sections.map((section) => (
        <section key={section.code} className="mt-6">
          <h3 className="font-serif text-lg">{section.title}</h3>
          <p className="mt-1 text-[15px] leading-relaxed whitespace-pre-line text-stone-800">
            {section.content}
          </p>
        </section>
      ))}
      {data.couldnt_see.length > 0 && (
        <section className="mt-8 rounded border border-stone-200 bg-stone-50 p-3">
          <h3 className="text-sm font-medium text-stone-700">What I couldn&apos;t see</h3>
          <ul className="mt-1 list-disc pl-5 text-sm text-stone-600">
            {data.couldnt_see.map((entry, index) => (
              <li key={index}>{entry}</li>
            ))}
          </ul>
        </section>
      )}
      <section className="mt-8">
        <h3 className="text-sm font-medium text-stone-700">Receipts</h3>
        <ol className="mt-1 text-sm text-stone-600">
          {data.receipts.map((receipt) => (
            <li key={receipt.number} className="mt-1">
              [{receipt.number}] {receipt.claim}{" "}
              <span className="text-xs text-stone-400">
                (observed {receipt.observed_at.slice(0, 10)})
              </span>
            </li>
          ))}
        </ol>
      </section>
      <p className="mt-8">
        <a className="text-sm text-sky-800 underline" href={api.briefPdfUrl(prospectId)}>
          Export as PDF
        </a>
      </p>
    </article>
  );
}
