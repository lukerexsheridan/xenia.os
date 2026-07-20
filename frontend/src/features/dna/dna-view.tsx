/**
 * The DNA document: readable, correctable, versioned (Doc 03 C2).
 *
 * Elements in plain language with their provenance; the changelog is total
 * and ships with the document (N4); corrections are gifts — ten seconds,
 * acknowledged with the named effect, never argued with (Doc 06 §6);
 * structural proposals await the customer's signature.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { TextSkeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api/client";

const CATEGORY_TITLES: Record<string, string> = {
  business_attributes: "The businesses",
  service_need_evidence: "Signs they need you",
  buying_signals: "When they buy",
  disqualifiers: "Hard lines — never crossed",
};

export function DnaView() {
  const queryClient = useQueryClient();
  const dna = useQuery({ queryKey: ["dna"], queryFn: api.dna, retry: false });
  const [effect, setEffect] = useState<string | null>(null);

  const endorse = useMutation({
    mutationFn: api.endorseDna,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["dna"] }),
  });
  const withdraw = useMutation({
    mutationFn: (elementId: string) => api.correct("dna_element", elementId),
    onMutate: () => setEffect("Removed — computing what that changes…"),
    onSuccess: (response) => {
      setEffect(response.effect_summary);
      void queryClient.invalidateQueries({ queryKey: ["dna"] });
      void queryClient.invalidateQueries({ queryKey: ["queue"] });
    },
    onError: (error) => setEffect(error.message),
  });
  const decideProposal = useMutation({
    mutationFn: ({ id, approve }: { id: string; approve: boolean }) =>
      api.decideProposal(id, approve),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["dna"] }),
  });

  if (dna.isPending)
    return (
      <div className="max-w-prose">
        <TextSkeleton lines={6} />
      </div>
    );
  if (dna.isError)
    return (
      <p className="text-ink-muted max-w-prose text-sm leading-relaxed">
        No DNA yet — the interview founds it. Head to the interview when you have ten minutes.
      </p>
    );

  const data = dna.data;
  const open = data.proposals.filter((proposal) => proposal.status === "proposed");
  const grouped = Object.entries(CATEGORY_TITLES)
    .map(([category, title]) => ({
      title,
      elements: data.elements.filter((element) => element.category === category),
    }))
    .filter((group) => group.elements.length > 0);

  return (
    <div className="animate-settle-in max-w-prose">
      <header className="flex items-baseline justify-between">
        <h2 className="text-ink font-serif text-xl">Your ideal-client DNA</h2>
        <span className="text-ink-faint text-xs">version {data.version}</span>
      </header>
      {!data.endorsed && (
        <div className="rounded-card border-hairline bg-possible-surface mt-3 border p-4">
          <p className="text-ink text-sm leading-relaxed">
            This is my model of who you sell to, in your words. Read it; when it&apos;s right,
            endorse it and it becomes our shared agreement.
          </p>
          <button
            data-testid="endorse"
            className="transition-settle rounded-control bg-accent text-accent-ink mt-2.5 px-3 py-1.5 text-sm font-medium hover:opacity-90"
            onClick={() => endorse.mutate()}
          >
            Endorse this DNA
          </button>
        </div>
      )}
      {data.endorsed && (
        <p data-testid="endorsed" className="text-confident-ink mt-2 text-sm">
          Endorsed — our shared agreement. Corrections keep it honest.
        </p>
      )}
      {effect && (
        <div data-testid="named-effect" className="animate-settle-in mt-3">
          <ErrorNoticeLike>{effect}</ErrorNoticeLike>
        </div>
      )}
      {grouped.map((group) => (
        <section key={group.title} className="mt-6">
          <h3 className="text-ink-muted text-xs font-medium tracking-wide uppercase">
            {group.title}
          </h3>
          <ul className="mt-2 space-y-2">
            {group.elements.map((element) => (
              <li
                key={element.element_id}
                className="text-ink flex items-start justify-between gap-3 font-serif text-[1.0625rem] leading-[1.65]"
              >
                <span>{element.statement}</span>
                <button
                  data-testid={`withdraw-${element.element_id}`}
                  className="transition-settle text-ink-faint hover:text-danger-ink shrink-0 pt-1 text-xs"
                  title="Wrong — remove this"
                  aria-label={`wrong — remove: ${element.statement}`}
                  onClick={() => withdraw.mutate(element.element_id)}
                >
                  wrong — remove
                </button>
              </li>
            ))}
          </ul>
        </section>
      ))}
      {open.length > 0 && (
        <section data-testid="proposals" className="border-hairline mt-8 border-t pt-4">
          <h3 className="text-ink text-sm font-medium">Awaiting your signature</h3>
          {open.map((proposal) => (
            <div
              key={proposal.proposal_id}
              className="rounded-card border-hairline bg-surface shadow-card mt-2 border p-4"
            >
              <p className="text-ink font-serif text-[1.0625rem]">{proposal.statement}</p>
              <p className="text-ink-muted mt-1 text-xs leading-relaxed">{proposal.rationale}</p>
              <div className="mt-2.5 flex gap-2">
                <button
                  className="transition-settle rounded-control bg-accent text-accent-ink px-3 py-1 text-xs font-medium hover:opacity-90"
                  onClick={() => decideProposal.mutate({ id: proposal.proposal_id, approve: true })}
                >
                  Endorse
                </button>
                <button
                  className="transition-settle rounded-control border-hairline text-ink hover:bg-paper border px-3 py-1 text-xs"
                  onClick={() =>
                    decideProposal.mutate({ id: proposal.proposal_id, approve: false })
                  }
                >
                  Decline
                </button>
              </div>
            </div>
          ))}
        </section>
      )}
      <section className="border-hairline mt-8 border-t pt-4">
        <h3 className="text-ink text-sm font-medium">Every change, explained</h3>
        <ul className="text-ink-faint mt-2 space-y-1 text-xs leading-relaxed">
          {data.changelog
            .slice(-10)
            .reverse()
            .map((entry, index) => (
              <li key={index}>
                {entry.occurred_at.slice(0, 10)} — {entry.cause.replaceAll("_", " ")} by{" "}
                {entry.author}
                {entry.element_statement ? `: ${entry.element_statement}` : ""}
              </li>
            ))}
        </ul>
      </section>
      <p className="mt-6">
        <button
          data-testid="export-dna-pdf"
          className="text-accent text-sm underline underline-offset-2"
          onClick={() => void api.downloadDnaPdf()}
        >
          Export the DNA document (PDF)
        </button>
      </p>
    </div>
  );
}

/** The named effect: an acknowledgment card, not an alarm. */
function ErrorNoticeLike({ children }: { children: string }) {
  return (
    <p className="rounded-card border-hairline bg-surface text-ink shadow-card border p-3 text-sm font-medium">
      {children}
    </p>
  );
}
