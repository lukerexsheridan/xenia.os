# ADR-003: openapi-typescript for client types

Status: Accepted
Date: 2026-07-19

## Context

AP4 requires TypeScript client types generated from the backend's OpenAPI schema so
frontend/backend drift is a build error. Doc 08 §13 (decision 3) defers the tool choice
to ADR.

## Decision

`openapi-typescript` generates types from the exported schema
(`make openapi` → `frontend/openapi.json` → `npm run generate:api` →
`src/lib/api/schema.d.ts`), consumed by a thin typed fetch wrapper
(`openapi-fetch`) inside `src/lib/api/`.

## Alternatives considered

- **orval / openapi-generator**: generate full client SDKs and query hooks —
  more magic, heavier templates, harder to keep inside the "TanStack Query is the only
  server-state mechanism" rule.
- **Hand-written types**: guarantees drift; rejected on principle (AP4).

## Consequences

- Types-only generation keeps hooks hand-written and legible (`useQueue`, `useBrief`),
  per Doc 08 §4's naming.
- The generated file is a build artefact, not edited by hand; CI exports the schema on
  every run so regeneration is always possible from a green build.
