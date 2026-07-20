/**
 * The export defect, pinned closed: a bare <a href> sends no Authorization
 * header, so downloads must go through the authenticated fetch helper.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { download, setToken } from "./client";

describe("authenticated download", () => {
  beforeEach(() => {
    setToken("test-token");
    vi.stubGlobal("URL", {
      createObjectURL: vi.fn(() => "blob:fake"),
      revokeObjectURL: vi.fn(),
    });
  });
  afterEach(() => vi.unstubAllGlobals());

  it("sends the bearer token the browser cannot attach to a plain link", async () => {
    const fetchSpy = vi.fn(async () => new Response(new Blob(["%PDF"]), { status: 200 }));
    vi.stubGlobal("fetch", fetchSpy);
    await download("/v1/dna/document.pdf", "dna.pdf");
    const [, init] = fetchSpy.mock.calls[0] as unknown as [string, RequestInit];
    expect((init.headers as Record<string, string>).Authorization).toBe("Bearer test-token");
  });

  it("surfaces a plain-voice error on failure instead of a broken file", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response("nope", { status: 401 })),
    );
    await expect(download("/v1/dna/document.pdf", "dna.pdf")).rejects.toMatchObject({
      status: 401,
    });
  });
});
