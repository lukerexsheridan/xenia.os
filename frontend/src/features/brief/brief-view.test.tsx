/** The fold (Doc 06 §7 / I5): identity and verdict above, the rest beneath. */
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { BriefView } from "./brief-view";

const BRIEF = {
  brief_id: "b",
  prospect_id: "p",
  sections: [
    {
      code: "b1_identity_snapshot",
      title: "Identity & snapshot",
      content: "Brightpath Ltd.",
      cited_evidence_ids: [],
    },
    {
      code: "b2_what_they_do",
      title: "What they do",
      content: "DTC skincare.",
      cited_evidence_ids: [],
    },
    {
      code: "b5_fit_thesis",
      title: "Fit thesis",
      content: "Worth a conversation.",
      cited_evidence_ids: [],
    },
  ],
  couldnt_see: [],
  confidence_word: "likely",
  receipts: [
    { number: 1, claim: "Running ads", evidence_type: "e1", observed_at: "2026-07-13T09:00:00" },
  ],
  finalised_at: "2026-07-20T00:00:00",
};

afterEach(() => vi.unstubAllGlobals());

describe("BriefView", () => {
  it("puts identity and the fit verdict above the fold, in reading order", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response(JSON.stringify(BRIEF), { status: 200 })),
    );
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const { container } = render(
      <QueryClientProvider client={client}>
        <BriefView prospectId="p" />
      </QueryClientProvider>,
    );
    await screen.findByTestId("brief");
    const text = container.textContent ?? "";
    const fold = container.querySelector("hr");
    expect(fold).not.toBeNull();
    // Above: B1 then B5; below: B2 — the ten-second depth reads first.
    expect(text.indexOf("Brightpath Ltd.")).toBeLessThan(text.indexOf("Worth a conversation."));
    expect(text.indexOf("Worth a conversation.")).toBeLessThan(text.indexOf("DTC skincare."));
  });
});
