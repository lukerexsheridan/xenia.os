# Runbook — Sev1: a Class A failure reached a customer

*A fabrication, a misattribution, or a disqualifier violation was delivered.
(Doc 04 §9: same-day response; the honesty rule is strategy, not penance.)*

## Declare (anyone, immediately)

1. Say "Sev1" in the founder channel with the workspace id, the brief or
   recommendation id, and one sentence on what is wrong. Declaring wrongly is
   free; not declaring is not.
2. The founder owns the incident from this moment. One owner, always.

## Contain (within the hour)

3. **Stop the artefact spreading.** In the Editor console, confirm the brief
   is not FINAL-reachable: if it was delivered, note the delivery time; the
   `/v1` gate means only finalised briefs can have reached anyone — find who
   finalised it (`audit_entries`, action `research_brief.finalised`).
4. **Check for siblings.** Run the grading queue and the golden set for the
   same business and the same evidence ids. A bad receipt poisons every brief
   citing it: `evidence` → briefs whose `receipt_table` cites the id.
5. If a source adapter caused it, quarantine the family: the politeness
   engine's circuit breaker plus a `source_health_events` note; stop the
   research schedule for that family if needed.

## Tell the customer (same day, before they find it)

6. The founder writes, personally, in the plain voice (Doc 06):
   *"We got this wrong; here's what happened and what has changed."* Name the
   error precisely. Do not soften it into "an inaccuracy may have occurred".
   The wounded buyer's trust survives a confessed error and does not survive
   a discovered cover-up (Doc 01 §12.2).

## Fix (same day)

7. Root cause in writing: which stage failed — extraction, binding,
   composition, L0, or the human gate — and why the L0 battery or the Editor
   did not catch it.
8. Ship the correction: withdraw or supersede the evidence, re-derive
   signals, re-assemble the affected queue, re-finalise a corrected brief if
   one is owed.

## Never again (within the week)

9. **Every Sev1 produces a regression test** — the suite is the company's
   scar tissue, accumulated deliberately (Doc 04 §9). The test cites the
   incident date in its name.
10. Post-incident note in `docs/runbooks/incidents/` (date, cause, fix,
    test), linked from the weekly review.

## Rehearsal

This runbook is rehearsed on a staged incident before the first paying
customer (Doc 10, Sprint 20): seed a staging workspace, hand-finalise a brief
with a deliberate misattribution, then walk steps 1-9 end to end, timed. The
rehearsal log lives beside the incident notes.
