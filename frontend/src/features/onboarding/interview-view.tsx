/**
 * The DNA interview: conversational, resumable, homework-first (Doc 03 C1).
 *
 * One question at a time in Xenia's voice; a closed tab loses nothing —
 * the server holds the transcript and always knows the next question.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { useState } from "react";

import { ErrorNotice } from "@/components/ui/error-notice";
import { TextSkeleton } from "@/components/ui/skeleton";
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

  if (interview.isPending)
    return (
      <div className="max-w-prose">
        <TextSkeleton lines={2} />
      </div>
    );
  if (interview.isError) return <ErrorNotice message={interview.error.message} />;

  const state = interview.data;
  if (state.completed) {
    return (
      <p className="text-ink-muted max-w-prose text-sm leading-relaxed">
        The interview is done and your DNA is founded — read it on the DNA page and endorse it when
        it&apos;s right.
      </p>
    );
  }

  return (
    <div className="animate-settle-in max-w-prose">
      <p className="text-ink-faint text-xs">
        Question {state.answered + 1} of {state.total} — stop any time, nothing is lost.
      </p>
      <p
        data-testid="interview-prompt"
        className="text-ink mt-3 font-serif text-lg leading-relaxed"
      >
        {state.prompt}
      </p>
      <textarea
        data-testid="interview-answer"
        className="rounded-card border-hairline bg-surface text-ink mt-4 w-full border p-3 font-serif text-[1.0625rem] leading-[1.65]"
        rows={state.one_per_line ? 5 : 3}
        placeholder={state.one_per_line ? "One per line" : "In your own words"}
        value={text}
        onChange={(event) => setText(event.target.value)}
      />
      <button
        data-testid="interview-send"
        className="transition-settle rounded-control bg-accent text-accent-ink mt-2 px-4 py-2 text-sm font-medium hover:opacity-90"
        onClick={() =>
          state.question_key && answer.mutate({ key: state.question_key, value: text })
        }
      >
        That&apos;s my answer
      </button>
      {error && <p className="animate-settle-in text-danger-ink mt-2 text-sm">{error}</p>}
    </div>
  );
}
