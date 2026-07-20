# CLAUDE.md

# Xenia Engineering Operating Manual

This document defines the permanent operating rules for Claude Code when working on Xenia.

These rules apply to every implementation unless the user explicitly overrides them.

---

# Mission

Build Xenia as a world-class software company.

Every engineering decision should optimise for:

- Simplicity
- Reliability
- Maintainability
- Scalability
- Performance
- Security
- Developer experience

Always optimise for long-term quality over short-term speed.

---

# Constitutional Documents

The `docs/` directory is the constitutional source of truth.

Before implementing anything:

1. Read all relevant documentation.
2. Read all ADRs.
3. Read the Build Plan.
4. Review the existing implementation.

If documentation conflicts with code:

- Assume documentation is correct.
- Explain the conflict.
- Propose the smallest correction.
- Stop if the conflict is significant.

Never silently diverge from the documented architecture.

---

# Previous Epic Review

Before beginning a new Epic:

- Review the previous Epic.
- Verify architectural integrity.
- Verify dependency direction.
- Verify documentation consistency.
- Verify test quality.
- Verify security.
- Verify naming consistency.
- Verify maintainability.

Small improvements may be made immediately.

Major architectural changes must be proposed before implementation continues.

---

# Scope Control

Implement exactly one Epic.

Never implement future Epics.

Never add features outside the current Epic.

Never introduce speculative functionality.

Never build "while we're here" improvements.

---

# Architecture Rules

Follow the documented architecture exactly.

Business logic belongs ONLY in the backend.

Maintain dependency direction.

Respect Clean Architecture boundaries.

Never bypass architectural layers.

Never leak infrastructure into the domain.

Never leak persistence into business logic.

Keep the domain pure.

---

# Engineering Philosophy

Prefer:

- Simple
- Deterministic
- Explicit
- Readable
- Testable

Avoid:

- Clever abstractions
- Premature optimisation
- Hidden behaviour
- Magic
- Global state
- Tight coupling

Every abstraction must have a clear reason to exist.

---

# AI Philosophy

Use AI only where it creates genuine value.

Prefer deterministic software whenever possible.

AI should assist judgement.

AI should never replace deterministic business rules.

Every AI output must be reviewable.

Every AI conclusion must be traceable.

---

# Code Quality

Write production-quality code only.

No temporary hacks.

No undocumented TODOs.

No commented-out code.

No dead code.

No speculative abstractions.

If something can be simplified, simplify it.

---

# Testing

Every feature must include appropriate tests.

Run all relevant checks before completion.

Backend:

- Ruff
- Formatter
- Mypy
- Pytest
- Import Linter
- Alembic validation

Frontend:

- ESLint
- Prettier
- TypeScript
- Vitest
- Production Build

Never ignore warnings without explanation.

---

# Self Review

Before considering work complete:

Perform a senior engineer review.

Review:

- Architecture
- Simplicity
- Maintainability
- Readability
- Security
- Performance
- Error handling
- Test quality
- Documentation
- Naming

Challenge unnecessary complexity.

Refactor anything below the project's standards.

---

# Git Workflow

When all of the following are true:

- Current Epic complete
- Tests pass
- Build passes
- Review passes
- Documentation updated

Then:

1. Stage relevant files.
2. Create one logical commit.
3. Use Conventional Commits.

Examples:

feat(epic-3): implement research workbench

fix(auth): resolve JWT verification

refactor(domain): simplify delegation rules

Never commit broken code.

Never create unnecessary commits.

Never push automatically.

Wait for approval before pushing.

---

# Pre-Commit Checklist

Before creating a commit, verify:

- The implementation matches the constitutional documents.
- No future Epic functionality has been introduced.
- Tests are green.
- Static analysis is clean.
- Documentation is up to date.
- The repository is in a deployable state.
- The commit represents one logical unit of work.

If any item fails, fix it before committing.

---

# Documentation

Keep documentation synchronised with the implementation.

Update documentation whenever architecture changes.

Update ADRs whenever architectural decisions change.

Never allow documentation drift.

---

# Communication

Before implementation:

Provide:

- Implementation plan
- Affected files
- Architectural decisions

After implementation provide:

- Summary
- Files changed
- Tests run
- Build results
- Review findings
- Documentation updates
- Architectural decisions
- Technical debt
- Suggested next step

---

# Technical Debt

Do not create technical debt intentionally.

If technical debt is unavoidable:

- Explain why.
- Record it.
- Propose a repayment plan.

---

# Continuous Improvement

Leave the repository cleaner than you found it.

Small improvements are encouraged.

Large refactors require approval.

Every Epic should improve the codebase.

---

# Default Behaviour

Unless explicitly instructed otherwise:

- Review the previous Epic.
- Read the documentation.
- Stay within the current Epic.
- Test everything.
- Review everything.
- Update documentation.
- Create one logical commit.
- Stop and wait for approval.

---

# Stop Conditions

Stop immediately and wait for approval if:

- The constitutional documents conflict.
- A new ADR is required.
- An architectural change affects future Epics.
- The implementation requires changing Epic scope.
- A dependency is proposed that was not previously justified.
- Security implications are uncertain.
- Tests cannot be made green without changing documented behaviour.
- The requested implementation conflicts with the Engineering Operating Manual.

Do not guess.

Explain the issue, present options with trade-offs, and wait for approval before proceeding.

---

# Decision Making

When multiple implementations satisfy the requirements:

Choose the solution that is:

1. Simplest.
2. Most maintainable.
3. Most aligned with the documented architecture.
4. Easiest to understand six months from now.
5. Easiest to extend without rewriting.

Avoid optimising for today's convenience at the expense of tomorrow's maintainability.

---

# Appendix — Project Context

## What this is

Xenia is an AI Sales Intelligence product ("an AI employee that finds and researches
your ideal clients") for founder-led UK performance-marketing agencies. This repo is a
**modular monolith**: FastAPI backend (API + worker, one image, two entrypoints) and a
Vite/React SPA, on PostgreSQL, deployed to Railway + Vercel.

## The constitution

`docs/01`–`docs/10` are the source of truth; the most-consulted:

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
make coverage-domain  # domain coverage gate (>=95%)
make lint / make format / make typecheck
make migrate / make revision m="message"
make openapi      # export OpenAPI schema for frontend codegen
```

Backend-only equivalents run from `backend/` with `uv run <tool>`; frontend from
`frontend/` with `npm run <script>`.

## Current state

**Epics 0–10 complete; Epic 11 not started.** Epic 1: the load-bearing core —
Workspace/User with workspace-scoped repositories and Postgres RLS (enabled + forced
on Ring-1 tables — the tenancy canary in `backend/tests/repositories/test_rls.py` is
permanent), Supabase JWT verification (`/v1/me` provisions workspace + owner,
audited), the append-only audit stream, feature flags, the Postgres job queue
(`SKIP LOCKED`, retry/backoff, dead-letter) with worker + scheduler + heartbeat
email, and the idempotent Stripe webhook receiver. Epic 2: the constitution as pure
code in `app/domain` — the DNA aggregate and its laws, the delegation ladder with
the never-automatic floor, four-word confidence banding, the Prospect/BusinessRecord
ring split, SuppressionEntry, the teaching shapes — every citable rule has a
doc-referenced test and domain coverage is CI-gated at ≥95%. Epic 3: the research
workbench — the politeness engine (N2's single enforcement point:
`app/integrations/sources/politeness.py`), the content-addressed snapshot store
(S3/MinIO + Ring-2 provenance rows), the fetch CLI (`python -m app.scripts.fetch`),
Evidence with the E1–E5 taxonomy and deterministic receipt tables, ResearchBrief
B1–B8 with the completeness floor, Ring-1 persistence for prospects/DNA (append-only
changelog)/briefs/edit log, the Editor-authorised internal sub-app at `/internal`
(its Swagger UI is the workbench's ugly-but-honest surface), deterministic
golden-file PDF renderers for the brief and the DNA document, and Sentry wiring.
Epic 4: source ingestion — the four-family alpha (ADR-007: Companies House, ad
library, websites, hiring) as fixture-tested adapters over the politeness engine,
the canonical content model with near-dup collapse, entity binding v1 (strong keys
bind, everything else queues for the Editor — ADR-008), the human floor queue,
source-health telemetry, and `AcquireFootprint` wiring it all behind
`/internal/workbench/business-records/{id}/acquire`. Epic 5: the evidence & knowledge layer —
deterministic extractors (Filing/AdRecord/Posting → Evidence, zero tokens), the
first AI pipeline (`app/ai`: schema-constrained page extraction, span-grounding
kills ungrounded claims, usage metered to the ai_call_records ledger),
content-derived Evidence IDs (ADR-009: extraction idempotent, receipt tables
replayable), the graph as columns (corroborates/conflicts/supersedes;
same-domain repetition never corroborates), and the four signal families as
rules with derivations stored and deterministic freshness decay (the daily
signal_decay_sweep job re-derives — stale signals demote toward unknown).
Epic 6: research orchestration —
the rules-based planner (`app/services/research_run.py`: cold/delta/refresh
recipes, cache-aware — stale or absent signal families re-verify, fresh ones
never re-crawl), recipe fetch budgets that bind structurally and degrade into
honest couldn't-see, per-family coverage reports computed from the plan, the
per-stage ledger, and "research this business" as one queued idempotent job
(research_run) whose retry resumes past completed work by construction.
Epic 7: brief generation — the contained composition pipeline
(`app/ai/pipelines/compose_brief.py`: B1–B8 against a frozen numbered receipt
table, bounded regeneration MAX_ATTEMPTS=2 with failures fed back), the
deterministic L0 battery (`app/ai/validation/l0.py`: citation binding,
structure, banned vocabulary, false-precision regex, entity consistency — pure
code holds the only door), machine briefs stored as DRAFTs with full derivation
(pipeline/prompt versions + receipt-table evidence IDs) so the Editor gate
remains the only exit, the rubric ship bar in `app/domain/rubric.py`
(≥16/20, no dimension <2, accuracy-0 zeroes the brief), rubric persistence +
the QA-delta dial (`quality_report`: unedited-pass = ship-bar pass AND zero
edit-log entries), and the CI golden-regression job now genuinely runs
`pytest tests/ai` when `backend/app/ai/` changes.
Epic 8: the loop's back half — deterministic DNA-x-signals scoring decomposed
per element (`app/domain/recommendation.py`; disqualifier exclusion runs
before ranking exists and `excluded_by_disqualifier` takes no score,
structurally), the bounded weekly queue (capacity 10, never padded, visible
exclusion at the end, rank reasons as data), the ratified Doc 06 chip
taxonomy (`app/domain/decision.py`: pattern chips generalise at the
3-occurrence threshold, the structural chip raises a DnaProposal for
endorsement, we-know-them/evidence-wrong teach nothing), corrections applied
synchronously with the named effect (a deterministic queue diff), WON
outcomes reinforcing exactly the elements in the stored decomposition,
`/v1` loop endpoints (queue/decision/corrections/outcomes/proposals), the
Monday assembly job + 14-day outcome prompt, and migration 0006 (five Ring-1
tables; decisions/corrections/outcomes have no UPDATE/DELETE policies at
all — append-only by absence).
Epic 9: the Editor console — the grading queue and quality report
(`grading-queue`, everything unscored, MVP samples 100%), the approval gate
(`approval-queue` + the existing finalise act; the delivery read model
`deliverable_for_prospect` bakes FINAL into the query and takes no status
parameter, so `/v1/prospects/{id}/brief` structurally cannot serve a draft —
the gate-enforcement test proves it), golden-set management (`app/evaluation/
golden.py`: only approved briefs may enter, every entry carries its
reasoning; migration 0007), the source-health page, and the one-file
no-framework console shell at `/internal/console` (dataless HTML; every byte
of data comes from the Editor-authorised workbench API). DomainRuleViolation
now maps to HTTP 422 globally.
Epic 10: the frontend alpha — /v1 grew the loop's remaining surfaces (the
deterministic scripted interview in `app/domain/interview.py` — resumable,
homework-first, the customer's words become the founding DNA verbatim;
migration 0008 — GET/POST /v1/interview*, GET /v1/dna + changelog +
proposals, POST /v1/dna/endorse, brief/DNA PDF export, the N1-safe prospect
CSV, queue items carrying business_name/has_brief as display data) plus
CORS (settings-driven origins). The SPA: token sign-in (hosted Supabase auth
UI arrives with the deployed environment), the authenticated shell, the
queue with verdict-first cards / decline chips / optimistic-then-server
acknowledgments / the visible exclusion / the deliberate empty week, the
brief as a typeset document with receipts and couldn't-see, the DNA document
with endorsement, ten-second corrections returning the named effect, and
proposal signatures, the chat-shaped interview, outcome capture narrating
what a win taught. Types are generated from OpenAPI
(`npm run generate:api`). The Playwright loop-walk
(`frontend/e2e/loop-walk.spec.ts`: signup → interview → endorsement → queue
→ pursue → outcome → correction with named effect) is green and wired into
CI as the `e2e` job.
MVP mode (weekly brief email, drafts, billing, metrics panel) belongs to
Epic 11.
Do not add features, AI implementation, or customer-facing functionality without
explicit instruction — the build plan sequences that work behind founder decisions
and the research-phase gate.

## Conventions worth knowing

- Tests mirror `app/` structure; golden fixtures live under `backend/tests/golden/`.
- Every package has a README stating what lives there and what may import it.
- Migrations: expand → migrate → contract; CI fails on model/migration drift.
- Structured JSON logging via `app/core/logging.py`; IDs only, never PII or prospect
  content in logs (Doc 05).
- Debt is logged in `DEBT.md` with dates when taken, not discovered later.
