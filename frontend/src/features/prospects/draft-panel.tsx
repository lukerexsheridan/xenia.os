/**
 * The opener draft (Doc 03 C6): composed from the approved brief, always
 * editable, never sent — the founder copies it into their own client.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { api } from "@/lib/api/client";

export function DraftPanel({ prospectId }: { prospectId: string }) {
  const queryClient = useQueryClient();
  const draft = useQuery({
    queryKey: ["draft", prospectId],
    queryFn: () => api.draft(prospectId),
    retry: false,
  });
  const [text, setText] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);

  const compose = useMutation({
    mutationFn: () => api.composeDraft(prospectId),
    onSuccess: (response) => {
      if (response.body) {
        setText(response.body);
        setNote(null);
      } else {
        setNote("The draft didn't pass my own checks — try again, or write it in your words.");
      }
      void queryClient.invalidateQueries({ queryKey: ["draft", prospectId] });
    },
    onError: (error) => setNote(error.message),
  });
  const save = useMutation({
    mutationFn: (body: string) => api.editDraft(prospectId, body),
    onSuccess: () => setNote("Saved — it's yours now."),
  });

  const body = text ?? draft.data?.body ?? null;

  return (
    <section data-testid="draft-panel" className="border-hairline mt-8 border-t pt-4">
      <h3 className="text-ink text-sm font-medium">Your opener — a starting point</h3>
      {body === null ? (
        <button
          data-testid="compose-draft"
          className="transition-settle rounded-control border-hairline text-ink hover:bg-paper mt-2 border px-3 py-1.5 text-sm"
          onClick={() => compose.mutate()}
        >
          Draft an opener from the brief
        </button>
      ) : (
        <div className="animate-settle-in mt-2">
          <textarea
            data-testid="draft-body"
            className="rounded-card border-hairline bg-surface text-ink w-full border p-3 font-serif text-[1.0625rem] leading-[1.65]"
            rows={6}
            value={body}
            onChange={(event) => setText(event.target.value)}
          />
          <div className="mt-2 flex gap-2">
            <button
              className="transition-settle rounded-control bg-accent text-accent-ink px-3 py-1.5 text-sm font-medium hover:opacity-90"
              onClick={() => body && save.mutate(body)}
            >
              Save my edit
            </button>
            <button
              className="transition-settle rounded-control border-hairline text-ink hover:bg-paper border px-3 py-1.5 text-sm"
              onClick={() => void navigator.clipboard.writeText(body)}
            >
              Copy
            </button>
          </div>
          <p className="text-ink-faint mt-1.5 text-xs">
            Always a draft, never sent by me — it goes out from your own email, in your name.
          </p>
        </div>
      )}
      {note && <p className="animate-settle-in text-ink-muted mt-2 text-sm">{note}</p>}
    </section>
  );
}
