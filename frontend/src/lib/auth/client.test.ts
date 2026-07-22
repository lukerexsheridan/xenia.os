/**
 * The auth seam's actual logic: which flow is active, and — when Supabase
 * is configured — that the synchronous token cache tracks
 * onAuthStateChange and that sign-out/sign-in delegate correctly. The SDK
 * itself is mocked; we're testing our wiring, not Supabase's client.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

describe("isSupabaseConfigured", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  it("is false when no Supabase project is configured (today's default)", async () => {
    const { isSupabaseConfigured } = await import("./client");
    expect(isSupabaseConfigured()).toBe(false);
  });
});

describe("the Supabase-backed flow", () => {
  let authStateCallback: ((event: string, session: unknown) => void) | undefined;
  const signInWithOtp = vi.fn(async () => ({ error: null }));
  const signOut = vi.fn(async () => ({ error: null }));

  beforeEach(() => {
    vi.stubEnv("VITE_SUPABASE_URL", "https://xyz.supabase.co");
    vi.stubEnv("VITE_SUPABASE_ANON_KEY", "anon-key");
    vi.resetModules();
    vi.doMock("@supabase/supabase-js", () => ({
      createClient: () => ({
        auth: {
          onAuthStateChange: (cb: (event: string, session: unknown) => void) => {
            authStateCallback = cb;
            // Supabase fires once immediately with the current (here: null) state.
            cb("INITIAL_SESSION", null);
            return { data: { subscription: { unsubscribe: vi.fn() } } };
          },
          signInWithOtp,
          signOut,
        },
      }),
    }));
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    vi.doUnmock("@supabase/supabase-js");
    vi.resetModules();
  });

  it("is configured, and the token cache tracks auth state changes", async () => {
    const { isSupabaseConfigured, getCachedAccessToken, initAuth } = await import("./client");
    expect(isSupabaseConfigured()).toBe(true);
    await initAuth(); // resolves on the guaranteed initial firing
    expect(getCachedAccessToken()).toBeNull();

    authStateCallback?.("SIGNED_IN", { access_token: "live-token" });
    expect(getCachedAccessToken()).toBe("live-token");

    authStateCallback?.("SIGNED_OUT", null);
    expect(getCachedAccessToken()).toBeNull();
  });

  it("delegates sign-in and global-scope sign-out to the SDK", async () => {
    const { signInWithMagicLink, signOut: signOutFn } = await import("./client");
    await signInWithMagicLink("founder@agency.example");
    expect(signInWithOtp).toHaveBeenCalledWith(
      expect.objectContaining({ email: "founder@agency.example" }),
    );
    await signOutFn();
    expect(signOut).toHaveBeenCalledWith({ scope: "global" });
  });
});
