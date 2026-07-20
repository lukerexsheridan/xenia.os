# XENIA — V1 BUILD PLAN

**The engineering execution roadmap for a single founder**

Version 1.0 · July 2026 · Internal — Owner: Founder/CTO. Governed by Documents 01–09.

---

*This is the execution plan, not architecture and not strategy: it converts nine governing documents into a linear sequence of shippable milestones for one person. It is dated, opinionated about order, and designed to be obsolete within weeks — a build plan that survives contact with reality unchanged wasn't a plan, it was a wish. One structural honesty before Section 1: this plan collides with the Research Phase Playbook (Document 07), which consumes the same founder for ~8 weeks at ~35–40 hours/week. The collision is resolved, not ignored: Epics 0–3 are designed to* serve *the research phase (the concierge kit is engineering), full feature build begins at the Week-7 Go gate, and Section 12 answers "can engineering begin immediately?" with that split explicitly.*

---

# SECTION 1 — BUILD PHILOSOPHY

**Why the roadmap is linear.** A solo founder's scarcest resource is not hours but *context* — every parallel workstream taxes the one brain that holds the whole system. The roadmap is therefore a single file of work: one epic at a time, each ending in a deployed state, each feeding the next. Parallelism exists only where it is free (CI runs while you sleep) or forced (concierge operations during research weeks). Linear also means honest: a linear plan slips *visibly* — parallel plans hide their slippage in the seams until integration day.

**Why unfinished infrastructure beats unfinished features.** An unfinished feature is a promise broken to a customer; unfinished infrastructure is a promise deferred to yourself. The plan front-loads the small set of infrastructure that everything rests on (tenancy, provenance, the receipt validator, CI) and *refuses* speculative infrastructure (Document 09's critique list — nothing is built until usage exists). The test for any infrastructure task: does a constitutional document require it for the next epic's exit criteria? If not, it waits.

**Why every milestone must remain deployable.** Deployability is the solo founder's safety net: a project that always runs can always be demonstrated, always be tested against reality, and always be paused without rot. Every sprint below ends with `main` deployed to staging and deployable to production — no long-lived branches, no big-bang integration, no "it'll compile again by Friday." The discipline costs perhaps 10% in ceremony and repays it the first time a design partner asks "can I see it?" mid-build.

**Engineering principles for one person.** **(1) Ship weekly or cut scope** — the unit of planning is the week; a task that doesn't fit becomes two tasks or a smaller task. **(2) Boring beats clever twice over** — cleverness costs at write time and again at every future read; a solo codebase is read by its author under stress. **(3) The constitution is the reviewer** — with no second engineer, review means the written self-review against Documents 03/06/08/09's citable rules, actually performed (the checklist lives in the PR template). **(4) Tests are the second engineer** — the domain suite is the colleague who remembers the rules; golden regressions are the colleague who remembers quality. **(5) Do not gold-plate what the Editor gate covers** — during MVP, the human QA gate absorbs imperfection in AI output; engineering effort goes to the rails, not to pre-polishing what sampling will catch. **(6) Log every decision** — the ADR discipline (Document 08) at solo scale is a paragraph, not a meeting; write it anyway, because future-you is a different engineer. **(7) When behind, cut scope, never quality floors** — the do-not-ship lines (fabrication gates, tenancy, audit) are not schedule variables; Section 11's cut list is.

---

# SECTION 2 — EPIC BREAKDOWN

The proposed thirteen-epic structure is adopted with **two deliberate reorderings, argued here**: *(a)* **the concierge tooling moves from Epic 11 to Epic 3** — the concierge is not a late product mode but the *first consumer* of the pipeline (Document 09: "the concierge is the pipeline run by hand"), it is needed within weeks for the research phase, and building its kit early means every subsequent epic upgrades a working intelligence operation rather than assembling toward a distant one; *(b)* **internal QA tooling moves ahead of the customer-facing frontend** — the Editor gate is constitutionally required before any brief reaches a customer (Documents 04/09), so the grading/approval screens must exist before the app that delivers briefs, not after.

**Epic 0 — Developer Experience & Skeleton.** *Purpose:* the one-command world — repo (monorepo per ADR), Docker Compose local stack, CI (lint/type/test/migration-lint/OpenAPI diff), deploy pipelines to Railway/Vercel staging, the PR self-review template. *Dependencies:* ADR batch #1 (Section 12). *Deliverables:* hello-world API + SPA deployed end-to-end with auth handshake. *Exit:* a commit reaches staging in <10 minutes untouched. *Risks:* gold-plating the tooling — timeboxed to one sprint, hard.

**Epic 1 — Foundations.** *Purpose:* the load-bearing core — typed config, DB + Alembic, structured logging, error taxonomy, Supabase JWT verification, Workspace/User with **workspace-scoped repository base + RLS from the first table** (tenancy is never retrofitted), audit stream, DB-backed flags, the jobs table + worker skeleton. *Dependencies:* Epic 0. *Deliverables:* authenticated multi-tenant skeleton with one background job running on schedule. *Exit:* two test workspaces provably isolated (a cross-tenant test that *fails loudly* when RLS is disabled); audit entries written for auth events. *Risks:* none novel — this is the most standard epic; velocity here calibrates all estimates.

**Epic 2 — Domain Model.** *Purpose:* the constitution as pure code — the Document 08 §5 ontology with its laws: DNA aggregate + changelog + decay asymmetry, delegation grants + never-automatic floor, confidence banding rules, disqualifier precedence, Prospect/BusinessRecord split, SuppressionEntry. *Dependencies:* Epic 1 (persistence beneath it), but the pure rules are written test-first against nothing. *Deliverables:* the domain package at near-total unit coverage, milliseconds-fast. *Exit:* every citable domain rule from Documents 03–06 has a named test; mypy strict clean. *Risks:* over-modelling — the DNA ships with the *four* signal-consuming categories (Document 09's cut), schema headroom for ten.

**Epic 3 — Research Workbench (the concierge kit).** *Purpose:* the reordering's payoff — internal tooling that makes the founder a faster, auditable concierge *and* seeds the real pipeline: the politeness engine (first code, per Document 09), snapshot store, manual+assisted evidence capture with receipt tables, the brief template renderer (B1–B8 → designed PDF per Document 06 §7), the edit log (QA-delta measurement from the first brief), DNA document renderer. *Dependencies:* Epics 1–2. *Deliverables:* the founder produces a concierge brief inside the system — evidence receipted, derivation recorded, PDF out. *Exit:* one real concierge brief produced end-to-end in the workbench in ≤2.5 hours; its derivation record replayable. *Risks:* scope bloat toward "product" — the workbench is ugly-but-honest by decree; its users number exactly one.

**Epic 4 — Source Ingestion (four families).** *Purpose:* the Document 09 alpha set as real adapters — Companies House, ad transparency library, websites, hiring surfaces — over the politeness engine, with canonical content model, dedup, entity binding + human floor queue, and the **adapter-testing harness with recorded fixtures** (the critique's demand, built with the first adapter, not after). *Dependencies:* Epic 3's engine/store. *Deliverables:* a prospect's four-family footprint acquired and normalised automatically. *Exit:* ≥90% of concierge-list prospects acquire cleanly; adapter fixtures in CI; source-health metrics emitting. *Risks:* the plan's highest — real-world mess; one sprint of buffer lives here by design.

**Epic 5 — Evidence & Knowledge Layer.** *Purpose:* Document 09 §6–7 mechanised — extractors (deterministic for structured, schema-constrained AI for prose), span-grounding, validation, Evidence objects + graph relations, receipt-table assembly, the four signal families, freshness clocks. *Dependencies:* Epic 4. *Deliverables:* validated evidence and signals generated from live acquisition. *Exit:* receipt tables assemble deterministically from real data; span-grounding rejects a seeded fabrication in tests; extraction cost metered per item. *Risks:* prose-extraction quality — mitigated by the workbench's human seam continuing to operate.

**Epic 6 — Research Orchestration.** *Purpose:* the planner (rules, cache-aware, budgeted), recipe execution across stages, typed failures → couldn't-see computation, checkpointed jobs, cost governors. *Dependencies:* Epics 4–5. *Deliverables:* "research this prospect" as one queued command producing evidence + signals + coverage report. *Exit:* a full research run replays deterministically from its derivation; budget caps demonstrably bind (a test recipe hits its cap and degrades honestly). *Risks:* moderate — this is plumbing over proven parts.

**Epic 7 — Brief Generation.** *Purpose:* the AI composition pipeline — insight, thesis, B1–B8 composition against frozen receipt tables; the full L0 validator battery (citation binding, vocabulary, structure, entity-consistency); bounded regeneration; derivation storage; golden regression suite seeded from concierge artefacts, wired into CI. *Dependencies:* Epics 5–6; golden data from research phase. *Deliverables:* machine briefs, gated. *Exit:* **the QA-delta dial live** — unedited-pass rate measured weekly against the Document 04 rubric on real prospects; zero fabrications escaping L0 in the regression suite. *Risks:* the R1 bet itself — the exit criterion measures it rather than assumes it.

**Epic 8 — Recommendation Engine.** *Purpose:* deterministic scoring against DNA, bounded weekly queue assembly, visible exclusion, decision/correction capture with **the named-effect computation** (the ten-second loop's engine), learning jobs (events → DnaChangeEvents), outcome capture model. *Dependencies:* Epics 2, 7. *Deliverables:* the loop's back half as APIs. *Exit:* a correction demonstrably alters the next queue assembly with its changelog entry and named effect; disqualifier violations impossible in test. *Risks:* low mechanically; the design risk (chip taxonomy) is a research-phase output, arriving calibrated.

**Epic 9 — Internal QA Tooling (the Editor console).** *Purpose:* the two screens Document 09 mandates before customers — the grading queue (rubric scoring UI, L1) and the approval gate (MVP's 100% review), plus golden-set management and the source-health page. *Dependencies:* Epics 7–8. *Deliverables:* the Editor gate operational. *Exit:* a brief cannot reach delivery without gate approval (enforced, tested); grading feeds the metrics store. *Risks:* console sprawl — two screens plus two pages, by decree.

**Epic 10 — Frontend Alpha (the customer app).** *Purpose:* the Document 06 experience on the Document 08 frontend architecture — auth shell, the DNA interview (conversational, resumable — the epic's hardest citizen), DNA document view + endorsement, the queue with verdict-first cards, the brief view (three depths), the ten-second correction loop, outcome capture, export. *Dependencies:* Epics 8–9 (APIs + gate). *Deliverables:* a design partner uses Xenia without the founder driving. *Exit:* the E2E loop walk (signup → interview → queue → correction → outcome) green in Playwright; the correction loop measured ≤10s in prototype testing. *Risks:* the plan's second-highest — conversational UI is a mini-product; Section 11 pre-declares this epic's overrun.

**Epic 11 — MVP Mode (productised concierge).** *Purpose:* Document 03's MVP stage assembled — weekly brief email (C8, Resend, one-tap actions), delivery scheduling, drafts (C6), Stripe founding-rate billing, the five-metric instrumentation panel, Sev1 runbook rehearsed. *Dependencies:* Epic 10. *Deliverables:* ten design partners served through the product with the Editor gate at 100%. *Exit:* Document 03's MVP entry criteria measurable in-product (unedited-pass, capture rate, unit cost per ledger); first paid invoices flowing. *Risks:* operational more than technical — the founder is now running product, gate, and cohort simultaneously.

**Epic 12 — V1 Hardening & Launch.** *Purpose:* the gate narrows to sampling as the harness earns it (Document 04's thresholds), cost governors tuned, offboarding/export machinery tested (the departure rule, exercised), deletion/rights machinery live, security pass (secrets rotation drill, RLS audit), the five runbooks written, polish to the Document 06 bar on the surfaces that exist, founding cohort → 25. *Dependencies:* Epic 11 + sustained MVP metrics. *Deliverables:* V1 per Section 9's definition. *Exit:* Section 9, in full. *Risks:* "hardening" becoming a euphemism for drift — this epic has a checklist, not a mood.

---

# SECTION 3 — SPRINT PLAN

Twenty-two sprints of one week each (nominal), grouped by epic. Conventions: every sprint ends with `main` deployed to staging; **DoD** is the definition of done; tests named are *required for the DoD*, not aspirational. Durations carry Section 11's honesty multiplier — the calendar total is stated there, not here. Sprints 1–4 run alongside the research phase's lighter weeks where possible; Sprint 5 onward assumes the Week-7 Go.

**Sprint 1 (Epic 0) — The skeleton.** *Objective:* one-command dev world, deployed hello-world. *Tasks:* monorepo scaffold; Compose stack (API, worker, Postgres, bucket-emulator); CI pipeline (ruff, mypy strict, pytest, Alembic lint, OpenAPI diff); Railway + Vercel staging deploys; Supabase project + JWT verification spike; PR template with the constitutional self-review. *Tests:* CI proves itself (a deliberate lint/type/test failure each blocks merge). *Deploy:* staging serves an authenticated ping. *DoD:* clean-machine `docker compose up` to working stack in one command; commit→staging <10 min.

**Sprint 2 (Epic 1) — Tenancy and bones.** *Objective:* multi-tenant, audited, observable core. *Tasks:* typed settings; Workspace/User models + migrations; workspace-scoped repo base; RLS policies + session-variable plumbing; audit stream; structured logging with request/workspace IDs; error taxonomy; flags table. *Tests:* the cross-tenant isolation suite (including the RLS-disabled canary); audit-write assertions. *Deploy:* two seeded workspaces on staging, provably isolated. *DoD:* isolation tests green; audit visible for auth events; zero raw-SQL paths outside repos.

**Sprint 3 (Epic 1) — Jobs and mail.** *Objective:* background machinery + first outbound surface. *Tasks:* jobs table (`SKIP LOCKED` consumer), worker entrypoint, scheduler, retry/backoff/dead-letter; Resend integration + templated send; Stripe account + webhook receiver (idempotent, queued). *Tests:* job idempotency, poison-job dead-lettering, webhook replay. *Deploy:* a scheduled heartbeat job emails the founder daily from staging. *DoD:* a killed worker resumes cleanly; dead-letter alerts.

**Sprint 4 (Epic 2) — The constitution in code.** *Objective:* the pure domain. *Tasks:* DNA aggregate (4 active categories, 10-slot schema), changelog events, decay asymmetry, conflict hierarchy; delegation grants + never-automatic floor; confidence banding; disqualifier precedence; Prospect/BusinessRecord split; SuppressionEntry; Decision/Correction/Outcome shapes. *Tests:* the named-rule suite — every citable law from Documents 03–06 as a test with the document reference in its name. *Deploy:* unchanged surface (domain is pure). *DoD:* domain coverage ≥95%; suite runs <2s; mypy strict.

**Sprint 5 (Epic 3) — Politeness and snapshots.** *Objective:* acquisition's foundations, concierge-grade. *Tasks:* politeness engine (rate limits, robots honour, circuit breakers, honest UA); content-addressed snapshot store; fetch CLI for workbench use; provenance metadata. *Tests:* politeness unit suite (robots cases, breaker trips); snapshot round-trip. *Deploy:* founder can snapshot any prospect URL from the workbench CLI. *DoD:* every fetch leaves a replayable snapshot; a blocked domain circuit-breaks and logs, never evades.

**Sprint 6 (Epic 3) — The workbench.** *Objective:* concierge production inside the system. *Tasks:* manual evidence capture UI-lite (internal), receipt-table builder, brief template renderer (B1–B8 → styled PDF per Document 06), DNA document renderer, edit log capture, derivation record assembly. *Tests:* receipt-table determinism; PDF golden-file snapshot. *Deploy:* internal workbench on staging behind Editor auth. *DoD:* one real concierge brief produced end-to-end ≤2.5h with full derivation; the PDF passes the shareable-rendering review.

**Sprint 7 (Epic 4) — Structured adapters.** *Objective:* the two highest-trust sources, automated. *Tasks:* Companies House adapter (filings→canonical `Filing`); ad-library adapter (`AdRecord`); adapter-testing harness with recorded fixtures; entity binding v1 (strong keys: domain, register number); source-health metrics. *Tests:* fixture-driven adapter contracts; binding precision suite on a labelled sample. *Deploy:* register + ad footprints acquired automatically for the concierge list. *DoD:* both adapters green on fixtures in CI; ≥95% binding precision on the labelled set.

**Sprint 8 (Epic 4) — Web and hiring adapters.** *Objective:* the messy two. *Tasks:* website adapter (sitemap rules, readability cleaning, `Page` model, rendering budget hook); hiring adapter (`Posting`, aggregator dedup); near-dup/syndication collapse; the human floor queue for ambiguous bindings. *Tests:* cleaning golden files; dedup property tests; floor-queue flow. *Deploy:* four-family acquisition live on staging. *DoD:* ≥90% of the concierge list acquires cleanly across four families; harness fixtures for every adapter.

**Sprint 9 (Epic 5) — Evidence machinery.** *Objective:* claims with receipts. *Tasks:* deterministic extractors (Filing/AdRecord/Posting → Evidence); schema-constrained AI extraction for `Page` prose with span-grounding; validation battery; Evidence IDs + graph relations (corroborates/conflicts/supersedes as columns); receipt-table assembly from live data. *Tests:* span-grounding rejects seeded fabrications; independence collapse on syndication fixtures; extraction-cost metering asserted. *Deploy:* evidence pipeline runs on staging prospects. *DoD:* a receipt table for a real prospect assembles deterministically twice identically; extraction drop-rate telemetry live.

**Sprint 10 (Epic 5) — Signals and freshness.** *Objective:* knowledge from evidence. *Tasks:* four signal families (facts, hiring, ads/tech, disqualifier triggers) as rules; promotion thresholds; confidence evolution math; freshness clocks + decay sweep job. *Tests:* rule-table suite per signal family; decay behaviour over simulated time. *Deploy:* signal store populated for staging prospects. *DoD:* signals derive with stored derivations; decay sweep demonstrably demotes stale signals.

**Sprint 11 (Epic 6) — The planner and the run.** *Objective:* one-command research. *Tasks:* recipe rules (cold/delta/refresh), budget caps, coverage tables + couldn't-see computation, orchestrated run across stages, checkpointing, cost ledger per stage. *Tests:* budget-binding test (cap hit → honest degradation); replay determinism; coverage-report correctness. *Deploy:* "research prospect X" queued from workbench, full run on staging. *DoD:* a cold run and a warm delta-run both complete with correct ledgers and coverage reports.

**Sprint 12 (Epic 7) — Composition, gated.** *Objective:* machine briefs behind the wall. *Tasks:* insight + thesis + composition pipelines against frozen receipt tables; L0 validator battery (citation binding, structure, vocabulary, entity-consistency); bounded regeneration; derivation storage; golden suite seeded from concierge artefacts, in CI. *Tests:* the L0 battery itself (each validator with pass/fail fixtures); golden regression baseline recorded. *Deploy:* machine briefs generating on staging, visible only in workbench. *DoD:* zero uncited material claims escape L0 across the golden set; rejection-rate metric live.

**Sprint 13 (Epic 7) — The QA-delta dial.** *Objective:* measure the company's biggest bet. *Tasks:* rubric-scoring flow on machine briefs (workbench), edit-log diffing vs. machine output, unedited-pass computation, weekly quality report; per-section composition sketch written (the held-ready ADR-6/9 variant). *Tests:* metric correctness on synthetic edits. *Deploy:* the dial on the internal metrics page. *DoD:* two weeks of real prospects scored; the unedited-pass baseline exists — *the number Documents 03/07/09 have all been waiting for.*

**Sprint 14 (Epic 8) — Scoring and the queue.** *Objective:* accountable recommendations. *Tasks:* deterministic scoring (DNA × signals, decomposed), bounded queue assembly + ranking, visible exclusion, recommendation records with derivations. *Tests:* scoring decomposition suite; disqualifier-impossibility test; rank-reason correctness. *Deploy:* weekly queue assembling for staging workspaces. *DoD:* every queue item's score decomposes to named DNA elements and evidence-backed signals.

**Sprint 15 (Epic 8) — Teaching and outcomes.** *Objective:* the loop closes. *Tasks:* decision/correction APIs with chip taxonomy (research-phase calibrated), named-effect computation (synchronous), learning jobs (events → DnaChangeEvents within one cycle), outcome capture + prompts scheduling. *Tests:* correction→next-queue integration test (the flywheel's first automated proof); changelog completeness. *Deploy:* corrections alter staging queues visibly. *DoD:* the named effect returns in <1s; a correction demonstrably reshapes the next assembly with its logged cause.

**Sprint 16 (Epic 9) — The Editor console.** *Objective:* the gate before customers. *Tasks:* grading queue screen (rubric UI), approval-gate screen (nothing delivers unapproved — enforced in the delivery path), golden-set management page, source-health page. *Tests:* gate-enforcement integration test; grading→metrics flow. *Deploy:* console live behind Editor auth. *DoD:* a brief provably cannot reach any delivery surface without gate approval.

**Sprints 17–19 (Epic 10) — The app.** *Objective:* design partners self-serve. *Sprint 17:* auth shell, layouts, generated API client, queue view (verdict-first cards), brief view (three depths, receipts, couldn't-see). *Sprint 18:* the DNA interview (conversational, resumable, homework-first opening) + DNA document view + endorsement flow — the pre-declared overrun candidate. *Sprint 19:* the ten-second correction loop (optimistic + named effect), outcome capture, export (CSV + PDF), empty-week and error-voice states per Document 06. *Tests:* Playwright loop-walk E2E (green = epic exit); correction-latency measurement; component tests on the confidence-vocabulary rendering. *Deploy:* the app on staging, design-partner accounts seeded. *DoD:* one design partner completes interview→queue→correction→outcome unassisted; loop-walk green in CI.

**Sprint 20 (Epic 11) — Delivery and money.** *Objective:* the MVP assembled. *Tasks:* weekly brief email (C8: composition, one-tap actions, workspace-local scheduling), drafts (C6, always-editable), Stripe founding billing (one plan, portal link), the five-metric panel, Sev1 runbook written + rehearsed on a staged incident. *Tests:* email golden files; billing webhook E2E; metric-panel correctness. *Deploy:* production goes live for the first design-partner cohort, Editor gate at 100%. *DoD:* Monday delivery runs unattended; first real invoice; the five numbers on one page.

**Sprints 21–22 (Epic 12) — Hardening to V1.** *Objective:* Section 9, met. *Tasks:* sampling narrows per harness thresholds; cost governors tuned on real ledgers; offboarding/export + deletion machinery exercised end-to-end; rights-request flow; security pass (rotation drill, RLS audit, dependency audit); remaining runbooks; polish pass on the six delight/failure moments that exist; cohort to 25. *Tests:* departure-rule E2E (a workspace leaves, data provably gone/exported); restore-from-backup drill. *Deploy:* V1 in production. *DoD:* every line of Section 9 checked, in writing, dated.

---

# SECTION 4 — IMPLEMENTATION ORDER

**The critical path, and why it is the spine:** tenancy → domain laws → politeness/snapshots → adapters → evidence → orchestration → composition → gate → app → delivery. Each link exists because the next is unsafe or unbuildable without it: no adapters before politeness (N2 has one enforcement point and it must exist first); no composition before evidence (the receipt rule needs a closed world to close); no delivery before the gate (constitutional); no app before the APIs it renders (business logic backend-only). The QA-delta dial (Sprint 13) sits deliberately at the path's midpoint: it is the earliest moment the company's central bet can be measured, and everything after it proceeds *informed*.

**Genuinely parallelisable (the short list):** golden-set curation (research-phase artefacts, curated in evenings as they accrue); the brief PDF's design iterations (against concierge feedback, continuous); ADR writing; fixture recording for adapters. Nothing else — parallel feature work is how solo projects die.

**Must never begin early:** the customer app before the gate (a beautiful app delivering ungated briefs would violate three documents at once); sending infrastructure (V2, constitutionally); embeddings, collections, open chat, native anything (the do-not-build list is a build-plan input, not a suggestion); billing tiers (one plan, decided). **Deferrable without harm if time tightens:** drafts (C6 — the loop closes without them, per Document 03's own 50% cut), reviews/news adapters (families five and six — trust texture, not scoring backbone), email one-tap actions (links suffice initially), export polish. Section 11 formalises the cut order.

---

# SECTION 5 — TESTING STRATEGY

Per epic, the required suites and their exit bars (the Document 08 pyramid, applied):

**Epics 0–1:** CI self-tests; the tenancy isolation suite (the RLS canary is permanent — it runs forever, because tenancy regressions are the one class that must be impossible); job semantics (idempotency, resume, dead-letter). **Epic 2:** the named-rule domain suite — one test per citable constitutional rule, document-referenced in the test name; ≥95% coverage; <2s runtime (this suite runs on every save, so speed is a feature). **Epics 3–4:** politeness unit suite; snapshot round-trips; **fixture-driven adapter contracts** (recorded real responses; adapters break in CI before they break in production) plus a weekly *live canary* per adapter against a stable known entity (fixtures catch our bugs; canaries catch the world's changes). **Epic 5:** span-grounding adversarial suite (seeded fabrications must die); independence/syndication fixtures; determinism tests (same snapshot → same evidence, always). **Epic 6:** budget-binding and replay tests; coverage-report correctness. **Epic 7:** the L0 battery with per-validator fixtures; **the golden regression suite in CI** — every AI-touching merge runs it, ship gates per Document 04 §6 enforced mechanically; recorded-fixture mode for deterministic pipeline logic tests. **Epics 8–9:** the correction→queue integration test (the flywheel's automated proof); gate-enforcement test (delivery without approval must be *unrepresentable*, and the test proves it). **Epic 10:** the Playwright loop-walk (the one E2E that matters, run nightly and on merge); correction-latency assertions; accessibility checks on the four confidence-word renderings (AA floor). **Epics 11–12:** billing E2E against Stripe test mode; email golden files; the departure-rule E2E; backup-restore drill (performed, dated, logged). **Manual verification, permanently:** the Editor's weekly read-ten-briefs ritual (Document 04's D3 defence) — no suite replaces taste.

---

# SECTION 6 — DEPLOYMENT STRATEGY

**Environments.** *Local:* the Compose stack, seeded with synthetic fixtures (ADR — the staging-data strategy: generated workspaces, real-shaped fake prospects; never customer data outside production). *Preview:* Vercel previews per PR for the SPA; API previews optional (staging suffices at solo scale). *Staging:* auto-deployed from `main`, synthetic data + the founder's own real test workspace; the concierge workbench runs here until Epic 11. *Production:* manual-gate deploy from tagged releases; boring by design.

**Flags.** DB-backed, typed, used for staged pipeline-version rollout and format experiments only (Document 08's anti-configuration rule); every flag has a removal date at creation.

**Rollback.** Images pinned per release; rollback = redeploy previous tag (<5 minutes, drilled once before first customers); **migrations expand-migrate-contract always** — no release depends on a migration that the previous release can't run against, which is what makes rollback a button and not an incident. Destructive contractions ship one release *after* their expansion proved out.

**Migration discipline.** Alembic autogen-diff lint in CI (drift impossible); every migration reversible or explicitly marked with its contraction plan; backup point before any marked migration; the restore drill (Sprint 22) repeated quarterly thereafter.

---

# SECTION 7 — RISK REGISTER

**Time estimation (probability: certain).** Solo estimates run 1.5–2× under lived reality — illness, design-partner fires, adapter breakage, the research phase's tail. *Mitigation:* the multiplier is applied to the calendar (Section 11), not hidden; weekly ship-or-cut keeps slippage visible at week grain; the cut order is pre-agreed so schedule pressure burns scope, never floors.

**The R1 bet lands mid-build (high impact).** Sprint 13's dial could read badly — unedited-pass far below 70%, or rejection rates pricing composition out of ceiling. *Mitigation:* the dial sits at the path's midpoint *so the plan can fork informed*: per-section composition (sketched, ADR-ready), heavier Editor gating for longer (margin cost, priced), or scope reshaping — all cheaper at Sprint 13 than at Sprint 20.

**Adapter maintenance during build (certain, recurring).** The world's HTML changes while you're building the thing that reads it. *Mitigation:* the harness + weekly canaries make breakage a CI event; a standing half-day/week maintenance budget from Epic 4 onward is *in the calendar* — unbudgeted maintenance is how linear plans go non-linear.

**AI cost surprises (moderate).** *Mitigation:* metering from the first AI call (Sprint 9), governors before customers (Sprint 11), the ledger read weekly from Sprint 13; no open-ended loops exist to explode (Document 09's structural guarantee).

**Provider dependency (low now, real later).** *Mitigation:* the provider interface from day one (AP6); recorded-fixture tests keep pipeline logic provider-independent; the second-provider ADR stays open deliberately.

**Security shortcuts under pressure (the quiet one).** Solo founders defer security when behind. *Mitigation:* tenancy/RLS/audit are Sprint 2 — done before pressure exists; the floors are named non-schedule-variables (Section 1); the Sprint 21 security pass is a checklist with dates, not intentions.

**Complexity/tech-debt accumulation.** *Mitigation:* the constitution-as-reviewer checklist; debt logged as it's taken (a `DEBT.md` with dates — unlogged debt is the compounding kind); Epic 12 includes a debt-burndown allocation.

**Founder capacity (the honest one).** One person is the SPOF for engineering, Editor duty, cohort operations, and company. *Mitigation:* the hiring triggers from Documents 05/08 (hat-relief criteria) reviewed monthly from MVP; the operating system (Section 8) protects recovery time structurally; and the plan's linearity itself — one thing at a time is also a sanity strategy.

---

# SECTION 8 — THE FOUNDER OPERATING SYSTEM

The engineering week, designed for sustainability at solo scale (and meshing with Document 07's rhythm while cohort operations run):

**Monday.** Deploy day + cohort day: the weekly delivery runs (MVP onward), production checks, then the week's plan — *one* sprint objective, written as the week's single sentence. No new work starts Monday afternoon; Monday absorbs operational surprises. **Tuesday–Thursday.** Deep work: two protected 3–4h implementation blocks daily, phone elsewhere; adapter-maintenance half-day lives Wednesday afternoon (scheduled, so breakage doesn't hijack mornings); interviews/partner calls batched to Thursday afternoon. **Friday.** The reflection stack (inherited from Document 07 and kept forever): tests-and-docs morning (the week's code gets its tests finished and its README/ADR paragraphs written — documentation debt dies weekly or compounds); the metrics read (five numbers + QA dial + cost ledger); the decision log (one paragraph per decision, append-only); retro (three lines: what shipped, what slipped, what changes next week); staging→production promotion if the week earned it. **Weekend.** Closed. The plan's multiplier already assumes a human; burning weekends is borrowing from the estimate at loan-shark rates. **Standing rules:** ship weekly or cut scope consciously (never silently); no new dependencies after Wednesday (Friday-you must test what Tuesday-you added); anything touching money, deletion, tenancy, or prompts gets the full checklist regardless of week; and when the week collapses (they will), the sprint shrinks to its DoD's smallest honest core — the DoD moves, the deploy discipline doesn't.

---

# SECTION 9 — THE DEFINITION OF V1

Xenia Version 1 is complete when every line below is true, checked in writing, dated. Everything absent from this list is V1.1+ by definition.

**Capabilities (Document 03's C1–C8, as shipped):** the DNA interview (conversational, resumable, ≥85% completion in cohort practice); the living DNA with changelog, endorsement, and correction; four-family ambient + directed research; briefs at B1–B8 with receipts, couldn't-see, three depths, shareable PDF; bounded weekly queue with decomposed scores and visible exclusion; the ten-second correction loop with named effects; outcome capture with intelligent prompts; the weekly brief email; drafts (C6) *if not cut under Section 11 — its absence does not block V1*; CSV/PDF export; offboarding with full export and deletion.

**Quality thresholds (live, not aspirational):** rubric ship-bar (≥16/20, no dimension <2) enforced on every delivered brief via gate-or-sampling; **unedited-pass ≥70% sustained four consecutive weeks** (the Document 03 entry criterion, met and held); zero fabrication/misattribution escapes in the regression suite *and* zero unresolved Sev1s; correction-application within one cycle, verified continuously by the integration test; astonishment-bar pass rate measured for every activation (the recalibrated thresholds from the research phase in force).

**Evaluation machinery:** golden set ≥50 briefs with held-out portion; regression suite gating CI; L1 grading operating weekly; calibration data accumulating (bands published to customers); the L2 judge running advisory (gating optional at V1 — its agreement threshold is allowed to mature).

**Engineering standards:** the named-rule domain suite green; tenancy canary green since Sprint 2; adapter fixtures + canaries green or consciously quarantined; loop-walk E2E green nightly; expand-contract migration discipline unbroken; unit-cost within the ratified COGS ceiling for four consecutive weeks.

**Documentation & operations:** the five runbooks written and each rehearsed once (Sev1, quarantine, provider outage, deletion request, rollback); ADR log current; DEBT.md honest; backup-restore drill performed; secrets rotation drilled; the Sev1 honesty protocol agreed as policy with the cohort's comms template drafted.

**Commercially:** ~25 founding customers onboarded and served; billing operating; the Document 07 gate evidence archived with the ledger.

---

# SECTION 10 — POST-V1 ROADMAP (EPIC HEADLINES ONLY)

**Version 1.1 (trigger-gated, per Document 03):** one-way CRM push; scoped→open conversation ("Ask Xenia"); inbox reply-detection for outcome capture; Slack delivery; collections; attribution-weighted corrections; reviews/news adapter families; per-section composition if Sprint 13's data demanded and deferred it.

**Version 2 (the back half, earned):** the AI inbox; delegated sending at L4–L5 with real deliverability/compliance infrastructure (N2-grade); pipeline intelligence; native mobile; the revenue-intelligence embryo on accumulated outcomes; US terrain tuning (rung 1b); the L2 judge to full gating; extraction distillation.

**Version 3 (the ladder climbs):** rung-2 vertical (creative agencies) with recalibrated intelligence; Ring-3 aggregated learning under its consent architecture; the advisor role's first surfaces; delegation's upper rungs as earned defaults; the ingestion platform's service extraction if scale demands.

---

# SECTION 11 — ENGINEERING CRITIQUE

**Where the roadmap is optimistic.** Twenty-two nominal weeks will not be twenty-two calendar weeks; the honest multiplier (1.5×) puts **V1 at ~30–34 weeks from build-start** — roughly seven to eight months, consistent with Document 03's "months 4–8" only if the research phase and build overlap as planned. Three pre-declared overruns: **Sprint 18** (the conversational interview is a mini-product; budget its double), **Epic 4** (real-world adapters always exceed fixtures — the buffer sprint will be spent), and **Sprint 20's** "runs unattended" (the first three Mondays will not be unattended). The plan also quietly assumes the research phase *passed* — a pivot verdict at the Week-7 gate reshapes Epics 4–8's targets, though 0–3 survive any wedge.

**Where it is too cautious.** The Epic 2 purity bar (95% coverage on *all* domain rules) can over-polish rules V1 barely exercises — coverage should concentrate on the citable laws, not every accessor. Preview environments for the API are ceremony at solo scale (staging suffices; already conceded). And two sprints of hardening may under-run if MVP weeks were disciplined — Epic 12 is allowed to compress; it is the only epic that is.

**Which milestones will move.** Sprint 13's *date* will move (it depends on golden data maturing); its *position* (before the app) must not. Sprints 17–19 will likely become four sprints. The founding-cohort growth (10→25) is a market event, not an engineering one — Epic 12's exit may wait on sales reality, and the plan should not pretend engineering controls it.

**The cut order if time constrains (pre-agreed, in sequence):** C6 drafts (loop survives); email one-tap actions (links suffice); reviews/news families (already deferred); export polish beyond CSV+PDF; the L2 judge entirely to V1.1 (L0+L1 carry MVP); interview *resumability polish* (session-resume can be cruder than designed for cohort one); and — last, reluctantly — queue-view refinement, never the correction loop, never the gate, never tenancy/audit/receipts, which are floors (Section 1, rule 7).

---

# SECTION 12 — SCORECARD

| # | Section | Score /10 | Justification & improvement |
|---|---|---|---|
| 1 | Build Philosophy | **9** | Linear-for-context, deployable-always, and the seven solo principles with rule 7's floors/scope distinction doing real work. *Improve:* none. |
| 2 | Epic Breakdown | **9.5** | The two reorderings (workbench to Epic 3, QA console before the app) are argued from the constitution and materially de-risk the plan; every epic has a falsifiable exit. *Improve:* none structural. |
| 3 | Sprint Plan | **9** | Twenty-two sprints, each week-shaped with DoD and required tests; Sprint 13 as the midpoint dial is the plan's best idea. Deduction: sprint-grain estimates are confessed guesses pending Sprint 1–2 calibration. *Improve:* re-estimate after the first two sprints measure real velocity. |
| 4 | Implementation Order | **9** | Critical path justified link-by-link; the never-early and deferrable lists inherit the constitution rather than taste. *Improve:* none. |
| 5 | Testing Strategy | **9** | The permanent canaries (tenancy, adapters), the named-rule suite, and gate-unrepresentability tests make the constitution mechanically enforced. *Improve:* live canary cadence may need tuning against source politeness. |
| 6 | Deployment | **8.5** | Expand-contract as rollback's enabler, flags with removal dates, drills scheduled. Deduction: single-region, single-provider assumptions unexamined (correctly deferred, but unstated until now). *Improve:* note the DR posture in the ops runbook. |
| 7 | Risk Register | **9** | Time honesty with a visible multiplier, the R1 fork at Sprint 13, maintenance in the calendar, and founder capacity named without romance. *Improve:* review monthly; risks age fast at solo scale. |
| 8 | Founder OS | **9** | Realistic: protected blocks, scheduled maintenance, weekends closed, the collapse rule ("the DoD moves, the deploy discipline doesn't"). *Improve:* revisit when the first hire changes the shape. |
| 9 | Definition of V1 | **9.5** | Checkable line-by-line, inherits every threshold from Documents 03/04/07, and explicitly allows C6's absence — scope courage where it counts. *Improve:* none; print it. |
| 10 | Post-V1 | **8.5** | Correctly headline-only and trigger-gated. *Improve:* nothing until V1 data exists. |
| 11 | Engineering Critique | **9.5** | Pre-declares its own overruns by sprint number, gives the real calendar (30–34 weeks), and pre-agrees the cut order ending at the untouchable floors. *Improve:* act on the re-estimate instruction. |
| 12 | Scorecard | **—** | Not self-scored, on principle. |

## Remaining founder decisions & pre-implementation blockers

**Decisions (ADR batch #1 — needed within Sprint 1):** monorepo confirmation; TanStack vs React Router; OpenAPI codegen tool; object-storage vendor; tracing/error vendors; synthetic-fixture design. **Decisions (before their sprints, not before starting):** Evidence-ID scheme (Sprint 9); entity floor + queue SLA (Sprint 8); chip taxonomy ratification (Sprint 15 — research output); shared-brief access model (Sprint 19); founding-rate billing terms in Stripe (Sprint 20); snapshot retention with counsel (before production data — a true blocker for Epic 11, not for build). **Process blockers:** the Week-7 gate verdict (blocks full commitment to Epics 4+ targets, not Epics 0–3); counsel engagement started (blocks production customer data, ~8 weeks of runway before it bites); Supabase/Stripe/Resend/Railway/Vercel accounts and the golden set's first artefacts (concierge output — arriving by design).

## Can engineering begin immediately?

**Yes — for Epics 0 through 3, today.** Nothing constitutional, commercial, or evidential blocks the skeleton, the foundations, the domain laws, or the research workbench: their ADRs are batch #1 (decidable in a morning), their scope serves the research phase rather than competing with it (the workbench makes the concierge faster and starts the golden dataset), and every one of their deliverables survives *any* Week-7 gate outcome including a pivot — tenancy, politeness, snapshots, and the constitution-in-code are wedge-independent assets. **Not yet — for Epics 4 onward as a committed calendar:** the full build's targets inherit the gate's verdict and the research phase's calibrations (chip taxonomy, astonishment thresholds, format learnings), and committing the adapter-through-app sequence before Week 7 would rebuild the documents' oldest warned-against error — engineering ahead of evidence. The plan is therefore already in motion and honestly conditional: **start Sprint 1 tomorrow; sign the rest at the gate.**

---

*End of V1 Build Plan v1.0. Governed by Documents 01–09; expected to be amended by reality weekly, except its floors (Section 1, rule 7), its gate conditions (Section 12), and the constitutional exit criteria it inherits — those move only through the documents that own them.*
