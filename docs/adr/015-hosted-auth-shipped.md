# ADR-015: Hosted Supabase auth shipped, superseding ADR-012

Status: Accepted — supersedes ADR-012
Date: 2026-07-22

## Context

ADR-012 accepted paste-a-token sign-in as an alpha-only measure and named
it a GA blocker: no self-serve signup, no refresh, no sign-out round-trip.
It was also, independently, the single most-repeated finding across two
external strategic audits of the product — "nothing else matters until
this is solved."

The backend needed no change to make this real: `SupabaseTokenVerifier`
already verifies genuine Supabase-issued JWTs (HS256 secret or JWKS,
Doc 08 §8), because the paste-a-token screen was always handing it a real
token shape. Only the client's *acquisition* of that token was provisional.

## Decision

Ship magic-link sign-in via `@supabase/supabase-js` as the production
path (`frontend/src/lib/auth/client.ts`): one email field, no password;
entering a new address creates the workspace on first use (the backend's
existing provision-on-first-request behaviour, unchanged); session
persistence and silent refresh are the SDK's documented defaults
(`persistSession`, `autoRefreshToken`); sign-out uses Supabase's
`scope: "global"`, revoking the whole refresh-token family server-side —
"sign out everywhere," not just this tab.

**The developer fallback is kept, not removed.** When `VITE_SUPABASE_URL`
/ `VITE_SUPABASE_ANON_KEY` are unset — true today in local dev and in
CI/E2E, where no live Supabase project exists to click a real magic link
against — the sign-in screen renders the original paste-a-token form
instead. This is a conscious, narrow scope: the app cannot exercise a true
magic-link round trip in a sandboxed CI environment without a live
project and an email inbox, so the dev path remains the tested surface
there, while production deployments (which set the two env vars) get the
real flow. Both paths are covered by tests; the loop-walk E2E continues
to exercise the dev path unchanged.

## Consequences

- ADR-012 is superseded; its GA-gating DEBT.md entry is repaid.
- Session-restoration UX is free: `main.tsx` awaits the auth cache priming
  (which resolves on Supabase's guaranteed first `onAuthStateChange`
  firing — covering both a persisted session and a magic-link session
  detected from the redirect URL) before the router evaluates its first
  guard, so a returning user never sees a flash of the sign-in screen.
- Bundle size grew by ~250KB raw (~40KB gzip) from the Supabase SDK.
  Logged in DEBT.md as low-priority; not worth code-splitting before the
  app has enough routes to split meaningfully against.
- Biometric/Face ID architecture for the future iOS app (Keychain-held
  refresh token, Doc 11 Phase 4) is unaffected and unbuilt — this ADR
  ships the web flow only.
