# DEBT.md — the honest ledger of technical debt

Rule (Doc 10 §7): debt is logged **when it is taken**, with a date — unlogged debt is
the compounding kind. One entry per item; remove entries when repaid, noting the date.

Format:

```
## YYYY-MM-DD — short title
What was deferred, why, the consequence of leaving it, and the trigger for repayment.
```

---

## 2026-07-19 — Supabase JWT verification is a stub
`app/integrations/supabase_auth` defines the verifier interface but raises
`NotImplementedError`. Deliberate: the skeleton ships no auth-protected endpoints.
Repay in Epic 1 (Sprint 2, tenancy) — the first authenticated route may not merge
without it.

## 2026-07-19 — Worker is a heartbeat loop, not a queue consumer
`app/workers/main.py` idles with a heartbeat log. The jobs table +
`FOR UPDATE SKIP LOCKED` consumer (Doc 08 §7) arrives in Epic 1/Sprint 3.
