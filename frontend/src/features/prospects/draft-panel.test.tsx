/** The opener draft: composed on request, always editable, never sent. */
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { DraftPanel } from "./draft-panel";

function withClient(children: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

afterEach(() => vi.unstubAllGlobals());

describe("DraftPanel", () => {
  it("offers composition when no draft exists, then an editable body", async () => {
    let composed = false;
    vi.stubGlobal(
      "fetch",
      vi.fn(async (_url: string, init?: RequestInit) => {
        if (init?.method === "POST") {
          composed = true;
          return new Response(JSON.stringify({ body: "Brightpath caught my eye", problems: [] }), {
            status: 200,
          });
        }
        return composed
          ? new Response(JSON.stringify({ body: "Brightpath caught my eye", problems: [] }), {
              status: 200,
            })
          : new Response(JSON.stringify({ code: "not_found", message: "no draft yet" }), {
              status: 404,
            });
      }),
    );
    render(withClient(<DraftPanel prospectId="p1" />));
    fireEvent.click(await screen.findByTestId("compose-draft"));
    const body = await screen.findByTestId("draft-body");
    expect((body as HTMLTextAreaElement).value).toContain("Brightpath");
    // The never-sent promise is stated where the draft lives.
    expect(screen.getByTestId("draft-panel").textContent).toContain("never sent by me");
  });
});
