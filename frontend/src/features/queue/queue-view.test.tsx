/** The empty week reads as integrity, and cards are verdict-first (Doc 06). */
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  createMemoryHistory,
  createRootRoute,
  createRouter,
  RouterProvider,
} from "@tanstack/react-router";
import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { QueueView } from "./queue-view";

/** Cards contain router Links, so the component renders inside a router. */
function renderQueue() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const router = createRouter({
    routeTree: createRootRoute({ component: QueueView }),
    history: createMemoryHistory(),
  });
  return render(
    <QueryClientProvider client={client}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  );
}

function mockQueue(payload: unknown) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response(JSON.stringify(payload), { status: 200 })),
  );
}

afterEach(() => vi.unstubAllGlobals());

describe("QueueView", () => {
  it("renders the empty week as deliberate, never as failure", async () => {
    mockQueue({ week_key: "2026-W30", items: [] });
    renderQueue();
    expect(await screen.findByTestId("empty-week")).toBeDefined();
    expect(screen.getByText(/quiet week/i)).toBeDefined();
    expect(screen.queryByTestId("queue-card")).toBeNull();
  });

  it("renders verdict-first cards with the API's confidence word verbatim", async () => {
    mockQueue({
      week_key: "2026-W30",
      items: [
        {
          recommendation_id: "r1",
          prospect_id: "p1",
          business_name: "Brightpath Ltd",
          polarity: "recommended",
          rank: 1,
          confidence_word: "likely",
          components: [
            {
              dna_statement: "Hiring for marketing roles",
              signal_name: "hiring_marketing_role",
              signal_family: "hiring",
              supporting_evidence_ids: [],
              contribution: 0.7,
            },
          ],
          rank_reason: null,
          exclusion_reason: null,
          has_brief: false,
        },
        {
          recommendation_id: "r2",
          prospect_id: "p2",
          business_name: "Franchico",
          polarity: "excluded",
          rank: null,
          confidence_word: "uncertain",
          components: [],
          rank_reason: null,
          exclusion_reason: "ruled out Franchico — franchise model, your disqualifier",
          has_brief: false,
        },
      ],
    });
    renderQueue();
    expect(await screen.findByText(/Brightpath Ltd/)).toBeDefined();
    expect(screen.getByTestId("confidence-word").textContent).toBe("likely");
    // The visible exclusion sits at the queue's end with its reasoning.
    expect(screen.getByTestId("visible-exclusions").textContent).toContain("your disqualifier");
  });
});
