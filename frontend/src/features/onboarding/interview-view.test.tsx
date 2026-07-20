/** The interview: resumable, transcript visible, answers amendable (I6). */
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { InterviewView } from "./interview-view";

const STATE = {
  question_key: "service_need_evidence",
  prompt: "What visible signs give it away?",
  one_per_line: false,
  answered: 2,
  total: 5,
  completed: false,
  dna_created: false,
  transcript: [
    {
      question_key: "homework",
      prompt: "Tell me about your shop.",
      text: "We run paid social.",
      one_per_line: false,
    },
    {
      question_key: "business_attributes",
      prompt: "Picture the clients.",
      text: "DTC brands",
      one_per_line: false,
    },
  ],
};

afterEach(() => vi.unstubAllGlobals());

function renderView() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <InterviewView />
    </QueryClientProvider>,
  );
}

describe("InterviewView", () => {
  it("shows the transcript and lets an earlier answer be amended in place", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response(JSON.stringify(STATE), { status: 200 })),
    );
    renderView();
    expect(await screen.findByText("We run paid social.")).toBeDefined();

    fireEvent.click(screen.getByTestId("amend-business_attributes"));
    const box = screen.getByTestId("interview-answer") as HTMLTextAreaElement;
    expect(box.value).toBe("DTC brands"); // the amendment starts from their words
    expect(screen.getByTestId("interview-prompt").textContent).toContain(
      "Changing an earlier answer",
    );
    // The retreat exists: never mind returns to the open question.
    fireEvent.click(screen.getByText("never mind"));
    expect(screen.getByTestId("interview-prompt").textContent).toContain("visible signs");
  });
});
