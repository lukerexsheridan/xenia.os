# Xenia

**AI Sales Intelligence — an AI employee that learns who you should sell to, finds and
understands those businesses, and helps you win them.**

This repository is a **modular monolith** implementing the architecture defined in the
constitutional documents under [`docs/`](docs/). Those documents are the source of truth;
this codebase implements them and any deviation requires an ADR
(see [`docs/adr/`](docs/adr/README.md)).

> Current state: **Epics 0–3 complete**. Epic 1: authenticated multi-tenant core
> (Supabase JWT → Workspace/User, workspace-scoped repositories + Postgres RLS),
> append-only audit stream, feature flags, Postgres job queue with worker/scheduler/
> dead-letter, heartbeat email, idempotent Stripe webhook receiver. Epic 2: the
> domain model as pure code — the DNA aggregate and its laws, the delegation ladder
> with the never-automatic floor, confidence banding, the ring split, the teaching
> shapes — named-rule tests at 100% domain coverage. Epic 3: the research workbench —
> politeness engine (robots honour, rate limits, circuit breakers; never evades),
> content-addressed snapshot store + fetch CLI, Evidence (E1–E5) with deterministic
> receipt tables, B1–B8 briefs with frozen receipt tables and replayable derivation
> records, Editor-authorised internal workbench API, and golden-tested PDF renderers
> for the brief and DNA document. No AI implementation, no customer-facing features —
> by design, per the [V1 Build Plan](docs/10_V1_BUILD_PLAN.md); Epic 4 (source
> adapters) awaits the research-phase gate.

## Stack

| Layer | Technology |
|---|---|
| Frontend | React · TypeScript (strict) · Vite · Tailwind · shadcn/ui · TanStack Query · TanStack Router |
| Backend | Python · FastAPI · SQLAlchemy · Alembic · PostgreSQL |
| Auth | Supabase Auth (JWT verification server-side; identity only) |
| AI | OpenAI Responses API, contained behind the `app/ai` provider interface (AP6) |
| Infra | Docker Compose (local) · Railway (API/worker/Postgres) · Vercel (SPA) · GitHub Actions |

## Repository layout

```
docs/            Constitutional documents 01–10 + ADRs (the source of truth)
backend/         FastAPI modular monolith: API + worker (one image, two entrypoints)
frontend/        Vite SPA — "the desk, not the brain" (business logic is backend-only)
docker-compose.yml  Local stack: api, worker, postgres, minio (bucket emulator)
Makefile         Every developer command
```

Backend package boundaries follow the dependency law (AP2, Doc 08):

```
api → services → domain ← repositories
        ↑ ai / integrations invoked by services through domain-defined interfaces
```

Enforced mechanically by import-linter in CI — the domain package imports nothing but
itself and the standard library.

## Getting started

Prerequisites: Docker, Python 3.12+, [uv](https://docs.astral.sh/uv/), Node 22+.

```bash
cp .env.example .env                 # local defaults work out of the box
cp frontend/.env.example frontend/.env
make setup                           # install backend + frontend deps, pre-commit hooks
make dev                             # docker compose up: api, worker, postgres, minio
```

The API serves at <http://localhost:8000> (`GET /v1/health`),
OpenAPI at <http://localhost:8000/openapi.json>.
Run the SPA dev server separately with `make dev-frontend` (<http://localhost:5173>).

## Developer commands

`make help` lists everything. The ones you'll use daily:

| Command | What it does |
|---|---|
| `make check` | Everything CI runs: lint, format-check, types, imports, tests (both apps) |
| `make lint` / `make format` | Ruff + ESLint/Prettier |
| `make typecheck` | mypy --strict + tsc --noEmit |
| `make test` | pytest + vitest |
| `make migrate` | Alembic upgrade head |
| `make revision m="msg"` | New Alembic autogenerate revision |
| `make openapi` | Export the OpenAPI schema (input to frontend type generation) |

## Engineering rules (the short version)

- **Business logic exists only in the backend** (AP5). The frontend renders state and
  collects intent. Even display logic that encodes a rule arrives from the API as data.
- **API-first**: one versioned public surface (`/v1`), additive-only; internal/ops
  endpoints live under `api/internal` and never appear in the public OpenAPI document.
- **Multi-tenancy is never retrofitted**: workspace-scoped repositories by constructor,
  plus Postgres RLS, from the first table (Doc 08 §8).
- **The ubiquitous language is the docs' ontology, verbatim**: `Workspace`, `Evidence`,
  `Recommendation`, `DnaChangeEvent` — never `client`, `data_item`, `suggestion`, `log`.
- **Quality floors are not schedule variables** (Doc 10 §1 rule 7): tenancy, audit,
  the receipt rule, fabrication gates.
- Any deviation from Documents 01–10 requires an ADR (Doc 08 §11).

See [CONTRIBUTING.md](CONTRIBUTING.md) for workflow and [CLAUDE.md](CLAUDE.md) for
AI-assistant context.
