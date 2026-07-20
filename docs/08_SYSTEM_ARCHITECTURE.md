# XENIA — TECHNICAL ARCHITECTURE

**The complete system architecture, from V1 through scale**

Version 1.0 · July 2026 · Internal — Engineering. Governed by Documents 01–07.

---

*This document marks the transition from strategy into engineering. It designs the system that implements the V1 scope (Document 03), enforces the Intelligence Standard (04), obeys the knowledge constitution (05), and renders the experience standard (06) — on the agreed stack: React/TypeScript/Vite/Tailwind/shadcn/TanStack Query; Python/FastAPI/SQLAlchemy/PostgreSQL; Docker/Railway/Vercel/GitHub Actions; Supabase Auth; Stripe; Resend; OpenAI Responses API. It is architecture, not implementation: no code, no table definitions, no tickets. One framing honesty up front: "support the company for ten years" is achieved not by predicting ten years of load but by drawing boundaries that survive ten years of change — the boundaries are the architecture; everything inside them is replaceable, and Section 10 says exactly what is expected to be replaced and when.*

---

# SECTION 1 — ARCHITECTURAL PRINCIPLES

**AP1 — Modular monolith, strict internal boundaries.** One deployable FastAPI application (plus its worker twin), organised internally as if it were services: `domain`, `services`, `repositories`, `ai`, `evaluation`, `integrations` are packages with enforced import rules, not folders of convenience. Microservices at zero customers is complexity cosplay; a monolith *without* boundaries is a future rewrite. The modular monolith is the only position consistent with both Document 03's craft-funding narrowness and this document's ten-year boundary claim: when a seam must become a service (Section 10 names the candidates), the seam already exists.

**AP2 — Dependency direction is law.** `api → services → domain ← repositories`, with `ai` and `integrations` invoked *by* services through interfaces the domain defines. The domain package imports nothing but itself and the standard library — no SQLAlchemy, no FastAPI, no OpenAI types. This is what makes the Intelligence Standard's rules (the receipt rule, the ring boundaries, the delegation gates) *testable in milliseconds* as pure logic, and what keeps a future stack change (any layer, either direction) from touching business truth.

**AP3 — Single responsibility at the use-case grain.** Services are named use-cases (`ComposeBrief`, `ApplyCorrection`, `ResolveOutcome`, `ProposeDnaChange`), not entity-managers (`ProspectService` with forty methods is where domain logic goes to hide). Each use-case orchestrates repositories, AI pipelines, and domain rules; each is one file a new engineer reads top to bottom.

**AP4 — API-first, contract-versioned.** The backend exposes one versioned HTTP API (`/v1`) described by OpenAPI, and the web frontend is merely its first client. Future iOS (Foundation 4.6's mobile-native future) is served by the *same* API — which forbids, from day one, any behaviour that exists only as web-app convenience: no endpoint shaped around a React component, no logic in a route handler. TypeScript client types are generated from the OpenAPI schema, making frontend/backend drift a build error rather than a runtime surprise.

**AP5 — Business logic exists only in the backend.** The constitutional instruction, enforced structurally: the frontend renders state, collects intent, and calls the API. Scoring, ranking, DNA evolution, delegation checks, confidence vocabulary assignment, evidence binding — all server-side. The test: the iOS app, when it comes, must be buildable without reimplementing a single rule. (Corollary: even display logic that *encodes* a rule — e.g., which confidence word appears — arrives from the API as data, not derived in the client.)

**AP6 — AI-first means AI-contained.** AI calls are powerful, expensive, and non-deterministic — three reasons they are *never* sprinkled through application code. Every model interaction lives in the `ai` package as a typed pipeline with declared inputs (context, evidence), validated outputs (schemas + L0 checks), cost metering, and evaluation hooks (Section 6). The rest of the codebase calls pipelines the way it calls repositories: through interfaces, ignorant of providers. The OpenAI Responses API is V1's provider *behind* that interface — honouring the Foundation's provider-dependency mitigation architecturally now, cheaply, rather than contractually later, expensively.

**AP7 — Composition over inheritance, protocols over frameworks.** Behaviour is assembled from small typed components (Python `Protocol`s, dependency injection at the app boundary); inheritance hierarchies are limited to trivial data shapes. No framework's base class ever appears in the domain.

**AP8 — Boring by default, novel where the product is novel.** The product's novelty budget is spent entirely on intelligence and experience (Documents 04/06); infrastructure gets none of it. Postgres is the answer to most storage questions (including queues and flags at V1 — Section 7); every new dependency or vendor is argued in a PR against the question "what does this cost us in ten years?"; and the whole system must remain runnable by one engineer on a laptop with `docker compose up`.

---

# SECTION 2 — HIGH-LEVEL SYSTEM ARCHITECTURE

## The subsystems

**Web application (Vercel).** The React SPA — Xenia's desk (Document 06 §11). Static hosting + CDN; no server-side business logic (AP5); talks only to the API.

**Backend API (Railway, Docker).** The FastAPI monolith: all use-cases, all rules, all AI orchestration. Stateless; horizontally scalable from day one by construction (no in-process session state).

**Worker (Railway, Docker).** The same codebase deployed as a second process consuming the job queue (Section 7): research runs, discovery sweeps, weekly briefs, evaluations, cleanup. API and worker share domain/services code — one repo, one image, two entrypoints.

**PostgreSQL (Railway).** The single source of truth: domain state, evidence store, job queue, audit log, feature flags, evaluation records. One database, many schemas-by-convention; pgvector available when (not before) semantic retrieval earns its place (Section 12 challenges it).

**Object storage.** Brief PDFs (the shareable rendering), source snapshots (the provenance contract's re-findability), export bundles (the departure rule). S3-compatible bucket; referenced by key from Postgres, never the reverse.

**Supabase Auth.** Identity only: signup, login, session JWTs. The backend verifies tokens (JWKS) and maps identity → User → Workspace; Supabase never holds domain data and the frontend never touches the database through it (the auth vendor is swappable by construction).

**Stripe.** Billing for the one-plan model (Document 03's billing simplicity): Checkout for entry, customer portal for self-service, webhooks (processed idempotently through the job queue) for state sync. The product never implements payment UI beyond linking out.

**Resend.** The ambient surface (C8): weekly briefs, outcome nudges, delivery in Xenia's voice — sent by workers, templated in code (versioned like prompts, per Document 06's voice law), with delivery telemetry captured for E10's metrics.

**AI provider (OpenAI Responses API).** Behind the `ai` package's provider interface (AP6): structured outputs against declared schemas, tool-use where pipelines need it, usage metering captured per call into the unit-cost ledger.

**Evaluation pipeline.** Not a separate deployment — a set of worker jobs plus internal endpoints implementing the harness (Document 04): L0 validators inline in every pipeline, golden-set regression runs in CI and on demand, L1 grading queues surfaced in the internal console, judge calibration jobs.

**Internal tooling (the Editor console).** The QA gate made software: an internal-only, separately-authorised section of the same API + a lightweight internal UI where the Intelligence Editor reviews sampled briefs against the rubric, processes the grading queue, manages golden sets, watches the source-health board, and — during MVP — approves every brief before delivery (the productised concierge's human seam, Document 03 §11).

## How a request flows (the canonical example: a brief reaches a founder)

Ambient discovery (worker, weekly per workspace) surfaces a candidate → identity resolution binds it to a verified Prospect → the research job assembles evidence via source adapters (Section 6/7), writing Evidence objects with full provenance → the `ComposeBrief` pipeline runs: context assembly (DNA + Memory from Ring 1, evidence table from Ring 2), prompt assembly, model call, output validation (schema + L0: every material claim cites an evidence ID, confidence words legal, structure B1–B8 complete) → failures regenerate or route to the Editor; passes are stored with their full derivation → ranking places it in the bounded weekly queue → the weekly-brief job renders queue + briefs into the Monday email (Resend) and the app state → the founder opens the app: the SPA fetches `/v1/queue`, renders verdict-first per Document 06, corrections post back in the ten-second loop → `ApplyCorrection` updates DNA (changelog entry, effect computed, acknowledgment with named consequence returned synchronously) → decisions, pursuits, and outcomes flow in over days, feeding the learning jobs and the flywheel metrics. Every arrow in that sentence is an auditable record; that is Document 05's inspectability rendered as data flow.

---

# SECTION 3 — BACKEND ARCHITECTURE

## Package layout

```
backend/
  app/
    api/            # HTTP layer: routers, request/response schemas, auth dependencies
      v1/           #   versioned public API (the only public surface)
      internal/     #   Editor console + ops endpoints (separately authorised)
    domain/         # pure business model: entities, value objects, domain rules
    services/       # use-cases: one file per named operation (AP3)
    repositories/   # persistence: SQLAlchemy implementations of domain-defined protocols
    ai/             # AI runtime (Section 6)
      pipelines/    #   typed pipelines: interview, discovery, brief, rank, draft, narrate
      prompts/      #   versioned prompt templates, colocated with their tests
      providers/    #   provider interface + OpenAI Responses implementation
      validation/   #   L0 validators: citation binding, vocabulary, structure, entailment sampling
    evaluation/     # the harness: rubric, golden sets, regression runner, judge, calibration
    integrations/   # outward-facing adapters: stripe/, resend/, supabase_auth/, sources/
      sources/      #   one adapter per data source (Document 05 §6 catalogue), + trust scoring
    workers/        # job definitions, queue consumer, schedules
    core/           # config (typed settings), db session, logging, security, flags, errors
  migrations/       # Alembic
  tests/            # mirrors app/ structure; golden fixtures under tests/golden/
```

## Responsibilities, layer by layer

**API layer.** Translation only: HTTP ↔ use-case. Validates shape (Pydantic), resolves identity and workspace context, calls exactly one service, maps results and domain errors to responses. A route handler longer than a screen is a code smell with a name (logic leaking upward). The `internal/` routers share services but carry Editor-grade authorisation and are never exposed in the public OpenAPI document.

**Domain layer.** The Document 03 ontology as pure objects (Section 5), plus the *rules as functions*: delegation checks, disqualifier enforcement, DNA evolution laws (decay asymmetry, conflict hierarchy), confidence-band assignment, ring-boundary predicates. No IO, no framework, total unit-test coverage — this layer is where the constitutional documents literally become code, and it is small enough to read in an afternoon by design.

**Service layer.** Use-cases (AP3): fetch through repository protocols, decide through domain rules, act through AI pipelines and integrations, record through repositories + audit log. Transactions are drawn at the use-case boundary. Services are where "what happens when a founder declines with a reason" exists as one legible unit.

**Repositories.** Persistence behind protocols the domain defines (`ProspectRepo`, `EvidenceRepo`…). Every repository is workspace-scoped *by constructor* — a repository instance without a workspace context cannot be built (Section 8's tenancy enforcement at the type level; Ring-1 isolation as a compile-time property, not a WHERE-clause habit). SQLAlchemy stays entirely inside this package.

**AI layer / Evaluation layer.** Sections 6 and the harness — colocated with the code they test because AI behaviour and its evaluation are one artefact (a prompt change without its regression run is an unfinished change, enforced in CI).

**Integrations.** Anti-corruption adapters: each external system speaks its own dialect inside its folder and the app's language at the boundary. `sources/` is the largest citizen — one adapter per catalogue source implementing a common protocol (fetch → observe → propose Evidence with provenance), plus per-source trust scoring and the quarantine switch (Document 05 §9–11).

**Workers.** Thin: a job is a named payload + a service call + retry semantics. No business logic in job bodies (the same rule as route handlers, for the same reason).

**Core.** Typed configuration (12-factor, env-driven, fails fast on missing keys), structured logging, security primitives, DB-backed feature flags, the error taxonomy. Utilities live here only if three call-sites exist; premature `utils/` is where architecture goes to dissolve.

---

# SECTION 4 — FRONTEND ARCHITECTURE

**Shape.** A Vite SPA in TypeScript strict mode — the desk, not the brain (AP5). Marketing site and VSL funnel live entirely outside this app (separate deployment, separate concerns, per Document 06's clean split between commercial contexts and the work).

**Routing & layouts.** File-conventional routes under a single authenticated shell layout (the workspace frame: queue, DNA, prospects, settings) plus a minimal public layout (auth screens, shared-brief view). Route guards redirect unauthenticated sessions; the shared-brief route is the one deliberately public surface (Document 06's shareable rendering — its access model is an open founder decision, flagged in Section 13). Router choice: **TanStack Router** for type-safe routes and coherent devtools with TanStack Query — recorded as ADR-001 territory (Section 13) since React Router is a defensible alternative.

**Server state.** TanStack Query is the *only* server-state mechanism: every API resource a typed query/mutation hook (`useQueue`, `useBrief`, `useApplyCorrection`), cache keys standardised per resource, invalidation rules colocated with mutations. No Redux, no global store of server data — duplicated server state is the SPA disease this stack was chosen to avoid. Client-local UI state (panels, drafts-in-progress) stays in components or a tiny store when genuinely shared.

**The correction loop's contract.** The ten-second loop (Document 06 §6) drives the mutation design: corrections apply optimistically (instant visual acknowledgment), the API returns the *named effect* payload ("removes two from this week's queue") which replaces the optimistic ack, and failure rolls back with the plain-voice error pattern. This is the one place the frontend is allowed to feel clever, because latency here is trust.

**Forms.** react-hook-form + zod, with zod schemas *generated from the OpenAPI contract* wherever the API defines the shape — one source of truth (AP4); hand-written schemas only for purely-local forms. The DNA interview is not a form (Document 06 §4): it is a conversation surface with resumable state, built as its own feature.

**Component & feature organisation.** `features/` by product concept (queue, brief, dna, prospects, outcomes, onboarding) — each owning its routes, hooks, and components; `components/ui` for the shadcn-derived primitives, themed once to the visual philosophy (Document 06 §8: typographic hierarchy, one accent, semantic colour tokens for the confidence vocabulary — the four words get design tokens, not ad-hoc styling); `components/shared` only for genuinely cross-feature pieces. Feature folders are the unit of ownership and of deletion — consistent with the do-not-build list's discipline: a cut feature is a deleted folder, not an archaeology project.

**Error handling & loading.** Error boundaries per route with the Document 06 failure voice (plain, competent, no mascots); API errors mapped to the shared error taxonomy so copy is consistent. Loading follows the *prepared* principle: instant skeleton-free renders from cache where possible, and honest waits with Xenia's voice where intelligence genuinely takes time — the "give me until morning" pattern is a designed state, not a spinner. Long-running jobs (research runs) surface as status resources polled via Query, never as hanging requests.

**Caching.** Aggressive Query caching with explicit invalidation on the writes that matter (corrections invalidate queue + DNA; outcomes invalidate prospect + metrics); the weekly rhythm means most sessions open on warm, fresh-enough data — background refetch keeps Monday's queue honest without blocking its render.

---

# SECTION 5 — DOMAIN ARCHITECTURE

The Document 03 ontology, promoted to the domain layer's vocabulary — business concepts and relationships, no tables (persistence shape is the repositories' private business).

**Workspace.** The aggregate root of tenancy and of Ring 1: one agency, its people, its DNA, its prospects-in-relationship, its memory, its grants. Every domain operation executes *within* a workspace context; nothing meaningful exists outside one except Ring-2 knowledge.

**User.** A human within a workspace: identity (from auth), attribution (who taught what — corrections carry their author even while V1 weights them flatly), and the flat-role model of Document 03 (owner/member; the delegation ladder, not roles, is where authority nuance lives).

**Ideal Client DNA.** The versioned aggregate at the system's centre: categorised elements (the ICP schema), each carrying per-element confidence, provenance (which interview answer, correction, or outcome pattern produced it), and decay class (customer law vs. learned preference — the asymmetry as a type distinction, not a flag). Every mutation is a **DnaChangeEvent** in an append-only changelog: cause, before/after, author (human or Xenia), reversibility. Structural changes exist first as **DnaProposals** awaiting endorsement (the human-in-the-loop zone as a state machine).

**Prospect.** A verified business entity in relationship to this workspace: identity binding (the misattribution defence — a Prospect *is* a claim that "this name, this domain, this register entry are one company," with confidence), lifecycle status (surfaced → recommended → pursued → resolved), and its trail of briefs, decisions, and outcomes. Distinct from the Ring-2 **BusinessRecord** (the world's facts about the company, workspace-agnostic); a Prospect *references* a BusinessRecord and adds everything relational.

**Evidence.** The receipt (Document 05 §3): observation + claim binding + provenance contract (source, timestamp, type E1–E5, extraction confidence, entity binding, freshness class). Immutable once written; superseded, never edited; disputable (a correction can mark evidence contested, which propagates per the derivation-graph rule).

**Research Brief.** The composed artefact: B1–B8 sections, each claim linked to Evidence IDs, confidence words assigned by domain rule (never by the model directly — the model proposes, the band-mapping rule disposes), couldn't-see declarations, freshness date, format version (so astonishment scores compare across versions, per the playbook), and its full derivation record (which pipeline, which prompt version, which evidence table — the regeneration and audit substrate).

**Recommendation.** The accountable judgment: prospect + brief + decomposed score (per DNA element, per Document 04's explainability) + queue position + the week it belongs to. The visible exclusion is a Recommendation with negative polarity — same object, same audit trail, different verdict.

**Decision & Correction.** The founder's responses: accept/decline/pursue with optional reason (the chip taxonomy as a typed vocabulary, extensible from harvest); Corrections target an element (evidence item, score factor, DNA element) and produce the *named effect* — the computed consequence returned in the ten-second loop and recorded alongside the correction.

**Draft.** The C6 opener: brief-derived, voice-informed, always human-sent; edits captured as voice-learning telemetry (stored, unused by V1 rules — Document 03's demotion honoured).

**Outcome.** Ground truth: pursued prospect + what happened + when + optional why. Append-only, never inferred (Document 03 §8's rule), the flywheel's title deeds.

**Memory.** The M-classes of Document 05 §4 as a typed store: organisation memory items with recency/repetition grading and re-confirmation state; behavioural aggregates with decay; all inspectable, all changelogged.

**DelegationGrant.** The ladder as data: activity × rung × granted-by × granted-at × revocable-instantly. Domain rules consult grants before any action-shaped operation; the never-automatic list is a hardcoded floor no grant can override.

**SuppressionEntry.** The prospect-rights machinery (Document 05 §8): a business or person who objected, suppressed globally across all workspaces — the one record class that deliberately spans tenancy, because rights-handling outranks ring symmetry (and it is the *only* such class; its uniqueness is documented where it lives).

**SourceRecord & Evaluation objects.** Per-source trust scores, health, quarantine state (the catalogue as data); RubricScores, GoldenBriefs, JudgeVerdicts, CalibrationRecords — the harness's nouns, first-class because Document 04 made evaluation a product organ, not a script.

**Relationships in one paragraph:** a Workspace holds Users, one DNA, Memory, and Prospects; Prospects bind to Ring-2 BusinessRecords and accumulate Briefs, Recommendations, Decisions, Drafts, and Outcomes; Briefs cite Evidence, which cites Sources; Corrections and Outcomes generate DnaChangeEvents through the evolution rules; DelegationGrants gate every acting operation; and the evaluation objects observe all of it without ever entering the customer's world. Every arrow is queryable, which is Document 05's "every arrow is inspectable" landed in the model.

---

# SECTION 6 — AI RUNTIME ARCHITECTURE

How every AI request moves through the platform — one pipeline shape, instantiated per operation (interview, discovery triage, brief composition, ranking, drafting, narration).

**1. Context assembly.** The pipeline declares its context needs; assembly fetches deterministically: the DNA (current version, relevant categories), Memory items (by relevance rules, not similarity magic — V1 retrieval is structured lookup; embeddings wait until a need proves itself, per Section 12), the workspace's teaching history where relevant (recent corrections bind harder — the weighting philosophy), and the **evidence table**: the numbered, typed, dated Evidence rows this generation is allowed to build from. Context assembly is code, not prompt-craft — testable, versioned, and logged in the derivation record.

**2. Prompt assembly.** Versioned templates (`prompts/`, colocated tests) render context into the model conversation: the persona register and vocabulary rules (Document 06) live *here*, once, not scattered; the confidence vocabulary is explained to the model but *assigned* by domain rule afterwards; banned vocabulary is listed for the model and enforced by validator regardless. Prompt versions are release artefacts: a prompt change is a diff, a review, and a regression run (CI-enforced).

**3. Model call.** Through the provider interface: OpenAI Responses API with structured outputs against the pipeline's declared schema; retries with backoff on transport failure; token usage and cost captured per call into the **unit-cost ledger** (workspace × pipeline × day), which feeds the COGS ceiling dashboard (Document 03 §9) and rate governors (Section 8).

**4. Output validation (L0, inline, blocking).** Schema conformance (Pydantic); **citation binding** — every material claim carries evidence IDs from the provided table, and claims citing nothing or citing non-existent IDs reject the output (the receipt rule as a validator, the fabrication defence as architecture); structure completeness (B1–B8, couldn't-see present); vocabulary legality (confidence words from the four; banned register absent); entity-consistency (all claims bind to the one Prospect); entailment sampling flags for the grading queue. Validation failure → bounded regeneration with the failure fed back; repeated failure → the Editor queue, never the customer.

**5. Evaluation hooks.** Every passing output: sampled into the L1 grading queue per the sampling policy (heavier on new prompt versions, new sources, new verticals); scored by the L2 judge where calibrated (advisory until agreement thresholds are met — Document 04's circularity rule); logged with derivation for the regression suite. During MVP, sampling rate is 100% — the QA gate *is* step 5 with a human in it, and the unedited-pass rate falls out of this step's records for free.

**6. Storage.** The artefact plus its full derivation record (pipeline version, prompt version, context snapshot reference, evidence table, validation results, cost). Nothing customer-facing is stored without its derivation — regeneration, audit, and the Sev1 protocol all depend on it.

**7. Learning.** Signals flow back as *events*, never as direct model mutation: decisions, corrections, outcomes enter the learning jobs, which apply the Document 04/05 weighting rules to produce DnaChangeEvents (auto-applied within endorsed categories, proposals where structural) and Memory updates. The "model" that learns per-customer is the DNA + Memory + weighting state — deliberate, inspectable, exportable — not fine-tuned weights; this is what makes the moat auditable and the departure rule honest.

**8. Human feedback.** Corrections apply within one recommendation cycle (the latency requirement from Document 03's loop rule, enforced by the learning jobs' scheduling); the named-effect computation runs synchronously at correction time so the ten-second loop never waits on a batch.

---

# SECTION 7 — BACKGROUND PROCESSING

**Queue choice: Postgres-backed jobs at V1** — a jobs table with `FOR UPDATE SKIP LOCKED` consumption, transactional enqueue (a job and its triggering state change commit together — no lost work, no phantom work), named job types, priorities, and scheduled runs. No Redis, no broker, no new infrastructure until the queue's *measured* profile demands it (Section 10 names the migration trigger). This is AP8 applied where teams most often over-buy.

**Job classes.** **Research & discovery:** ambient weekly sweeps per workspace (batched across the week, not thundering-herded on Monday); directed research runs; identity resolution; freshness refresh sweeps (staleness-driven, per Document 05's half-lives). **Composition:** brief generation, ranking runs, weekly brief assembly. **Communication:** Resend sends (weekly brief Monday 08:00 workspace-local, nudges, outcome checks) with delivery telemetry ingestion. **Evaluation:** golden-set regressions (on AI-touching merges), judge runs, calibration jobs, sampling queue maintenance. **Learning:** signal consolidation (the weekly smoothing pass), DNA decay sweeps, Memory re-confirmation scheduling. **Lifecycle:** Stripe webhook processing (idempotent by event ID), data-retention enforcement (the Document 05 expiry policies as scheduled deletions with audit entries), export bundle builds, departure execution. **Ops:** source-health sampling, dead-letter reprocessing.

**Retry semantics.** Every job idempotent by design (keyed on natural identity — "compose brief for prospect X, week W" runs twice harmlessly); exponential backoff with class-specific caps; poison jobs to a dead-letter state with alerting (a dead research job is an ops signal; a dead *send* job is a customer-facing incident and pages accordingly). Long jobs checkpoint (a research run resumes after its last completed source, not from zero — cost discipline as much as robustness).

**Scheduling.** A single scheduler process (the worker's clock) emits due jobs from schedule definitions in code; workspace-local times respected for the ambient surface (Monday 08:00 *their* time — the employee arrives when the office opens).

---

# SECTION 8 — SECURITY ARCHITECTURE

**Authentication.** Supabase Auth issues JWTs; the API verifies via JWKS (cached, rotated), maps `sub` → User → Workspace membership, and rejects anything else. No session state server-side; internal console access requires a separate role claim and is network-restricted besides.

**Authorization.** Three gates, in order: workspace membership (tenancy), role (owner/member — the few owner-only operations: billing, departure, delegation granting), and **DelegationGrants** for anything action-shaped — with the never-automatic floor hardcoded in domain rules so no grant, role, or bug in *this* layer can authorise what Documents 03/06 forbid.

**Multi-tenancy — belt and braces.** Belt: repository-level scoping (Section 3) — workspace context is a constructor requirement, cross-tenant queries are unrepresentable in application code. Braces: **Postgres RLS** enabled on every Ring-1 table with policies keyed to a per-request session variable set at transaction start — so even a raw-SQL mistake, a future analytics tool, or a compromised query path hits the same wall. Ring-2 tables carry no workspace column at all (structurally incapable of leaking tenancy); the SuppressionEntry's deliberate tenancy-spanning is the documented exception with its own narrow access path.

**Secrets.** Railway/Vercel environment configuration; typed settings fail fast on absence; no secrets in code, logs, or error reports; rotation is a documented runbook from day one (rotating in a panic is how rotation goes wrong).

**Rate limiting & cost governance.** Per-user and per-workspace API limits (generous — this is not an abuse-prone product) plus the limits that actually matter here: **AI-cost governors** — per-workspace daily pipeline budgets aligned to the COGS ceiling, with graceful degradation (research queues rather than fails, and Xenia says "tomorrow morning" per the honest-waits pattern) and alerting before ceilings, not after.

**Audit logging.** An append-only audit stream for every consequential act: DNA changes (the changelog *is* audit), delegation changes, deletions, exports, internal-console actions, auth events. Who, what, when, from-where; queryable; retained per policy. This is simultaneously Document 05's inspectability, the Sev1 forensics substrate, and the future SOC 2 down-payment.

**Validation & encryption.** Pydantic at every boundary (nothing unvalidated crosses into services); TLS everywhere; encryption at rest via managed Postgres and bucket defaults; personal-data fields inventoried (the Document 05 professional-minimum means the inventory is short — by design) with the deletion machinery (rights requests, departure) exercised in tests, not just documented.

---

# SECTION 9 — OBSERVABILITY

**Logging.** Structured JSON throughout: request ID, workspace ID, user ID (IDs only — no names, no prospect content, no PII in logs, per Document 05), pipeline and prompt versions on every AI call. Log levels mean things; `error` pages someone.

**Tracing.** OpenTelemetry wiring from day one (it costs little at birth and much at retrofit), exported to a lightweight backend; traces span API → services → pipelines → provider calls, so "why was Monday's queue late" is a query, not an investigation.

**Metrics — two dashboards, deliberately separate.** **System:** latency percentiles, error rates, queue depth and job latency by class, provider error/latency, DB health. **Product/intelligence (the five watched, per Documents 03/07):** unedited-pass rate, acceptance rate, pursue rate, outcome-capture rate, error reports per 100 briefs — plus the unit-cost ledger against ceiling and the L0 validation-failure rate (the earliest smoke signal of model drift). The five live on one screen; everything else is a drill-down. Weekly review reads the product screen first (Document 04 §9's cadence, wired to real panels).

**AI evaluation metrics.** Rubric score distributions by dimension and by prompt version; golden-set regression deltas per release; judge-vs-human agreement; calibration curves per confidence band; per-source accuracy sampling results feeding trust scores. These are release-gating inputs (Document 04's ship gates), so they are first-class time series, not spreadsheet exports.

**Health & flags.** Liveness/readiness per process; a status endpoint the internal console renders (queue depth, last successful sweep per job class, source health board). Feature flags: DB-backed, typed, boring — used for staged rollout of pipeline versions and format experiments (the playbook's format versioning), not for permanent configuration (P4 applies to engineers too).

**Error reporting.** Sentry (or equivalent) on both apps, release-tagged, PII-scrubbed; every Sev-classified incident (Document 04 §9) traces to its derivation record — the architecture's promise to the honesty rule: when we tell a customer what happened, we actually know.

---

# SECTION 10 — SCALABILITY

The evolution map: what changes at each order of magnitude, and what deliberately never does.

**10 customers (MVP → V1 entry).** One API instance, one worker, one Postgres. Sampling at 100% (the human QA gate); ops by hand; costs trivial. The architecture is *over-built* for this stage on purpose — the boundaries cost little now and everything later.

**100 customers (V1 at target).** Two-plus API instances behind Railway's balancer; worker split into two pools (interactive-latency jobs vs. heavy research sweeps) — still one codebase, one queue table. Ring-2 caching starts paying (repeat-prospect research amortises); the unit-cost ledger becomes a weekly management input. Postgres untouched except indices earned from real query shapes. L2 judge takes grading weight as calibration data accumulates.

**1,000 customers.** The queue migrates to a dedicated broker (Redis-backed) — the trigger is measured contention/latency on the jobs table, not fashion; the enqueue-transactionality is preserved via outbox pattern. Worker pools become per-class deployments with independent scaling. Read replica for analytics and the internal console. Discovery sweeps become continuous rather than weekly-batched. First serious cost-optimisation pass on pipelines (model mix per step, caching sub-results). SOC 2 groundwork begins (the audit stream and secrets discipline were the down-payment).

**10,000 customers.** The first true service extractions, along the seams drawn in Section 1: the **AI runtime + evaluation** (independent scaling and release cadence from the API) and the **source-ingestion platform** (its own workers, storage, and politeness governors — by now it is effectively a data-engineering product). Postgres partitioning by workspace for the largest Ring-1 tables; the Ring-2 store possibly its own database. Multi-region *reads* if the US expansion (rung 1b long since taken) demands latency parity. A second model provider live behind the interface — by this scale, negotiating leverage and resilience justify what AP6 prepared for.

**100,000 customers.** Honest answer: the company that reaches here rebuilds several organs with money and teams this document should not pretend to spend today. What it *can* promise: the API contract (`/v1` discipline means clients survived every internal upheaval), the domain language, the evidence provenance model, and the ring boundaries carry through — because those are the ten-year commitments.

**What deliberately never changes, at any scale:** business logic backend-only; the dependency direction; the receipt rule and derivation records; Ring-1 isolation (belt and braces both); the never-automatic floor; evaluation as release gate; and the one-engineer-on-a-laptop property for the core loop (a system that can no longer run small can no longer be reasoned about small).

---

# SECTION 11 — ENGINEERING STANDARDS

**Testing philosophy.** The pyramid, with a Xenia-specific peak: **domain unit tests** (pure, milliseconds, exhaustive — the constitutional rules live here, so this suite *is* compliance); **service tests** against in-memory fakes of repository/provider protocols (no mocking libraries against owned code — fakes are first-class citizens in `tests/`); **API contract tests** (the OpenAPI schema as executable truth; breaking-change detection in CI); **AI pipeline tests** in two modes — deterministic (recorded provider fixtures for logic and validators) and evaluative (the golden-set regression, run on every AI-touching change, gating per Document 04 §6); **E2E** happy paths only (Playwright): signup → interview → queue → correction → outcome — the loop, walked by a robot, nightly.

**Code review & branches.** Trunk-based, short-lived branches, every merge PR-reviewed — at team-of-one, review means a written self-review against the checklist (principles P1–P8 of Document 03, the eighteen of Document 06, this document's APs) plus mandatory second eyes on anything touching money, deletion, tenancy, or prompts once a second engineer exists. CI (GitHub Actions): ruff + mypy strict, tests, migration lint (Alembic autogen diff must be empty), OpenAPI diff, golden regression when `ai/` or `prompts/` changed, image build. Deploys: merge → staging (auto) → production (one manual gate), rollback-first mentality (every migration reversible or explicitly flagged with its expand/contract plan).

**ADRs.** Numbered, in-repo, one page: context, decision, alternatives, consequences. ADR-000 is this document's summary; every Section 13 open decision becomes an ADR when taken; any deviation from Documents 01–08 *requires* one (the amendment procedure's engineering face).

**Documentation.** README-per-package (what lives here, what may import it); the derivation record and audit stream are self-documenting by design; runbooks for the five operational emergencies (Sev1 intelligence incident, source quarantine, provider outage, deletion request, rollback) written *before* each is first needed.

**Naming.** The ubiquitous language is Documents 03/05's ontology, verbatim: code says `Workspace`, `Evidence`, `Recommendation`, `DnaChangeEvent` — never `client`, `data_item`, `suggestion`, `log`. A concept renamed in code without a document amendment is a bug in either the code or the documents; find out which.

**Versioning & migrations.** API: `/v1` additive-only; breaking changes mean `/v2` and a deprecation window (the iOS promise depends on this discipline). Prompts and pipelines: versioned artefacts, referenced in every derivation record. Schema: Alembic, expand-migrate-contract for anything hot; destructive migrations require the audit entry and a backup point. Brief format versions per the playbook, so quality metrics compare like with like.

**Dependencies.** A budget, not a buffet: every new runtime dependency argued in its PR (maintenance cost, security surface, ten-year question); automated update PRs (Renovate) batched weekly; lockfiles everywhere; the standard library preferred wherever it is honestly sufficient.

---

# SECTION 12 — FOUNDER CRITIQUE

**What is premature.** pgvector and embeddings appear in this document only as "when earned" — correctly, and the critique doubles down: V1's retrieval is structured lookup over small, well-modelled data; semantic search is a solution shopping for a problem until Memory or Ring 2 grows past hand-tuned relevance. OpenTelemetry-from-day-one is defensible but watchable — if the wiring exceeds an afternoon, defer it; Sentry plus structured logs carries a two-service system a long way. The internal console could over-grow: MVP needs a grading queue and a brief-approval button, not an admin platform — build the two screens, resist the platform.

**What is missing — named honestly.** **The source-ingestion subsystem is this document's hand-wave.** `integrations/sources/` is one folder name carrying half the product's engineering difficulty: fetching politely at scale, snapshot storage, identity resolution across messy real-world data, per-source parsing that breaks weekly, the ad-library and register adapters' particulars, cost-per-observation accounting. Document 05 governs its *policy*; nothing yet designs its *machinery* — and R1's unit-cost question lives substantially in exactly this machinery. This is the next document, and Section 13 says so. Also thin here: the prompt-management workflow at team scale (fine for one engineer, undesigned for five), staging-environment data strategy (real-ish data without real customer data — synthetic workspace fixtures need building), and the export/departure bundle's format (promised in three documents, specified in none).

**Assumptions that could bite.** That the **OpenAI Responses API's structured outputs + citation-binding validation** yields acceptable regeneration rates at brief complexity — if the model fights the receipt rule hard, unit costs inflate exactly where the ceiling is tightest; the MVP's 100% sampling answers this fast, but the architecture should be ready to decompose brief composition into smaller per-section calls (cheaper retries, tighter validation) — a pipeline-shape change the design permits but hasn't priced. That **Railway + Vercel + Supabase** remain adequate and aligned through, say, SOC 2 — plausible, not promised; the mitigations (Docker everywhere, auth behind an interface, no PaaS-proprietary features) keep the exit doors oiled. That **Postgres-as-queue** survives the research sweeps' burstiness at hundreds of workspaces — the migration trigger is defined, but the outbox refactor should be sketched *before* it's urgent. And the quiet one: **the single developer**. This architecture is legible to one careful engineer — that is its virtue — but several standards (review, second eyes, runbooks-before-need) presuppose a team; until hiring, the honest mitigation is ruthless scope discipline (the do-not-build list is load-bearing for engineering too) and the self-review checklist actually performed, not performed at.

**Where refactors are likely (predicted now, so they surprise nobody):** the Evidence store's schema (real-world provenance is messier than any first model; version it and expect churn); the queue (named); brief composition's pipeline shape (monolithic → per-section, per above); the internal console (screens → app, when the Editor is a hire, not the founder); and Memory's relevance rules (hand-tuned → learned, eventually vector-assisted — the pgvector moment, arriving with evidence rather than fashion).

---

# SECTION 13 — SCORECARD

| # | Section | Score /10 | Justification & improvement |
|---|---------|-----------|------------------------------|
| 1 | Architectural Principles | **9.5** | Eight principles that decide arguments (AP2's import law, AP5's iOS test, AP6's containment); modular-monolith stance argued from the documents, not fashion. *Improve:* enforce AP2 mechanically (import-linter) from the first commit. |
| 2 | System Architecture | **9** | Every subsystem placed with its reason; the canonical request flow doubles as an onboarding document; the Editor console correctly promoted to a subsystem. *Improve:* a one-page diagram belongs beside this section the day drawing beats prose. |
| 3 | Backend Architecture | **9** | The layout enforces the constitution (workspace-scoped repositories, prompts colocated with tests, sources as anti-corruption adapters); responsibilities stated with their smells. *Improve:* the sources/ package is a placeholder for the next document's real design. |
| 4 | Frontend Architecture | **8.5** | Server-state discipline, generated types, the correction loop's optimistic contract, features-as-deletable-units. Deduction: router choice deferred (rightly) and the shared-brief access model still open. *Improve:* resolve both as ADR-001/002 in week one of build. |
| 5 | Domain Architecture | **9.5** | The ontology lands with its laws intact — decay as a type distinction, proposals as a state machine, the Prospect/BusinessRecord split protecting the rings, SuppressionEntry's exception documented. *Improve:* nothing before contact with Alembic reality. |
| 6 | AI Runtime | **9.5** | The eight-step pipeline makes Documents 04/05 executable: citation-binding as blocking validation, derivation records under everything, learning as events not weight-mutation, MVP's QA gate as a sampling rate. *Improve:* sketch the per-section composition variant before unit-cost data forces it hastily. |
| 7 | Background Processing | **9** | Postgres-queue with transactional enqueue and a named migration trigger — AP8 at its best; job classes map one-to-one to the documents' obligations. *Improve:* the outbox sketch, pre-need. |
| 8 | Security | **9** | Belt-and-braces tenancy (typed scoping + RLS), the never-automatic floor beneath authorization, AI-cost governors as first-class limits, audit-as-SOC2-downpayment. *Improve:* the personal-data field inventory should exist as a checked-in artefact, not a principle. |
| 9 | Observability | **8.5** | Two-dashboard separation guards the five-watched discipline; eval metrics as gating time series. Deduction: vendor choices (tracing backend) deferred. *Improve:* pick the boring defaults in ADR form and move on. |
| 10 | Scalability | **9** | Triggers instead of dates, extraction along pre-drawn seams, and the honest 100k answer; the never-changes list is the ten-year claim made concrete. *Improve:* none — revisit at each magnitude, as designed. |
| 11 | Engineering Standards | **9** | The golden-regression-as-CI-gate and migration lint are the standards that matter; ubiquitous-language naming wired to the documents; ADR-on-deviation closes the governance loop. *Improve:* write the five runbooks during MVP quiet moments, not during their emergencies. |
| 12 | Founder Critique | **9.5** | Names its own hand-wave (source ingestion) as the biggest gap, predicts its refactors, and prices the single-developer reality without romance. *Improve:* act on the next-document recommendation. |
| 13 | Scorecard | **—** | Not self-scored, on principle. |

## Unresolved engineering decisions (each becomes an ADR when taken)

**(1)** Router: TanStack Router vs React Router — week one. **(2)** Shared-brief access model (public link vs gated) — inherits the Document 06 founder decision. **(3)** OpenAPI→TypeScript codegen tool. **(4)** Monorepo vs two repos (lean: monorepo — one PR can change API + client + contract together). **(5)** Tracing backend and Sentry-vs-alternative. **(6)** Staging data strategy (synthetic fixtures design). **(7)** Object storage vendor (Supabase storage vs S3/R2). **(8)** Prompt-version → release mapping convention. **(9)** The outbox/queue-migration sketch's timing. **(10)** Second-provider timing and the abstraction's first real test. **(11)** Brief composition shape (monolithic vs per-section) — to be decided by MVP unit-cost data, not preference.

## The next document

**Recommendation: "Xenia — Source Ingestion & Research Pipeline Design."** The critique names the reason: this document hand-waves, in one folder name, the machinery that carries half the product's engineering risk and most of R1's unit-cost question — polite acquisition at scale, snapshot and provenance storage, identity resolution, per-source adapters for the Document 05 catalogue, freshness sweeps, cost-per-observation accounting, and the quarantine mechanics. It is the last deep design the build needs; after it, the writing is tickets.

Per instruction: recommended, not written.

---

*End of Technical Architecture v1.0. Governed by Documents 01–07; amendable by ADR with document-amendment escalation where constitutional. The dependency direction (AP2), the receipt-rule validation (Section 6), Ring-1 tenancy enforcement (Section 8), and the never-changes list (Section 10) are citable in any engineering review.*
