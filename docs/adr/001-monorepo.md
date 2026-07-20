# ADR-001: Monorepo

Status: Accepted
Date: 2026-07-19

## Context

Doc 08 §13 (open decision 4) and Doc 10 §12 (ADR batch #1) require a ruling on
monorepo vs. two repos for backend and frontend.

## Decision

One repository containing `backend/`, `frontend/`, `docs/`, and infrastructure config.

## Alternatives considered

**Two repos** (backend, frontend): cleaner deploy wiring per platform, but splits every
API-contract change across two PRs and lets frontend/backend drift — precisely what
AP4's generated-types discipline exists to prevent.

## Consequences

- One PR can change API + client + contract together (Doc 08's own lean).
- CI paths are scoped per app; Railway and Vercel each watch their subdirectory.
- The docs live beside the code they govern, which the ADR/amendment procedure needs.
