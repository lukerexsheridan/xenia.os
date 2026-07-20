/** Outcome capture: one tap, and a win narrates its lesson (Doc 03 §7). */
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { OutcomeForm } from "./outcome-form";

function withClient(children: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

afterEach(() => vi.unstubAllGlobals());

describe("OutcomeForm", () => {
  it("offers every stage and narrates what a win taught", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async () =>
          new Response(
            JSON.stringify({
              outcome_id: "o1",
              kind: "won",
              reinforced_statements: ["Hiring for marketing roles"],
            }),
            { status: 200 },
          ),
      ),
    );
    render(withClient(<OutcomeForm prospectId="p1" />));
    for (const stage of ["contacted", "replied", "meeting", "won", "lost", "disqualified"]) {
      expect(screen.getByTestId(`outcome-${stage}`)).toBeDefined();
    }
    fireEvent.click(screen.getByTestId("outcome-won"));
    const note = await screen.findByTestId("outcome-note");
    expect(note.textContent).toContain("I learned from it");
    expect(note.textContent).toContain("Hiring for marketing roles");
  });
});
