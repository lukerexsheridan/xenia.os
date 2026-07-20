/** The DNA document: grouped, endorsable, revertible where honest. */
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { DnaView } from "./dna-view";

const DNA = {
  dna_id: "d",
  version: 3,
  endorsed: false,
  elements: [
    {
      element_id: "e1",
      category: "disqualifiers",
      statement: "No franchise businesses",
      decay_class: "customer_law",
      origin: "interview",
    },
  ],
  changelog: [
    {
      event_id: "ev1",
      cause: "correction",
      author: "customer",
      element_statement: "Old element",
      occurred_at: "2026-07-20T00:00:00",
      reversible: true,
    },
    {
      event_id: "ev2",
      cause: "interview",
      author: "customer",
      element_statement: "No franchise businesses",
      occurred_at: "2026-07-19T00:00:00",
      reversible: false,
    },
  ],
  proposals: [],
};

afterEach(() => vi.unstubAllGlobals());

describe("DnaView", () => {
  it("groups by category, offers endorsement, and reverts only where honest", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response(JSON.stringify(DNA), { status: 200 })),
    );
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={client}>
        <DnaView />
      </QueryClientProvider>,
    );
    expect(await screen.findByText("Hard lines — never crossed")).toBeDefined();
    expect(screen.getByTestId("endorse")).toBeDefined();
    // Revert is offered only on reversible entries — never dishonestly.
    expect(screen.getByTestId("revert-ev1")).toBeDefined();
    expect(screen.queryByTestId("revert-ev2")).toBeNull();
  });
});
