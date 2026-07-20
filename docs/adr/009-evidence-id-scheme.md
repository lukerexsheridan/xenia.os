# ADR-009: Content-derived Evidence IDs

Status: Accepted
Date: 2026-07-20

## Context

Doc 09 §6 requires Evidence IDs to be "stable, content-derived — the same
observation re-extracted yields the same ID, which is what makes citation
stable across regeneration". Doc 09 §14 (unresolved ADR 4) requires the
derivation scheme to be decided, balancing stability against supersession
semantics.

## Decision

`evidence_id = uuid5(EVIDENCE_NAMESPACE, business_record_id | evidence_type
| claim_slot | normalised(claim) | snapshot_id)`.

- Re-extracting the same snapshot yields byte-identical IDs — extraction is
  idempotent and receipt tables are replayable.
- A *new observation* of the same claim-slot (new snapshot) is a new ID:
  supersession is a temporal chain of distinct observations (Doc 05 §3's
  "superseded, never edited"), linked by the `supersedes` relation column.
- Manual workbench capture generates random IDs (each capture is its own
  observation event); the scheme governs pipeline extraction.

## Alternatives considered

Snapshot-independent IDs (claim-slot keyed): stable across re-observation,
but then a "new" observation would overwrite history — supersession becomes
mutation, violating immutability.

## Consequences

The `evidence` table's primary key doubles as the idempotency key for
extraction (`ON CONFLICT DO NOTHING`); re-runs are harmless by construction.
