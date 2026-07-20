# ADR-005: Sentry now, tracing backend deferred

Status: Accepted
Date: 2026-07-19

## Context

Doc 08 §9 wants structured logging, error reporting, and OpenTelemetry wiring; §12's
critique explicitly allows deferring the tracing backend if wiring exceeds an afternoon
("Sentry plus structured logs carries a two-service system a long way"). Doc 08 §13
(decision 5) defers vendors to ADR.

## Decision

- **Structured JSON logging** via the standard library (`app/core/logging.py`) — no
  logging dependency; IDs only, never PII or prospect content (Doc 05).
- **Sentry** on both apps, release-tagged, PII-scrubbed, from first deploy.
- **Tracing backend deferred**: OTel wiring is added when the system has enough moving
  parts for traces to answer questions logs cannot (revisit at Epic 6, research
  orchestration). This follows Doc 08 §12's own concession.

## Alternatives considered

Full OTel + hosted backend (Honeycomb/Grafana) from day one: better at scale, an
afternoon-plus of wiring and a vendor decision the skeleton doesn't need.

## Consequences

- A revisit trigger is on record (Epic 6) so the deferral cannot silently become
  permanent.
- Log correlation fields (request ID, workspace ID) are in the log schema from the
  start, so adding trace IDs later is additive.
