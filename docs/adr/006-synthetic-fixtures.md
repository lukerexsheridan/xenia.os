# ADR-006: Synthetic fixtures for every non-production environment

Status: Accepted
Date: 2026-07-19

## Context

Doc 08 §12 names the staging-data strategy a gap: "real-ish data without real customer
data — synthetic workspace fixtures need building". Doc 10 §6 rules: local and staging
run synthetic data; customer data exists only in production. Doc 10 §12 puts the
fixture design in ADR batch #1.

## Decision

- A seed module (`backend/tests/` fixtures now; a `seed` script when Epic 1 adds
  models) generates **synthetic workspaces**: generated agency names, real-shaped fake
  prospects/DNA/evidence, deterministic under a fixed random seed.
- Fixtures are code, versioned with the schema they populate — a migration that breaks
  the seed breaks CI.
- Staging additionally carries the founder's own real test workspace (their data,
  their consent) and nothing else real.
- Recorded source-adapter fixtures (Epic 4's harness) are captured from public pages of
  a small set of stable, named companies and stored under `backend/tests/` — public
  business information per Doc 05's posture, never customer data.

## Alternatives considered

Anonymised production copies: the industry default and a standing Doc 05 violation
(Ring-1 data leaving production); rejected permanently.

## Consequences

- The departure-rule and deletion tests can run destructively anywhere but production.
- Demo environments are always safe to show.
