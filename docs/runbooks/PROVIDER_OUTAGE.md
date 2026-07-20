# Runbook — AI provider outage

*The model API is down or degraded. The system is built to keep its shape:
deterministic surfaces keep working; composition pauses honestly.*

1. **What still works with no provider:** the queue (scoring is
   deterministic), corrections and their named effects, outcomes, the DNA,
   the weekly email, the whole Editor console, all delivery of already
   approved briefs. Nothing customer-facing lies about the outage.
2. **What pauses:** brief composition and opener drafts. Both fail with an
   explicit error, route nothing to customers, and can simply be retried —
   the research_run job's stages are idempotent and resume past completed
   work by construction.
3. **Do:** confirm with the provider's status page; silence the alert with a
   note; let queued composition jobs retry on backoff (they dead-letter
   rather than spin). If the outage crosses a Monday, the weekly email still
   sends — it reports what exists.
4. **After:** re-run dead-lettered composition jobs; check the ai_call
   ledger for partial spends; note the episode.
