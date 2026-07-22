/**
 * The hosted auth seam (Doc 11 Phase 4; ADR-015 — supersedes ADR-012).
 *
 * Supabase is the auth provider; the backend already verifies real
 * Supabase-issued JWTs (HS256 or JWKS) and needs no change here. This
 * module owns exactly two jobs: (1) hold the current access token in a
 * synchronously-readable cache so the rest of the app never has to go
 * async to read it, kept live via `onAuthStateChange`; (2) the two acts a
 * customer takes — request a magic link, sign out everywhere.
 *
 * When no Supabase project is configured (`VITE_SUPABASE_URL`/
 * `VITE_SUPABASE_ANON_KEY` unset — true in local dev and in CI/E2E today),
 * auth falls back to a manually-pasted token stored in localStorage. This
 * is not a shortcut taken here; it is the dev-only path the product has
 * used since alpha, preserved so existing tests and local development
 * need no Supabase project to run. Production deployments set the two
 * env vars and get the real flow.
 */
import { createClient, type SupabaseClient } from "@supabase/supabase-js";

const DEV_TOKEN_KEY = "xenia_access_token";

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL ?? "";
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY ?? "";

export function isSupabaseConfigured(): boolean {
  return Boolean(SUPABASE_URL && SUPABASE_ANON_KEY);
}

let supabaseClient: SupabaseClient | null = null;
function getSupabaseClient(): SupabaseClient {
  supabaseClient ??= createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true },
  });
  return supabaseClient;
}

// The synchronously-readable cache every API call reads from. Kept live by
// onAuthStateChange, which Supabase guarantees fires once immediately with
// the current state (a persisted session, a magic-link session detected
// from the URL, or null) — that first firing is what "primed" waits for.
let cachedToken: string | null = null;
let primed = !isSupabaseConfigured();
let resolvePrimed: (() => void) | null = null;
const primedPromise = new Promise<void>((resolve) => {
  if (primed) resolve();
  else resolvePrimed = resolve;
});

if (isSupabaseConfigured()) {
  getSupabaseClient().auth.onAuthStateChange((_event, session) => {
    cachedToken = session?.access_token ?? null;
    if (!primed) {
      primed = true;
      resolvePrimed?.();
    }
  });
} else {
  cachedToken = localStorage.getItem(DEV_TOKEN_KEY);
}

/** Awaited once at boot, before the router's auth guard runs. */
export function initAuth(): Promise<void> {
  return primedPromise;
}

export function getCachedAccessToken(): string | null {
  return cachedToken;
}

/** Dev-fallback only: the pasted-token screen writes here directly. */
export function setDevToken(token: string): void {
  cachedToken = token;
  localStorage.setItem(DEV_TOKEN_KEY, token);
}

export async function signInWithMagicLink(email: string): Promise<void> {
  const { error } = await getSupabaseClient().auth.signInWithOtp({
    email,
    options: { emailRedirectTo: window.location.origin },
  });
  if (error) throw error;
}

/** Signs out everywhere (Doc 11 Phase 4: revocation, not just this tab). */
export async function signOut(): Promise<void> {
  if (isSupabaseConfigured()) {
    await getSupabaseClient().auth.signOut({ scope: "global" });
  } else {
    cachedToken = null;
    localStorage.removeItem(DEV_TOKEN_KEY);
  }
}
