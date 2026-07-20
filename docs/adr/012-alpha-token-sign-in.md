# ADR-012: Alpha token-based sign-in

Status: Accepted (alpha only — a GA blocker by its own terms)
Date: 2026-07-20

## Context

Doc 08 specifies Supabase Auth with the hosted UI. No Supabase project
exists during the build phase, so Epic 10 shipped a sign-in screen that
accepts a pasted access token, verified server-side exactly as a
hosted-flow token would be (same verifier, same claims, same HS256/JWKS
paths).

## Decision

Token paste is acceptable **only** for founder-provisioned design-partner
accounts at alpha. The server-side verification path is final; only the
client-side acquisition of the token is provisional.

## Consequences

- A design partner cannot self-serve sign-up; the founder issues tokens.
  This is compatible with the MVP's concierge posture and incompatible with
  anything beyond it.
- Wiring the hosted Supabase flow (sign-in, refresh, sign-out) is a
  prerequisite for onboarding anyone the founder has not personally
  provisioned. Tracked in DEBT.md as release-gating for GA.
- No token refresh exists: sessions end when the pasted token expires.
