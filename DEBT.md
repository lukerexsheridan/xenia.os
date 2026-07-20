# DEBT.md — the honest ledger of technical debt

Rule (Doc 10 §7): debt is logged **when it is taken**, with a date — unlogged debt is
the compounding kind. One entry per item; remove entries when repaid, noting the date.

Format:

```
## YYYY-MM-DD — short title
What was deferred, why, the consequence of leaving it, and the trigger for repayment.
```

---

*No open debt.*

<!-- Repaid 2026-07-20: "Supabase JWT verification is a stub" (2026-07-19) — real
     verifier (JWKS + HS256) shipped in Epic 1 with the authenticated /v1/me route.
     Repaid 2026-07-20: "Worker is a heartbeat loop, not a queue consumer"
     (2026-07-19) — jobs table, SKIP LOCKED consumer, scheduler, retry/backoff and
     dead-lettering shipped in Epic 1.
     Repaid 2026-07-20: "Sentry wiring not yet installed" (2026-07-20) — sentry-sdk
     initialised from both entrypoints in Epic 3 (app/core/observability.py),
     PII-scrubbed, per ADR-005. -->
