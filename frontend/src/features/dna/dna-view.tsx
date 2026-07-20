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

  if (dna.isPending) return <p className="text-sm text-stone-500">Opening your DNA…</p>;
  if (dna.isError)
    return (
      <p className="max-w-prose text-sm text-stone-600">
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
    <div className="max-w-prose">
      <header className="flex items-baseline justify-between">
        <h2 className="font-serif text-xl">Your ideal-client DNA</h2>
        <span className="text-xs text-stone-500">version {data.version}</span>
      </header>
      {!data.endorsed && (
        <div className="mt-3 rounded border border-amber-200 bg-amber-50 p-3">
          <p className="text-sm text-stone-800">
            This is my model of who you sell to, in your words. Read it; when it&apos;s right,
            endorse it and it becomes our shared agreement.
          </p>
          <button
            data-testid="endorse"
            className="mt-2 rounded bg-stone-900 px-3 py-1 text-sm text-white"
            onClick={() => endorse.mutate()}
          >
            Endorse this DNA
          </button>
        </div>
      )}
      {data.endorsed && (
        <p data-testid="endorsed" className="mt-2 text-sm text-emerald-800">
          Endorsed — our shared agreement. Corrections keep it honest.
        </p>
      )}
      {effect && (
        <p data-testid="named-effect" className="mt-3 rounded bg-stone-100 p-2 text-sm">
          {effect}
        </p>
      )}
      {grouped.map((group) => (
        <section key={group.title} className="mt-6">
          <h3 className="text-sm font-medium tracking-wide text-stone-700 uppercase">
            {group.title}
          </h3>
          <ul className="mt-2 space-y-2">
            {group.elements.map((element) => (
              <li
                key={element.element_id}
                className="flex items-start justify-between gap-3 text-[15px] text-stone-800"
              >
                <span>{element.statement}</span>
                <button
                  data-testid={`withdraw-${element.element_id}`}
                  className="shrink-0 text-xs text-stone-400 hover:text-red-800"
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
        <section data-testid="proposals" className="mt-8 border-t border-stone-200 pt-4">
          <h3 className="text-sm font-medium text-stone-700">Awaiting your signature</h3>
          {open.map((proposal) => (
            <div key={proposal.proposal_id} className="mt-2 rounded border border-stone-200 p-3">
              <p className="text-sm text-stone-800">{proposal.statement}</p>
              <p className="mt-1 text-xs text-stone-500">{proposal.rationale}</p>
              <div className="mt-2 flex gap-2">
                <button
                  className="rounded bg-stone-900 px-3 py-1 text-xs text-white"
                  onClick={() => decideProposal.mutate({ id: proposal.proposal_id, approve: true })}
                >
                  Endorse
                </button>
                <button
                  className="rounded border border-stone-300 px-3 py-1 text-xs"
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
      <section className="mt-8 border-t border-stone-200 pt-4">
        <h3 className="text-sm font-medium text-stone-700">Every change, explained</h3>
        <ul className="mt-2 space-y-1 text-xs text-stone-500">
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
          className="text-sm text-sky-800 underline"
          onClick={() => void api.downloadDnaPdf()}
        >
          Export the DNA document (PDF)
        </button>
      </p>
    </div>
  );
}
