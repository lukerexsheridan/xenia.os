# XENIA — DATA & COMPLIANCE STANDARD

**What Xenia may observe, use, and remember — the knowledge constitution**

Version 1.0 · July 2026 · Internal — Every data, memory, retrieval, and compliance decision references this document

---

*Governed by the Foundation Document v1.1, the ICP & Wedge Strategy, the Product Strategy & V1 Scope, and the Intelligence & Evaluation Standard; contradicts none of them. This document defines Xenia's knowledge boundaries: what may be known, how it is acquired, how much it is trusted, what is remembered, and what is forgotten. It is not a legal document — one standing caveat governs throughout: **this standard sets the company's posture; specialist counsel ratifies its legal load-bearing walls before launch** (a Foundation requirement, restated as this document's first founder decision). Its relationship to the Intelligence Standard is exact: that document governs how knowledge is judged; this one governs what knowledge may exist at all. Where the two meet (freshness, source trust, quality detection), this document defers to the harness for measurement and owns the policy.*

---

# SECTION 1 — KNOWLEDGE PHILOSOPHY

## The five epistemic classes

Everything Xenia holds belongs to exactly one of five classes, and the discipline of the entire document flows from refusing to blur them.

**Observation.** Something seen, at a time, at a place: "this page, on this date, displayed this pricing." Observations are the atomic layer — they cannot be wrong in the way claims can (the page really did display it), only stale or misread. Every other class is built on them.

**Evidence.** An observation *bound to a claim*: promoted, structured, attributed, dated — the Evidence object of the Product Strategy's ontology, given its full constitution in Section 3. Evidence is knowledge with a receipt.

**Inference.** A conclusion derived from evidence but not directly observed: "their ad spend is likely £15–40k/month, from footprint and category norms." Inference is legitimate and essential — most valuable knowledge is inferential — but it must *always carry its derivation and its confidence*, and it may never silently harden into fact. The Intelligence Standard's N5 enforcement lives on this boundary.

**Memory.** Knowledge retained across time because it remains useful: the customer's preferences, the resolved outcomes, the corrected mistakes. Memory is knowledge with a *tenure policy* (Section 4) — what earns retention, what decays, what requires re-confirmation.

**Belief.** Xenia's current working model — the DNA's weightings, the learned patterns, the fit priors. Beliefs are *positions held for action*, revisable by design, and never presented to the customer as anything grander than they are ("based on what I've seen so far, I think…"). A belief presented as a fact is this document's cardinal sin, mirroring the Intelligence Standard's cardinal failure class.

## Why the distinctions matter

Three reasons, in ascending order. **Operationally:** each class has different storage, decay, correction, and deletion rules — a system that stores inference like observation cannot honour a correction properly (fix the inference and the bad observation re-derives it; fix the observation and the inference must visibly re-derive). **Contractually:** the customer's trust is calibrated per class — they will forgive a wrong belief ("fair, you're still learning us") and will not forgive a fabricated observation; collapsing the classes collapses the forgiveness structure with it. **Constitutionally:** the Foundation's explainability and honesty principles (N4, N5) are enforceable only if the epistemic type of every statement is machine-known — "explain your reasoning" has no implementation if the system cannot distinguish what it saw from what it concluded from what it merely remembers believing.

---

# SECTION 2 — KNOWLEDGE HIERARCHY

Eight knowledge classes, each defined by five properties: **ownership** (whose is it), **confidence** (default trust), **freshness** (how fast it rots), **expiry** (when it must go), **auditability** (what trace it must keep).

**K1 — Public business facts.** The observable business world: what companies exist, what they sell, where, at what evident scale. *Ownership:* nobody's — public reality; Xenia's compilation of it is Xenia's asset. *Confidence:* varies by source (Section 6), never assumed. *Freshness:* per-claim-type half-lives (the Intelligence Standard's tolerance windows, owned here as policy). *Expiry:* superseded on re-observation; never expires as history (dated snapshots may be retained for trajectory analysis). *Auditability:* full provenance, always.

**K2 — Observed evidence.** K1 promoted into claim-bound Evidence objects for active research. Same ownership; higher structure; audit-grade provenance mandatory (Section 3).

**K3 — Derived intelligence.** Briefs, gap analyses, fit theses, scores — Xenia's work product, built from K1/K2 conditioned by K5–K7. *Ownership:* the work product is Xenia's; *the instance is the customer's* — their briefs serve them alone (a fit thesis about prospect X for agency A never informs agency B — Section 7's ring boundary). *Confidence:* explicit per artefact (B8). *Freshness:* regeneration cadence; served stale only with staleness declared. *Auditability:* decomposable to evidence, per the rubric.

**K4 — Customer-provided knowledge.** The interview, uploads, CRM exports, stated strategy, disqualifiers. *Ownership:* entirely the customer's — held in trust, exportable always, deleted on departure (the offboarding promise of the Product Strategy's critique, made policy here). *Confidence:* authoritative about their intent; *not* automatically authoritative about their market (a customer's belief about which clients suit them is data, and the DNA may respectfully test it — the sovereignty rule). *Expiry:* never by time; only by customer action. *Auditability:* attributed to the providing user, timestamped.

**K5 — Behavioural learning.** Patterns from decisions, pursuit, dwell, edits. *Ownership:* the customer's, unambiguously — behavioural exhaust is not a company asset to repurpose (Foundation Section 14 posture). *Confidence:* low per event, meaningful in patterns (Intelligence Standard Section 5's weighting). *Freshness/expiry:* rolling windows; raw events age out, learned aggregates persist with decay **[calibrates]**. *Auditability:* aggregates traceable to event classes, not necessarily to each event forever.

**K6 — Historical outcomes.** Won, lost, meetings, reasons. *Ownership:* the customer's — the most valuable data they will ever give us, held under the strictest ring (Section 7). *Confidence:* ground truth (the harness's L3/L4 substrate). *Expiry:* never, while the customer remains; fully deleted or exported on departure. *Auditability:* total — outcomes are the flywheel's title deeds.

**K7 — Working memory.** Task-scoped context: the current research run, the session's thread. *Ownership:* operational. *Expiry:* aggressive — hours to days; working memory that lingers becomes unaudited belief, which is how systems develop superstitions. Anything worth keeping is *promoted deliberately* into K4–K6/K8 with provenance, never retained by inertia.

**K8 — Long-term organisational memory.** The Memory object of the Product Strategy: preferences, cadence, voice, history-of-relationship ("no December pitches"; "hates the word synergy"). *Ownership:* the customer's. *Confidence:* graded by recency and repetition; important memories are *re-confirmed in conversation* rather than assumed forever. *Expiry:* decay-toward-neutral with changelog (the DNA Standard's asymmetry applied to memory: stated laws persist, observed habits decay). *Auditability:* inspectable by the customer — an employee's notebook their boss may always read.

The hierarchy's single load-bearing rule: **knowledge only moves up-hierarchy through explicit promotion with provenance** — an observation becomes evidence by binding, evidence becomes intelligence by derivation, events become memory by pattern-confirmation. Silent class-jumping (a working hypothesis quietly becoming permanent belief) is the pollution pathway every data system dies of, and it is banned by architecture, not by intention.

---

# SECTION 3 — THE EVIDENCE STANDARD

The Evidence object, given its constitution. The Intelligence Standard made evidence-mandatory composition the defence against fabrication; this section defines what qualifies.

## Evidence types, by epistemic strength

**E1 — Measured observation** (strongest): machine-verifiable states — site performance, technology presence, active ad units, posting cadence. Objective, repeatable, datable. **E2 — Third-party attestation:** reviews, press coverage, directories, filings — someone other than the subject says it; strength varies with the attester (Section 6's per-source trust). **E3 — Self-declaration:** what the company says about itself — its site, its posts, its careers page. Authoritative for *intent and positioning* ("they present themselves as premium"), weak for *fact* ("we're the UK's leading…"); the standard requires self-declared claims to be framed as self-declarations whenever they carry weight. **E4 — Market-behavioural:** hiring activity, expansion signals, review velocity — actions that imply states. Strong precisely because costly to fake (companies rarely post jobs they don't want filled). **E5 — Customer-attested:** what the customer knows firsthand ("we pitched them in 2024; they went quiet"). Authoritative within their experience, dated, attributed.

## The provenance contract

Every Evidence object carries: source (specific enough to re-find), observation timestamp, evidence type (E1–E5), extraction confidence (was the source clear or ambiguous?), entity binding (which verified company — the misattribution defence), and freshness class. An observation missing any of these may inform *working* hypotheses (K7) but may not underwrite a customer-facing claim. This is the receipt rule: **no receipt, no claim.**

## Corroboration, conflict, and absence

**Agreement:** independent sources agreeing raises confidence multiplicatively only when genuinely independent — twenty sites syndicating one press release are one source wearing twenty hats, and independence assessment is part of the evidence layer's job, not a nicety. **Conflict:** conflicting evidence is *reported, not resolved silently* — recency and source-trust weight the presentation ("their site says 12 staff; the register shows 30+ — possibly stale site or contractor-heavy model"), and the conflict itself is often the insight (B4 material). Silent resolution destroys exactly the honesty the couldn't-see discipline builds. **Absence:** missing evidence is first-class information — the mandatory couldn't-see declaration (B8) plus the deeper rule: *absence of evidence is evidence of absence only where presence would be expected* (no ads observed means "not advertising visibly," never "not advertising" — the modality is policed by lint). **Decay:** confidence decays on the freshness half-life of the claim type — ad activity in weeks, staffing in months, location in years **[calibrates]** — and decayed evidence *demotes* (from underwriting claims to suggesting re-observation), it does not silently vanish.

## Citation philosophy

Customer-facing citation is calibrated to usefulness, not to academic completeness: material claims link their strongest one or two receipts inline (checkability at the point of doubt); the full evidence trail lives one click deeper; and the couldn't-see list is always visible. The philosophy: citations exist so the customer can *check us fast*, and so that when we are wrong, they can see exactly where — a citation practice designed for the trust catastrophe it will someday have to survive (Sev1 honesty rule, Intelligence Standard Section 9), not for decoration.

---

# SECTION 4 — MEMORY

The memory taxonomy, with its tenure law. The classes extend the Product Strategy's DNA/Memory distinction into a complete system.

**M1 — Working memory** (the current task). Expires in hours-to-days; promotion-only retention (K7's rule). Never requires confirmation — it is scaffolding.

**M2 — Session memory** (this conversation, this research session). Expires with the session plus a short grace window; distilled conclusions promote to M3/M4 with provenance; the raw transcript is retained per the customer-data retention schedule (Section 8), owned by the customer.

**M3 — Organisation memory** (the relationship: preferences, cadence, tone, history). Decays toward neutral without reinforcement; *stated* preferences persist until revoked but are re-confirmed conversationally on a long cycle ("still true that December is off-limits?") — the re-confirmation is a product moment (an attentive employee checks), not a compliance chore. Customer-inspectable always.

**M4 — Ideal Client DNA memory** (their market model). Governed by the DNA Standard entire (duties, decay asymmetry, conflict hierarchy, changelog); listed here for completeness and for one addition: the DNA's *history* is memory too — reverted elements, seasonal patterns, the record of how their strategy evolved — and it never expires while the customer remains, because year-three Xenia citing year-one context is the moat made conversational.

**M5 — Outcome memory** (ground truth). Never expires; never decays; the one class where forgetting would be malpractice. Deleted only by customer action or departure.

**M6 — Behaviour memory** (the learned patterns from K5). Rolling raw windows; persistent aggregates with decay; never customer-facing in raw form (nobody wants their dwell-times narrated), always customer-facing in effect ("I've noticed you prefer…" — the reconciliation moments).

**M7 — Knowledge memory** (Xenia's model of the business world — the global cache of K1/K2). Owned by Xenia; refreshed on freshness policy; expires by supersession. The one memory class that serves all customers (Section 7's outer ring), and therefore the one class that must *never* contain anything customer-derived.

**The confirmation rule:** memory that *changes Xenia's behaviour materially* requires confirmation at formation or at first use ("you mentioned avoiding hospitality — I've made that a working preference; make it a rule?"), and structural memory (disqualifiers, strategy shifts) requires it absolutely (the Product Strategy's human-in-the-loop zone). **The expiry summary:** working and session memory expire by design; organisation and behaviour memory decay without reinforcement; DNA and outcome memory persist while the relationship does; global knowledge memory refreshes forever. And all of it — every class — honours the departure rule: when a customer leaves, what is theirs leaves with them (export), and what remains of them here is deleted on the schedule counsel ratifies, with the Foundation's N6 (leaving as easy as joining) as the design bar.

---

# SECTION 5 — LEARNING BOUNDARIES

The hard lines. Everything in this section is enforceable by architecture where possible and by policy everywhere, and every line inherits a Foundation non-negotiable.

## What Xenia may learn

About **businesses**: anything observable in their public commercial footprint, for the purpose businesses publish it — being found, evaluated, and approached commercially (the Foundation's purpose-alignment principle). About **markets**: patterns across businesses — category norms, signal-outcome correlations, vertical dynamics — within the ring rules of Section 7. About **the customer**: their stated intent, their market model, their preferences and cadence and voice, their outcomes — everything required to be their employee, held in their ring. About **individuals**: the *professional minimum* — that a person holds a role at a company, professional contact routes published for professional contact, and what they have publicly stated in their professional capacity. Individuals appear in Xenia as officers of businesses, never as subjects of profiles.

## What Xenia may never infer (the prohibited inferences)

No inference, however statistically available, of: protected characteristics (race, religion, health, sexuality, political affiliation — of anyone, prospect or customer); private-life facts from professional data (relationship status from posting patterns; health from activity gaps); creditworthiness or financial distress of *individuals*; and no sentiment profiling of named individuals ("the founder seems difficult") — business-culture observations must attach to observable business behaviour (public communications style, stated values), never to psychological assessment of persons. The rationale is constitutional, not merely legal: the Foundation's business-not-surveillance principle defines the company, and the test is permanent — *if the inference would feel like surveillance to its subject, it is not ours to make.* These prohibitions bind even when a customer asks ("what's the founder like?" receives business-observable answers only).

## What requires explicit customer approval

Ingesting any new category of *their* data (a CRM export, an inbox connection when V1.5 proposes it, uploaded documents beyond the interview's scope); any use of their data beyond serving them (a case study, an anonymised benchmark contribution — Section 7's aggregation requires opt-in **[calibrates — opt-out with prominence is the fallback posture counsel may prefer, but opt-in is the default proposal because the moat is trust]**); structural DNA changes (already law, Product Strategy Section 8); and any external representation (nothing goes out under their name without their hand — N3's territory).

## What remains customer-controlled, always

Disqualifiers (their law, never decayed, never overridden); deletion (of any memory, any correction, any prospect from their world — with the system honest about consequences: "deleting this outcome removes what I learned from it"); export (everything theirs, always, in usable form); delegation levels; and the relationship's end (departure executes the Section 4 rule without friction — churn prevention by product excellence, never by data hostage-taking, which is both N6 and, bluntly, the UK village-market reputation play the Product Strategy's critique identified).

---

# SECTION 6 — DATA SOURCES

The source catalogue: purpose, trust, limitations, legal posture, cadence, failure modes — and the standing admission rule that governs every future addition (Section 11): *a source joins the catalogue only if we would comfortably describe our use of it to a regulator, to the source, and on a front page* (the Foundation's provenance discipline, operationalised).

**Company websites.** *Purpose:* the richest single source — self-declared positioning (E3) plus measured states (E1: performance, technology, content cadence). *Trust:* high for what-they-say-about-intent, moderate for facts. *Limits:* staleness (sites outlive their truths); aspiration dressed as description. *Legal:* public commercial publication; accessed respectfully (rate discipline, robots/technical-signal honour — N2's "respectful acquisition"). *Cadence:* weeks for active prospects, on-demand at research time. *Failure:* redesigns breaking observation; JS-walled content limiting E1 depth — declared in couldn't-see.

**LinkedIn company pages.** *Purpose:* headcount bands, hiring posture, positioning, activity. *Trust:* moderate-high for structure, self-declared for the rest. *Limits & legal — stated bluntly:* LinkedIn's terms are restrictive, enforcement is real, and half our competitor set lives in violation of them. **Xenia's posture: compliant means only** — public pages within technical and contractual boundaries, licensed data via approved partners where available, and *no* member-profile scraping, credential automation, or ToS-evading collection, whatever the competitive cost (N2 decides this, and Section 12 prices the cost honestly). *Cadence:* per research event. *Failure:* access tightening — treated as a permanent strategic assumption, not a surprise (Section 10).

**Public registers & filings (Companies House and international equivalents).** *Purpose:* legal existence, age, officers, filing health — the skeleton facts. *Trust:* highest available (E2 at attestation-grade). *Limits:* lagging, minimal for small companies. *Legal:* explicitly public records; personal data within them (directors' names) handled under data-protection law with the professional-minimum rule. *Cadence:* monthly-to-quarterly. *Failure:* jurisdictional unevenness — a UK advantage (Companies House is generous) that rung 1b must not assume of the US.

**Review platforms.** *Purpose:* customer-experience reality, volume-as-trajectory (E2/E4). *Trust:* moderate — manipulable in both directions; velocity and distribution trusted over averages. *Limits:* category coverage varies. *Legal:* platform terms honoured; review *authors* are never profiled. *Cadence:* weeks. *Failure:* review-gating and astroturfing — pattern-detection belongs in per-source trust scoring.

**News & trade press.** *Purpose:* trigger events (funding, expansion, leadership) — timing gold (E2/E4). *Trust:* publication-graded. *Limits:* SMB coverage sparse; churnalism recycles single press releases (the independence rule catches this). *Cadence:* continuous monitoring for active DNAs. *Failure:* paywalls (couldn't-see), syndication inflation.

**Hiring pages & job boards.** *Purpose:* the highest-signal E4 source — hiring is costly, specific, and forward-looking (a marketing-manager posting is a beachhead timing signal *par excellence*). *Trust:* high (companies rarely fake hiring). *Limits:* ghost postings exist; posting-to-intent lag. *Cadence:* weekly for active DNAs. *Failure:* aggregator duplication inflating apparent activity — deduplication is part of the ingestion contract.

**Public social content.** *Purpose:* activity cadence, voice, campaigns (E1/E3). *Trust:* low-moderate — performance theatre is the medium's nature. *Limits & legal:* platform terms honoured per platform; *company accounts only* — the professional-minimum rule keeps individual accounts out of scope except where an individual *is* the business channel (a founder-led brand account, treated as company communications). *Cadence:* weeks. *Failure:* API/policy volatility — never a single point of dependence.

**Advertising transparency surfaces (ad libraries).** *Purpose:* the beachhead's killer E1 — who is running what, where. *Trust:* high (platform-attested). *Limits:* coverage varies by platform and region. *Legal:* purpose-built public transparency — the cleanest source we have. *Cadence:* weeks. *Failure:* scope changes at platform whim; the D2 monitoring watches exactly this.

**Customer-uploaded documents & CRM exports.** *Purpose:* K4 — their world, in their words. *Trust:* authoritative for their experience, dated for the world ("their 2023 client list" is history, not state). *Legal:* processed under the customer agreement, their ring only, approval-gated at ingestion (Section 5). *Failure:* stale uploads silently anchoring the DNA — upload dating is mandatory and staleness surfaced.

**Customer conversations & manual corrections.** *Purpose:* the highest-intent signal in the system (Intelligence Standard Section 5's hierarchy). *Trust:* authoritative for intent. *Legal:* their ring, their ownership, inspectable. *Failure:* the sycophancy loop — governed by the sovereignty rule, not by source policy.

**How sources combine.** Corroboration across *independent* sources builds confidence (Section 3); precedence follows evidence type and per-source trust scores, never source convenience; and every combined judgment retains its decomposition — the combination rule is the citation rule: a claim built from three sources can show all three. One prohibition completes the catalogue: **no purchased data of undisclosable provenance** — data brokers whose collection methods we couldn't describe on the front page fail the admission rule regardless of utility, which forecloses a real competitive convenience and is the intended price of the moat (Foundation, Section 14).

---

# SECTION 7 — CUSTOMER KNOWLEDGE VS GLOBAL KNOWLEDGE

The three-ring architecture — likely a future moat, and certainly a present trust contract.

## Ring 1 — Customer-private intelligence (the inner ring)

Everything derived from or about one customer: their DNA, their Memory, their outcomes, their behaviour, their fit theses and scores, their pipeline's existence. **Never crosses the boundary. Ever.** Not as training data, not as "anonymised examples," not as retrieval context for another customer, not in aggregate below the thresholds of Ring 3. The rule has a commercially uncomfortable corollary embraced deliberately: two rival agencies may both employ Xenia, and *neither will ever detect the other's existence through the product* — no "others are pursuing this prospect" signals, no demand-heat indicators built on customer pipelines, however monetisable. N7 wrote this rule; this document refuses the clever exceptions in advance, because every one of them is a leak wearing a feature costume.

## Ring 2 — Global business knowledge (the outer ring)

Xenia's model of the observable world: K1/K2/M7 — the facts and evidence about businesses, compiled from public sources. Shared across all customers by design: when two agencies research the same prospect, the *facts* come from one cache (fresher, cheaper, consistent), while the *fit theses* built on those facts live in each agency's Ring 1 and differ because their DNAs differ. This split is the unit-economics engine (research cost amortises across the base — the COGS ceiling's best friend) and it is philosophically clean: public facts belong to nobody; judgments belong to whoever they serve.

## Ring 3 — Aggregated learning (the guarded middle)

Cross-customer patterns: which signal types predict conversion in which verticals, category norms, benchmark curves — the across-customer flywheel and outcome graph of the Foundation. Admission rules, all mandatory: **minimum-population thresholds** before any pattern exists (no aggregate that could describe fewer than N customers **[calibrates — N set with counsel]**); **irreversibility** (no aggregate from which a customer's data could be reconstructed or inferred); **contribution consent** (opt-in per Section 5, revocable); and the **explanation test** — every aggregate must be comfortably explainable *to the customers whose data fed it* (N7's own language). What Ring 3 improves for everyone: vertical priors, timing-signal weights, DNA templates, the improving cold start the Foundation promises ("day-one Xenia in 2029 outperforms day-ninety Xenia of 2027"). What it never contains: identities, pipelines, win-loss specifics attributable to anyone, or DNA content as such. The Foundation already capped this ring's *claims* pre-scale (its critique: negligible at seed); this document caps its *contents* permanently.

The three-ring summary the whole company can memorise: **facts are shared, judgments are private, patterns are guarded.**

---

# SECTION 8 — COMPLIANCE AS PRODUCT DESIGN

The Foundation argued compliance is a moat; this section makes it mechanism. Each principle is stated as the product behaviour that embodies it — compliance the customer can *see* is the only kind that builds trust.

**Privacy (data minimisation as architecture).** The generate-fresh-don't-hoard posture (Foundation Section 14) is the default: Xenia compiles understanding on demand from sources, retains the minimum that serves the customer, and treats personal data as radioactive inventory — the professional-minimum rule (Section 5) caps what enters; freshness policy caps how long it stays. One edge the beachhead makes live and counsel must ratify: **sole traders and single-director companies blur business data into personal data** (UK reality: much of the SMB prospect terrain *is* legally personal data), so the lawful-basis work — legitimate-interest assessments, balancing tests — is not enterprise theatre but core product infrastructure, built once, early, properly.

**Transparency.** The couldn't-see declarations, the confidence language, the AI-generated labelling (Foundation Section 14's commitments) — plus this document's addition: **the prospect-facing answer.** When a prospect asks a customer "how did you know that about us?", the honest answer must be comfortable: "public information, professionally researched." If any sourcing decision would make that answer squirm, the source fails admission. And when a *prospect* contacts Xenia directly (it will happen — "what do you have on my company and why?"), the answer is a process, not a panic: a public statement of what Xenia does, sources used, and their rights — drafted with counsel before launch, not after the first email.

**Consent & rights (operationalised, not filed).** Subject-access, correction, erasure, and objection are *product features with SLAs*, not legal inbox tickets: a prospect's erasure or objection request suppresses them from all customers' discovery (a global suppression list — one request, honoured everywhere, permanently); corrections propagate on the evidence layer; and the machinery is built into V1, because retrofitting rights-handling is how compliance becomes the constraint the Foundation promised it wouldn't be.

**Auditability.** The provenance contract (Section 3) plus the changelogs (DNA, memory) mean every judgment, every datum, every mutation can answer "where did this come from and why is it here" — which is simultaneously the N4 explainability promise, the regulator's first question, and the debugging tool engineering would have built anyway. One artefact, three masters: this is what compliance-as-design *means*.

**Customer ownership & deletion.** Ring 1 is theirs: export always, deletion honoured with consequences stated, departure clean (Section 4's rule). The retention schedule — how long each class persists after departure — is drafted by this document's principles (minimum defensible, uniformly applied) and ratified by counsel.

**Regional philosophy.** The Foundation's strictest-major-regime default, applied concretely: UK GDPR/PECR posture as the design floor for all markets including the US (rung 1b inherits UK-grade behaviour even where US law demands less), because one product behaving one way is buildable and auditable, and because "we treat your data like Europeans require" is a *selling line* in the post-AI-backlash market, not a burden. Regime divergence is handled by adding strictness locally, never by subtracting it anywhere.

**Why this increases trust — the mechanism, not the slogan.** Every behaviour above is *visible* at a trust-critical moment: the citation when the founder doubts, the couldn't-see when the data thins, the deletion that actually deletes, the answer the prospect receives. The wounded buyer (ICP Section 5) cannot be argued into trust; they can only observe their way there — and compliance-as-design is the discipline of making the observable moments prove the posture. The moat compounds the same way the DNA does: every honoured right, every clean answer, every refused grey source is a deposit competitors constitutionally cannot match, because their unit economics depend on the greyness (Foundation, Section 14 — their exposure is our high ground).

---

# SECTION 9 — DATA QUALITY

Detection and remediation per defect class — the policy layer above the Intelligence Standard's harness (which owns measurement). The division: the harness *finds*; this section says *what happens next*.

**Stale knowledge.** *Detection:* freshness metadata against per-type half-lives (L0); staleness-complaint clustering from corrections. *Remediation:* demote-and-refresh (Section 3's decay rule) — and when refresh fails (source gone), the claim degrades to dated-historical or retires; it never lingers as implicit current truth.

**Contradictory knowledge.** *Detection:* entity-level consistency checks at ingestion; cross-source conflict flags. *Remediation:* the report-don't-resolve rule for customer-facing surfaces; internally, conflicts queue for source-trust adjudication — repeated conflicts *lower the losing source's trust score*, so the catalogue learns which sources lie.

**Hallucinated knowledge.** *Detection:* the receipt rule makes it architecturally hard (claims without Evidence can't render as fact); entailment sampling (L0) and grader audits (L1) catch what slips. *Remediation:* Sev1 protocol (Intelligence Standard Section 9) — plus this document's addition: the offending generation path is traced, and any *derived* artefacts built on the hallucination are regenerated, because pollution propagates through K3 and cleanup must follow the derivation graph, not just delete the visible error.

**Incomplete knowledge.** *Detection:* coverage checklists per brief section (B1–B8 completeness at L0); couldn't-see density trending. *Remediation:* honest declaration always; systematic gaps (whole claim-types missing for a vertical or region) escalate to source-catalogue review — incompleteness at scale is a sourcing-strategy defect, not a research defect.

**Weak evidence.** *Detection:* claims resting on single low-trust sources; independence violations (syndication rings). *Remediation:* confidence down-grading enforced in language; weak-evidence claims barred from B5 fit theses (judgments need strong receipts; colour may rest on weaker ones).

**Missing sources.** *Detection:* the per-source health monitoring (D2) — yield, accuracy sampling, access-failure rates. *Remediation:* the quarantine protocol (source suspended, dependent claims demoted, customers' affected briefs flagged for refresh) and the Section 11 removal decision when quarantine becomes permanent.

The remediation meta-rule: **every fix propagates through the derivation graph** — evidence corrections re-derive inferences, source removals demote dependent claims, and nothing customer-facing silently keeps citing what the system no longer believes. This is expensive by design; it is what "the evidence layer is load-bearing" costs, and the cost was accepted when N4 was written.

---

# SECTION 10 — FAILURE MODES

The register, with the two inherited entries (D1 coverage, D2 silent decay) deepened and six new ones named.

**Coverage gaps (D1, deepened).** The terrain thins non-uniformly: niches, regions, and company-size bands where public footprint is sparse (the sub-10-employee prospect may be near-invisible). *Mitigation:* coverage mapped per DNA at onboarding — Xenia should *know and say* "your niche is 70% observable" — converting a silent quality lottery into a managed expectation; the thin-market conversation (Product Strategy R3) is this failure mode's product face.

**Source outages & access tightening (D2 + the LinkedIn assumption).** Platforms will tighten; the catalogue's compliant-means-only posture concentrates this risk (we refuse the workarounds competitors use). *Mitigation:* no single-source dependence for any claim type; licensed-data relationships cultivated early; and the strategic stance stated for the record — **when a source closes, we lose coverage; competitors lose legality.** We can survive our loss; theirs compounds.

**Platform policy changes.** Ad libraries narrowing scope, registers throttling, review platforms restricting. *Mitigation:* the source-health dashboard treats policy watch as monitoring, not news; material changes trigger catalogue review within the week (Section 11).

**Regulatory changes.** GDPR-family tightening on legitimate interest; AI-transparency duties; new scraping jurisprudence. *Mitigation:* the strictest-regime default absorbs most tightening as already-compliant; counsel briefings scheduled, not reactive; and the honest asymmetry from the Foundation restated — regulation that raises the floor drowns the grey competitors first (their exposure, our high ground).

**Silent decay.** Sources rotting without failing loudly. *Mitigation:* per-source accuracy sampling (L1's source-health slice), trust scores that move, quarantine that triggers on trend, not just on incident.

**Overfitting & knowledge pollution — including the AI-slop problem, named directly.** The public web is filling with machine-generated content: fake reviews, AI-written company blogs, synthetic press, SEO-spun directories. Evidence built on synthetic exhaust is pollution wearing E2's clothes. *Mitigation:* per-source trust scoring weights *attestation cost* (E4's costly-to-fake logic generalised — hiring posts and ad spend are expensive lies; blog posts are free ones); independence analysis discounts syndication; and the evidence-type taxonomy already prices self-declaration low. This failure mode grows every year the company exists; it is a standing agenda item, not a solved problem.

**Knowledge poisoning (adversarial).** Eventually, prospects or competitors may learn what signals Xenia reads and manufacture them. *Mitigation:* costly-signal weighting again (the defence is economic, not detective); anomaly detection on signal patterns; and honesty that this is a scale problem — at 100 customers nobody games us; the mitigation matures with the exposure.

**Customer misuse.** The customer exporting Ring 2 compilations to feed a spam cannon; using research to harass; requesting individual profiling. *Mitigation:* product design (no bulk contact export — the Product Strategy's refusal, now a data rule), acceptable-use policy with teeth (the ICP's disqualified-customer discipline applied post-sale), and the prohibited-inference lines that hold *against* customer requests (Section 5). We refuse the revenue rather than carry the complicity — priced into the plan since the Foundation's N1/N2.

---

# SECTION 11 — GOVERNANCE

**Ownership.** The **Data Steward** owns this standard — source catalogue, trust scores, retention schedule, rights machinery, the register of Section 10. Initially the founder (the third hat, after CEO and Intelligence Editor — Section 12 prices this honestly); the first senior data/compliance-literate hire inherits it. The Steward and the Intelligence Editor are deliberately *two* roles even when one person: the Editor asks "is it good?"; the Steward asks "may we know it?" — and product decisions need both signatures when they touch both questions.

**Source admission.** New sources enter by checklist, in writing: purpose, evidence types provided, trust assessment, legal posture (the front-page/regulator/source test), cost, failure modes, and the Steward's signature. No engineering convenience admits a source; no deadline waives the checklist. **Source review:** quarterly health review of the full catalogue (trust scores, yield, accuracy samples); ad-hoc review within a week of any material policy change. **Source removal:** triggered by legal-posture change, trust-score collapse, or failed quarantine; removal executes the Section 9 propagation rule (dependent claims demoted, affected briefs flagged).

**Customer notification.** Required when: their data was touched by an incident (Sev1 data class — same-day, per the honesty rule); a source loss materially degrades their coverage ("your niche's observability dropped; here's what changed and what I can still see" — an employee reports bad news, not just good); retention or policy changes alter what is held about them; and a rights request from a prospect affects their pipeline (suppression explained without drama). The notification philosophy inherits Foundation 12.2: we say so first.

**Override.** Only the founder may override a Steward decision — in writing, in the log, with reasoning — mirroring the Editor's protocol exactly. Two named overrides that can never happen regardless: the prohibited inferences (Section 5) and the Ring 1 boundary (Section 7), which are constitutional (Foundation N7 territory) and outside any individual's authority, including the founder's. A constitution someone can override is a preference.

---

# SECTION 12 — FOUNDER CRITIQUE

**Where we are too conservative — priced honestly.** The compliant-means-only sourcing posture, the no-broker rule, and the professional-minimum cap on people-data mean Xenia will sometimes *know less than competitors* — a rival tool will surface the personal mobile number and the enriched contact graph we refuse. The document bets that the beachhead values clean over complete; the ICP's psychology section supports the bet; but nobody has measured the demo-day cost of the moment a prospect tool shows more columns. The bet stays (it is constitutional), but the *sales narrative* for the gap must be built deliberately — "here's why we don't have that, and why that protects you" — or the principle will read as weakness precisely when it is the point. Also arguably over-conservative: default opt-in for Ring 3 aggregation may starve the across-customer flywheel at exactly the scale it starts mattering; the [calibrates] fallback (prominent opt-out) exists because trust-with-momentum may beat purity-with-stagnation, and counsel plus the first fifty customers should decide, not this document alone.

**Where we are too permissive.** Ring 2's shared fact-cache assumes public facts carry no customer fingerprints — but *which* facts get compiled, when, is driven by customers' research, and a sufficiently clever observer of cache freshness could theoretically infer interest patterns. Low risk at our scale, nonzero in principle; the mitigation (cache warming decoupled from individual customer queries) should be an architecture note now, not a retrofit. Behaviour memory (M6) is also broadly drawn — "dwell patterns" is a wide licence written by people who currently have no dwell data; the first privacy-conscious design partner who asks "what exactly do you record about how I use this?" deserves an answer this document hasn't fully specified. Tighten before V1, not after the question.

**What still requires validation.** All of it that touches law: the legitimate-interest balancing for sole-trader-heavy terrain, the retention schedule, the Ring 3 thresholds, the prospect-rights machinery — this document repeatedly says "counsel ratifies" and counsel has not yet existed; until that engagement, this standard is a well-reasoned posture, not a cleared one. Empirically: the freshness half-lives (invented, pending decay data); the coverage-percentage promise ("your niche is 70% observable" requires coverage measurement nobody has built); and the AI-slop discount weights (the pollution problem is real; our pricing of it is guesswork until source-accuracy sampling produces numbers).

**What risks remain, unresolved by design.** The concentration of three governance hats (CEO, Editor, Steward) on one founder is the standard's largest practical weakness — every protocol above assumes signature-separation that is fictional until the first hires; the honest mitigation is calendared self-review and the explicit promise that the *first senior hire* relieves one hat. And the deepest risk: this document, like the Intelligence Standard before it, could function as sophisticated procrastination — constitutional perfection as a substitute for the concierge test's contact with reality. The ship-the-third rule applies here too: V1 needs the receipt rule, the ring boundaries, the professional-minimum cap, the source checklist, and the departure rule. The rest activates on contact with customers, counsel, and scale.

---

# SECTION 13 — SCORECARD

| # | Section | Score /10 | Justification & improvement |
|---|---------|-----------|------------------------------|
| 1 | Knowledge Philosophy | **9** | Five epistemic classes with different correction/decay/deletion behaviour, and the forgiveness-structure argument for why blurring them destroys trust. *Improve:* none structural. |
| 2 | Knowledge Hierarchy | **9** | Eight classes × five properties, and the promotion-only rule that bans silent class-jumping — the document's quiet load-bearer. *Improve:* the K5 aggregate-decay windows need real data. |
| 3 | Evidence Standard | **9.5** | The receipt rule, the independence test for corroboration, report-don't-resolve for conflicts, and absence-as-information — the Evidence object now has a constitution worthy of its architectural role. *Improve:* half-lives await decay data. |
| 4 | Memory | **9** | Seven types with a coherent tenure law; the confirmation rule and the departure rule give it edges; M7's never-customer-derived cap protects the ring model. *Improve:* M6's breadth — the critique's own instruction to tighten pre-V1. |
| 5 | Learning Boundaries | **9.5** | The prohibited-inference list with the surveillance test, binding even against customer requests — the section a regulator, a journalist, and a design partner could each read with rising confidence. *Improve:* none; counsel ratification only. |
| 6 | Data Sources | **9** | Eleven categories with honest legal postures (the LinkedIn bluntness especially), the admission rule, and the no-broker prohibition priced as intended cost. *Improve:* per-source trust scores need their first real numbers from L1 sampling. |
| 7 | Customer vs Global | **9.5** | "Facts are shared, judgments are private, patterns are guarded" — the three-ring model resolves the moat/privacy tension cleanly, refuses the leak-as-feature exceptions in advance, and gives unit economics its engine. *Improve:* the cache-fingerprint mitigation from the critique becomes an architecture note. |
| 8 | Compliance as Design | **9** | Every principle rendered as visible product behaviour; the sole-trader edge caught; the prospect-facing answer prepared; strictest-regime as one-product simplicity. *Improve:* counsel, counsel, counsel — the section is a brief for that engagement. |
| 9 | Data Quality | **8.5** | Clean division of labour with the harness; the derivation-graph propagation rule is the expensive right answer. Deduction: remediation SLAs unstated. *Improve:* attach timeframes per defect class. |
| 10 | Failure Modes | **9** | The AI-slop pollution entry and the costly-signal economic defence are ahead of most of the industry's thinking; the "we lose coverage, they lose legality" framing will be quoted. *Improve:* the poisoning entry matures with scale, as stated. |
| 11 | Governance | **8.5** | Two-role separation with constitutional no-override zones. Deduction: the three-hats fiction, named only in the critique. *Improve:* calendar the hat-relief hire criteria now. |
| 12 | Founder Critique | **9** | Prices conservatism honestly (the demo-day column gap), catches its own permissiveness (M6, cache fingerprints), and re-applies the ship-the-third discipline to itself. *Improve:* act on the two tighten-before-V1 items. |
| 13 | Scorecard | **—** | Not self-scored, on principle. |

## Remaining founder decisions

**(1)** Engage specialist counsel and put this document in front of them — the standing caveat converted to an engagement letter (blocks: retention schedule, legitimate-interest assessments, Ring 3 thresholds, prospect-rights process); **(2)** ratify the compliant-means-only sourcing posture with its priced coverage cost — this is the decision competitors would most like us to fumble; **(3)** decide Ring 3 consent default (opt-in proposal vs. prominent opt-out fallback) after counsel and design-partner soundings; **(4)** ratify the no-broker prohibition; **(5)** approve the professional-minimum people-data cap as product law, including against customer requests; **(6)** set the M6 behavioural-memory specification (the tighten-before-V1 instruction); **(7)** ratify the departure rule and offboarding export scope before the first design partner signs; **(8)** adopt the source-admission checklist as binding process; **(9)** define the hat-relief criteria (which hire, at what milestone, relieves Editor or Steward first).

## The next document

**Recommendation: "Xenia — Design & Experience Standard: how Xenia looks, speaks, and behaves."** The reasoning: the standards layer is now complete — what we build (03), how good it must be (04), what it may know (05) — and the sharpest remaining gap is the one the concierge test hits *first in the calendar*: the research brief must be *designed* — its visual form, its voice, its narrative shape — before ten design partners receive one, because the astonishment bar measures a felt experience and the Foundation stakes the brand on craft (Stripe authority, Mercury warmth, the calm premium). That document should define: the voice and tone system (Xenia's language — the ICP's vocabulary rules made generative); the brief and DNA document as designed artefacts (the screenshot moment is a design deliverable); the interface principles that enforce "Xenia is the product" (P2's no-dashboard rule made visual); the motion and speed standards (fast software as brand); and the delight moments' specifications from the Product Strategy's journey. It is the last document before the work becomes making things — which is exactly when it is needed.

Per instruction: recommended, not written.

---

*End of Data & Compliance Standard v1.0. Governed by the Foundation Document v1.1, the ICP & Wedge Strategy, the Product Strategy & V1 Scope, and the Intelligence & Evaluation Standard; amendable by the Foundation's procedure. The receipt rule (Section 3), the ring boundaries (Section 7), the prohibited inferences (Section 5), and the source-admission rule (Section 6) are citable by name in any future data decision — and the first two are constitutional: no one, including the founder, may override them.*
