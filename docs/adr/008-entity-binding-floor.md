# ADR-008: Entity-binding confidence floor and the human queue

Status: Accepted
Date: 2026-07-20

## Context

Misattribution is a Class-A failure — deadlier than fabrication because it
verifies partially (Doc 04 §8 A2). Doc 09 §4 rules entity resolution hybrid:
deterministic strong keys first, human floor beneath; §14 (unresolved ADR 5)
requires the confidence floor and queue SLA to be decided.

## Decision

- **Strong keys bind automatically**: website domain (confidence 1.0) and
  register number (1.0) — attestation-grade identity.
- **Everything else queues**: at Epic 4 the only heuristic is normalised-name
  equality (legal suffixes stripped), scored 0.7 — deliberately *below* the
  floor, because colliding names are the misattribution vector (Doc 09 §11).
- **The floor is 0.85** [calibrates]: nothing between 0.85 and strong-key
  certainty exists yet; when richer heuristics arrive (Epic 5's AI
  adjudication), they must clear this floor to bind unattended.
- **Queue SLA**: ambiguous bindings are resolved by the Editor before any
  brief citing the affected items is finalised — enforced by the workbench
  (unbound canonical content cannot become evidence), not by a timer.

## Alternatives considered

Auto-binding exact name matches: cheap coverage, but the same-name-
different-company case is exactly the Class-A trap; rejected.

## Consequences

Ad-library and other name-keyed acquisitions route through the review queue
until resolved — slower, honest, and the human share of resolutions is
itself a cost/quality signal (Doc 09 §10).
