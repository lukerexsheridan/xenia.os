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
    <section data-testid="draft-panel" className="mt-8 border-t border-stone-200 pt-4">
      <h3 className="text-sm font-medium text-stone-700">Your opener — a starting point</h3>
      {body === null ? (
        <button
          data-testid="compose-draft"
          className="mt-2 rounded border border-stone-300 px-3 py-1 text-sm"
          onClick={() => compose.mutate()}
        >
          Draft an opener from the brief
        </button>
      ) : (
        <div className="mt-2">
          <textarea
            data-testid="draft-body"
            className="w-full rounded border border-stone-300 p-3 text-[15px]"
            rows={6}
            value={body}
            onChange={(event) => setText(event.target.value)}
          />
          <div className="mt-1 flex gap-2">
            <button
              className="rounded bg-stone-900 px-3 py-1 text-sm text-white"
              onClick={() => body && save.mutate(body)}
            >
              Save my edit
            </button>
            <button
              className="rounded border border-stone-300 px-3 py-1 text-sm"
              onClick={() => void navigator.clipboard.writeText(body)}
            >
              Copy
            </button>
          </div>
          <p className="mt-1 text-xs text-stone-500">
            Always a draft, never sent by me — it goes out from your own email, in your name.
          </p>
        </div>
      )}
      {note && <p className="mt-2 text-sm text-stone-600">{note}</p>}
    </section>
  );
}
