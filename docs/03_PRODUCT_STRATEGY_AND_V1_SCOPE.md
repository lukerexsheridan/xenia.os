# XENIA — PRODUCT STRATEGY & V1 SCOPE

**What exactly we build first**

Version 1.0 · July 2026 · Internal — Founders, Investors, Senior Product & Engineering Hires

---

*Governed by the Foundation Document v1.1 and the ICP & Wedge Strategy; contradicts neither. This document answers "what exactly should we build first?" as strategy, not specification — no screens, no schemas, no stack. One dependency stated honestly up front: the ICP document prescribed writing this after first concierge-test results. We write it concurrently by necessity, and resolve the tension the only defensible way — every number and scope call below that the concierge test can falsify is marked as **[calibrates]**, and this document commits to a formal revision when Instruments 1–2 report (~week six of research). A scope document that won't bend to the concierge data is a guess wearing a Gantt chart; this one names its bending points in advance.*

---

# SECTION 1 — PRODUCT THESIS

## Why V1 exists

V1 exists to prove one sentence to one buyer: **"An AI can find and understand your ideal clients better than you can — and gets better every week you employ it."** Everything in the Foundation — the employee relationship, the flywheel, the revenue-intelligence destination — depends on this sentence being demonstrably true for a founder-led UK performance agency within their first session and increasingly true across their first year. V1 is the smallest product that makes the sentence true, measurable, and improvable. It is not the smallest product that *demos* well — the AI SDR wave built those and died of them. It is the smallest product that survives contact with the hardest grader in SMB software (the ICP's evaluator advantage) and comes back sharper.

## What success looks like

Success at V1 is precise because the prior documents made it so: the astonishment bar passed by real agencies at the ICP's thresholds, with the concierge test's behavioural truth carried into the product — founders *act* on what Xenia finds (≥40% of recommendations pursued in month one, ≥60% by month three **[calibrates]**); the Monday-morning return habit forming without prompting; first meetings booked within 30 days at the median; the flywheel's joints all measurably moving (teaching rate, DNA velocity, acceptance trend); and the referral behaviour appearing unpaid — briefs screenshotted, peers summoned. Twenty-five founding customers who would be *angry* if Xenia disappeared beats two hundred who would shrug. V1's success is passionate depth, because depth is what cohort proof is made of and cohort proof is the entire phase-two GTM.

## What success does NOT look like

Signups, waitlist length, demo requests, LinkedIn applause, or feature completeness against the Foundation's pillar list. Most dangerously: success does not look like *impressive activity metrics* — prospects researched, briefs generated, tokens burned. A thousand briefs nobody pursues is failure wearing a dashboard. Nor does success look like early revenue from the wrong buyers: volume-hungry customers the ICP disqualified will appear with money, and taking it would poison the cohort data that is V1's actual product (the Foundation's misfit-customer warning, made operational: our learning system's diet is as important as our revenue).

## What V1 must prove

Four propositions, in order of importance: **(1) The intelligence proposition** — machine-produced research briefs meet the astonishment bar at automated cost, the question the concierge test answers for manual production and V1 must answer for scaled production, including the unit-cost question the ICP flagged and this document budgets (Section 9). **(2) The learning proposition** — the DNA measurably improves from behaviour and corrections within weeks, visible to the customer ("Xenia learned from our win"), visible to us in acceptance-rate trend. This is the flywheel's first empirical test. **(3) The habit proposition** — an AI employee with no send button and no native app can still become a weekly ritual through recommendation quality and the ambient brief alone. **(4) The economics proposition** — the pricing hypothesis survives real invoices: founding customers renew at month three and convert toward the core price band.

## What V1 intentionally ignores

The entire back half of the Foundation's loop — inbox, pipeline machinery, delegated sending, revenue analytics — per the ICP's do-not-build ruling (its Section 14), plus everything in this document's Section 5. Ignoring is not deferring by neglect; it is the strategy. The wedge's binding constraint is the top of the funnel, the astonishment artefact is the wedge's weapon, and every unit of build effort spent below the funnel's neck weakens the blade. V1 also intentionally ignores scale concerns beyond ~100 customers, multi-vertical generality (rung-2 temptations arrive early and are refused), and monetisation optimisation — the founding cohort's price is fixed by the ICP; V1's job is to earn the renewal, not maximise the invoice.

---

# SECTION 2 — PRODUCT PRINCIPLES

The Foundation's principles, translated into the specific decisions a product team makes at a desk on a Tuesday. Each principle is stated as a rule that *changes an argument's outcome*, because principles that don't decide fights are decoration (the Foundation's own standard).

**P1. Intelligence over automation → build the brain before the hands.** Any hour that could improve brief quality or make discovery sharper outranks any hour spent letting Xenia *do* more. Decision consequence: V1 has no send button (Section 4, C6) — the single largest scope refusal in this document, and the correct one, because sending is hands, and our hands would be judged before our brain had earned the verdict.

**P2. Employee over software → every surface is Xenia showing or asking.** The Foundation's 4.2 test applied literally: each screen must be describable as "Xenia showing you something she did, or asking you something she needs." Decision consequence: there is no "dashboard" in V1's information architecture — there is *Xenia's desk*: what she found, what she's asking, what she learned. Navigation is organised around her work, not around data types. Empty states are her voice ("I'm researching your market — first briefs tomorrow morning"), never grey placeholders.

**P3. Quality over quantity → ten briefs that astonish beat fifty that inform.** Discovery precision is judged on the ICP's acceptance thresholds, never on volume delivered. Decision consequence: V1 delivers a *bounded* weekly recommendation set (order of ten, not hundreds **[calibrates]**), and when Xenia's confidence is low she says so and delivers fewer — an under-promising product in a category that died of over-promising. The temptation to pad the queue when discovery runs thin must be structurally impossible, not just discouraged.

**P4. Opinionated over configurable → defaults, not preference matrices.** The customer teaches Xenia about *their market*, never about *our product*. Decision consequence: no settings pages beyond the essential; scoring weights are learned, not sliders; the DNA is edited by conversation and correction, not by form-field grid. Where the Foundation permits configuration (delegation levels), V1 ships the bottom two levels only — suggest and draft — so the "configuration" is a single, meaningful trust decision, not a control panel.

**P5. Explain or don't ship → the reasoning is the interface.** N4/N5 applied at feature grain: every score decomposes, every claim carries evidence, every inference is marked as inference with confidence. Decision consequence: the Research Brief's format *is* an argument (thesis, evidence, counter-evidence, confidence — the analyst's note from the Foundation) and any capability that cannot show its reasoning at V1 quality is cut rather than shipped opaque. This principle also settles the "impressive but unexplainable model output" debates in advance: no.

**P6. The flywheel eats first → every capability feeds a joint or justifies itself extraordinarily.** The Foundation's feature test applied to V1's scope with the ICP's KPI set as the scoreboard. Decision consequence: outcome capture — the least glamorous capability in Section 4 — is a P0, built with the care other products spend on onboarding, because the learning proposition dies without it. Conversely, several delightful ideas (Section 5) are excluded *because* they feed no joint.

**P7. Calm premium, even at V1 → craft is not a later phase.** The Foundation's brand demands (Stripe authority, Mercury warmth) apply to the founding cohort's product, because the wounded buyer's trust forms in the first session and the screenshot moment is a growth channel — an ugly brief doesn't get shared. Decision consequence: V1's surface area is kept small *so that* every surface can be finished to the bar; scope narrowness is what funds craft (the ICP critique's cost warning, answered by subtraction).

**P8. Desktop-class web, ambient by email → mobile-native waits.** Foundation 4.6's budget discipline plus the ICP's do-not-build: V1 is a desktop-class responsive web product, and the *ambient relationship* — the daily presence in the founder's pocket — is carried by the weekly/daily brief in the founder's inbox (read-mostly, one-tap actions), not by a native app. Decision consequence: the brief email is designed as a first-class product surface with P7 craft, not as "notifications."

---

# SECTION 3 — THE CORE LOOP

The smallest complete loop that makes the thesis sentence true and the flywheel spin. Eight steps; each earns its place by what breaks without it.

**1. Teach → The DNA interview.** The founder gives Xenia an hour (target: under 40 minutes **[calibrates]**) of structured conversation; Xenia arrives having done homework on the agency's own site, cases, and visible client base. *Why it exists:* the DNA is the moat's seed and the interview is the ICP's self-referential twist — first value delivered before any prospect exists. Without it, Xenia is a generic researcher; with it, everything downstream is *theirs*.

**2. Generate → The DNA document.** Xenia synthesises the interview plus homework into the readable, correctable Ideal Client DNA (the ICP's ten-category schema), endorsed by the founder before discovery begins. *Why:* endorsement converts Xenia's model into a shared agreement — the psychological contract that makes later corrections feel like managing an employee rather than fighting a tool. It is also the first shareable artefact.

**3. Discover → Xenia hunts.** Continuous ambient discovery against the DNA, plus directed natural-language asks. *Why:* discovery is the employee's initiative made visible — "while you were delivering, I found" — and the flywheel's momentum joint. Bounded output per P3.

**4. Research → The brief.** Every surfaced candidate arrives *understood*: the evidence-linked analyst's note, with the marketing-gap analysis that doubles as the founder's pitch material. *Why:* the brief is the astonishment artefact — the unit of value, of sharing, and of GTM. It is the product's centre of gravity and gets the deepest investment of any capability.

**5. Recommend → The queue and the reasons.** A ranked, bounded set with decomposable scoring and at least one visible act of judgment (an exclusion with reasoning). *Why:* ranking without recommending is a tool; the Foundation requires the accountable posture. The visible exclusion is engineered in because the ICP's astonishment bar counts it.

**6. Act → The founder contacts the prospect.** Xenia drafts the opener from the brief's evidence in the founder's voice; the founder edits, and sends *from their own email client*. *Why the step exists:* without action, no outcome; without outcome, no learning. *Why the send stays human in V1:* Section 8's ruling — the brain-before-hands principle, deliverability risk avoided entirely, and the trust ladder's bottom rungs honoured (N3).

**7. Record → The outcome.** Contacted, replied, meeting, won, lost, disqualified — captured with near-zero friction, prompted intelligently ("you contacted Brightpath eleven days ago — anything back?"). *Why:* the flywheel's most fragile joint. The ICP set ≥70% outcome-capture as a KPI because unrecorded outcomes starve the loop; V1 treats capture UX as a first-class design problem, not a form.

**8. Learn → The DNA evolves, visibly.** Behaviour, corrections, and outcomes update the DNA; Xenia narrates the change ("I've noticed you pursue smaller DTC brands than we discussed — I've adjusted; here's the changelog; revert if wrong"). *Why:* the learning is real (acceptance trend proves it internally) and *felt* (the narration proves it to the customer) — both are required, because the Foundation's compounding claim must be experienced to drive renewal, not just measured to satisfy us.

The loop closes back to step 3 within the same week: learning that doesn't change next Monday's recommendations isn't learning, it's logging.

---

# SECTION 4 — V1 CAPABILITIES

Eight capabilities. Each carries the full justification the brief demands; none survives on "obviously we need it." Priorities: P0 = the loop breaks without it; P1 = the loop weakens without it; P2 = earns its place but is the first cut under pressure.

## C1 — The DNA Interview & Homework · P0

**Purpose:** convert an hour of founder attention into Xenia's founding knowledge, having already studied the agency's public footprint. **Problem solved:** no agency has articulated its ideal client; every downstream capability needs it articulated. **User value:** the consulting-grade artefact (standalone value before any prospect). **Business value:** onboarding-as-value is the activation mechanism and the free-session GTM offer. **AI value:** the highest-density training signal the customer will ever provide in one sitting. **Flywheel:** ignites the teaching joint. **Dependencies:** none — deliberately first. **Complexity:** high (conversational quality is the product's first impression). **Success metrics:** ≥85% completion once started; artefact endorsed "more precise than our own" by ≥8/10 (ICP Instrument 5 thresholds). **Risk:** interview feels like a form in disguise; mitigated by the homework-first opening (Xenia leads with observations, not questions). **Alternatives considered:** form-based setup (rejected — violates P4 and the employee metaphor at the exact moment it must be established); importing an existing ICP doc (accepted as *input to* the interview, not a bypass).

## C2 — The Ideal Client DNA (living document) · P0

**Purpose:** the readable, correctable, versioned model of who the customer sells to — the moat's unit. **Problem solved:** targeting knowledge trapped in the founder's intuition. **User value:** clarity artefact; shareable with their team; visibly improving. **Business value:** the primary moat per Foundation Section 11; the switching cost. **AI value:** the conditioning context for every downstream act. **Flywheel:** the evolving centre — DNA velocity is a named KPI. **Dependencies:** C1. **Complexity:** medium-high (the schema is the ICP's ten categories; the hard part is plain-language rendering and changelog/revert). **Success metrics:** DNA velocity high in month one, asymptotic thereafter; corrections applied within one recommendation cycle; zero customer-reported "it ignored my correction" incidents. **Risk:** over-schematisation — ten categories could make V1's learning brittle; ruling: the schema is the *ceiling*, V1 may ship with the six categories the concierge test proves load-bearing **[calibrates]**. **Alternatives:** free-text profile (rejected — unlearnable); invisible learned model (rejected — violates N4 and forfeits the endorsement moment).

## C3 — Discovery (ambient + directed) · P0

**Purpose:** continuously find candidate businesses matching the DNA; answer natural-language hunts. **Problem solved:** the founder's empty top-of-funnel and dead Saturday research hours. **User value:** "while you were delivering, I found" — the employee's initiative. **Business value:** the differentiation from every reactive tool; the weekly reason to return. **AI value:** every accept/decline on discovered candidates trains precision. **Flywheel:** the momentum joint — discovery quality is where compounding is *felt*. **Dependencies:** C2. **Complexity:** high (the honest engineering centre of V1, and the unit-cost question lives here and in C4). **Success metrics:** acceptance rate ≥40% month one → ≥60% month three **[calibrates]**; ≥1 "didn't know this company" per first session. **Risk:** thin-market DNA (niche too narrow → empty queue) — mitigated by Xenia *saying so* and proposing DNA-consistent widenings, never silently padding (P3). **Alternatives:** customer-uploaded lists as the primary source (rejected as primary — it makes Xenia reactive; accepted as supplement: "research these for me" is a legitimate directed ask).

## C4 — The Research Brief · P0

**Purpose:** the astonishment artefact — evidence-linked understanding of one prospect: what they do, trajectory, marketing-gap analysis, fit thesis, counter-evidence, confidence. **Problem solved:** the 30–60 minutes of per-prospect research nobody does. **User value:** walks into every pitch already understanding the room; the gap analysis is their opener. **Business value:** the unit of GTM (shareable proof), the ship-gate artefact, the reason the price is defensible. **AI value:** brief feedback (corrections of errors, confirmations) trains the research layer. **Flywheel:** deepens understanding joint; briefs are what acceptance decisions are made *on*. **Dependencies:** C3 (candidates), C2 (fit thesis conditioning). **Complexity:** highest in V1 — this is the craft centre. **Success metrics:** the astonishment bar's a–e, plus factual-error rate below an explicit threshold set by the evaluation standard (next document); pursuit behaviour ≥30% (concierge-carried). **Risk:** the trap the ICP named — manual astonishment failing to automate at cost; this is V1's central engineering bet and gets the Section 9 unit-cost budget and a named quality-evaluation harness before scale. **Alternatives:** shallower "enriched profile" format (rejected — that's Apollo with adjectives; the analyst's-note form is the category difference); on-demand-only research with no default depth (rejected — the astonishment bar requires depth as default).

## C5 — Recommendations, scoring & corrections · P0

**Purpose:** the bounded ranked queue with decomposable reasons, accept/decline/correct mechanics, and the engineered visible exclusion. **Problem solved:** priority — understanding many prospects creates the "which first?" problem. **User value:** Monday morning answered in ten minutes. **Business value:** the accountable-recommendation posture that separates employee from tool. **AI value:** the densest routine training signal (every accept/decline, every reason given). **Flywheel:** the acting and teaching joints' meeting point. **Dependencies:** C2–C4. **Complexity:** medium (the AI is in C2–C4; this is judgment presentation and feedback capture). **Success metrics:** acceptance trend (the KPI); correction rate ≥3/week month one; decline-with-reason ≥50% of declines (reasons are the teaching gold). **Risk:** feedback friction — founders won't annotate (Foundation flywheel honesty clause); mitigation: one-tap reasons, behaviour-first learning, reasons optional but delightful to give. **Alternatives:** unbounded feed (rejected — P3); auto-pursue thresholds (rejected — N3, V1 trust rungs).

## C6 — Assisted first contact (drafts, no sending) · P1

**Purpose:** evidence-grounded opener drafts in the founder's voice; copied or mailto'd into their own client. **Problem solved:** the blank-page tax that stalls action after research. **User value:** ten minutes from brief to sent email, sounding like *them*. **Business value:** converts intelligence into the meetings that become case studies. **AI value:** edits to drafts are voice-training signal. **Flywheel:** lubricates the acting joint — pursued-rate is the KPI it serves. **Dependencies:** C4 (evidence), C1 (voice sample from interview + site). **Complexity:** medium. **Success metrics:** drafts used-or-edited (vs discarded) ≥60%; time-from-brief-to-contact halved against concierge baseline. **Risk:** voice-miss embarrassment — mitigated by always-draft-never-send framing and explicit "this is a starting point" posture. **Why P1 not P0:** the loop technically closes with the founder writing their own emails from the brief; drafts accelerate but don't enable. The 50%-cut test (Section 12) confirms this ranking. **Alternatives:** in-product sending (rejected for V1 — Section 8's ruling: deliverability infrastructure, compliance surface, and trust-ladder violations, all for the "hands" while the "brain" is on trial); sequence templates (rejected permanently — N1 adjacency).

## C7 — Outcome capture & the learning narrative · P0

**Purpose:** frictionless recording of what happened (contacted → replied → meeting → won/lost/disqualified + optional reasons), and Xenia's visible narration of what she learned from it. **Problem solved:** the flywheel's starvation risk; the customer's invisible ROI. **User value:** minimal admin, and the running ledger that makes renewal a non-event (Foundation's obviousness stage); "Xenia learned from our win" is the felt-compounding moment. **Business value:** cohort win-rate data — the company's proof asset — and the churn-defence ledger. **AI value:** outcomes are the only ground truth the learning loop gets. **Flywheel:** the recording and learning joints entire. **Dependencies:** C5, C6. **Complexity:** low mechanically, high behaviourally (the design problem is human memory and motivation). **Success metrics:** outcome-capture ≥70% of pursued prospects (ICP KPI); prompted-capture response ≥50%. **Risk:** the highest-probability failure in V1 — busy founders not reporting; mitigations: intelligent prompts tied to elapsed time, one-tap capture from the weekly brief email, and honest acceptance that *pursued/not-pursued behaviour* (which we observe directly) must carry learning weight when outcomes lag. **Alternatives:** inbox integration to auto-detect replies (deferred to V1.5+ — powerful, but drags email-access permissions and privacy surface into V1's trust-critical window **[calibrates]** if capture rates disappoint); full pipeline board (Section 5 — refused).

## C8 — The Weekly Brief (ambient email) · P1

**Purpose:** Xenia's presence in the founder's week without the app: found-this-week, what-I-learned, what-needs-you, one-tap outcome nudges. **Problem solved:** the week-3-to-6 adoption dip (ICP journey stage 8) and the ambient-relationship requirement of Foundation 4.6 at V1 budget. **User value:** the employee reporting in — calm, skimmable, worth forwarding. **Business value:** the retention surface and a viral artefact (briefs get forwarded to co-founders). **AI value:** engagement telemetry on what earns clicks = interest signal. **Flywheel:** keeps the wheel turning through attention troughs. **Dependencies:** C3–C5, C7. **Complexity:** low-medium. **Success metrics:** open rate ≥60% cohort-sustained; ≥1 action per brief median. **Risk:** becoming noise — mitigated by P3 discipline (skip the send when there's nothing worth saying — an email that respects silence teaches trust). **Alternatives:** native-app notifications (Section 5 — refused for V1); Slack integration (V1.5 candidate, not before).

**Explicitly absent from this list and noted for honesty:** a general "Ask Xenia" chat surface. Ruling: V1 ships *scoped* conversation only — follow-up questions on a brief and the DNA interview itself — not an open assistant. The employee metaphor pulls hard toward open chat; the astonishment bar pulls harder toward depth-on-fewer-surfaces, and P5 (explain or don't ship) is hardest to honour in open-ended chat. Open conversation is V1.5's flagship candidate, entering when the knowledge it draws on (briefs, DNA, outcomes) is proven solid. **[calibrates — if design partners' first instinct is to talk to Xenia and the scoped surface frustrates, this ruling is revisited at the six-week revision.]**

---

# SECTION 5 — WHAT V1 WILL NOT BUILD

The refusals, each with its reason — organised by *why* refused, because the categories teach the discipline. Everything here inherits the Foundation's permanent refusals (its Section 7) and the ICP's do-not-build list; this section extends them to V1 grain.

**Refused because the back half hasn't earned entry (sequencing refusals — these return later):**
- **AI inbox / reply management** — powerful, but it manages conversations V1 must first prove it can create; drags email-permission trust costs into the trust-formation window.
- **Pipeline boards & deal management** — the beachhead's problem is top-of-funnel (ICP Section 4); V1 tracks outcomes as *learning data*, not deals as *workflow objects*. A kanban is a CRM cosplay.
- **Revenue/positioning analytics (5.6 embryo)** — needs quarters of outcome data to say anything honest; shipping it early means shipping horoscopes.
- **In-product sending & deliverability infrastructure** — Section 8's ruling; the largest deliberate absence and the one sales pressure will attack first. The answer is scripted: *Xenia's judgment is on trial before her hands; and your domain is not our test environment.*
- **Native mobile apps** — Foundation 4.6's own budget discipline; the ambient layer is C8 email in V1. Native arrives when the interaction layer has proven what deserves a pocket presence.

**Refused because they contradict the strategy (philosophical refusals — these never return):**
- **Mass outreach, sequences, campaign builders, send-time optimisers** — N1. Not at V1, not ever. Listed anyway because a surprising number of "just one small template feature" requests are this in disguise.
- **AI SDR autonomy (auto-send, auto-follow-up)** — N3 plus the entire counter-positioning; autonomy is earned per-customer up a delegation ladder whose upper rungs don't exist in V1 by design.
- **Contact-data brokering / email-finding as a headline feature** — sells records, invites the database comparison, and drags scraping-adjacency risk (Foundation Section 14) into the trust window. V1 surfaces publicly available business contact routes within the brief, modestly, compliantly, and without bulk export.
- **A configurable platform** (custom fields, scoring-weight sliders, workflow automation) — P4; configuration is how tools outsource their thinking to customers.

**Refused because focus is finite (opportunity-cost refusals — argued individually later, if ever):**
- **Chrome extension** — a second surface to polish before the first is proven; also nudges the product toward "research what I'm looking at," which is reactive-tool physics, not employee physics.
- **Team seats, roles & permissions** — the beachhead buyer is a founder + maybe one; multi-seat complexity (permissions, activity attribution, billing tiers) taxes every feature for a user who is mostly one person. Simple seat-sharing suffices; real collaboration is V2.
- **Integrations beyond one CRM export** — the ICP allowed one sync (HubSpot or Pipedrive one-way push, and even that is V1.5 **[calibrates]**); V1 ships clean CSV/copy export. Every integration is a promise to maintain; V1 makes almost none.
- **Billing sophistication** (tiers, usage metering, add-ons) — one plan, one founding rate, annual option. Pricing experiments happen in conversations, not in checkout engineering.
- **Marketplace / community features, white-labelling, API access** — each a business model decision disguised as a feature; all premature by years.
- **Collections & saved-view machinery** — the Foundation's smart-collections pillar is real and V1.5-bound; at V1 scale (tens of active prospects) the recommendation queue *is* the organisation, and building organisational furniture before there's volume to organise is scope theatre.

The list's governing sentence, for every future debate: **V1 is a brain, a voice, and a memory — not hands, not a filing cabinet, not a switchboard.**

---

# SECTION 6 — THE V1 USER JOURNEY

The complete journey, with the two annotations that matter for a trust-critical product: **✦ delight moments** (engineered, not hoped-for) and **⚠ risk moments** (named, owned, designed against).

**Landing page.** One promise in the customer's language (ICP Section 9's sentence), one proof artefact (a real, anonymised research brief rendered beautifully — the product demonstrating itself before claiming anything), one entry action. ⚠ *Risk: guru-funnel pattern-matching* — the wounded buyer is scanning for tells; every pixel obeys P7 and the brand's calm. The VSL, when live, sits here under its ICP leash.

**Signup.** Minutes, card-free for the DNA session (the GTM's free-session offer), honest about what happens next. ✦ *First delight seeded immediately:* before the interview, Xenia has already read the agency's site — the confirmation email says so: "I've had a look at your work — looking forward to talking properly."

**Onboarding / DNA interview.** The emotional hinge (Foundation, ICP Instrument 5). Xenia opens with informed observations, asks the questions a brilliant new hire would, handles tangents gracefully, and never feels like a form. ✦ **Delight 1 — being seen:** "no tool has ever asked me these questions." ⚠ *Risk: length* — 40-minute target, resumable, value visible *during* (the DNA assembling live on screen as they talk), because the ICP flagged onboarding length as the single most dangerous UX bet.

**The DNA document.** Delivered immediately after, in plain language, endorsed section by section. ✦ **Delight 2 — the artefact:** the consulting-grade output they'd charge clients for; explicitly shareable. ⚠ *Risk: generic echo* — if the DNA reads like their inputs paraphrased, trust dies here; the document must contain at least one synthesis the founder didn't say but recognises as true (the "you didn't say this, but your last three case studies suggest…" moment — engineered, tested in Instrument 5).

**First research cycle.** Xenia sets expectations like an employee would ("give me until tomorrow morning — first briefs then") rather than spinning a loader. ⚠ *Risk: the empty-market discovery* — a too-narrow DNA returning three candidates; handled by honesty plus proposal (P3), never padding.

**First recommendations session.** The astonishment bar's home. Bounded queue, decomposed scores, the engineered visible exclusion, briefs one click deep. ✦ **Delight 3 — the "I didn't know this company" moment** (bar criterion b). ✦ **Delight 4 — the visible exclusion:** "ruled out X — franchise model, your disqualifier." ⚠ **Risk moment of the entire product: a confidently wrong brief.** A factual error about a business the founder knows personally, in session one, is the trust catastrophe; defences: evaluation-harness quality gates pre-ship, confidence marking (P5), instant correction UX that *visibly* updates ("fixed — and I've noted why I got that wrong"), and the humility posture in every brief's language.

**Decision & first contact.** Accept/decline/correct, then the C6 draft in their voice, sent from their own client. ✦ **Delight 5 — the ten-minute pitch-ready state:** brief → edited draft → sent, before their coffee cools. ⚠ *Risk: the voice-miss* — a draft that sounds like AI is a small embarrassment spend; always-editable framing and voice-learning from edits contain it.

**Export.** Clean CSV / copy-paste of prospects and statuses for whatever the agency already uses. Unglamorous, respectful of their existing world, deliberately boring.

**Outcome capture.** One-tap statuses, intelligent elapsed-time prompts, capture actions embedded in the weekly brief email. ✦ **Delight 6 — the learning narration:** the first time Xenia says "Brightpath replied — noted; I'm weighting site-speed gaps higher, it's the third reply from that pattern." This is the flywheel made *felt*. ⚠ *Risk: capture decay* (C7's named failure mode) — watched weekly at cohort level from day one.

**The weekly rhythm & retention.** Monday session (ten minutes), Thursday-ish brief email, month-end "what Xenia learned this month" note — the running ledger that makes renewal a non-event. ⚠ *Risk: the week-3–6 dip* — novelty gone, outcomes not yet landed; C8 carries the relationship, and the design partners' calendar includes a human check-in exactly there (process covering what product will later absorb).

---

# SECTION 7 — PRODUCT ARCHITECTURE (CONCEPTUAL)

The objects V1's world is made of, and their relationships — the nouns of the product, defined so that product, design, and engineering share one vocabulary. (No schemas; this is ontology, not database design.)

**Workspace (the Agency).** The container of employment: one agency, its DNA, its prospects, its memory. Everything below lives inside exactly one Workspace. V1: one Workspace per customer; Users within it share one Xenia (she works for the agency, not per-seat — a conceptual decision with pricing consequences later).

**User (the Founder + colleagues).** Humans who direct Xenia. V1 keeps roles flat (P4; Section 5's team-permissions refusal): all users see everything, corrections are attributed but equally weighted **[calibrates — if design partners show founder-vs-staff correction conflicts, attribution weighting arrives in V1.5]**.

**The Ideal Client DNA.** The living document: categorised (ICP schema), versioned, with a changelog of every evolution and its cause (interview, correction, outcome, behaviour), endorsable and revertible. *Relationships:* conditions every Discovery run, every Brief's fit thesis, every Recommendation's score; is updated by Corrections and Outcomes. The DNA is the only object the customer and Xenia *co-own* — everything else is either the customer's (Outcomes) or Xenia's work product (Briefs).

**Prospect (the Business).** A real-world company Xenia has surfaced or been pointed at: identity, footprint, current state. Prospects carry *status* (recommended → pursued → outcome), but deliberately not "deal" semantics (no value, stage, probability — that's the refused pipeline). *Relationships:* subject of exactly one live Research Brief; target of Recommendations; owner of Outcomes.

**Evidence.** An observed, linkable fact about a Prospect (their ad is running; their site scores X; they're hiring a marketing manager) with source and timestamp. The atomic unit of P5: Briefs cite Evidence; scores decompose to Evidence-backed claims; Corrections can dispute Evidence. Making Evidence a first-class object — not prose inside briefs — is this section's most consequential ruling, because it is what makes explainability structural rather than stylistic.

**Research Brief.** Xenia's analyst note on one Prospect: thesis, Evidence citations, gap analysis, counter-evidence, confidence, freshness date. Regenerable (freshness is a feature); shareable as the GTM artefact. *Relationships:* composed of Evidence; conditioned by DNA; feeds Recommendation.

**Recommendation.** Xenia's accountable judgment: this Prospect, now, because — with decomposed score, suggested next action, and its place in the bounded weekly set. Includes the *negative* recommendation (visible exclusion). *Relationships:* about one Prospect; justified by one Brief; resolved by a Decision.

**Decision (accept / decline / correct).** The founder's response, with optional reason — the teaching event. *Relationships:* resolves a Recommendation; may spawn a Correction to DNA or Evidence.

**Draft.** The C6 opener: grounded in a Brief's Evidence, written in the Workspace's learned voice, always human-sent. *Relationships:* derived from Brief; edits feed the voice model.

**Outcome.** Ground truth: what actually happened with a pursued Prospect, when, and (optionally) why. The scarcest, most valuable object in the system. *Relationships:* attached to Prospect; feeds DNA evolution and the cohort proof.

**Memory.** Xenia's accumulated context beyond the DNA: preferences, past conversations, decisions, narrative history ("we don't pitch in December"; "the founder hates the word 'synergy'"). Distinct from DNA (which models *their market*) — Memory models *them*. *Relationships:* conditions tone, timing, and interaction everywhere; grows from every exchange.

**The Weekly Brief.** The composed ambient artefact: this week's Recommendations, learning narration, outcome nudges. *Relationships:* a rendering of the week's objects, not a store of its own — which is exactly why it can be excellent cheaply.

The object graph in one sentence: **the DNA and Memory condition Discovery, which surfaces Prospects, which get Evidence-built Briefs, which justify Recommendations, which meet Decisions, which produce Drafts and eventually Outcomes, which evolve the DNA — and every arrow is inspectable.** That final clause is the Foundation's explainability principle expressed as architecture.

---

# SECTION 8 — AI RESPONSIBILITIES

The division of labour, ruled explicitly — because "AI-first" without boundaries is how trust dies (Foundation N3, 4.3). Four zones.

**Xenia does autonomously (no approval, always inspectable):** homework on the customer's own agency; ambient discovery; all research and Evidence gathering; Brief composition; scoring and queue ranking; visible exclusions; DNA evolution *within* endorsed categories (with changelog and revert — evolution is her job; the log is her accountability); learning narration; Weekly Brief composition; freshness refreshes of stale Briefs. *Reasoning:* these are all "brain" acts — analysis and judgment-proposal — whose failure mode is a correctable wrong opinion, never an irreversible act in the world. Autonomy here is what makes her an employee; inspectability is what makes the autonomy safe.

**Xenia does with the human in the loop (proposal → human disposes):** outreach Drafts (founder edits and sends); DNA *structural* changes (new disqualifier, category rewrite, market pivot — proposed with reasoning, applied only on endorsement, because disqualifiers are the customer's law per the ICP schema); widening or narrowing the discovery mandate; anything touching how the agency is represented externally. *Reasoning:* these acts either speak in the customer's name or amend the constitution she works under — both are the boss's signature by right.

**Humans do exclusively (V1):** all sending, in every channel; all commercial conversation with prospects; outcome truth (Xenia prompts, never assumes — a guessed outcome would poison ground truth, and the flywheel's diet must stay clean); the endorsement moments (DNA, structural changes); and the delegation decisions themselves. *Reasoning:* P1's brain-before-hands, the deliverability/compliance surface avoided entirely, and the trust ladder's design — V1 occupies rungs "suggest" and "draft" so that later rungs are *earned upgrades with data behind them*, not launch-day promises. The commercial logic bears repeating: our category died once from hands-before-brain; V1's restraint *is* the positioning.

**Never automated (V1 and beyond — inherits Foundation non-negotiables):** sending without granted delegation (N3); overriding a hard Disqualifier by score (ICP schema rule); presenting inference as fact (N5); fabricating or guessing Evidence; deceiving a prospect about the nature of the exchange (Foundation Section 14); and deleting the customer's corrections. *Reasoning:* these lines define the company, not the version.

The zone boundaries are themselves product surface: the customer should be able to *see* the ladder, see which rung they're on, and see what earning the next rung would mean. Trust architecture hidden in a settings page is trust theatre.

---

# SECTION 9 — SUCCESS METRICS

The measurement system, three layers deep, inheriting the ICP's numbers wherever they exist (every threshold **[calibrates]** against concierge and design-partner data — stated once here rather than per line).

**Activation (the gate into the cohort):** DNA completed *and* endorsed; first recommendations session held; astonishment bar criteria a–c met; ≥1 Recommendation pursued within 14 days. All four, not any — activation is the loop having turned once with a real act at step 6. *Anti-metric:* signups are reported but never celebrated.

**The loop metrics (weekly, per cohort):** acceptance rate (≥40% m1 → ≥60% m3); pursue rate ≥30% of accepted; outcome-capture ≥70%; correction rate ≥3/week m1 with decline-reasons ≥50%; weekly return without prompt (the "employed" signal); Weekly Brief opens ≥60% sustained; time-to-first-meeting median ≤30 days; brief factual-error reports per 100 briefs (quality line — threshold set by the evaluation standard, direction: relentlessly down).

**Flywheel metrics (the ICP's KPI set, monthly, cohort-versus-cohort):** teaching rate; DNA velocity (high → asymptotic; flat-at-start = broken teaching joint); acceptance-rate *trend within customer tenure* — the single most important internal chart in the company, because it is the compounding claim in line form; and, once tenure allows, the cohort win-rate delta (m12 vs m1) that the Foundation stakes the thesis on.

**Commercial & advocacy:** founding-cohort m3 renewal ≥80%; conversion toward core band on schedule; referral rate (new design partners sourced from existing ones — target ≥1 per 3 customers by m6); unprompted share events (screenshots, forwards — instrumented via share artefacts).

**The North Star Metric: Right-Fit Conversations Started per week** — the count of recommendations customers pursue with an actual first contact. *Why this and not alternatives:* "clients won" is the true goal but too slow and rare to steer weekly product work; "briefs generated" is activity theatre; "meetings" depends on the prospect's calendar. Pursued-with-contact is the customer *acting on Xenia's judgment with their own reputation* — the exact behaviour that proves the thesis sentence, leads the financial outcome, and requires every capability C1–C8 to have worked. It is also gameable only by making recommendations genuinely better, which is the definition of a well-chosen North Star.

**The company dashboard (weekly, one screen):** North Star and its trend; acceptance rate by cohort; outcome-capture rate; astonishment-bar pass rate for new activations; error-report rate; **unit economics per active customer** — the ICP's flagged open question given a permanent home: intelligence cost per active customer per month against the price band, with an explicit ceiling (hypothesis: COGS ≤25% of subscription price at the core band **[calibrates hard]** — if Xenia-grade intelligence can't live under that ceiling, the finding goes to pricing and scope *immediately*, not to a quarterly review).

**The board dashboard (per Foundation 12.1 — customer outcomes before our revenue, in that order):** customers' clients won (count and value); North Star trend; cohort retention curves; flywheel compounding chart (acceptance-by-tenure); then MRR, founding-cohort conversion, CAC by channel; then the risk watchlist deltas (ICP Section 13). The ordering is constitutional: the day the board pack leads with MRR is the day the Foundation's first value has quietly died.

---

# SECTION 10 — PRODUCT RISKS

Every capability challenged; the honest register, ranked by expected damage.

**R1 — The brief doesn't automate (C3/C4).** The central bet: concierge-grade astonishment at machine cost and machine consistency. Failure modes: factual error rate above trust threshold; analysis that's accurate but *obvious* to a professional grader; unit cost blowing the COGS ceiling. *This risk is why the next document exists* (see Section 13) — V1 build must not start at scale before an evaluation harness defines brief quality operationally and a cost model prices it. *Contingency if partially true:* a human-QA gate on briefs for the founding cohort (concierge hybrid) is acceptable and honest — margin-negative at 25 customers, fatal only if still needed at 500.

**R2 — Outcome capture starves the loop (C7).** Named repeatedly because probability is high and the damage is silent: the flywheel appears to spin while learning from nothing. *Watch:* capture rate weekly from customer one; *trigger:* two cohort-weeks below 50% forces the V1.5 inbox-detection decision early.

**R3 — The empty-market problem (C2/C3).** Niche DNAs (the ICP *celebrates* niching) may exhaust their UK candidate pools within months. Discovery must know the difference between "no matches this week" and "this market is finite and we've seen most of it" — and say the second honestly when true, proposing DNA-consistent adjacencies. Underestimating this turns our best customers (the most-niched) into our first churns. *Genuinely hard; flagged to the evaluation standard.*

**R4 — The DNA interview underwhelms (C1).** If the hinge moment feels like a smart form, activation economics collapse. Mitigated by Instrument 5 pre-build testing; residual risk in the gap between scripted-human and automated delivery.

**R5 — Drafts leak voice-miss embarrassment (C6).** Contained by design (never sent automatically), but a bad draft still taxes the session's magic. Acceptable risk at P1; the metric (used-or-edited ≥60%) will tell us fast.

**What is unnecessary (and stays out despite temptation):** collections, open chat, integrations breadth, native mobile — already refused in Section 5; re-listed because each will be *requested by design partners within weeks* and the refusals must survive contact with beloved customers. **What is too ambitious for V1 and knows it:** fully automated DNA structural evolution (V1 proposes, human disposes — full autonomy here is a V2 trust milestone); real-time freshness on every brief (V1 refreshes on cadence and on-demand, not continuously). **What could wait even within V1 if the six-week revision demands cuts:** C6 drafts and C8's daily variant — the loop closes without them (the 50% test below proves it).

---

# SECTION 11 — MANUAL VALIDATION → MVP → V1 → V1.5 → V2 → LONG-TERM

**Manual validation (now → week 6; no product).** The ICP's Instruments 1–5 exactly: interviews, the concierge test (hand-built DNAs and briefs), pricing conversations, landing-page smoke tests, scripted-interview usability. *Output:* calibrated astonishment bar, validated-or-killed wedge, design-partner cohort, case-study raw material — and the recalibration of every **[calibrates]** mark in this document. *Why first:* it tests the value hypothesis at a fortnight's cost, per the ICP's ranking of the concierge test above all other instruments.

**MVP (weeks ~6–14; the productised concierge, ten design partners).** The loop's spine with humans in the seams: C1 interview (AI-led, human-observed), C2 DNA, C3 discovery + C4 briefs *with a human QA gate before anything reaches a customer*, C5 recommendations, C7 capture handled high-touch, C8 assembled semi-manually. *Why this shape:* it ships the astonishment artefact at guaranteed quality while measuring the R1 gap (what % of machine briefs pass QA unedited — the automation-readiness dial), builds the evaluation dataset from QA edits, and keeps ten customers' trust unexposed to raw model variance. The MVP's product *is* the QA delta.

**V1 (months ~4–8; the self-serve loop, 25 founding customers → 100).** C1–C8 complete per Section 4; QA gate narrowing to sampled auditing as the harness proves briefs at bar; instrumentation per Section 9 live from day one; astonishment bar enforced as ship-gate per activation. *Entry criteria, explicit:* MVP briefs passing QA unedited ≥70%; unit cost inside ceiling; capture rate ≥60% under high-touch (proving the behaviour exists to be productised). *Why these criteria:* V1 is MVP minus the humans — it may only ship when the humans are demonstrably removable.

**V1.5 (opportunistic, data-triggered — not calendar-triggered).** The candidates and their named triggers: one-way CRM push (trigger: ≥40% of cohort exporting weekly); scoped→open "Ask Xenia" conversation (trigger: the C4-conversation usage signal from Section 4's ruling); inbox reply-detection for capture (trigger: R2's threshold breach); Slack brief delivery (trigger: cohort demand ≥30%); collections (trigger: median active prospects per workspace >40); attribution-weighted corrections (trigger: the Section 7 multi-user conflict signal). *Why trigger-based:* V1.5 is where roadmaps go to bloat; tying each item to an observed threshold keeps the flywheel test (P6) sovereign over the wishlist.

**V2 (the back half begins, earned).** The AI inbox; delegated sending at the ladder's next rungs (with the deliverability and compliance machinery done properly — the refusal reverses only with N2-grade infrastructure); pipeline intelligence; native mobile (the interaction layer now proven — Foundation 4.6's annual surface decision made with data); the 5.6 revenue-intelligence embryo on real outcome volume; rung-1b US market tuning. *Why here:* each item needs either trust rungs (sending), data volume (analytics), or proven interaction patterns (mobile) that only V1's cohort can supply.

**Long-term (the Foundation's horizon, restated for discipline).** The advisor role, the across-customer outcome graph, delegation's upper rungs, rung 2+ verticals — *governed entirely by the Foundation's ladder gates and flywheel doctrine; listed here only so nobody mistakes their absence from V1 for their absence from the company.*

---

# SECTION 12 — FOUNDER CRITIQUE

**The 50% cut, performed honestly.** Forced to halve V1, what survives is the spine: **C1+C2 (interview → DNA), C3+C4 (discovery → briefs), C5 (recommendations + corrections), and a minimal C7 (status capture).** Cut: C6 drafts (founders can write emails from a great brief; the brief is the moat, the draft is a convenience), C8's weekly brief (a hand-sent email replaces it at founding scale), scoped chat, export polish, changelog UI (keep the log, defer the surface), and all V1.5 candidates pre-emptively. What this exercise reveals is the document's true center: **Xenia V1 is the DNA and the brief; everything else is packaging.** If build pressure comes, this paragraph is the cut list, pre-agreed.

**What should be delayed that this document didn't delay:** an honest reviewer would challenge C8's P1 status (retention surface, yes — but at 10–25 customers, founder-sent emails are *better* than automated ones, and automating the relationship this early is exactly the industrial reflex the Foundation warns against). Fair. C8 automation moves to late-V1; the *cadence* stays human until then. Likewise the voice-learning in C6 — V1 needs a decent draft, not a voice model; learning-from-edits can be V1.5 telemetry before it's V1 capability.

**Assumptions still unexamined:** that weekly is the right rhythm (the entire product breathes on a 7-day cycle borrowed from agency habit assumptions — the design partners might reveal daily-checkers or monthly-batchers, and the cadence should be learned, not imposed — P4 cuts both ways); that the founder is the only persona (ICP says founder-led, but the first delegation *inside the agency* — to an ops person or junior — will happen fast if the product works, and V1's flat-role ruling has never met that user); that discovery precision is primarily a DNA-quality problem (it may be primarily a *coverage* problem — R3 — in which case the constraint is the observable-terrain map, not the model); and the quiet one — that agencies will tolerate *a product this restrained*. The do-not-build list is strategically right and emotionally demanding: customers burned by overpromising tools may still *miss* the promises. The counter is P3's under-promise posture plus visible compounding; but it is a bet about buyer psychology, not a fact.

**Where we're overengineering:** the DNA's ten categories at V1 (Section 4's own ruling suspects six suffice — take the suspicion seriously); Evidence as fully first-class from day one (right ontology, but MVP can carry evidence as structured citations within briefs and promote it to independent object when disputes and reuse actually occur); metric count (Section 9 defines ~20 measures — the company can *watch* five; the rest are quarterly, and pretending otherwise dilutes the five).

**Where we're underthinking:** the correction experience (one line in C5 carrying the whole teaching joint — it deserves design investment equal to the brief, because the flywheel's teaching rate lives or dies in exactly that ten-second interaction); the R3 finite-market conversation (what Xenia says in month four to a brilliantly-niched agency is a *product moment* nobody has designed); and offboarding — a founding customer who leaves should leave impressed (export everything, DNA included, gracefully — N6's easy-leaving applied), because in a village-sized market like UK agencies, churned customers talk as loudly as current ones.

---

# SECTION 13 — SCORECARD

| # | Section | Score /10 | Justification & improvement |
|---|---------|-----------|------------------------------|
| 1 | Product Thesis | **9** | One-sentence thesis, four falsifiable propositions, and anti-success defined (activity theatre, wrong-buyer revenue). The [calibrates] convention resolves the sequencing tension with the ICP honestly. *Improve:* attach the six-week revision date the moment research starts. |
| 2 | Product Principles | **9** | Every principle decides a named fight (P1 kills the send button; P8 kills native mobile); consequences stated at desk-level grain. *Improve:* none structural — publish P1–P8 on the office wall, literally. |
| 3 | Core Loop | **9** | Eight steps, each justified by what breaks without it; the closing rule (learning must change next Monday) converts philosophy into a testable latency requirement. *Improve:* define that latency numerically post-MVP. |
| 4 | V1 Capabilities | **8.5** | Full twelve-attribute justification per capability; the scoped-chat ruling and C6's P1 demotion show real scope courage. Deduction: complexity ratings are gut-grade pre-engineering. *Improve:* re-rate complexity with a technical co-founder/lead in the room. |
| 5 | Do Not Build | **9.5** | The document's sharpest section (a pattern in this series — refusals age best): three-way categorisation by *why*, pre-scripted answers to sales pressure, and the governing sentence. *Improve:* maintenance only. |
| 6 | User Journey | **8.5** | Delight engineered rather than hoped (six named moments), risks owned (the wrong-brief catastrophe centred). Deduction: journey ends at retention — offboarding surfaced only in the critique. *Improve:* add the graceful-exit design as a journey stage. |
| 7 | Product Architecture | **8.5** | Clean ontology with the Evidence-as-first-class ruling making explainability structural; DNA/Memory distinction (their market vs. them) will pay for years. Deduction: the critique rightly questions Evidence-object timing at MVP. *Improve:* adopt the critique's promote-when-needed path. |
| 8 | AI Responsibilities | **9** | Four zones with reasoning, the never-list inheriting non-negotiables, and the ladder-as-visible-surface insight. *Improve:* draft the actual delegation-rung definitions before V2 planning, not during. |
| 9 | Success Metrics | **8.5** | North Star argued against alternatives and gaming-resistant; unit-cost ceiling given a permanent dashboard home; board ordering made constitutional. Deduction: the critique's own point — 20 metrics defined, 5 watchable. *Improve:* name the five; demote the rest to monthly. |
| 10 | Product Risks | **8.5** | R1–R5 ranked by expected damage with named contingencies; the temptation re-list (what beloved customers will request) is practical wisdom. Deduction: no probability×impact grid — third document running with this gap. *Improve:* build the shared risk register across all three documents now. |
| 11 | MVP→V2 Staging | **9** | The staging logic is the section's strength: MVP defined as "measuring the QA delta," V1 as "MVP minus removable humans," V1.5 as trigger-gated not calendar-gated. *Improve:* add explicit cost gates alongside quality gates at each transition. |
| 12 | Founder Critique | **9** | The 50% cut is performed, not gestured at; it demotes two of the document's own P1s and finds the underthought correction UX. *Improve:* none — schedule the assumptions (cadence, second persona) as design-partner research questions. |
| 13 | Scorecard | **—** | Not self-scored, on principle. |

## Remaining founder decisions before build

**(1)** Ratify the no-send ruling for all of V1 — the largest scope decision and the one sales pressure will test first; **(2)** ratify the scoped-chat ruling (and its revisit condition); **(3)** set the unit-cost ceiling number (the 25% COGS hypothesis needs a real figure against the chosen price); **(4)** choose the MVP's human-QA staffing model (founder-does-QA vs. early hire — it defines the founder's next three months); **(5)** approve the DNA six-vs-ten category start; **(6)** approve C8's demotion to human-sent at founding scale (accepting the critique); **(7)** name the five watched metrics; **(8)** set the six-week revision meeting and the MVP→V1 gate review as calendar events with the kill criteria attached (the ICP's decision-11 discipline, extended); **(9)** decide the design-partner offboarding promise (what leavers keep) before the first one signs, not after the first one leaves.

## The next document

**Recommendation: "Xenia — The Intelligence & Evaluation Standard."** The reasoning is forced by this document's own risk register: R1 (briefs must automate at quality and cost) is the central bet of the entire company, every quality gate in Sections 9 and 11 references an evaluation harness that does not yet exist, and the astonishment bar cannot govern engineering until it is decomposed into operational definitions — what a factual error *is*, what "worth a conversation" decomposes into, how brief quality is scored, sampled, and regression-tested, what the unit-cost model prices, and how the concierge test's human-produced gold standard becomes the benchmark dataset. That document is the bridge between this strategy and any responsible build: it converts "astonishing" from an adjective into an instrument. It should be written against the concierge test's actual artefacts — which makes it, correctly, the companion piece to the research phase already scheduled.

Per instruction: recommended, not written. Waiting.

---

*End of Product Strategy & V1 Scope v1.0. Governed by the Foundation Document v1.1 and the ICP & Wedge Strategy v1.0; amendable by the Foundation's procedure. The [calibrates] marks constitute this document's pre-registered bending points; the six-week revision reads them against evidence.*
