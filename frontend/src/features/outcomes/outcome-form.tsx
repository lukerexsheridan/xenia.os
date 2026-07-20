/**
 * Outcome capture: ground truth, always yours to state, never inferred
 * (Doc 03 §7). One tap per stage; the win narrates what it taught.
 */
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { api, type OutcomeKind } from "@/lib/api/client";

const STAGES: { kind: OutcomeKind; label: string }[] = [
  { kind: "contacted", label: "Contacted" },
  { kind: "replied", label: "They replied" },
  { kind: "meeting", label: "Meeting booked" },
  { kind: "won", label: "Won" },
  { kind: "lost", label: "Lost" },
  { kind: "disqualified", label: "Disqualified" },
];

export function OutcomeForm({ prospectId }: { prospectId: string }) {
  const queryClient = useQueryClient();
  const [note, setNote] = useState<string | null>(null);

  const record = useMutation({
    mutationFn: (kind: OutcomeKind) =>
      api.recordOutcome(prospectId, kind, new Date().toISOString()),
    onSuccess: (response) => {
      setNote(
        response.reinforced_statements.length > 0
          ? `Recorded — and I learned from it: ${response.reinforced_statements.join("; ")} now weighs more.`
          : "Recorded. Ground truth is the most valuable thing you give me.",
      );
      void queryClient.invalidateQueries({ queryKey: ["queue"] });
    },
    onError: (error) => setNote(error.message),
  });

  return (
    <section data-testid="outcome-form" className="border-hairline mt-8 border-t pt-4">
      <h3 className="text-ink text-sm font-medium">What happened?</h3>
      <div className="mt-2 flex flex-wrap gap-2">
        {STAGES.map((stage) => (
          <Button
            key={stage.kind}
            data-testid={`outcome-${stage.kind}`}
            variant="outline"
            onClick={() => record.mutate(stage.kind)}
          >
            {stage.label}
          </Button>
        ))}
      </div>
      {note && (
        <p data-testid="outcome-note" className="animate-settle-in text-ink mt-3 text-sm">
          {note}
        </p>
      )}
    </section>
  );
}
