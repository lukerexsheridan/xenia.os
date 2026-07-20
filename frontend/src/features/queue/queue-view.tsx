/**
 * The weekly queue: ranked, bounded, honest about its order (Doc 06 §7).
 *
 * Verdict-first cards; one decision per item, made where the item is; the
 * visible exclusion at the queue's end styled as information; the empty
 * week reads as integrity, not failure. Decline chips are the ten-second
 * loop's teaching vocabulary — one tap, free text never required.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { useState } from "react";

import { ConfidenceWord } from "@/components/ui/confidence-word";
import { api, type DeclineChip, type DecisionKind, type QueueItem } from "@/lib/api/client";

const CHIPS: { value: DeclineChip; label: string }[] = [
  { value: "wrong_industry", label: "wrong industry" },
  { value: "too_small", label: "too small" },
  { value: "bad_timing", label: "bad timing" },
  { value: "we_know_them", label: "we know them" },
  { value: "evidence_is_wrong", label: "evidence is wrong" },
  { value: "not_our_kind_of_client", label: "not our kind of client" },
];

export function QueueView() {
  const queue = useQuery({ queryKey: ["queue"], queryFn: api.queue });

  if (queue.isPending) return <p className="text-sm text-stone-500">Fetching this week…</p>;
  if (queue.isError) return <p className="text-sm text-red-800">{queue.error.message}</p>;

  const ranked = queue.data.items.filter((item) => item.polarity === "recommended");
  const excluded = queue.data.items.filter((item) => item.polarity === "excluded");

  if (ranked.length === 0 && excluded.length === 0) {
    return (
      <div data-testid="empty-week" className="max-w-prose">
        <h2 className="font-serif text-xl">A quiet week — deliberately.</h2>
        <p className="mt-2 text-sm text-stone-600">
          Nothing this week met the bar, so nothing is here. I don&apos;t pad the queue: when
          discovery runs thin I say so and keep looking. You&apos;ll see what I checked, and next
          Monday starts fresh.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl space-y-4">
      <p className="text-sm text-stone-500">
        Week {queue.data.week_key} — {ranked.length} recommended, ranked. One decision per card.
      </p>
      {ranked.map((item) => (
        <QueueCard key={item.recommendation_id} item={item} />
      ))}
      {excluded.length > 0 && (
        <section data-testid="visible-exclusions" className="border-t border-stone-200 pt-4">
          <h3 className="text-sm font-medium text-stone-700">Ruled out, with reasons</h3>
          {excluded.map((item) => (
            <p key={item.recommendation_id} className="mt-2 text-sm text-stone-600">
              {item.exclusion_reason}
            </p>
          ))}
        </section>
      )}
    </div>
  );
}

function QueueCard({ item }: { item: QueueItem }) {
  const queryClient = useQueryClient();
  const [chipsOpen, setChipsOpen] = useState(false);
  const [resolution, setResolution] = useState<string | null>(null);

  const decide = useMutation({
    mutationFn: ({ kind, chip }: { kind: DecisionKind; chip?: DeclineChip }) =>
      api.decide(item.recommendation_id, kind, chip),
    onMutate: ({ kind }) => {
      // Optimistic acknowledgment (Doc 08 §4): instant, then replaced by
      // the server's own words when they arrive.
      setResolution(kind === "decline" ? "Noted." : "On it.");
    },
    onSuccess: (response) => {
      setResolution(
        response.lesson ??
          (response.kind === "pursue" ? "Marked as pursuing — I'll ask how it went." : "Noted."),
      );
      void queryClient.invalidateQueries({ queryKey: ["queue"] });
      void queryClient.invalidateQueries({ queryKey: ["dna"] });
    },
    onError: (error) => setResolution(error.message),
  });

  return (
    <article
      data-testid="queue-card"
      className="rounded-lg border border-stone-200 bg-white p-4 shadow-sm"
    >
      <header className="flex items-baseline justify-between">
        <h3 className="font-serif text-lg">
          {item.rank}.{" "}
          <Link
            to="/prospects/$prospectId"
            params={{ prospectId: item.prospect_id }}
            className="hover:underline"
          >
            {item.business_name}
          </Link>
        </h3>
        <ConfidenceWord word={item.confidence_word} />
      </header>
      <ul className="mt-2 space-y-1 text-sm text-stone-700">
        {item.components.slice(0, 3).map((component, index) => (
          <li key={index}>
            {component.dna_statement} — {component.signal_name.replaceAll("_", " ")}
          </li>
        ))}
      </ul>
      {item.rank_reason && <p className="mt-2 text-xs text-stone-500">{item.rank_reason}</p>}
      {resolution ? (
        <p data-testid="resolution" className="mt-3 text-sm font-medium text-stone-800">
          {resolution}
        </p>
      ) : (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <button
            data-testid="pursue"
            className="rounded bg-stone-900 px-3 py-1 text-sm text-white"
            onClick={() => decide.mutate({ kind: "pursue" })}
          >
            Pursue
          </button>
          <button
            className="rounded border border-stone-300 px-3 py-1 text-sm"
            onClick={() => decide.mutate({ kind: "accept" })}
          >
            Good call
          </button>
          <button
            data-testid="decline"
            aria-label="decline this recommendation"
            className="rounded border border-stone-300 px-3 py-1 text-sm"
            onClick={() => setChipsOpen(true)}
          >
            Decline
          </button>
          {item.has_brief && (
            <Link
              to="/prospects/$prospectId"
              params={{ prospectId: item.prospect_id }}
              className="ml-auto text-sm text-sky-800 underline"
            >
              Read the brief
            </Link>
          )}
        </div>
      )}
      {chipsOpen && !resolution && (
        <div data-testid="chips" className="mt-2 flex flex-wrap gap-1.5">
          {CHIPS.map((chip) => (
            <button
              key={chip.value}
              data-testid={`chip-${chip.value}`}
              aria-label={`decline: ${chip.label}`}
              className="rounded-full border border-stone-300 px-2.5 py-0.5 text-xs"
              onClick={() => decide.mutate({ kind: "decline", chip: chip.value })}
            >
              {chip.label}
            </button>
          ))}
          <button
            className="px-2 py-0.5 text-xs text-stone-500"
            onClick={() => decide.mutate({ kind: "decline" })}
          >
            just decline
          </button>
        </div>
      )}
    </article>
  );
}
