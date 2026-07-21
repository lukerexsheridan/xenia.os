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
import { useEffect, useRef, useState } from "react";

import { ConfidenceWord } from "@/components/ui/confidence-word";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorNotice } from "@/components/ui/error-notice";
import { Button } from "@/components/ui/button";
import { CardSkeleton } from "@/components/ui/skeleton";
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

  if (queue.isPending)
    return (
      <div className="max-w-2xl space-y-4">
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
      </div>
    );
  if (queue.isError) return <ErrorNotice message={queue.error.message} />;

  const ranked = queue.data.items.filter((item) => item.polarity === "recommended");
  const excluded = queue.data.items.filter((item) => item.polarity === "excluded");

  if (ranked.length === 0 && excluded.length === 0) {
    return (
      <EmptyState title="A quiet week — deliberately." testId="empty-week">
        Nothing this week met the bar, so nothing is here. I don&apos;t pad the queue: when
        discovery runs thin I say so and keep looking. You&apos;ll see what I checked, and next
        Monday starts fresh.
      </EmptyState>
    );
  }

  return (
    <div className="animate-settle-in max-w-2xl space-y-3">
      <p className="mono-label text-ink-faint">
        Week {queue.data.week_key} · {ranked.length} recommended · one decision per card
      </p>
      {ranked.map((item) => (
        <QueueCard key={item.recommendation_id} item={item} />
      ))}
      {excluded.length > 0 && (
        <section data-testid="visible-exclusions" className="border-hairline border-t pt-4">
          <h3 className="text-ink text-sm font-medium">Ruled out, with reasons</h3>
          {excluded.map((item) => (
            <p key={item.recommendation_id} className="text-ink-muted mt-2 text-sm">
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
  const firstChipRef = useRef<HTMLButtonElement | null>(null);
  const declineRef = useRef<HTMLButtonElement | null>(null);

  // Opening the chips moves focus to the vocabulary; escape retreats and
  // returns focus where it came from (Doc 13 I2's floor).
  useEffect(() => {
    if (chipsOpen) firstChipRef.current?.focus();
  }, [chipsOpen]);

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
    <article data-testid="queue-card" className="panel shadow-card p-4">
      <header className="flex items-baseline justify-between gap-3">
        <h3 className="text-ink font-display text-lg">
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
      <ul className="text-ink-muted mt-2 space-y-1 text-sm">
        {item.components.slice(0, 3).map((component, index) => (
          <li key={index}>
            {component.dna_statement} — {component.signal_name.replaceAll("_", " ")}
          </li>
        ))}
      </ul>
      {item.rank_reason && <p className="text-ink-faint mt-2 text-xs">{item.rank_reason}</p>}
      {resolution ? (
        <p data-testid="resolution" className="animate-settle-in text-ink mt-3 text-sm font-medium">
          {resolution}
        </p>
      ) : (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <Button data-testid="pursue" onClick={() => decide.mutate({ kind: "pursue" })}>
            Pursue
          </Button>
          <Button variant="outline" onClick={() => decide.mutate({ kind: "accept" })}>
            Good call
          </Button>
          <Button
            ref={declineRef}
            data-testid="decline"
            variant="outline"
            aria-label="decline this recommendation"
            aria-expanded={chipsOpen}
            onClick={() => setChipsOpen(true)}
          >
            Decline
          </Button>
          {item.has_brief && (
            <Link
              to="/prospects/$prospectId"
              params={{ prospectId: item.prospect_id }}
              className="text-accent ml-auto text-sm underline underline-offset-2"
            >
              Read the brief
            </Link>
          )}
        </div>
      )}
      {chipsOpen && !resolution && (
        <div
          data-testid="chips"
          role="group"
          aria-label="decline reasons"
          className="animate-settle-in mt-2 flex flex-wrap gap-1.5"
          onKeyDown={(event) => {
            if (event.key === "Escape") {
              setChipsOpen(false);
              declineRef.current?.focus();
            }
          }}
        >
          {CHIPS.map((chip, index) => (
            <button
              key={chip.value}
              ref={index === 0 ? firstChipRef : undefined}
              data-testid={`chip-${chip.value}`}
              aria-label={`decline: ${chip.label}`}
              className="transition-settle border-hairline text-ink hover:bg-paper rounded-full border px-2.5 py-1 text-xs"
              onClick={() => decide.mutate({ kind: "decline", chip: chip.value })}
            >
              {chip.label}
            </button>
          ))}
          <button
            className="text-ink-faint px-2 py-1 text-xs"
            onClick={() => decide.mutate({ kind: "decline" })}
          >
            just decline
          </button>
        </div>
      )}
    </article>
  );
}
