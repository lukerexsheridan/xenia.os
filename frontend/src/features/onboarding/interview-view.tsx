/**
 * The DNA interview: conversational, resumable, homework-first (Doc 03 C1).
 *
 * One question at a time in Xenia's voice; a closed tab loses nothing —
 * the server holds the transcript and always knows the next question.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorNotice } from "@/components/ui/error-notice";
import { TextSkeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api/client";

export function InterviewView() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const interview = useQuery({ queryKey: ["interview"], queryFn: api.interview });
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [amending, setAmending] = useState<string | null>(null);

  const answer = useMutation({
    mutationFn: ({ key, value }: { key: string; value: string }) => api.answerInterview(key, value),
    onSuccess: async (state) => {
      setText("");
      setError(null);
      setAmending(null);
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
      <EmptyState title="The interview is done.">
        Your DNA is founded from your words — read it on the DNA page and endorse it when it&apos;s
        right. From here, corrections are how you teach.
      </EmptyState>
    );
  }

  const amendingQuestion = state.transcript.find((entry) => entry.question_key === amending);
  const activePrompt = amendingQuestion?.prompt ?? state.prompt;
  const activeKey = amendingQuestion?.question_key ?? state.question_key;
  const activeOnePerLine = amendingQuestion?.one_per_line ?? state.one_per_line;

  return (
    <div className="animate-settle-in max-w-prose">
      <p className="text-ink-faint text-xs">
        Question {state.answered + 1} of {state.total} — stop any time, nothing is lost.
      </p>
      {state.transcript.length > 0 && (
        <ul className="border-hairline mt-4 space-y-2 border-l-2 pl-4">
          {state.transcript.map((entry) => (
            <li key={entry.question_key} className="text-sm">
              <span className="text-ink-muted">{entry.text}</span>{" "}
              <button
                data-testid={`amend-${entry.question_key}`}
                className="transition-settle text-accent text-xs hover:underline"
                aria-label={`change your answer: ${entry.text}`}
                onClick={() => {
                  setAmending(entry.question_key);
                  setText(entry.text);
                }}
              >
                change
              </button>
            </li>
          ))}
        </ul>
      )}
      <p
        data-testid="interview-prompt"
        className="text-ink mt-4 font-serif text-lg leading-relaxed"
      >
        {amending ? `(Changing an earlier answer) ${activePrompt}` : activePrompt}
      </p>
      <textarea
        data-testid="interview-answer"
        className="rounded-card border-hairline bg-surface text-ink mt-4 w-full border p-3 font-serif text-[1.0625rem] leading-[1.65]"
        rows={activeOnePerLine ? 5 : 3}
        placeholder={activeOnePerLine ? "One per line" : "In your own words"}
        value={text}
        onChange={(event) => setText(event.target.value)}
      />
      <div className="mt-2 flex items-center gap-2">
        <Button
          data-testid="interview-send"
          size="lg"
          onClick={() => activeKey && answer.mutate({ key: activeKey, value: text })}
        >
          That&apos;s my answer
        </Button>
        {amending && (
          <Button
            variant="quiet"
            onClick={() => {
              setAmending(null);
              setText("");
            }}
          >
            never mind
          </Button>
        )}
      </div>
      {error && <p className="animate-settle-in text-danger-ink mt-2 text-sm">{error}</p>}
    </div>
  );
}
