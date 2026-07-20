/**
 * The brief is a document, not a dashboard (Doc 06 §7): a typeset memo in
 * the B1–B8 reading order, receipts and couldn't-see at the end, the
 * confidence word above the fold. Scrolling is the disclosure.
 */
import { useQuery } from "@tanstack/react-query";

import { ConfidenceWord } from "@/components/ui/confidence-word";
import { TextSkeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api/client";

export function BriefView({ prospectId }: { prospectId: string }) {
  const brief = useQuery({
    queryKey: ["brief", prospectId],
    queryFn: () => api.brief(prospectId),
    retry: false,
  });

  if (brief.isPending)
    return (
      <div className="max-w-prose">
        <TextSkeleton lines={8} />
      </div>
    );
  if (brief.isError)
    return (
      <p data-testid="no-brief" className="text-ink-muted max-w-prose text-sm leading-relaxed">
        No approved brief here yet. Briefs reach you only after review — when this one clears, it
        appears.
      </p>
    );

  const data = brief.data;
  return (
    <article data-testid="brief" className="animate-settle-in max-w-prose">
      <header className="flex items-baseline justify-between">
        <p className="text-ink-faint text-xs tracking-wide uppercase">Research brief</p>
        <ConfidenceWord word={data.confidence_word} />
      </header>
      {data.sections.map((section) => (
        <section key={section.code} className="mt-6">
          <h3 className="text-ink font-serif text-lg">{section.title}</h3>
          <p className="text-ink mt-1 font-serif text-[1.0625rem] leading-[1.65] whitespace-pre-line">
            {section.content}
          </p>
        </section>
      ))}
      {data.couldnt_see.length > 0 && (
        <section className="rounded-card border-hairline bg-paper mt-8 border p-4">
          <h3 className="text-ink text-sm font-medium">What I couldn&apos;t see</h3>
          <ul className="text-ink-muted mt-1 list-disc pl-5 text-sm leading-relaxed">
            {data.couldnt_see.map((entry, index) => (
              <li key={index}>{entry}</li>
            ))}
          </ul>
        </section>
      )}
      <section className="mt-8">
        <h3 className="text-ink text-sm font-medium">Receipts</h3>
        <ol className="text-ink-muted mt-1 text-sm leading-relaxed">
          {data.receipts.map((receipt) => (
            <li key={receipt.number} className="mt-1">
              [{receipt.number}] {receipt.claim}{" "}
              <span className="text-ink-faint text-xs">
                (observed {receipt.observed_at.slice(0, 10)})
              </span>
            </li>
          ))}
        </ol>
      </section>
      <p className="mt-8">
        <button
          data-testid="export-brief-pdf"
          className="text-accent text-sm underline underline-offset-2"
          onClick={() => void api.downloadBriefPdf(prospectId)}
        >
          Export as PDF
        </button>
      </p>
    </article>
  );
}
