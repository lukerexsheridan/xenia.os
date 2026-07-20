# CLAUDE.md — AI assistant context for the Xenia repository

## What this is

Xenia is an AI Sales Intelligence product ("an AI employee that finds and researches
your ideal clients") for founder-led UK performance-marketing agencies. This repo is a
**modular monolith**: FastAPI backend (API + worker, one image, two entrypoints) and a
Vite/React SPA, on PostgreSQL, deployed to Railway + Vercel.

## The constitution comes first

`docs/01`–`docs/10` are the **source of truth**. Before implementing anything
non-trivial, read the governing document:

- `docs/03_PRODUCT_STRATEGY_AND_V1_SCOPE.md` — what V1 is and (crucially) is NOT
- `docs/04_INTELLIGENCE_AND_EVALUATION_STANDARD.md` — brief rubric, evaluation harness, failure taxonomy
- `docs/05_DATA_KNOWLEDGE_AND_COMPLIANCE_STANDARD.md` — the receipt rule, ring boundaries, prohibited inferences
- `docs/06_BEHAVIOUR_INTERACTION_AND_EXPERIENCE_STANDARD.md` — voice, 18 design principles, correction loop
- `docs/08_SYSTEM_ARCHITECTURE.md` — architectural principles AP1–AP8, package layout, security
- `docs/09_SOURCE_INGESTION_AND_RESEARCH_PIPELINE.md` — deterministic-vs-AI rulings, pipeline stages
- `docs/10_V1_BUILD_PLAN.md` — epic/sprint sequence, definition of V1, cut order

**Any deviation from the documents requires an ADR in `docs/adr/`.**

## Hard rules (violating these is never acceptable)

1. **Business logic backend-only (AP5).** The frontend renders state and collects
   intent. Even display logic encoding a rule (e.g. which confidence word shows)
   arrives from the API as data.
2. **Dependency direction (AP2):** `api → services → domain ← repositories`; `ai` and
   `integrations` invoked by services through domain-defined interfaces. `app/domain`
   imports ONLY itself + stdlib (no SQLAlchemy/FastAPI/Pydantic/OpenAI). Enforced by
   import-linter (`backend/pyproject.toml` `[tool.importlinter]`).
3. **Tenancy:** repositories are workspace-scoped by constructor; Ring-1 tables get
   Postgres RLS. Never write a cross-tenant query in application code.
4. **The receipt rule:** AI-generated claims must cite validated Evidence IDs; the L0
   validator is deterministic code and holds the only door. Never weaken it.
5. **Never-automatic floor:** no external sending, no disqualifier overrides, no
   structural DNA changes without endorsement, nothing irreversible without a human —
   at any delegation level, regardless of feature requests.
6. **No mass-outreach capability, ever** (Foundation N1). No sequences, no campaign
   builders, no bulk contact export.
7. **The ubiquitous language is the docs' ontology, verbatim:** `Workspace`,
   `Evidence`, `Recommendation`, `DnaChangeEvent`, `Prospect`, `BusinessRecord` —
   never `client`, `data_item`, `suggestion`, `log`.
8. **AI calls only inside `app/ai`** (AP6): typed pipelines, declared schemas, cost
   metering, evaluation hooks. Nothing else imports the provider SDK.
9. **Confidence vocabulary:** exactly four words — confident / likely / possible /
   uncertain — assigned by domain rule, never by the model.
10. **API versioning:** `/v1` is additive-only. Internal endpoints live under
    `api/internal` and are excluded from the public OpenAPI document.

## Commands

```bash
make setup        # install everything (uv + npm + pre-commit)
make dev          # docker compose stack (api, worker, postgres, minio)
make dev-frontend # Vite dev server
make check        # ALL checks — run before claiming anything is done
make test         # pytest + vitest
make lint / make format / make typecheck
make migrate / make revision m="message"
make openapi      # export OpenAPI schema for frontend codegen
```

Backend-only equivalents run from `backend/` with `uv run <tool>`; frontend from
`frontend/` with `npm run <script>`.

## Current state

**Repository skeleton only (Epic 0 of Doc 10).** Domain, services, repositories, ai,
evaluation, integrations packages exist with READMEs and no business logic. Do not add
features, AI implementation, or customer-facing functionality without explicit
instruction — the build plan sequences that work (Epics 1+) behind founder decisions
and the research-phase gate.

## Conventions worth knowing

- Tests mirror `app/` structure; golden fixtures live under `backend/tests/golden/`.
- Every package has a README stating what lives there and what may import it.
- Migrations: expand → migrate → contract; CI fails on model/migration drift.
- Structured JSON logging via `app/core/logging.py`; IDs only, never PII or prospect
  content in logs (Doc 05).
- Debt is logged in `DEBT.md` with dates when taken, not discovered later.
