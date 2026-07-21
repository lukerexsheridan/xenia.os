# Technical Debt Register

Debt is logged with the date it was **taken**, not discovered. An empty
register earlier in this repository's history was itself a debt of honesty;
this file now records what is knowingly owed. Items marked **GA-gating**
must be repaid before onboarding anyone the founder has not personally
provisioned.

## GA-gating

- **2026-07-20 — Hosted auth flow absent (ADR-012).** Sign-in is a pasted,
  founder-issued token; no self-serve signup, no refresh, no sign-out
  round-trip. Server-side verification is final; the client acquisition is
  provisional. *Repay:* wire the hosted Supabase flow before any
  non-provisioned user exists.
- **2026-07-20 — Least-privileged DB role unexercised in CI (ADR-010).**
  Worker and API now attach tenancy context everywhere, but no CI job runs
  the suite as a non-superuser application role beyond the RLS canary's
  probe. *Repay:* a CI lane on a dedicated role, then tighten the
  production role to match.

## Medium (repay within the MVP phase)

- **2026-07-21 — Brand fonts load from Fontshare/Google CDNs** (ADR-014,
  matching xenia-source). Third-party requests on every app load: privacy
  posture + latency. *Repay:* self-host Cabinet Grotesk, IBM Plex Sans,
  and JetBrains Mono before GA.

- **2026-07-20 — The golden-set store is managed but unconsumed.** The
  Editor curates entries; no harness reads them (CI's golden job runs
  static fixtures). The evaluation layer is thinner than Doc 04 describes.
- **2026-07-20 — AI budget is global, not per-workspace.** The ledger has
  no workspace column, so one tenant can exhaust the shared ceiling when
  the governor is enabled. Acceptable for a trusted ~10-partner cohort.
- **2026-07-20 — No rate limiting on /v1.** Authenticated-only, but
  composition endpoints spend tokens per call.
- **2026-07-20 — Stripe subscription events are not ordered.** A late
  `customer.subscription.updated` replayed after `deleted` can resurrect
  an active status. Low likelihood at founding scale; the console shows
  the truth from Stripe's dashboard.
- **2026-07-20 — Known N+1 catalogue.** `GET /v1/queue` (3 queries/item),
  `quality_report` (edits per scored brief), weekly-brief naming
  (2 queries/prospect), assembly signal loads (per prospect). All fine at
  cohort scale; none fine at 100x.
- **2026-07-20 — `app/api/internal/workbench.py` is a god-module** (~950
  lines, ten concerns). Split when it next needs a non-trivial change.

## Low

- **2026-07-20 — Domain shapes awaiting consumers:** `SuppressionEntry`
  and the delegation ladder are constitution-as-code with no call sites
  yet; `Dna.revert` has no API surface despite Doc 03 promising revert.
  Decide per shape at V1.1: wire or remove.
- **2026-07-20 — E2E runs against the Vite dev server**, not the
  production build; the console shell's ~160 lines of inline JS are
  unlinted and untested; frontend component coverage is thin outside the
  queue (DNA view, interview, brief view untested).
- **2026-07-20 — Named-effect diff can mislead across an ISO week
  boundary** (correction lands in a week with no assembled queue).
