# DEBT.md — the honest ledger of technical debt

Rule (Doc 10 §7): debt is logged **when it is taken**, with a date — unlogged debt is
the compounding kind. One entry per item; remove entries when repaid, noting the date.

Format:

```
## YYYY-MM-DD — short title
What was deferred, why, the consequence of leaving it, and the trigger for repayment.
```

---

## 2026-07-20 — Sentry wiring not yet installed
ADR-005 accepts Sentry "from first deploy"; the SDK is not yet a dependency and
`SENTRY_DSN` is read but unused. Taken (retroactively logged — it was Epic 0's
unlogged deferral): the skeleton and Epic 1 have no customer traffic, and structured
logs cover local/CI. Consequence: unhandled production exceptions rely on Railway
logs until wired. Repay: before the first staging deploy that serves anyone but the
founder, and no later than Epic 3 (the workbench, the first real users).

<!-- Repaid 2026-07-20: "Supabase JWT verification is a stub" (2026-07-19) — real
     verifier (JWKS + HS256) shipped in Epic 1 with the authenticated /v1/me route.
     Repaid 2026-07-20: "Worker is a heartbeat loop, not a queue consumer"
     (2026-07-19) — jobs table, SKIP LOCKED consumer, scheduler, retry/backoff and
     dead-lettering shipped in Epic 1. -->
