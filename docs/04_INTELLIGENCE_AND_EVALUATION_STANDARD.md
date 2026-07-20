# XENIA — THE INTELLIGENCE & EVALUATION STANDARD

**What "good intelligence" means, how it is measured, and how it improves**

Version 1.0 · July 2026 · Internal — Every engineer, PM, and AI researcher, before shipping anything involving AI

---

*Governed by the Foundation Document v1.1, the ICP & Wedge Strategy, and the Product Strategy & V1 Scope; contradicts none of them. This document exists because the Product Strategy's central risk (R1: briefs must automate at quality and cost) references quality gates that had no operational definition. It is the company's equivalent of a payments-reliability standard or search-quality guideline: the reference every AI-touching decision is tested against. Its numbers inherit the series' honesty convention — thresholds are pre-registered hypotheses, calibrated against the concierge test's artefacts, and marked **[calibrates]** where that data will move them. One sentence governs everything below: **in this company, "the model said so" is never an answer; "here is the evidence, the reasoning, and the measured track record" always is.***

---

# SECTION 1 — THE INTELLIGENCE THESIS

## What intelligence is, for Xenia

Xenia's intelligence is **the reliable production of judgments about businesses that a competent, honest human analyst would endorse — about the right subjects, with calibrated confidence, improving measurably with feedback.** Four clauses, each load-bearing. *Judgments, not information:* Xenia's unit of output is a defensible position ("pursue this company, because…"), not retrieved facts — facts are the inputs, and the incumbent stack already drowns customers in inputs. *The right subjects:* intelligence includes knowing what to think *about* — a brilliant analysis of an irrelevant company is a failure of intelligence, not a success of analysis; discovery precision is as much "intelligence" as brief quality. *Calibrated confidence:* an analyst who is 90% sure and right 90% of the time is intelligent; one who is always certain and usually right is dangerous — calibration is not a nicety of tone but a measurable property this document tests (Section 5). *Improving with feedback:* per the Foundation's flywheel doctrine, static competence is not intelligence in our definition — the standard requires demonstrable learning, which is why evaluation (Section 6) measures trajectories, not just snapshots.

## What intelligence is not

Not **fluency** — the ability to produce confident, well-structured prose is the commodity output of every frontier model and the camouflage of every failure mode in Section 8; this document exists largely to prevent fluency from being mistaken for intelligence, internally or by customers. Not **breadth** — knowing something about everything is a search engine; Xenia's intelligence is depth against one DNA. Not **model sophistication** — which model, how many steps, what architecture are engineering choices invisible to this standard; a lookup table that produced analyst-endorsed judgments would pass, and a frontier model that fabricates would fail. Not **activity** — briefs generated, tokens spent, sources crawled are cost lines, never quality evidence (the Product Strategy's anti-metric ruling, inherited). And not **agreement** — telling the customer what they already believe is a specific failure mode (sycophancy, Section 8), not a success; intelligence sometimes respectfully disagrees, with evidence.

## Why intelligence is the product, and features are secondary

The Foundation's 4.2 ("Xenia is the product; the interface is where you meet her") gets its operational meaning here: every feature in the Product Strategy is a *delivery mechanism* for judgments this standard governs. A beautiful brief rendering a wrong judgment is a beautifully delivered failure. This has a budgetary consequence the whole company must accept: **when intelligence quality and feature velocity conflict, quality wins** — a quarter spent halving the error rate outranks a quarter of new surfaces, because the moat (DNA, per Foundation Section 11) is made of accumulated *trusted* judgments, and one distrusted judgment un-accumulates months of them. It also has a hiring consequence: people who evaluate AI output rigorously are as core to the product organisation as people who build AI systems — the grader is a first-class role (Section 9).

---

# SECTION 2 — WHAT MAKES A GREAT RECOMMENDATION?

Ten properties. Each defined, each with its measurable proxy, because a property this document cannot measure is an aspiration, not a standard. A recommendation is the composite object from the Product Strategy — the judgment, its score decomposition, and its underlying brief — and it is evaluated as a whole.

**1. Correctness.** The factual claims underneath the judgment are true, current, and about the right company. The floor property: nothing else matters if this fails, which is why the rubric (Section 3) makes fabrication an automatic zero. *Proxy:* verified-claim rate in audits; customer error reports per 100 briefs.

**2. Evidence-grounding.** Every material claim traces to a linkable, dated observation (the Evidence object). Distinct from correctness: a true claim without traceable evidence is still substandard, because the customer cannot check it and N4/N5 require that they can. *Proxy:* claims-with-evidence ratio; broken-evidence-link rate.

**3. Calibration.** Stated confidence matches observed accuracy across many judgments — "likely" things happen more often than "possible" things. The property that makes Xenia's uncertainty *usable*: a founder can rationally act on "high confidence" only if high confidence means something statistically. *Proxy:* calibration curves per confidence band, measured quarterly against resolved outcomes (Section 5).

**4. Explainability.** The reasoning from evidence to judgment is visible, followable, and would survive the founder reading it aloud to a sceptical colleague. *Proxy:* rubric dimension score; correction-comprehension rate (customers who correct *the right element* — a signal they understood the reasoning's structure).

**5. Novelty.** The recommendation tells the founder something they did not already know — a company outside their awareness, or a fact that reframes a company inside it. Novelty is graded against *this customer* (their CRM overlap, their stated knowledge), not against the general public. *Proxy:* the "didn't know this" session signal (Section 7); overlap rate with customer-supplied known lists.

**6. Specificity (the transplant test).** Every insight must fail when transplanted: if a sentence still reads plausibly with a different company's name substituted, it is filler, not intelligence. "Their paid social is active but their PDP load time is 6.1s on mobile" survives; "they could benefit from improved conversion optimisation" does not. *Proxy:* transplant-test audits on sampled briefs — the single most efficient quality probe we have, because generic filler is the commonest failure of AI research at scale.

**7. Actionability.** The recommendation arrives with a usable next move — what to say, to whom, on what evidence — such that the distance from reading to acting is minutes. *Proxy:* pursue rate; time-from-brief-to-contact.

**8. Fit-alignment.** The judgment is derived from *this customer's DNA*, visibly — including honouring disqualifiers absolutely and weighting what their behaviour has taught. A recommendation can be correct, novel, and specific about a company the customer would never serve; that is a fit failure. *Proxy:* acceptance rate; disqualifier-violation count (target: zero, always — an ICP schema law).

**9. Timing.** The recommendation arrives when the prospect is approachable (buying signals, trajectory) and when the customer can act (their cadence, their capacity — Memory-informed). Right company, wrong month is a polite decline. *Proxy:* pursue rate on timing-flagged vs unflagged recommendations; reply-rate differential (once outcome data allows).

**10. Attention-worthiness (the composite duty).** The scarcest resource in the system is the founder's attention (ICP and Product Strategy, repeatedly); every recommendation spends it. A great recommendation is one where the spend was justified *even if declined* — the founder learned something about their market. This is the property that justifies the bounded queue: we ship fewer, attention-positive recommendations rather than more, attention-neutral ones. *Proxy:* the acceptance trend plus the session return rate — founders keep granting attention to systems that repay it.

---

# SECTION 3 — THE RESEARCH BRIEF STANDARD

The brief is the astonishment artefact and the craft centre of V1 (Product Strategy C4). This section is its constitution: required sections, per-section quality bars, failure conditions, and the scoring rubric that the MVP's human QA gate and the later automated harness both apply.

## Required structure (eight parts)

**B1 — Identity & snapshot.** Who this company is, in three sentences a busy founder absorbs in ten seconds: name, what they sell, to whom, scale band, location. *Bar:* zero ambiguity about which company this is (misattribution is the deadliest error class — Section 8); scale claims banded and sourced, not falsely precise.

**B2 — What they do and for whom.** The business model as it actually operates — products, price architecture, customer type, channels. *Bar:* must contain at least one observation beyond the company's own homepage self-description; a brief that paraphrases the prospect's marketing copy is retrieval, not research.

**B3 — Trajectory.** Direction and momentum: hiring, launches, expansion, review velocity, visible investment — or their absence, stated plainly. *Bar:* every trajectory claim dated and sourced; "growing" without evidence is banned vocabulary.

**B4 — Marketing state & gap analysis.** The heart for the beachhead: the observable marketing reality versus evident intent, and the specific gaps that constitute the customer's opening (ICP DNA category 3). *Bar:* gaps must pass the transplant test individually; each gap paired with its evidence; at least one gap should be *non-obvious to a professional* — the section where "astonishing" lives or dies, and the hardest bar in the document (a performance-marketing founder grades this section as an expert; obvious-to-them equals failure even when true).

**B5 — Fit thesis.** The argued judgment: why this company, for this agency, against this DNA — with the score decomposition. *Bar:* must reference specific DNA elements (never generic desirability); must be falsifiable ("a good fit because X, Y" where X and Y could be checked and disputed).

**B6 — Counter-evidence & risks.** What argues against pursuit, stated with the same care as the case for. *Bar:* never empty and never cosmetic — a brief with a hollow counter-evidence section ("no significant concerns identified") is marked down *more* than one with strong stated doubts, because the section exists to prove epistemic honesty (N5), and honest research into any real company finds friction. This inversion — rewarding stated doubt — is deliberate and cultural.

**B7 — Suggested approach.** The actionable bridge: the angle, the evidence to lead with, who to address, and the timing note. Feeds C6's draft. *Bar:* derived visibly from B4's gaps; no generic outreach advice.

**B8 — Confidence & freshness.** Overall confidence with its main drivers; observation dates; what Xenia could *not* see (paywalled, ambiguous, unverifiable) declared. *Bar:* the couldn't-see list is mandatory — declared blindness is the cheapest trust-builder we own.

## Failure conditions (automatic, regardless of other merit)

A brief **fails absolutely** if it contains: a fabricated fact or fabricated evidence link; a misattribution (true fact, wrong company); a violated disqualifier presented as a recommendation; stale evidence presented as current (observation older than its section's freshness tolerance, undated); or a confidence statement contradicted by its own evidence ("high confidence" resting on a single weak source). A brief **fails softly** (returned for regeneration, logged as quality debt) if: any section fails the transplant test; B6 is hollow; B4 contains only professional-obvious gaps; or the couldn't-see declaration is missing.

## The scoring rubric

Five dimensions, 0–4 each, applied by the MVP QA gate and later by the calibrated automated judge (Section 6). **Accuracy** (4 = every sampled claim verifies; 2 = minor imprecision, nothing material; 0 = any fabrication/misattribution — and a 0 here zeroes the brief). **Evidence** (4 = all material claims traced and dated; 2 = mostly traced with gaps; 0 = untraceable assertions throughout). **Insight** (4 = ≥2 non-obvious, transplant-proof observations a professional would value; 2 = accurate but expert-obvious; 0 = generic filler). **Fit reasoning** (4 = thesis argued from named DNA elements with honest counter-case; 2 = fit asserted more than argued; 0 = DNA-blind). **Actionability** (4 = approach usable within minutes, angle evidenced; 2 = pursued only with extra work; 0 = no bridge to action). **Ship bar per brief: total ≥16/20 with no dimension below 2 [calibrates].** The MVP's unedited-pass metric (Product Strategy's automation-readiness dial) is measured against this rubric, making the QA delta a number two documents have now demanded.

---

# SECTION 4 — THE DNA STANDARD

The DNA is the primary moat (Foundation Section 11); this section defines what a *good* one is and the laws of its evolution.

## What a DNA must achieve — five duties

**Predictive:** the DNA's fit scores must correlate with the customer's actual decisions and outcomes — the standard's definition of "the DNA works," measured by acceptance rate and, later, win-rate concentration in high-scored prospects. **Expressive:** the customer, reading it, says "that's us — sharper than we'd have written it" (ICP Instrument 5's ≥8/10 endorsement). **Discriminative:** it must exclude well — a DNA that fits everything predicts nothing; the visible-exclusion moment is its public proof, and the exclusion rate is monitored (a DNA rejecting almost nothing is broken even if acceptance looks healthy). **Teachable:** every element correctable in one interaction, with effect visible in the next cycle (the Product Strategy's learning-latency rule). **Inspectable:** readable in plain language at all times, with a changelog explaining every evolution — the co-owned document ruling from the Product Strategy's ontology.

## Evolution: what changes, and at what speed

DNA elements carry per-element confidence, and confidence dictates change speed: low-confidence elements (one source, no corroboration) move readily; high-confidence elements (corroborated by outcomes) resist casual revision. Evolution sources rank by evidential weight (Section 5's hierarchy), and *structural* changes — new disqualifiers, category rewrites, market pivots — are proposed, never imposed (Product Strategy Section 8's human-in-the-loop zone). The changelog is total: every mutation records its cause (which correction, which outcome, which behavioural pattern), because an unexplainable DNA change violates N4 at the moat's own centre.

## Memory and forgetting

The DNA must **remember**: everything explicitly taught; every resolved outcome and its lesson; stable preferences confirmed across time; and its own history (reverted changes stay in the log — an employee remembers being corrected). The DNA must **forget** — meaning *decay toward neutral with the log retained*, never silent deletion: preferences contradicted by sustained behaviour (stated "no small brands," pursued five — surfaced for reconciliation, then re-weighted); market conditions that have shifted (a 2026 signal pattern is not a 2028 truth — signal weights carry freshness half-lives **[calibrates]**); and single-event lessons never corroborated (one bad franchise client must not become a permanent law unless the customer makes it one). The governing asymmetry: **customer-stated laws (disqualifiers) never decay without the customer; learned statistical preferences always decay without corroboration.** Momentum in the wrong direction is worse than none (Foundation flywheel doctrine), and forgetting is how the wheel steers.

## Conflict resolution

When signals disagree, the hierarchy rules — and where the hierarchy itself feels wrong, Xenia *surfaces the conflict rather than resolving it silently*: **(1)** explicit disqualifiers (absolute, ICP schema law); **(2)** recent explicit corrections; **(3)** resolved outcomes (what actually won/lost); **(4)** sustained behaviour (what they pursue and ignore); **(5)** original interview statements; **(6)** vertical priors (the beachhead template). The interesting conflicts are 3-versus-1 and 4-versus-5. When outcomes contradict a stated preference (franchises keep converting despite the no-franchise rule), Xenia reports the tension with evidence and lets the customer rule — the customer is sovereign over their own strategy, and *quietly overriding their stated intent to chase conversion statistics is sycophancy's mirror-image failure* (Section 8): both replace the customer's judgment instead of informing it. When behaviour contradicts stated preference, Xenia proposes the reconciliation (the "I've noticed…" narration from the Product Strategy) and applies it only on acknowledgment or sustained repetition.

## Confidence over time

Aggregate DNA confidence should follow a learning curve: rising steeply through month one (teaching-dense), asymptoting as elements corroborate, dipping locally when the customer's market or strategy shifts — and those dips are *features*, reported honestly ("your last five wins look different from your DNA; time to talk?"). A DNA reporting monotonically increasing confidence forever is either not learning or not honest; the evaluation harness watches for exactly that pathology.

---

# SECTION 5 — LEARNING

How Xenia learns, signal by signal, with the weighting philosophy stated as principles an engineer can argue from — not tuning constants, which belong to implementation and to data.

## The six signal classes, ranked by evidential weight

**1. Outcomes (highest weight, lowest volume).** Won, lost, meeting, ghosted — ground truth about the world, the only signal class that tests the *entire* chain (discovery → research → fit → approach). Weighted highest per event precisely because scarce; but never allowed to swing the DNA on a single event (the one-bad-franchise rule, Section 4). Outcome lessons attach to *patterns across events*, and Xenia's narration must distinguish "one data point noted" from "third occurrence — adjusting."

**2. Explicit corrections (high weight, moderate volume, highest intent).** "Wrong — we don't serve hospitality"; "this score overweights size." The customer spending effort to teach; disrespecting it once (a correction visibly ignored) does more trust damage than ten mediocre briefs — hence the Product Strategy's zero-tolerance metric for correction-ignored incidents. Corrections apply within one cycle, always acknowledged, always logged.

**3. Decisions (moderate weight, high volume).** Accept/decline/pursue — revealed preference on every recommendation. The workhorse signal: individually noisy (a decline can mean bad fit, bad timing, or a busy Tuesday), collectively the richest pattern source. Decline-*with-reason* upgrades the signal to near-correction weight, which is why the ten-second correction UX carries the teaching joint (Product Strategy critique — the design investment lands here).

**4. Ignored recommendations (low weight, ambiguous by nature).** Not-acted-upon is not "no": the standard requires disambiguation before learning from silence — *seen-and-skipped* (viewed, not pursued: weak negative), *unseen* (never opened: no signal about the prospect, possible signal about queue position or volume), and *deferred* (opened repeatedly, no decision: a timing or courage signal, interesting and distinct). Learning from undifferentiated silence is how systems teach themselves their users' busiest week as a preference.

**5. Implicit behaviour (low per-event weight, highest volume).** Dwell patterns, section engagement, edit patterns in drafts, directed-search phrasing. Texture, not verdicts: used to form *hypotheses* that stronger signals confirm, never to change the DNA alone. The privacy posture is inherited (Foundation Section 14): behavioural signal serves the customer's own model, full stop.

**6. Time (the universal modifier).** Freshness half-lives on evidence; decay on uncorroborated preferences; seasonality patterns (the "no December pitches" Memory). Time never adds knowledge; it discounts staleness honestly.

## The weighting philosophy, in four rules

**Intent outranks volume:** one deliberate correction outweighs a hundred dwell-signals — systems that let high-volume weak signals swamp low-volume strong ones learn their users' habits instead of their intent. **Recency outranks history, gently:** a preference shift is followed, not chased — smoothing over weeks, because thrash (Section 8) destroys the trust that feedback requires. **Patterns outrank events:** minimum-evidence thresholds before any learned generalisation, stated in Xenia's narration ("third time — adjusting"). **The customer outranks the statistics:** when learning and stated intent conflict, surface, don't override (Section 4's sovereignty rule). These four rules are the arbitration protocol for every future "should the model update on this?" debate.

## Confidence, operationally

Confidence is a *prediction about being right*, and it is audited as one: quarterly calibration reviews compare stated confidence bands against resolved outcomes (of all "high confidence" fit theses whose prospects were pursued to resolution, what fraction converted at the DNA-predicted rate?). Where bands and reality diverge, the presentation layer re-maps before the reasoning layer retrains — customers experience calibration through language ("likely," "possible," "uncertain"), and that language must mean the same thing every month, everywhere in the product. Calibration drift is a Sev2 quality incident (Section 9), because it silently corrupts every downstream decision the customer makes on Xenia's word.

---

# SECTION 6 — THE EVALUATION HARNESS

The machinery that makes every claim in this document enforceable. Five layers, from cheap-and-continuous to expensive-and-longitudinal; each layer states what it tests, against what benchmark, and how often.

## L0 — Mechanical verification (every brief, automatically)

Evidence links resolve; dates present and within freshness tolerance; claim-to-source entailment spot-checks (does the cited source actually support the sentence citing it?); disqualifier compliance; structure completeness (B1–B8 present, couldn't-see declared); banned-vocabulary and transplant-pattern linting (statistical filler detection). *Benchmark:* absolute rules, no judgment. *Gate:* any L0 failure blocks the brief from the customer — mechanical failures are never quality-judgment calls.

## L1 — Human rubric grading (the gold layer)

Trained human graders — initially the founder as Intelligence Editor (Section 9), then hired graders with domain competence — apply the Section 3 rubric to samples. **The golden dataset** is founded on the concierge test's artefacts: the hand-built DNAs, the human-produced briefs, and every QA edit made during MVP (each edit is a labelled example of the gap between machine and standard — the most valuable training-and-evaluation asset the company will own, and the reason MVP's QA gate doubles as dataset construction). Target: **50 gold briefs across ≥10 real DNAs at launch, refreshed quarterly** — stale gold is a named failure mode (real businesses change; a gold brief about last year's company teaches last year's world) — with a **held-out portion never used in development**, guarding against the harness teaching the system to pass the harness. Inter-rater reliability is measured before grader scores are trusted (two graders, sampled overlap, agreement threshold **[calibrates]** — if humans can't agree on brief quality, the rubric is revised before anything else is concluded).

## L2 — Calibrated automated judging (the scale layer)

An automated judge applies the rubric continuously — but earns trust only by *agreement with L1*: the judge is validated against human-graded samples, its agreement rate published internally, and its verdicts weighted accordingly (below the agreement threshold, it advises; above, it gates). Standing rule: **the judge never grades its own generator's changes without an L1 sample** — model-judging-model circularity is a named risk (Section 10), managed by keeping humans in the calibration loop permanently, not until it's inconvenient.

## L3 — Behavioural evaluation (the truth layer)

Production behaviour as the ultimate test: acceptance, pursuit, correction rates, error reports — the Product Strategy's loop metrics reread as evaluation. L3 outranks L1/L2 when they disagree (a brief graders love but founders never pursue is failing at the only bar that pays), but lags them by weeks; the layered design exists precisely so we don't ship on rubric hope and learn on customer trust.

## L4 — Longitudinal evaluation (the thesis layer)

Cohort trajectories: acceptance-by-tenure (the compounding chart), DNA predictive power over time, calibration curves, per-vertical quality when rung 2 arrives. This is the flywheel doctrine's empirical court — where "it learns" is proven or the Foundation's central claim is confronted (its named risk: the flywheel fails to spin).

## Regression testing, thresholds, and ship gates

Every change to any intelligence-touching component runs the regression suite (gold set + held-out sample) before deployment. **Ship gates, pre-registered:** no release ships with fabrication/misattribution detected in its regression run (absolute); rubric mean not below the current baseline minus a small tolerance, and *no dimension* regressing materially even if the mean holds **[calibrates]** (means hide dimensional collapse — an Insight regression paid for by an Actionability gain is a worse product wearing a stable average); L0 pass rate ≥99%; unedited-pass rate (the QA delta) not regressing at MVP→V1 transition, where the Product Strategy's ≥70% entry criterion is measured *by this harness*. **Cadence:** L0 continuous; L1 weekly samples (heavier at every model/prompt change); L2 continuous once calibrated; L3 weekly cohort review; L4 monthly, and quarterly in depth. **Benchmarks, in rank order:** the concierge gold standard (can the machine match the hand?), the previous version (are we improving?), and the time-matched human analyst (does Xenia beat what a competent human produces in the same minutes? — the customer's implicit comparison, tested explicitly twice a year).

---

# SECTION 7 — ASTONISHMENT, DECOMPOSED

The ICP defined the astonishment bar's five criteria (a–e); the Product Strategy made it the ship-gate. This section defines what each felt reaction *is*, mechanically, so it can be engineered for and measured — the section that turns "astonishing" from adjective to instrument.

**"I didn't know this." (novelty realised).** Mechanically: a company absent from the customer's awareness set (not in their CRM/known-list overlap check, confirmed by the session's explicit question), *or* a reframing fact about a known company (B4's non-obvious gap). Measured: the overlap rate; the explicit first-session marker (ICP criterion b: ≥1 within fifteen minutes); the per-brief novelty grade (rubric Insight ≥3 requires it). Engineered by: discovery breadth beyond the customer's own hunting patterns (Xenia must search where they *don't*), and B4's professional-obviousness bar.

**"I need to contact them." (fit-plus-urgency realised).** Mechanically: fit thesis + timing signal + actionable angle landing together — the three properties (8, 9, 7 of Section 2) compounding. Measured: pursue rate within 14 days (the activation criterion); time-from-brief-to-contact; the ICP's ≥7/10 worth-a-conversation criterion (a). Engineered by: B5's falsifiable thesis and B7's ready bridge — urgency is legitimate only when *evidenced* (a real timing signal), never manufactured (that is the funnel-cosplay failure the brand forbids).

**"This saved me hours." (substitution realised).** Mechanically: the brief substitutes for the 30–60 minutes of manual research the ICP documented — and the customer *knows* it did, which requires the brief to visibly contain work (sources checked, angles considered, blind alleys declared in couldn't-see). Measured: session time-to-decision versus the concierge baseline; the twice-yearly human-analyst benchmark (the harness's third benchmark, Section 6); the design-partner interview question asked verbatim. Engineered by: depth-as-default (Product Strategy C4's ruling against on-demand-only depth).

**"I trust this." (calibration felt).** The compound reaction the other three feed, plus its own mechanics: predictions that resolve as stated (calibration, experienced over weeks); corrections that visibly take (the teaching contract honoured); doubt honestly stated (B6/B8 — trust in AI is built faster by declared limitation than by demonstrated capability, the standard's most counterintuitive design rule); and zero experienced fabrications, the non-negotiable substrate. Measured: correction-application latency; return rate; the forward/screenshot event (ICP criterion d — trust made public); error reports trending to zero.

**The astonishment index.** Per first-session: criteria a–e recorded as the composite (the ship-gate); per ongoing cohort: a weekly composite of novelty rate, pursue rate, time-to-decision delta, and trust signals **[calibrates]**. One warning, inherited from the series' honesty tradition and expanded in Section 10: the index *summarises* astonishment, it is not astonishment — the moment teams optimise the composite instead of the components' causes, the number will improve as the experience degrades. The index is a smoke detector, not a target.

---

# SECTION 8 — FAILURE MODES

The taxonomy: every known way the intelligence fails, with detection and mitigation. Ranked within classes by expected trust damage.

## Class A — Truth failures (catastrophic; zero-tolerance posture)

**A1 Fabrication** (invented facts, invented evidence). *Detection:* L0 entailment checks, L1 sampling, customer reports. *Mitigation:* evidence-mandatory composition (claims without Evidence objects can't render as fact), couldn't-see declarations as the pressure valve (the system needs a legitimate way to say "unknown" or it will invent), and Sev1 incident handling (Section 9). **A2 Misattribution** (true fact, wrong company — deadlier than fabrication because it verifies *partially* and the customer may repeat it in a pitch). *Detection:* entity-consistency checks at L0 (every Evidence object bound to a verified entity identity); same-name-different-company linting. *Mitigation:* identity resolution as a first-class research step; B1's zero-ambiguity bar. **A3 Stale truth** (was true, isn't). *Detection:* freshness metadata, tolerance windows per claim type (ad activity decays in weeks; company location in years). *Mitigation:* dated claims everywhere, regeneration cadence, and staleness *stated* when tolerance is exceeded rather than silently served.

## Class B — Judgment failures (corrosive; the quality war's daily front)

**B1 Generic insight** (transplant-test failures — the commonest scaled-AI failure). *Detection:* transplant audits, filler linting, Insight dimension. *Mitigation:* the rubric's teeth (expert-obvious = 2 max), and culture: filler is treated as a defect, not a style issue. **B2 Obvious insight** (accurate, worthless to a professional grader). *Detection:* domain-competent graders (why grader hiring specifies beachhead fluency). *Mitigation:* B4's non-obviousness bar; vertical priors deepening per rung. **B3 Weak fit reasoning** (right facts, wrong conclusion for *this* customer). *Detection:* Fit dimension; decline-reasons clustering ("not our kind of client" repeated = DNA-blindness). *Mitigation:* DNA-referenced theses (B5 bar), acceptance-trend monitoring per customer. **B4 Poor prioritisation** (good briefs, wrong ranking — the queue's top spends attention the bottom deserved). *Detection:* position-vs-acceptance curves (if slot 8 outperforms slot 1, ranking is broken). *Mitigation:* ranking evaluated as its own artefact, not assumed from brief quality. **B5 False confidence / hidden uncertainty.** *Detection:* calibration audits (Section 5); B8-vs-evidence consistency lint. *Mitigation:* confidence language standardised and audited; the B6 inversion (rewarding stated doubt).

## Class C — Learning failures (slow-acting; visible only in trends)

**C1 Thrash** (over-updating on recent signal — last week's decline becomes this week's blind spot). *Detection:* DNA velocity spikes; recommendation-set instability metrics. *Mitigation:* smoothing rules, pattern-thresholds (Section 5). **C2 Sycophancy** (learning to please stated bias against outcome evidence — and its mirror: silently overriding stated intent for statistics). *Detection:* stated-preference-vs-outcome divergence monitoring (Section 4's conflict machinery). *Mitigation:* the sovereignty rule — surface, don't override, either direction. **C3 Feedback starvation** (capture rates collapse; the wheel spins on nothing — Product Strategy R2 restated as intelligence risk). *Mitigation:* behaviour-first learning design; capture UX investment; the V1.5 trigger. **C4 Overfit to the vertical prior** (the beachhead template overwhelming individual DNAs — every agency getting the same "ideal client" with different logos). *Detection:* cross-customer recommendation-overlap monitoring (two agencies with different DNAs receiving suspiciously similar queues). *Mitigation:* per-customer divergence as a health metric — the moat *is* the divergence.

## Class D — Systemic failures (environmental; slow then sudden)

**D1 Coverage blindness** (the terrain thins — sources decay, the finite-market problem R3). *Detection:* discovery yield trends per DNA; source-health monitoring. *Mitigation:* honest thin-market conversations (the designed product moment), source diversification, and the next document's remit (data sourcing strategy). **D2 Silent upstream degradation** (a data source quietly rots; briefs inherit the rot). *Detection:* source-level accuracy sampling in L1. *Mitigation:* per-source trust scores; quarantine protocol. **D3 Format rut** (every brief structurally perfect and cognitively identical — astonishment decaying through sameness while every metric holds). *Detection:* the one failure mode metrics won't catch — grader rotation and the quarterly "read ten briefs in a row as a customer would" ritual exist for exactly this. *Mitigation:* controlled variation in composition; treating monotony as a defect class at all.

The taxonomy's governing insight: Class A is fought with *architecture* (evidence-mandatory composition), Class B with *rubrics and graders*, Class C with *weighting philosophy*, Class D with *rituals and monitoring* — four different defence systems, which is why "just make the model better" is never an acceptable quality plan in this company.

---

# SECTION 9 — COMPANY QUALITY PROCESS

Standards without process are wall art. This section assigns ownership, cadence, and consequences.

## Ownership: the Intelligence Editor

Quality has a named owner from day one: the **Intelligence Editor** — initially the founder (an explicit answer to the Product Strategy's founder-decision 4 about QA staffing), later a dedicated hire whose profile is *editor with domain fluency*, not ML engineer: the role's ancestors are the newspaper editor and the search-quality rater programme lead, and its authority is real — **the Editor can block any release on quality grounds, and only the founder can overrule, in writing, in the log.** The Editor owns the rubric's evolution, the golden datasets, grader training and inter-rater calibration, the incident register, and the quarterly read-as-a-customer ritual (D3's defence). Engineering owns *building to* the standard; the Editor owns *whether it was met*. Separating those two owners is the process design's one non-negotiable — self-graded quality drifts, in AI systems faster than anywhere.

## Incident handling: severities and the honesty rule

**Sev1 — a Class A failure reached a customer** (fabrication, misattribution, disqualifier violation). Same-day: correction shipped, root cause identified, *and the customer told* — proactively, plainly ("we got this wrong; here's what happened and what changed"). The honesty rule is strategy, not penance: the wounded buyer's trust survives a confessed error and does not survive a discovered cover-up, and the Foundation's 12.2 ("when we break something, we say so first") gets its operational test here. **Sev2 — systemic quality drift** (calibration drift, gate-threshold breach, capture collapse): fix scheduled within the week, cohort impact assessed, trend reported at the weekly review. **Sev3 — quality debt** (soft-fail patterns, rut signals): logged, batched, burned down on a visible schedule. Every Sev1/Sev2 produces a regression test — the suite is the company's scar tissue, accumulated deliberately.

## Release discipline

A release touching intelligence is blocked when: the regression suite's ship gates fail (Section 6); the Editor withholds sign-off; a Sev1 is open; or the unit-cost ceiling would be breached by the change (the Product Strategy's COGS ceiling enforced at release time, because quality-at-any-cost quietly becomes a different company's economics). Blocked means blocked — the Foundation's N8 (quality bar over ship date) already decided every argument this paragraph will ever host.

## Cadence and dashboards

**Weekly quality review** (Editor + engineering + product, one hour): the five watched metrics — unedited-pass rate (the QA delta), acceptance rate, pursue rate, error reports per 100 briefs, capture rate — plus incident register and any gate approaching its threshold. **Monthly:** L4 trends (acceptance-by-tenure, DNA predictive power), calibration curves, per-source health, golden-set refresh status. **Quarterly:** the deep read ritual; rubric revision; grader reliability re-measurement; the human-analyst benchmark (twice yearly). **Board dashboard** (inheriting the Product Strategy's constitutional ordering — customer outcomes first): the compounding chart (acceptance-by-tenure), Sev1 count and time-to-resolution (a board that sees trust incidents governs like trust matters), the QA delta trend toward automation-readiness, and quality-cost per customer against ceiling. What the board does *not* get: rubric minutiae, model comparisons, activity metrics — the board governs the thesis (is intelligence compounding, trustworthy, and affordable?), not the kitchen.

---

# SECTION 10 — FOUNDER CRITIQUE

**Where we are overcomplicating.** This standard specifies five evaluation layers, a ten-property recommendation ontology, an eight-part brief structure, and four failure-mode defence systems — for a company with zero customers. The honest defence is that most of it is *sequenced* (L2 waits for calibration data, L4 for tenure); the honest concession is that the MVP needs perhaps a third of this document: L0, the rubric, the golden set, the Editor, and the Sev1 rule. The rest must not become pre-launch procrastination — building measurement apparatus is a seductive substitute for facing customers, and this document's length is itself evidence of the temptation. **Ship the third; let the rest activate on contact.**

**Where we still rely on intuition.** Every threshold — 16/20, 99%, ≥70%, the freshness half-lives, the agreement bars — is constructed, not derived; the [calibrates] convention manages this but does not dissolve it. Deeper: the *rubric dimensions themselves* are intuition — we believe Accuracy/Evidence/Insight/Fit/Actionability spans brief quality, but the concierge test may reveal that founders pursue briefs for reasons our rubric doesn't score (a compelling narrative shape; a single killer fact; brevity). The rubric must be validated *against pursuit behaviour*, not just against grader consensus — L3 disagreeing with L1 is findable gold, and the document says L3 wins but the temptation will be to trust the beautiful rubric over the messy behaviour.

**What needs real customer data.** The entire astonishment decomposition (Section 7 reverse-engineers felt reactions from armchair mechanics — twenty design-partner sessions will embarrass at least one of the four mechanisms); the conflict-resolution hierarchy (the sovereignty rule is philosophically clean and empirically untested — customers may *want* to be overridden by conversion statistics more than we assume, or may churn at the first "your stated preference is losing you money" conversation however gently surfaced); the forgetting half-lives (no data exists anywhere on how fast agency-market signal decays); and inter-rater reliability (if two competent humans can't agree on Insight scores, Section 3 is a vocabulary, not a standard — this is the first thing the concierge artefacts must test).

**Assumptions that could destroy us.** Three. **First, that fabrication can be engineered to near-zero at acceptable cost.** The evidence-mandatory architecture helps enormously; it does not repeal the underlying statistics of generative systems. If the true floor is one confident falsehood per N briefs and N is small, the entire trust strategy needs a different shape (heavier human gating, permanently — with the margin consequences the Product Strategy's ceiling forbids). The MVP's QA data answers this question before it can bankrupt us; nothing else in the company matters more than that number. **Second, that graded quality predicts pursued value.** The rubric could be perfected while the North Star stalls — measurement success, product failure. L3's primacy is the paper answer; the cultural answer is refusing to celebrate rubric wins at weekly review without behaviour moving. **Third, that the harness stays honest as it automates.** L2's circularity (models judging models) is managed by permanent human calibration — but "permanent" is a budget line someone will one day propose cutting, and this paragraph exists to be quoted at them.

**What a top AI-product leader would push back on.** That the document defines quality entirely as *per-artefact* excellence and only glancingly as *portfolio* experience: a customer's Monday session is a set, and sets have properties briefs don't — variety, arc, the one-great-brief-versus-five-good-briefs question. Session-level quality deserves promotion from D3's afterthought to a first-class evaluated artefact. Second pushback: the standard is silent on *speed as quality* — a 9/10 brief tomorrow versus an 8/10 brief this morning is a real product decision the rubric can't currently express; latency belongs in the standard, not just in engineering SLOs. Both critiques are accepted and queued for the document's first revision.

---

# SECTION 11 — SCORECARD

| # | Section | Score /10 | Justification & improvement |
|---|---------|-----------|------------------------------|
| 1 | Intelligence Thesis | **9** | Four-clause definition, each testable; the not-list (fluency, breadth, sophistication, activity, agreement) will settle real arguments; budgetary and hiring consequences stated rather than implied. *Improve:* none structural. |
| 2 | Recommendation Properties | **8.5** | Ten properties each with a measurable proxy; the transplant test and attention-worthiness are the durable contributions. Deduction: ten is above the memorable limit (a recurring series vice) — the working five (correctness, evidence, novelty, fit, actionability) should be named as primary. *Improve:* mark the primary five; audit the rest quarterly. |
| 3 | Brief Standard | **9.5** | The document's core: eight sections with bars, absolute-vs-soft failure conditions, the B6 inversion (rewarding stated doubt), and a rubric with gates. This is what "ship-gate" has meant since document 03 without saying. *Improve:* validate rubric dimensions against pursuit behaviour (the critique's own instruction). |
| 4 | DNA Standard | **9** | Five duties, decay asymmetry (customer law never decays; statistics always do), and the sovereignty rule for conflicts — the moat now has laws, not just praise. *Improve:* the confidence-curve pathology check deserves a named metric. |
| 5 | Learning | **9** | Six signal classes ranked, silence disambiguated (seen/unseen/deferred), four arbitration rules that end debates. *Improve:* define the minimum-evidence thresholds numerically post-concierge. |
| 6 | Evaluation Harness | **9** | Five layers with benchmarks and cadence; golden-set holdout and grader-reliability preconditions show real eval literacy; ship gates pre-registered including the dimensional-collapse guard. Deduction: full apparatus vs. MVP-third tension, named only in the critique. *Improve:* mark each layer MVP/V1/V2 in the next revision. |
| 7 | Astonishment | **8.5** | The four utterances mechanised with engineering handles and measures; the index-as-smoke-detector warning is the right epistemics. Deduction: confessed armchair reverse-engineering pending twenty real sessions. *Improve:* re-derive from design-partner session recordings. |
| 8 | Failure Modes | **9.5** | Four classes mapped to four different defence systems — the taxonomy's governing insight ("just make the model better" is never a plan) is worth the section alone; D3 (format rut) catches what metrics can't. *Improve:* maintenance; add modes as reality supplies them. |
| 9 | Quality Process | **9** | A named owner with blocking power, the Sev1 honesty rule as strategy, release discipline anchored to N8, and a board view that governs the thesis not the kitchen. *Improve:* draft the Editor hire profile now — the founder-as-Editor phase has a capacity ceiling arriving fast. |
| 10 | Founder Critique | **9** | Attacks the document's real dangers: apparatus-as-procrastination, rubric-vs-behaviour, the fabrication floor as the company's single most important number, and two accepted expert pushbacks (session-level quality, latency-as-quality). *Improve:* act on the ship-the-third instruction. |
| 11 | Scorecard | **—** | Not self-scored, on principle. |

## Remaining founder decisions

**(1)** Ratify the Section 3 rubric and its gates as the operating definition of brief quality (the MVP QA gate applies it from day one); **(2)** confirm founder-as-Intelligence-Editor and the Editor's blocking authority — including the overrule-in-writing rule; **(3)** ratify the Sev1 honesty rule (proactive customer notification) as policy before the first incident, not during it; **(4)** set the fabrication-tolerance posture formally (the zero-tolerance gate plus the acknowledged detection-vs-occurrence gap); **(5)** approve the golden-set investment (50 briefs, quarterly refresh, holdout discipline) as a first-class MVP deliverable alongside the product; **(6)** set the evaluation budget as a named fraction of the COGS ceiling (eval tokens and grader hours compete with serving costs — unowned, this line gets eaten); **(7)** decide the MVP-third scope of this standard explicitly (which layers activate when), converting the critique's instruction into a plan; **(8)** schedule the rubric-vs-pursuit validation as a named concierge-test analysis. 

## The next document

**Recommendation: "Xenia — Data & Compliance Standard: what Xenia may observe, use, and remember."** The reasoning: this document governs how intelligence is *judged*; it deliberately does not govern what the intelligence may be *built from* — yet every Evidence object presumes sourcing decisions (what sources, acquired how, retained how long, under what legal basis), the Foundation stakes a moat on compliance-by-design (its Section 14) and demanded a written data-governance policy before launch, the ICP's risk register flags source-dependency, and this document's D1/D2 failure modes are source-strategy problems wearing quality costumes. That document should define: the permitted-source taxonomy and its provenance discipline; the personal-data boundary (business intelligence vs. people data) with GDPR/PECR posture made operational; retention and freshness policy unified with this document's half-lives; the per-source trust-scoring and quarantine protocol; and the regulator-and-front-page test applied to every sourcing decision in advance. It is the last standards document the build needs — after it, the series returns to execution (design language, GTM assets) with every foundation laid.

Per instruction: recommended, not written.

---

*End of Intelligence & Evaluation Standard v1.0. Governed by the Foundation Document v1.1, the ICP & Wedge Strategy, and the Product Strategy & V1 Scope; amendable by the Foundation's procedure. The rubric (Section 3), the gates (Section 6), and the Sev1 honesty rule (Section 9) are citable by name in any dispute about whether something is good enough to ship.*
