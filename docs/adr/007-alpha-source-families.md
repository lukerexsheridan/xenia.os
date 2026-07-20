# ADR-007: Four source families at the ingestion alpha

Status: Accepted
Date: 2026-07-20

## Context

Doc 09 §3 specifies six V1 source families; its own engineering critique
(§13) rules "the honest floor for the alpha is four (register, ad library,
websites, jobs) — reviews and news add trust texture but not scoring
backbone, and each deferred adapter is a fortnight returned to brief
quality." Doc 09 §14 (unresolved ADR 1) requires the count to be decided.

## Decision

The Epic 4 alpha ships **four families**: Companies House (register), the
ad transparency library, company websites, and hiring surfaces — exactly
the families whose signals the four active DNA categories consume
(Doc 09 §13; Doc 10 Epic 2). Reviews and news wait for the trust-texture
phase, entering only through the source-admission checklist (Doc 05 §11).

## Alternatives considered

All six at alpha: two more adapters to maintain (the pipeline's true
recurring cost centre, Doc 09 §13) for families that feed no V1 scoring.

## Consequences

- The canonical content model ships `ReviewSet`/`Article` shapes only when
  their families are admitted.
- Coverage gaps from the deferred families are *known* gaps, declared in
  couldn't-see, not discovered (Doc 09 §11).
