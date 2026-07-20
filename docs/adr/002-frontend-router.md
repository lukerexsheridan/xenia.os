# ADR-002: TanStack Router for the SPA

Status: Accepted
Date: 2026-07-19

## Context

Doc 08 §4 leans TanStack Router "for type-safe routes and coherent devtools with
TanStack Query", recording React Router as a defensible alternative and deferring the
ruling to ADR (Doc 08 §13, decision 1; Doc 10 ADR batch #1).

## Decision

TanStack Router, code-based route definitions (file-based generation can be adopted
later without changing the choice).

## Alternatives considered

**React Router**: ubiquitous, stable, but stringly-typed params and no type-level
integration with TanStack Query's cache keys. Since server state is exclusively
TanStack Query (Doc 08 §4), a single mental model and typed search/params win.

## Consequences

- Route params and search params are compile-time checked, consistent with the
  generated-API-types discipline (AP4): drift is a build error.
- One more early-adopter dependency than React Router; accepted within the AP8
  dependency budget because it removes a class of runtime errors.
