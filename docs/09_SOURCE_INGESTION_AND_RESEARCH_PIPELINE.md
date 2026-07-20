# XENIA — SOURCE INGESTION & RESEARCH PIPELINE DESIGN

**The complete lifecycle of intelligence: from public information to trusted judgment**

Version 1.0 · July 2026 · Internal — Engineering. Governed by Documents 01–08.

---

*This document designs the machinery Document 08 named as its own largest gap: how raw public information becomes trusted business intelligence, at auditable provenance and survivable unit cost. Everything the customer ultimately sees originates in this pipeline. The governing engineering rule is stated once and applied everywhere: **if a stage can be deterministic, it does not use AI.** AI is reserved for problems deterministic software cannot reasonably solve — because deterministic stages are testable, free, fast, and honest by construction, and every unnecessary AI call spends the COGS ceiling (Document 03), adds a failure mode (Document 04 §8), and dilutes auditability (Document 05). This is architecture, not implementation: no prompts, no APIs, no code.*

---

# SECTION 1 — RESEARCH PHILOSOPHY

**Why research is Xenia's primary capability.** The entire documentation stack converges on one dependency: the wedge was chosen for signal observability (Document 02), the product's centre of gravity is the brief (Document 03), the moat's first turn is trust in judgments (Document 01), and judgments are only as good as what they rest on. Xenia is not a reasoning company that happens to gather data; it is a *research* company whose reasoning is the last mile. The pipeline is therefore not infrastructure behind the product — it *is* the product's substance, and it gets first-class design, observability, and ownership accordingly.

**Why evidence comes before reasoning.** Reasoning over unverified input launders noise into confident prose — the generative failure mode that killed the AI SDR wave's credibility (Document 02) and that Class A of the failure taxonomy (Document 04) treats as catastrophic. Architecturally: the reasoner *never touches the raw web*; it receives only validated Evidence with receipts. This ordering is what makes the receipt rule enforceable rather than aspirational — you cannot cite what the pipeline never validated, and you cannot claim what you cannot cite.

**Why reasoning comes before recommendation.** A recommendation is a judgment with a stake (Document 03 C5); a judgment without visible reasoning is a verdict without a trial (N4). The pipeline enforces the order physically: fit theses are composed *from* extracted knowledge and scored *against* the DNA, and the decomposition is stored before the recommendation exists. There is no path through the pipeline where a recommendation is generated first and rationalised afterwards.

**Why recommendation comes before action.** The delegation ladder (Documents 03/06): Xenia's hands are gated behind trust rungs, so the pipeline's terminal output at V1 is always *presented judgment* — queue, brief, draft — never external action. The pipeline design must make this boundary structural: no stage has network egress toward a prospect.

**Why incomplete truth beats fabricated certainty.** Every stage below has a legitimate way to say "couldn't see" (Document 05's declared-blindness discipline), because a system denied an honest path to ignorance will manufacture knowledge — this is as true of pipelines as of models. Partial output flagged as partial (Document 06 §10) is a first-class success state at every stage, and completeness theatre is a named defect.

**How trust compounds over years.** Every brief either deposits or withdraws trust (Document 01's balance sheet). The pipeline's contribution: provenance that survives audit (any claim, any time, traceable to a dated snapshot), errors that are traceable and therefore honestly confessable (the Sev1 protocol runs on derivation records this pipeline writes), freshness that is managed rather than lied about, and per-source trust scores that make the *system's* scepticism improve with age. A pipeline that can always answer "how do you know?" is the only foundation on which a decade of "I trust this" can be built.

---

# SECTION 2 — PIPELINE OVERVIEW

The canonical flow, identical for every research request (ambient discovery, directed ask, or refresh — one pipeline, three entry points):

```
Prospect selected
   ↓  [1] PLAN        — research recipe from DNA + budget + cache state
   ↓  [2] ACQUIRE     — fetch from planned sources (politeness engine)
   ↓  [3] NORMALISE   — parse, clean, deduplicate, canonical content model
   ↓  [4] EVIDENCE    — extract candidate claims, bind to entity, span-ground
   ↓  [5] VALIDATE    — schema, entity, span, freshness checks → Evidence objects
   ↓  [6] KNOWLEDGE   — evidence → typed signals & attributes (rules first)
   ↓  [7] INSIGHT     — gap analysis, fit thesis, timing read (AI, receipt-bound)
   ↓  [8] EVALUATE    — L0 blocking checks, sampling to L1/L2
   ↓  [9] COMPOSE     — brief B1–B8 from validated parts (AI, receipt-bound)
   ↓ [10] STORE       — artefact + full derivation record
   ↓ [11] LEARN       — outcomes/corrections feed DNA & source trust (async)
```

Per-stage summary (each stage expanded in Sections 5–8):

| Stage | Latency target | Retry | Cache | Human intervention |
|---|---|---|---|---|
| 1 Plan | ms | n/a (pure) | recipe reuse per DNA version | none |
| 2 Acquire | secs–mins | per-source backoff, checkpointed | snapshot store (Ring 2) | quarantine decisions |
| 3 Normalise | ms–secs | deterministic re-run | normalised content, content-hash keyed | adapter repair queue |
| 4 Evidence | secs | bounded re-extract | extraction keyed to snapshot hash | low-confidence entity queue |
| 5 Validate | ms | n/a (pure) | n/a | dispute resolution |
| 6 Knowledge | ms–secs | deterministic re-run | signal store per BusinessRecord | none |
| 7 Insight | secs | bounded regenerate on validation failure | per (prospect, DNA-version) | Editor queue on repeated failure |
| 8 Evaluate | ms (L0) / async (L1/2) | n/a | n/a | the grading queue (L1) |
| 9 Compose | secs | bounded regenerate | per format version | MVP: 100% approval gate |
| 10 Store | ms | transactional | n/a | none |
| 11 Learn | async, ≤1 cycle | job retries | n/a | DNA structural proposals |

**Failure handling, uniformly:** every stage emits typed failures (source-unreachable, entity-ambiguous, validation-reject, budget-exhausted…); failures degrade the *output* honestly (couldn't-see entries, partial flags) rather than blocking the pipeline where partiality is acceptable; only Class-A risks (fabrication, misattribution) hard-block. **Observability, uniformly:** every stage logs its derivation contribution (input hashes, versions, costs, decisions) so the finished brief's derivation record is the concatenation of the pipeline's honesty about itself.

---

# SECTION 3 — THE SOURCE ECOSYSTEM

The Document 05 catalogue, engineered. Per source: purpose · trust (per-source score, seeded as below, then earned) · freshness/refresh · failure modes · cost · legal posture · expected longevity. **V1 ships six source families; the rest are staged** (Section 13 defends the cut).

**S1 Company websites (V1).** Purpose: self-declared positioning (E3) + measured states (E1: performance, technology, content cadence). Trust: high-for-intent, moderate-for-fact. Refresh: weeks for active prospects; on research. Failures: JS-walled content (headless rendering budgeted, not default — cost discipline), redesigns, blocking. Cost: cheap to fetch, moderate to render. Legal: public commercial publication, politeness engine mandatory. Longevity: permanent.

**S2 Public registers — Companies House first (V1).** Purpose: skeleton facts (existence, age, officers, filing health) at attestation grade (E2). Trust: highest seeded. Refresh: monthly + event-driven. Failures: lag, minimal small-company data, US unevenness at rung 1b. Cost: near-free (open API). Legal: explicitly public records; professional-minimum rule on officer data. Longevity: permanent.

**S3 Advertising transparency libraries (V1).** Purpose: the beachhead's killer E1 — active campaigns, platforms, creative cadence. Trust: high (platform-attested). Refresh: weekly for active DNAs. Failures: scope changes at platform whim (D2 watch), regional coverage gaps. Cost: cheap-to-moderate. Legal: purpose-built transparency surfaces — cleanest in the catalogue. Longevity: medium-high, policy-dependent.

**S4 Hiring surfaces — careers pages + job boards (V1).** Purpose: the highest-value E4 (costly-to-fake, forward-looking; the marketing-hire trigger). Trust: high. Refresh: weekly. Failures: aggregator duplication (dedup contract), ghost postings. Cost: cheap. Legal: public postings; aggregator terms respected per source. Longevity: permanent.

**S5 Review platforms (V1).** Purpose: E2/E4 — experience reality, velocity-as-trajectory. Trust: moderate (manipulable; velocity over averages). Refresh: weeks. Failures: astroturf (trust-score input), category coverage gaps. Cost: cheap. Legal: platform terms honoured; reviewers never profiled. Longevity: high.

**S6 News & trade press (V1).** Purpose: trigger events (E2/E4) — funding, expansion, leadership. Trust: publication-graded. Refresh: continuous monitoring for active DNAs. Failures: paywalls (couldn't-see), syndication inflation (independence collapse mandatory). Cost: cheap-to-moderate. Legal: headlines/facts with attribution; no paywall circumvention. Longevity: permanent.

**Staged (V1.5+):** LinkedIn company pages (compliant means only per Document 05 — official surfaces/licensed partners; the posture is settled, the adapter waits for the licensed route), press releases as a distinct feed, blogs/content feeds (E3, cheap, low-trust — easy add), podcasts & video (transcription cost vs. beachhead value unproven — deferred until a DNA demonstrably needs them), social content (platform-API volatility; company-accounts-only rule ready). **Customer-side sources (V1, different ring):** uploads, CRM exports, manual notes, conversation-attested facts (E5) — ingested through the same normalise→evidence path but stored in Ring 1, approval-gated (Document 05 §5), and never entering the global cache. **Future integrations** join only through the source-admission checklist (Document 05 §11) — the checklist is the API for growing this section.

---

# SECTION 4 — DETERMINISTIC VS AI RESPONSIBILITIES

The mandatory rulings. Default is deterministic; AI must argue its way in. **D** = deterministic, **AI** = model-driven, **H** = hybrid (deterministic backbone, AI for the residual).

| Task | Ruling | Why |
|---|---|---|
| URL discovery | **D** | Registries, sitemaps, search APIs, link-following rules. Enumerable problem; determinism = testable coverage. |
| HTML retrieval | **D** | Fetching is engineering (politeness, retries, rendering budget). No judgment involved. |
| Parsing | **D** | Parsers + per-source adapters. Breakage is a maintenance cost, not an AI use-case (Section 13 prices it). |
| Cleaning / boilerplate removal | **D** | Readability-class algorithms; deterministic output enables content-hash caching. AI here would poison cache determinism. |
| Language detection | **D** | Solved by libraries. V1 is English; other languages → declared couldn't-see. |
| Entity resolution | **H** | Deterministic matching first (domain, register ID, name+geo+officer heuristics) resolves the large majority; AI adjudicates the ambiguous residue with evidence shown; lowest-confidence cases → human queue. Misattribution is Class-A, so the *decision* is always recorded with its method and confidence. |
| Evidence extraction | **H** | Structured sources (registers, ad libraries, job feeds) extract deterministically — schema in, evidence out, zero tokens. Unstructured prose (about pages, news) uses schema-constrained AI extraction, span-grounded (Section 6). AI earns its place only where the input has no schema. |
| Knowledge extraction (signals) | **H** | Predominantly rules over typed evidence ("ad activity in ≥2 channels for ≥6 weeks → active-paid-media signal"). AI only for genuine classification residue ("is this DTC or marketplace-led?") with the answer stored as inference-with-confidence, never fact. |
| Insight generation (gaps, timing) | **AI** | The genuinely non-deterministic value: professional-grade interpretation (B4's non-obvious bar). Receipt-bound, budgeted, validated. This is what the tokens are *for*. |
| Fit scoring | **D** | Scores compute deterministically from knowledge × DNA weights — auditable, decomposable (N4), instant, free. |
| Fit thesis & recommendation narrative | **AI** | Turning a decomposed score into the argued analyst's note is language work; the *numbers* it narrates are deterministic inputs it may not alter. |
| Brief composition | **AI** | Language work over validated parts, receipt-bound, L0-gated. |
| Receipt validation | **D** | ID-binding, structure, vocabulary, entity-consistency checks are pure code — the blocking layer *must* be deterministic (an AI guarding AI is circular at the exact point circularity is fatal). Sampled entailment (AI judge) sits above, advisory-then-gating per Document 04 L2. |
| Confidence calibration | **D** | Band assignment from evidence type/count/agreement/freshness via fixed rules, adjusted by measured calibration data. The model proposes nothing here (Document 06: the vocabulary is assigned by rule). |
| Evaluation | **H** | L0 deterministic (blocking), L1 human, L2 AI judge (calibrated, never self-grading) — per Document 04, unchanged. |
| Storage / caching / scheduling | **D** | Obviously. Listed because "let the agent decide what to cache" is a real industry failure mode we are declining explicitly. |
| Learning (signal weighting, DNA updates) | **D** | The weighting philosophy (Document 04 §5) is *rules*, applied deterministically to events; AI drafts only the human-facing narration of changes. Learning that isn't deterministic isn't auditable, and the changelog demands audit. |

**The pattern the table encodes:** AI appears exactly three load-bearing times — unstructured extraction, insight, and composition — each receipt-bound, budgeted, validated by deterministic code, and evaluated by the harness. Everything else is software. This is the unit-cost strategy (Section 9), the auditability strategy (Document 05), and the testability strategy (Document 08 §11) expressed as one design decision.

---

# SECTION 5 — SOURCE INGESTION

The acquire→normalise half of the pipeline, stage by stage.

**Discovery.** Inputs: a Prospect (or candidate identity) + the research recipe. Deterministic expansion: known domain → sitemap and key-page rules (home, about, pricing, careers, blog index); register lookups by name/number; ad-library and job-board queries by resolved identity; news queries by canonical name + aliases. Output: a fetch plan (URLs × source adapters × priority × budget). Quality gate: plan bounded by recipe budget — discovery can never expand unboundedly (cost governor, Section 9).

**Fetching — the politeness engine.** One shared subsystem all adapters use: per-domain rate limits and concurrency caps, robots and technical-signal honour (Document 05's respectful acquisition as code), honest user-agent, retry-with-backoff, per-domain circuit breakers, and a **rendering budget** — headless browsing only where an adapter declares it necessary and the recipe affords it. Failures: unreachable → typed failure feeding couldn't-see; blocked → circuit-break + source-health signal, never evasion (N2; the compliant-means-only posture is enforced here, in one place, rather than trusted to every adapter).

**Snapshotting.** Every successful fetch persists an immutable raw snapshot (object storage, content-addressed by hash, with fetch metadata: URL, timestamp, adapter version, HTTP context). The snapshot is the provenance contract's anchor — "re-findable" (Document 05 §3) means *we kept what we saw*, because the web won't keep it for us. Retention per the Document 05 schedule; snapshots are Ring 2 (no customer fingerprint — and cache-warming decoupling per Document 05's critique note applies here).

**Cleaning & normalisation.** Deterministic reduction of raw snapshots into the **canonical content model** — a small set of typed shapes: `Page` (readable text + structure), `Posting` (role, location, dates), `Filing` (typed register facts), `AdRecord` (platform, dates, creative meta), `ReviewSet` (aggregates + velocity), `Article` (headline, body, publication, date). Adapters own the mapping; the rest of the pipeline consumes only canonical shapes — this is the anti-corruption boundary that contains per-source churn (when a source changes its HTML, exactly one adapter changes).

**Deduplication.** Content-hash for exact dupes; near-duplicate detection for boilerplate and syndication (the same press release across twenty outlets collapses to one canonical Article with twenty sightings — the independence analysis of Document 05 §3 running at ingestion, where it's cheap, not at reasoning, where it's too late). Job-board aggregator dedup keyed on role+company+window.

**Metadata & entity binding.** Every canonical item is bound to a **BusinessRecord** via the entity-resolution ruling (Section 4): deterministic match where strong keys exist (domain, register number), scored heuristics where they don't, AI adjudication for the residue, human queue below the confidence floor. Binding confidence is stored *on the binding* — a low-confidence binding taints everything downstream of it, and the validate stage (Section 6) knows.

**Language handling.** Detection deterministic; V1 processes English, declares the rest ("their site is primarily in Welsh — I could read only the English pages"). No silent translation at V1 (translation is an inference layer with its own error modes; it queues behind demonstrated need).

**Versioning & storage.** Canonical items are versioned by supersession (new fetch of the same logical thing supersedes, never overwrites; history retained per retention policy). Storage split per Document 08: raw snapshots in object storage, canonical items and all downstream objects in Postgres, referenced by snapshot key.

---

# SECTION 6 — THE EVIDENCE PIPELINE

The Evidence object's full lifecycle — and the receipt rule as mechanism.

**Raw content → Candidate evidence.** Extractors (deterministic for structured shapes, schema-constrained AI for prose) emit *candidates*: claim text, claim type, the source item, and — for extractive claims — **span references** into the canonical content (start/end offsets into the snapshot-derived text). A candidate is a proposal, not knowledge.

**Candidate → Validated evidence.** Deterministic validation: schema conformance; entity-binding confidence above floor; **span-grounding** — for extractive claims, the span must actually exist in the referenced content (the anti-fabrication check at the *extraction* layer, before any reasoning model ever sees the claim); temporal sanity (observed_at within source item's validity); type-legality (an E3 self-declaration cannot be typed E1). Failures: candidate dropped with a typed reason (extraction-quality telemetry) — never patched.

**Validated → Evidence object.** The Document 05 §3 contract, now with identity: **Evidence ID** (stable, content-derived — the same observation re-extracted yields the same ID, which is what makes citation stable across regeneration); **Source ID** (the source item + adapter version + snapshot key); type E1–E5; observed_at; extraction confidence; freshness class with its half-life clock. Immutable; superseded by newer observations of the same claim-slot; disputable via corrections (contested state propagates per the derivation graph rule, Document 05 §9).

**Evidence → Evidence graph.** Relationships computed deterministically and stored as edges: **corroborates** (independent sources, same claim-slot — raises confidence per the agreement rules; syndication-collapsed sightings explicitly do *not* corroborate), **conflicts** (same slot, incompatible values — surfaces per report-don't-resolve), **supersedes** (temporal chains). "Graph" is a data model, not a graph database (Section 13 keeps this honest) — at V1 these are relations on the evidence store.

**Evidence graph → Receipt table.** The pipeline's most important artefact: for each generation task, a **numbered, frozen table of validated Evidence** — IDs, claim texts, types, dates, confidence — assembled deterministically from the graph (conflicts included *as* conflicts, freshness-decayed items demoted or excluded by rule). The generating model receives the table and **may only make material claims that cite table IDs**; the L0 validator rejects any output whose claims cite nothing, cite non-existent IDs, or contradict the cited entry. The receipt table snapshot is stored in the derivation record, making every brief's epistemic basis replayable. **This is the receipt rule as architecture:** not a guideline the model follows, but a closed world the model cannot escape — fabrication requires citing evidence that doesn't exist, and the validator holds the only door.

**Citation rules & conflict handling** inherit Documents 05/06 unchanged: strongest one-two receipts inline, full trail one level deep, conflicts presented as findings with both receipts cited, absence declared in couldn't-see (which is itself generated deterministically from the *plan* — the recipe knows what it tried and failed to see, so declared blindness is computed, not remembered).

---

# SECTION 7 — THE KNOWLEDGE PIPELINE

Evidence is what was observed; knowledge is what it *means*. This stage converts validated evidence into the typed signal layer the DNA scores against — predominantly by rules (Section 4's ruling).

**The signal taxonomy** maps directly onto the DNA schema's categories (Document 02 §7), because knowledge exists to be scored: **facts** (firmographics: size band, age, location, model — from register + site evidence); **technology indicators** (stack, platform, site quality measures); **hiring indicators** (roles, cadence, the marketing-hire trigger); **growth indicators** (trajectory composites: hiring + review velocity + expansion evidence); **buying indicators** (timing signals per DNA category 5); **ICP indicators** (the customer-relevant attributes: DTC-ness, price point, category); **negative indicators & disqualifier triggers** (in-house team signals, category exclusions — evaluated with absolute precedence per the schema's law); **risk indicators** (filing health, instability markers).

**Promotion rules.** A signal exists only when its evidence basis meets its type's threshold (counts, types, independence — e.g., "active paid media" requires E1 ad-library evidence, not a self-declared "we advertise"). Signals store their derivation (which evidence, which rule version) — knowledge is as auditable as evidence, one level up.

**Confidence evolution.** Deterministic update on new evidence: corroboration raises (with independence checks), conflict lowers and flags, freshness decay lowers on each half-life sweep (the Document 05 clocks, executed by the scheduled jobs of Document 08 §7). Confidence maps to the four-word vocabulary by fixed banding — the same bands everywhere, per Document 06.

**Decay and retirement.** Signals decay toward *unknown*, not toward false (absence-of-evidence semantics, Document 05); a decayed signal demotes from scoring inputs to research-prompting ("their ad activity was last confirmed in March — refreshing"); superseded signals retire with history retained. Retirement is visible to the planner: stale knowledge is precisely what the refresh recipe exists to re-verify — the decay system and the acquisition scheduler are two halves of one freshness economy.

---

# SECTION 8 — RESEARCH ORCHESTRATION

The engine that runs Sections 5–7 as one accountable process, mapped onto Document 08's worker architecture.

**Planner (deterministic).** Input: prospect, DNA version, trigger (ambient/directed/refresh), budget, cache state. Output: the research recipe — sources to consult, depth per source, rendering allowances, spend cap, and the *expected coverage* (which claim-slots this recipe should fill). The planner is rules, not an agent: recipes are versioned, testable, and cost-bounded by construction. Cache-awareness is its core intelligence — a warm BusinessRecord yields a delta-recipe (verify staleness, fetch gaps), not a full crawl.

**Retriever.** Executes the fetch plan through the politeness engine; checkpoints per source (Document 08's resumable jobs); emits snapshots and typed failures.

**Extractor.** Runs the per-shape extractors over new canonical content; emits candidates; meters AI extraction cost per item class.

**Validator.** The deterministic gates of Section 6; also the aggregation point for extraction-quality telemetry (drop rates by adapter and extractor version — the earliest warning of adapter rot or prompt regression).

**Reasoner.** The three AI stages (insight, thesis narrative, composition) against frozen receipt tables, per Document 08 §6's pipeline shape — including the per-section composition variant held ready (each B-section its own bounded call with its own receipt subset) if unit-cost data demands cheaper retries.

**Evaluator.** L0 inline and blocking; sampling per policy into the L1 queue and L2 judge; MVP's 100% Editor gate is a sampling-rate configuration, not a different code path (one pipeline from concierge to scale — the QA delta measured on the same rails it will later be enforced on).

**Composer & Storage.** Brief assembly at the current format version; artefact + derivation record stored transactionally; queue placement by deterministic ranking.

**Learning.** Async, event-driven per Document 08: decisions/corrections/outcomes → weighting rules → DnaChangeEvents and source-trust updates. Source trust closes the loop back into planning: a source whose evidence keeps getting corrected loses recipe priority — the pipeline's own scepticism compounding (Section 1's promise, mechanised).

**Retries & fallbacks.** Stage-local retries per Section 2's table; fallback philosophy uniform: *degrade honestly* — a failed source becomes couldn't-see, a failed insight pass becomes a leaner brief flagged partial, a failed composition after bounded regeneration goes to the Editor queue, and nothing customer-facing ships silently degraded. **Human review points, exhaustively:** entity-resolution floor cases; repeated validation failures; the L1 grading queue; MVP's approval gate; quarantine decisions; and DNA structural proposals — six doors, all through the internal console, all audited.

---

# SECTION 9 — COST ARCHITECTURE

The unit-economics model that decides whether R1 survives (Document 03's central risk).

**The cost anatomy of one brief.** Cheap and fixed: fetching, parsing, normalising, dedup, signals, scoring, storage — engineering costs, fractions of pence, flat with scale. Expensive and variable: AI extraction (prose sources only), insight generation, composition — plus rendering (headless browsing) where required. The design's entire cost strategy is that the expensive three are (a) minimised by the deterministic-first rulings, (b) receipt-bounded so retries are cheap and rare, (c) budgeted per recipe with governors, and (d) amortised by the ring architecture.

**What is globally reusable (Ring 2):** snapshots, canonical content, Evidence, BusinessRecords, signals — the entire understanding of *the world*. **What is customer-specific (Ring 1):** fit theses, scores, briefs' B4–B7 framing, recommendations — the judgment layer. The split means the second customer researching the same prospect pays only the judgment layer — and the beachhead concentrates demand (UK e-commerce SMBs, a shared terrain by design, Document 02), so cache density rises *fast* exactly where we operate.

**What expires and recomputes:** per the freshness economy (Section 7) — refresh recipes re-acquire only decayed slots; insight/composition regenerate only when their inputs changed materially or format version advanced (input-hash comparison, deterministic).

**The declining cost curve — four compounding mechanisms:** cache hit rate rises with customer density in-terrain; deterministic coverage expands (each adapter and rule added converts a token cost into a code cost permanently); model prices per unit of capability keep falling industry-wide (a tailwind we plan with but never depend on); and extraction distils (schema-constrained extraction is the classic candidate for smaller/cheaper models once the golden set can prove parity — an evaluation-gated migration, per Document 04). **Worked hypothesis [calibrates hard, per the ledger]:** cold-brief marginal cost target at MVP in the low single pounds; cache-warm target under a third of cold; the COGS ceiling (≤25% of price, Document 03) implies roughly £80–£100/customer/month at the core band — comfortable at ten briefs/week warm, tight cold, which is *why the planner's cache-awareness is a P0 pipeline feature and not an optimisation*. The unit-cost ledger (per stage × per source × per workspace) is the instrument panel; the MVP exists to replace this paragraph's hypotheses with its measurements.

**Governors.** Recipe-level spend caps; workspace daily budgets (Document 08 §8) with honest-wait degradation; global provider budget alarms; and the structural guarantee that no stage can loop unboundedly (plans are finite, retries bounded, agentic open-ended browsing does not exist in this architecture — the planner enumerates, the retriever executes, nothing "explores").

---

# SECTION 10 — OBSERVABILITY

What engineers watch, organised as the three dashboards the pipeline ships with (extending Document 08 §9's two-dashboard rule with the pipeline's own board).

**The source-health board (the Steward's screen).** Per source: fetch success rates, circuit-breaker state, adapter drop rates (extraction-quality telemetry), accuracy sampling results (L1's per-source slice), trust score and trend, quarantine state, cost per acquired item. Alert lines: drop-rate spikes (adapter rot — the most frequent operational event this pipeline will ever have), accuracy decline (silent decay, D2), any politeness violation (a bug class treated as Sev2 minimum, because N2 lives here).

**The pipeline board (engineering's screen).** The funnel per stage: throughput, latency percentiles, retry rates, typed-failure distribution, queue depths per job class; receipt-rule metrics — **validation rejection rate** (the model fighting the closed world; its trend prices the composition-shape decision), regeneration counts, Editor-queue arrivals; entity-resolution mix (deterministic/AI/human shares — the human share is a cost and a quality signal both); coverage attainment (recipe expected-coverage vs. achieved — the couldn't-see rate, per DNA, which feeds the thin-market conversation's data, R3).

**The intelligence board (the Editor's screen, per Documents 04/08).** Rubric distributions by dimension and version; golden regression deltas; judge agreement; calibration curves; hallucination/misattribution detections (target: zero, tracked forever); correction rates and what they targeted (evidence vs. judgment — corrections against *evidence* indict the pipeline's front half; against *judgment*, its back half — this split is the single most diagnostic number the system produces); unedited-pass rate through MVP; freshness distribution of served briefs; knowledge-decay backlog (staleness debt).

**Cost telemetry** cross-cuts all three: the unit-cost ledger per stage/source/workspace, cache hit rates (Ring-2 economics realised), budget-governor events. Weekly review reads: five watched product metrics first (Document 03), then intelligence board, then cost — in that order, constitutionally.

---

# SECTION 11 — FAILURE MODES

The pipeline challenged, with mitigations — extending the Document 04/05 taxonomies to this machinery's specifics.

**Source outages & access tightening.** Expected, continuous, planned-for: circuit breakers, couldn't-see degradation, no single-source claim-slots where avoidable (recipes list fallback sources per slot), and the strategic posture already ruled (Document 05: we lose coverage; competitors lose legality). *Residual:* an ad-library scope change is the single most damaging plausible event for the beachhead's B4 sections — tracked as a named watch item with a quarterly "what would we do Monday" note.

**Entity ambiguity.** The hardest real-world problem in the pipeline — small businesses with no domain, colliding names, franchise/branch structures. Mitigations: strong-key-first resolution, binding confidence stored and propagated, the human floor, and *honest scoping*: V1's beachhead terrain (UK e-commerce, register-covered, domain-bearing) is close to the easiest entity population available — a deliberate wedge dividend. The critique (Section 13) says what happens outside it.

**AI extraction errors & prompt regressions.** Span-grounding catches fabricated extraction; schema constraints catch drift; the golden regression gates prompt changes (CI-enforced, Document 08); extraction-drop and validation-rejection telemetry catch what tests miss, fast. *Residual:* subtle misreading (right span, wrong interpretation) — L1 sampling's job, weighted toward new extractor versions.

**Knowledge pollution & synthetic content.** The AI-slop problem (Document 05 §10) lands here concretely: mitigation is the evidence-type economics (attestation-cost weighting — E1/E4 lead scoring; E3 self-declaration priced low), source trust scores that *move*, independence collapse at ingestion, and — honestly — vigilance over solution: this degrades gradually and is watched, not solved.

**Receipt failures (the model fighting the closed world).** If validation rejection runs hot, costs inflate and latency grows. Mitigations, in order: prompt engineering against the golden set; per-section composition (smaller worlds, cheaper retries — the held-ready variant); and, at the limit, the honest concession that some section styles must simplify. The rejection-rate metric decides, with the MVP's 100% sampling providing the data almost immediately.

**Cost explosions.** Structurally prevented (no unbounded loops, budgeted recipes, governors) — the residual risk is *aggregate* creep: rendering budgets, refresh frequency, retry accumulation. The ledger's weekly read plus governor alarms own it; any week's COGS above ceiling triggers the Document 04 release-discipline analogue for recipes (freeze recipe expansion until back under).

**Quality regressions & coverage gaps.** The harness gates releases; coverage attainment per DNA makes gaps visible per customer (feeding the honest conversations Document 06 designed); the deferred sources (podcasts, social) are *known* gaps, declared, not discovered.

---

# SECTION 12 — EVOLUTION

**Prototype (now → research phase).** The pipeline exists as the founder's scripts + model calls producing concierge briefs — but *the artefacts follow this document's shapes from day one* (evidence tables kept, snapshots saved, derivations recorded, edit log per Document 07): the concierge is the pipeline run by hand, so its data seeds the golden sets and its costs seed the ledger. **Concierge → Alpha.** The six V1 source families get real adapters in dependency order (register and ad library first — structured, deterministic, highest trust-per-effort; websites next; jobs, reviews, news following); the politeness engine and snapshot store land before any scale; extraction goes schema-constrained; the Editor console's two screens arrive. Human gate at 100%. **V1 (founding cohort).** The full orchestration live; sampling narrows as the harness earns it; the unit-cost ledger runs hot weekly; the planner's cache-awareness lands (the first cost inflection). **100 customers.** Cache density pays; refresh economy tuned on real decay data (the half-lives calibrated at last); extraction distillation evaluated; adapter maintenance becomes the visible recurring cost it always was. **1,000.** Continuous discovery; broker-backed queues (Document 08's trigger); the source ecosystem grows through the admission checklist (LinkedIn's licensed route, content feeds); per-section composition likely standard by here. **10,000.** The ingestion platform extracts as a service on the pre-drawn seam (Document 08 §10): own workers, own store, internal API; multi-region acquisition for rung-1b terrain. **100,000.** Honest per Document 08: rebuilt organs with money and teams; what carries through unchanged is the point of this section:

**Stable across all stages:** the eleven-stage shape; the canonical content model as anti-corruption boundary; the Evidence contract and receipt mechanism; the politeness posture; provenance and derivation records; the deterministic-first rulings; the ring split. **Expected to change constantly:** adapters (weekly, forever — this is the maintenance mortgage the company signs today with open eyes); extraction models and prompts (evaluation-gated); recipes (tuned per vertical per rung); the entity resolver's sophistication; storage engines under the stable contracts.

---

# SECTION 13 — ENGINEERING CRITIQUE

**Where we are overengineering.** The evidence *graph* — corroboration/conflict/supersession edges — is, at V1 scale, three columns and two queries; building it as a general graph abstraction would be resume-driven design, and this document's own "data model, not graph database" caveat must be enforced in review. The signal taxonomy risks premature ontology: eight indicator families defined before one real DNA has scored one real prospect — ship the four the beachhead's scoring actually consumes (facts, hiring, ads/technology, disqualifiers) and let the rest earn instantiation from concierge evidence. The three-dashboard suite is two dashboards too many for a solo founder; one page with the diagnostic split (corrections: evidence vs. judgment) and the rejection rate covers month one.

**Where we are underengineering.** Adapter maintenance is named but not resourced: at six source families the realistic steady-state is *something is broken somewhere most weeks* — the design needs (and doesn't yet have) an adapter-testing harness with recorded fixtures and a breakage-triage runbook; this is the pipeline's true recurring cost centre, above tokens. Headless rendering is budgeted but unpriced — modern e-commerce sites (our exact terrain) are JS-heavy, so the rendering share of cost may be structurally higher than the anatomy suggests; the concierge phase must measure it. And the entity resolver's human-floor *rate* is assumed low because the wedge terrain is easy — the first adjacent-terrain expansion (rung 2's design partners, US rung 1b) will test that assumption before the resolver is ready for it.

**Assumptions that will almost certainly prove wrong somewhere.** The freshness half-lives (invented, all of them — the decay sweeps will be re-tuned within a quarter); the expected-coverage tables per recipe (real couldn't-see rates will surprise us per niche); the cost hypothesis's absolute numbers (kept only as targets; the ledger replaces them); and "structured sources extract deterministically" — registers and ad libraries change schemas too, just slower; deterministic is a maintenance promise, not a maintenance exemption.

**What should be simplified.** The V1 source list is already cut to six; the honest floor for the *alpha* is four (register, ad library, websites, jobs) — reviews and news add trust texture but not scoring backbone, and each deferred adapter is a fortnight returned to brief quality. Language handling, the graph abstraction, and dashboard count, per above.

**What must not be built until real usage exists.** Podcast/video ingestion; social adapters; embeddings anywhere in this pipeline; extraction distillation (requires the golden set at maturity); multi-region acquisition; the ingestion platform's service extraction; and any planner "intelligence" beyond cache-aware rules — the agentic-researcher temptation will knock repeatedly (it demos beautifully) and the answer is in Section 9's last sentence: nothing explores.

---

# SECTION 14 — SCORECARD

| # | Section | Score /10 | Justification & improvement |
|---|---|---|---|
| 1 | Research Philosophy | **9** | The evidence→reasoning→recommendation→action ordering grounded in the constitutional stack, with "the reasoner never touches the raw web" as its architectural crux. *Improve:* none. |
| 2 | Pipeline Overview | **9** | Eleven stages, one shape, three entry points; the uniform failure/observability contracts do real work. *Improve:* the latency column needs real numbers after alpha. |
| 3 | Source Ecosystem | **8.5** | Six V1 families fully specified with legal posture and longevity; staging honest. Deduction: the critique immediately and rightly cuts alpha to four. *Improve:* adopt the four-family alpha. |
| 4 | Deterministic vs AI | **9.5** | The document's core: nineteen rulings, each argued, converging on AI-appears-exactly-three-times — the unit-cost, auditability, and testability strategies as one table. *Improve:* enforce in review; the table is law only if cited. |
| 5 | Source Ingestion | **9** | The politeness engine as single enforcement point for N2, content-addressed snapshots as provenance anchor, canonical model as churn container. *Improve:* the adapter-testing harness the critique demands. |
| 6 | Evidence Pipeline | **9.5** | Span-grounding + the frozen receipt table make the receipt rule a closed world with one guarded door — the constitutional mechanism this document existed to design. *Improve:* nothing before contact; expect schema churn (Document 08 predicted it). |
| 7 | Knowledge Pipeline | **8.5** | Signals mapped to DNA categories with promotion thresholds and the freshness economy. Deduction: premature ontology risk, self-identified. *Improve:* instantiate four families, earn the rest. |
| 8 | Orchestration | **9** | Planner-as-rules (not agent), six named human doors, one code path from concierge to scale. *Improve:* per-section composition sketch should be written before MVP data forces it. |
| 9 | Cost Architecture | **9** | The anatomy, the ring amortisation, four compounding decline mechanisms, governors with no-unbounded-loops as structure. Deduction: absolute numbers are confessed guesses. *Improve:* the ledger replaces them — the MVP's true deliverable. |
| 10 | Observability | **8.5** | The corrections evidence-vs-judgment split is the design's most diagnostic single metric. Deduction: three dashboards for one founder, self-caught. *Improve:* one page at MVP. |
| 11 | Failure Modes | **9** | The ad-library scope-change named as the most damaging plausible event with a standing what-Monday note; rejection-rate as the composition-shape decider. *Improve:* maintenance as reality supplies new modes. |
| 12 | Evolution | **9** | Concierge-as-pipeline-by-hand (seeding golden sets and the ledger from week one) is the section's best idea; stable/changing lists honest. *Improve:* none. |
| 13 | Engineering Critique | **9.5** | Cuts its own scope twice (six→four sources, three→one dashboards), names the true cost centre (adapter maintenance, above tokens), and bars the agentic-researcher door explicitly. *Improve:* act on all of it. |
| 14 | Scorecard | **—** | Not self-scored, on principle. |

## Unresolved ADRs

**(1)** Alpha source count: four vs six families (critique recommends four). **(2)** Headless rendering engine and its budget policy. **(3)** Snapshot retention durations per source class (with counsel, per Document 05). **(4)** Evidence-ID derivation scheme (content-addressing details — stability vs. supersession semantics). **(5)** Entity-resolution confidence floor and human-queue SLA. **(6)** Per-section vs monolithic composition — decided by MVP rejection-rate data (held from Document 08, restated). **(7)** The adapter-testing harness design (fixtures, contract tests, breakage triage). **(8)** News-source licensing posture (which feeds, what cost). **(9)** Recipe versioning and rollout mechanics (recipes as release artefacts like prompts?). **(10)** The couldn't-see computation's coverage tables (per-recipe expected slots — first draft from concierge data).

## The next engineering document

**Recommendation: "Xenia — V1 Build Plan: Sprint 0, milestones, and the definition of done."** The design stack is complete: strategy (01–03), standards (04–06), validation (07), architecture (08), and now the pipeline (09). Document 08 said that after this document "the writing is tickets" — the build plan is the bridge: Sprint 0's skeleton (repo, CI, the domain package's pure rules, the politeness engine and snapshot store as first code), the milestone sequence tied to Document 07's gates and Document 03's MVP entry criteria, the definition of done per milestone (which golden-set thresholds, which dashboards live, which ADRs closed), and the honest calendar for one founder plus the hiring triggers the documents have accumulated. It should be short, dated, and obsolete within weeks by design — the last document before the work is code and customers.

Per instruction: recommended, not written. Waiting.

---

*End of Source Ingestion & Research Pipeline Design v1.0. Governed by Documents 01–08; amendable by ADR with document-amendment escalation where constitutional. The deterministic-first table (Section 4), the receipt mechanism (Section 6), the politeness engine's single-point enforcement (Section 5), and the no-unbounded-loops guarantee (Section 9) are citable in any engineering review.*
