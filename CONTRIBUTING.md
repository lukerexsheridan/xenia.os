# Contributing to Xenia

This document defines how work happens in this repository. It operationalises the
engineering standards of [Doc 08 §11](docs/08_SYSTEM_ARCHITECTURE.md) and the build
philosophy of [Doc 10 §1](docs/10_V1_BUILD_PLAN.md).

## The governing rule

The documents in `docs/` are constitutional. Code implements them.
**A deviation from Documents 01–10 requires an ADR** (`docs/adr/`), and constitutional
deviations escalate to a document amendment. When code and documents disagree, one of
them is wrong — find out which before merging.

## Workflow

- **Trunk-based development.** Short-lived branches off `main`, merged via PR.
  `main` is always deployable; every merge deploys to staging.
- **Every PR uses the self-review checklist** in the PR template. At team-of-one this
  is a written self-review, actually performed (Doc 10 §1, principle 3).
- **Ship weekly or cut scope.** A task that doesn't fit a week becomes two tasks or a
  smaller task. When behind, cut scope — never quality floors (tenancy, audit, receipt
  validation, fabrication gates).
- **Log decisions.** One paragraph per decision in an ADR. Future-you is a different
  engineer. Log debt in `DEBT.md` as it is taken, with dates.

## Code standards

### Backend (Python)

- Python 3.12, `ruff` (lint + format), `mypy --strict`, `pytest`.
- **Dependency direction is law (AP2):** `api → services → domain ← repositories`;
  `ai` and `integrations` are invoked by services through interfaces the domain defines.
  The `domain` package imports nothing but itself and the standard library — no
  SQLAlchemy, no FastAPI, no Pydantic, no OpenAI types. Enforced by import-linter.
- **Services are use-cases** (AP3): one file per named operation (`ComposeBrief`,
  `ApplyCorrection`) — never entity-managers with forty methods.
- **Route handlers translate, only.** A route handler longer than a screen is a code
  smell with a name (logic leaking upward). Same rule for worker job bodies.
- **Repositories are workspace-scoped by constructor.** A repository instance without a
  workspace context must be unrepresentable. SQLAlchemy stays inside `repositories/`.
- Naming uses the documents' ontology verbatim (Doc 08 §11): `Workspace`, `Evidence`,
  `Recommendation`, `DnaChangeEvent`.
- New runtime dependencies are argued in the PR: maintenance cost, security surface,
  and the ten-year question (AP8).

### Frontend (TypeScript)

- TypeScript strict mode; ESLint + Prettier; Vitest.
- **TanStack Query is the only server-state mechanism.** No Redux, no global store of
  server data. Client-local UI state stays in components.
- **No business logic.** Scoring, ranking, confidence-word assignment — all arrive from
  the API as data (AP5). If you are deriving a rule in the client, stop.
- Features live in `src/features/<concept>/` and are the unit of ownership and of
  deletion. `components/ui` holds shadcn-derived primitives; `components/shared` only
  for genuinely cross-feature pieces.

### Migrations

- Alembic, **expand → migrate → contract** for anything hot. Every migration is
  reversible or explicitly flagged with its contraction plan.
- CI runs the autogenerate-diff lint: model/migration drift is a build failure.
- Destructive migrations require an audit entry and a backup point.

### Testing

The pyramid, per Doc 08 §11:

1. **Domain unit tests** — pure, milliseconds, exhaustive. The constitutional rules
   live here; tests for citable rules carry the document reference in their name.
2. **Service tests** against in-memory fakes of repository/provider protocols.
   Fakes are first-class citizens in `tests/`; no mocking libraries against owned code.
3. **API contract tests** — the OpenAPI schema as executable truth.
4. **AI pipeline tests** — deterministic (recorded fixtures) and evaluative (golden-set
   regression, gating, once pipelines exist).
5. **E2E** — happy-path loop walk only (Playwright), once the app exists.

Required tests are part of a task's definition of done, not aspiration.

## Commits and PRs

- Small, focused commits with imperative messages.
- PR descriptions state what changed and which document/ADR governs it.
- Anything touching **money, deletion, tenancy, or prompts** gets the full checklist
  regardless of the week (Doc 10 §8).

## Local environment

See [README.md](README.md). `make check` must pass before every PR — it is exactly
what CI runs.
