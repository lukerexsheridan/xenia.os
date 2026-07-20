# ADR-013: Family-level disqualifier matching

Status: Accepted
Date: 2026-07-20

## Context

Doc 09 §13 ships one alpha disqualifier-trigger rule
(`in_house_marketing_team`). Epic 8's exclusion gate matches at family
level: any fresh DISQUALIFIER_TRIGGERS signal trips any disqualifier law.
With a single trigger rule this is exact; with several laws it cannot know
*which* law a trigger crossed.

## Decision

Keep family-level matching until the trigger taxonomy grows beyond one
rule per semantic law — a per-law mapping designed today would be guessed,
and a guessed mapping that silently fails to exclude is worse than a
coarse one that over-excludes (a visible exclusion invites correction; a
missed disqualifier is a Class A failure).

With one honesty rule, enforced in `exclusion_reason` and pinned by test:
**an exclusion names a specific law only when attribution is unambiguous**
(exactly one distinct matched law); otherwise it names the trigger and says
"crosses your disqualifiers". The queue's judgment moment never carries a
confidently wrong explanation.

## Consequences

- Over-exclusion is possible and visible; the correction loop is the
  remedy, which is the system's intended shape.
- When a second trigger rule lands, this ADR must be revisited with a
  trigger→law mapping table; the honesty rule stays regardless.
