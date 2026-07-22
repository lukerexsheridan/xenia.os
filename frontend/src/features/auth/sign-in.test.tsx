/**
 * Sign-in branches correctly on whether Supabase is configured — nothing
 * else in the app should have to make that decision.
 */
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/lib/auth/client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/auth/client")>("@/lib/auth/client");
  return { ...actual, isSupabaseConfigured: vi.fn() };
});

describe("SignIn", () => {
  it("renders the magic-link flow when Supabase is configured", async () => {
    const auth = await import("@/lib/auth/client");
    vi.mocked(auth.isSupabaseConfigured).mockReturnValue(true);
    const { SignIn } = await import("./sign-in");
    render(<SignIn />);
    expect(screen.getByTestId("email-input")).toBeDefined();
    expect(screen.queryByTestId("token-input")).toBeNull();
  });

  it("renders the developer fallback when it is not", async () => {
    const auth = await import("@/lib/auth/client");
    vi.mocked(auth.isSupabaseConfigured).mockReturnValue(false);
    const { SignIn } = await import("./sign-in");
    render(<SignIn />);
    expect(screen.getByTestId("token-input")).toBeDefined();
    expect(screen.queryByTestId("email-input")).toBeNull();
  });
});
