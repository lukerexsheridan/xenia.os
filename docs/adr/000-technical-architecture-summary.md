# ADR-000: Technical architecture summary

Status: Accepted
Date: 2026-07-19

## Context

[Doc 08 (Technical Architecture)](../08_SYSTEM_ARCHITECTURE.md) governs all engineering
in this repository and mandates that its summary exist as ADR-000. This record is the
pointer and the précis; the document is the authority.

## Decision

- **Modular monolith** (AP1): one FastAPI application deployed as two processes (API +
  worker) from one image; internal packages with enforced boundaries, not microservices.
- **Dependency direction is law** (AP2): `api → services → domain ← repositories`; `ai`
  and `integrations` invoked by services through domain-defined interfaces; the domain
  package imports only itself and the standard library. Enforced by import-linter in CI.
- **API-first, contract-versioned** (AP4): one public `/v1` surface described by
  OpenAPI; TypeScript client types generated from the schema; internal endpoints
  separately authorised and excluded from the public document.
- **Business logic backend-only** (AP5); the SPA renders state and collects intent.
- **AI contained** (AP6): every model interaction is a typed pipeline in `app/ai` with
  declared schemas, L0 validation, cost metering, and evaluation hooks; the OpenAI
  Responses API sits behind a provider interface.
- **Boring by default** (AP8): Postgres answers most storage questions (including the
  job queue at V1); every new dependency argues its ten-year cost; the whole system
  runs with `docker compose up`.
- **Multi-tenancy belt and braces**: workspace-scoped repositories by constructor +
  Postgres RLS on every Ring-1 table.
- **Platforms**: Railway (API, worker, Postgres), Vercel (SPA), Supabase Auth
  (identity only), Stripe, Resend — each behind an interface or an adapter.

## Alternatives considered

Microservices (complexity cosplay at zero customers); unstructured monolith (a future
rewrite); serverless (fights the worker/queue model and local runnability). All argued
in Doc 08 §1.

## Consequences

Seams exist where services may one day be extracted (AI runtime + evaluation; source
ingestion). The never-changes list (Doc 08 §10) binds at every scale: dependency
direction, receipt rule, Ring-1 isolation, never-automatic floor, evaluation as
release gate, one-engineer-on-a-laptop.
