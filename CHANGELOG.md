# Changelog

Format: keep-a-changelog-ish; one entry per released state, newest first.

## Hosted auth shipped — 2026-07-22

Execution-mode Tier 1 (ADR-015, supersedes ADR-012): magic-link sign-in
replaces paste-a-token as the production flow. One email field, no
password; entering a new address provisions the workspace on first use
(unchanged backend behaviour). Session persistence, silent refresh, and
sign-out-everywhere are the Supabase SDK's defaults, wired through a
small `lib/auth/client.ts` seam that keeps a synchronously-readable token
cache live via `onAuthStateChange`. The developer paste-a-token screen is
preserved as an explicit fallback for environments with no live Supabase
project — local dev, CI, the E2E harness — so the existing test suite
needed zero changes to keep passing. Zero backend changes: the JWT
verifier already accepted real Supabase tokens. This was the
most-repeated finding across both prior strategic audits — the
precondition every other recommendation sat behind.

## Design authority adopted — 2026-07-21

The founder supplied the actual landing page (`xenia-source/`); ADR-014
ratifies it as the design source of truth, superseding the interim
warm-paper system. The app re-skins to its language: deep-space black with
a dimmed royal ambient wash, white/muted/faint ink on white-alpha
hairlines, the royal-blue signature (CTA gradient pills, focus rings,
active states), panel cards, glass reserved for chrome and transient
surfaces, Cabinet Grotesk display / IBM Plex Sans body / JetBrains Mono
label voices, and the BlackHoleMark in the topbar. Dark-first single
theme. The demo's fictional modules ratify no capabilities; AA, visible
focus, and the reduced-motion law are retained. All suites + loop-walk
E2E green on the new skin; screens re-reviewed from captures.

## V1.1 constitution + Phase 2 (in progress) — 2026-07-20

Doc 12 (Product Manifesto, M1–M12) and Doc 13 (Product Intelligence
Standard, I1–I11) join the constitution; the Evolution Plan gains an
Intelligence phase (now Phase 3) between Experience and Authentication.
Phase 2 delivered so far: revert surfaced on the DNA changelog
(revert-with-log, honest reversibility flags), amendable interview answers
with the visible transcript, the brief's typographic fold, chip focus
discipline (focus moves in, escape retreats, aria-expanded), furnished
empty states, sign-in pending state, responsive shell, and the Button
primitive on tokens. Phase 2 closed at its exit bar: component tests now cover every feature
directory (23 frontend tests), all action surfaces share the one Button
primitive, and the both-themes/three-widths screen review was actually
performed against captured stills via the new env-gated screens harness —
finding and fixing a mobile header collision. The landing-page storyboard
(docs/design/LANDING_PAGE_STORYBOARD.md) joins the design constitution.

## V1.1 Phase 1 — the design system as code — 2026-07-20

Governed by docs/11_V1_1_PRODUCT_EVOLUTION_PLAN.md (six quality phases, no
new capabilities). This phase: the Doc 06 §8 visual philosophy made
executable — ink/paper/one-accent tokens with first-class automatic dark
mode (warm blacks, AA in both themes), the serif reading face for briefs,
DNA statements and Xenia's voice, a fixed motion vocabulary
(120/200/320ms, settle curves, one global reduced-motion law), visible
focus everywhere, two shadows, tokenised confidence colours, and the
UX-state primitives (shape-true skeletons — no spinners anywhere — designed
empty states, plain-voice error alerts) swept across every screen. Zero raw
palette utilities remain in feature components; loop-walk E2E green.

## Hardening pass — 2026-07-20 (post-review)

An independent release review of the completed V1 build produced findings;
the confirmed Release-Blocking and High items were fixed, the rest recorded
in DEBT.md. Highlights:

### Fixed
- **Architecture:** the AP2 layers contract had been broken since Epic 9
  (`repositories` importing `evaluation`) and masked locally by piped
  lint-imports output; the golden-set shape and its membership law moved to
  the domain, restoring both contracts.
- **Tenancy:** worker jobs now attach their workspace RLS context; Monday
  assembly fans out one idempotent job per workspace (blast radius);
  one composition root for assembly (`build_assemble_queue`).
- **Security:** draft edits scoped to the caller's prospects (cross-tenant
  write/DoS closed); CSV formula-injection escaping on the prospect
  export; interview one-per-line answers bounded at 20 elements.
- **API honesty:** decisions can no longer resolve visible exclusions
  (pursuing a ruled-out business is a DNA change, refused with that
  message); exclusion reasons never name a law they cannot attribute.
- **Exports:** brief/DNA PDF and prospect CSV downloads now carry the
  bearer token (bare anchors 401ed in a real browser).
- **A11y:** accessible names on the confidence word, decline chips, and
  DNA withdraw controls.

### Validated
- Docker image builds; migrations, API, and worker all boot from the image
  against a fresh Postgres 16 (health checks green, scheduler live).

### Documented
- ADR-010 (tenancy enforcement in deployment), ADR-011 (scripted
  interview), ADR-012 (alpha token sign-in — a GA blocker), ADR-013
  (family-level disqualifier matching); DEBT.md now carries the honest
  register.

## V1 engineering complete — 2026-07-20

Epics 0–12 implemented per docs/10_V1_BUILD_PLAN.md (commits `209163a`
through `d304031`): foundations, domain model, research workbench, source
ingestion, evidence & signals, research orchestration, brief generation,
recommendation engine, Editor console, frontend alpha, MVP mode, and the
hardening deliverables. V1 sign-off per Doc 10 §9 additionally requires
founder-side operational gates (drills, golden set ≥50, sustained
unedited-pass ≥70%, cohort).
