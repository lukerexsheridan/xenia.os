/**
 * The DNA interview: conversational, resumable, homework-first (Doc 03 C1).
 *
 * One question at a time in Xenia's voice; a closed tab loses nothing —
 * the server holds the transcript and always knows the next question.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { useState } from "react";

import { api } from "@/lib/api/client";

export function InterviewView() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const interview = useQuery({ queryKey: ["interview"], queryFn: api.interview });
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);

  const answer = useMutation({
    mutationFn: ({ key, value }: { key: string; value: string }) => api.answerInterview(key, value),
    onSuccess: async (state) => {
      setText("");
      setError(null);
      queryClient.setQueryData(["interview"], state);
      if (state.completed) {
        await queryClient.invalidateQueries({ queryKey: ["dna"] });
        await navigate({ to: "/dna" });
      }
    },
    onError: (mutationError) => setError(mutationError.message),
  });

  if (interview.isPending) return <p className="text-sm text-stone-500">One moment…</p>;
  if (interview.isError) return <p className="text-sm text-red-800">{interview.error.message}</p>;

  const state = interview.data;
  if (state.completed) {
    return (
      <p className="max-w-prose text-sm text-stone-700">
        The interview is done and your DNA is founded — read it on the DNA page and endorse it when
        it&apos;s right.
      </p>
    );
  }

  return (
    <div className="max-w-prose">
      <p className="text-xs text-stone-500">
        Question {state.answered + 1} of {state.total} — stop any time, nothing is lost.
      </p>
      <p data-testid="interview-prompt" className="mt-3 font-serif text-lg text-stone-900">
        {state.prompt}
      </p>
      <textarea
        data-testid="interview-answer"
        className="mt-4 w-full rounded border border-stone-300 p-3 text-[15px]"
        rows={state.one_per_line ? 5 : 3}
        placeholder={state.one_per_line ? "One per line" : "In your own words"}
        value={text}
        onChange={(event) => setText(event.target.value)}
      />
      <button
        data-testid="interview-send"
        className="mt-2 rounded bg-stone-900 px-4 py-2 text-sm text-white"
        onClick={() =>
          state.question_key && answer.mutate({ key: state.question_key, value: text })
        }
      >
        That&apos;s my answer
      </button>
      {error && <p className="mt-2 text-sm text-red-800">{error}</p>}
    </div>
  );
}
