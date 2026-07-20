# Xenia — V1.1 Product Evolution Plan

*Governed by Documents 01–10; deviations require ADRs. This plan turns the
engineering-complete V1 into a product of benchmark quality — Linear,
Stripe, Mercury, Apple, Notion, Vercel, Wise — without adding a single
capability the Build Plan did not ratify. V1.1 is a quality phase, not a
feature phase.*

---

## 1. What the benchmark actually means

The named benchmarks share one school: **calm, typographic, subtractive,
fast, honest**. That school is already our constitution — Doc 06 §8 wrote
it before we had screens: whitespace is confidence, hierarchy through
typography not chrome, one accent with semantic colour only, motion that
explains and never performs, honest waits over loading theatre, premium
feel achieved *subtractively*, AA as a floor. V1.1 does not import a new
aesthetic; it executes the documented one at the benchmarks' level of
finish. Every review question in this phase is: *would this survive Doc 06
§8 read aloud?*

## 2. Constitutional rulings (tensions resolved before work begins)

Requests that arrived with this phase are ruled on here so nothing is
silently adopted or silently dropped:

- **Glassmorphism** — admitted in exactly one role: elevated transient
  surfaces (dialogs, command palette, mobile sheet) may use a tokenised
  backdrop blur. Glass as ambient decoration on cards or panels is refused
  (Doc 06 §8: no chrome multiplying into clutter; visual confidence is the
  absence of cheapness).
- **Gradients** — refused inside the application ("no gradient-of-hype
  buttons" is verbatim law). The marketing site may use *atmospheric*
  gradients — background light, never on interactive elements, never as
  hype.
- **Scroll animations** — on the marketing site only, and only where they
  *explain the product* (the correction rippling to the queue, the receipt
  table assembling). Scroll theatre for its own sake is performance, which
  motion is forbidden to be.
- **Testimonials** — no fabricated quotes, ever (Doc 01 honesty; Doc 05's
  regulator-and-front-page test). The site ships a trust section built
  from what is true — the receipt rule, the Editor gate, the departure
  rule — and adds design-partner quotes only when real ones exist, with
  permission.
- **Animation timings** — a fixed motion vocabulary (three durations, two
  curves, one reduced-motion law) defined once in the Design System and
  never improvised per screen.

## 3. Gap inventory (from the V1 release review, DEBT.md, and re-reading every screen)

**Experience gaps:** loading states are placeholder sentences, not
skeletons; no dark mode (founders read at midnight — ICP; Doc 06 names
them); default-Tailwind grey palette rather than the ink/paper/accent
identity; no motion vocabulary at all; focus states are browser defaults;
empty/error states exist in the right voice but without visual form; no
keyboard shortcuts; the interview cannot amend an answer; rank reasons and
score decompositions render but aren't typographically differentiated;
mobile is untested beyond responsive classes.

**Product gaps carried from DEBT.md:** hosted auth (ADR-012 — the single
GA blocker and also the worst experience moment: a pasted token); `Dna.revert`
unexposed despite the changelog promising it; outcome prompts write audit
rows with no surface; the golden set is curated but unconsumed.

**Absent entirely:** marketing website; brand guidelines beyond Doc 06's
prose; screenshot/demo/VSL assets; iOS anything.

## 4. Workstreams → phases

Eight workstreams, six phases. Each phase has an exit bar; no phase starts
until the previous one's bar is met. One commit discipline, full battery,
E2E green — unchanged from V1.

### Phase 1 — Foundation: the design system as code *(this session)*
Design tokens (colour, type, spacing, radius, shadow, blur, motion) as CSS
custom properties + Tailwind theme; automatic dark mode; the UX-state
primitives (Skeleton, EmptyState, ErrorNotice) replacing placeholder text;
the motion vocabulary with the reduced-motion law; visible-focus states;
every existing screen swept onto the tokens. *Exit:* no raw palette
utility remains in a feature component; dark mode passes AA on every
screen; loop-walk E2E green; `docs/design/DESIGN_SYSTEM.md` is review law.

### Phase 2 — Experience: every screen to the bar
Screen-by-screen polish against Doc 06's moments: the queue's verdict-first
rhythm and the deliberate empty week; the brief's three reading depths made
typographic (above-the-fold verdict block); DNA document as the co-owned
artefact (category headers, provenance marks, revert surfaced — repaying
that debt); interview with amendable answers; micro-interactions for the
named effect (the correction visibly rippling — motion's one constitutional
job); keyboard shortcuts (j/k queue traversal, 1–6 chips, ⌘K later);
optimistic patterns audited; component tests for every screen. *Exit:* a
design partner walks the loop and nothing feels unfinished; frontend
component coverage covers every feature directory.

### Phase 3 — Authentication experience *(repays ADR-012, the GA gate)*
The hosted Supabase flow: sign-in/sign-up/magic link, session persistence
with silent refresh, "remember this device", sign-out everywhere (token
revocation), session-restoration UX. **Architecture now, biometrics later:**
the session layer is designed so the future iOS app adds Face ID/Touch ID
without backend change — Supabase refresh token held in iOS Keychain behind
`kSecAccessControlBiometryCurrentSet`, biometric unlock releases the stored
refresh token to mint a short-lived access token; the web app never sees
biometrics; revocation invalidates the refresh token family server-side;
passkeys slot in as a Supabase auth method when adopted. Documented as
`docs/design/AUTH_ARCHITECTURE.md` + an ADR superseding 012. *Exit:* a
design partner signs up unassisted; ADR-012's fence is demolished.

### Phase 4 — The marketing website
A separate static site (`website/`, Astro or plain Vite — decided by ADR),
sharing the design tokens: narrative hero (the employee, not the tool),
product storytelling in the brief's own typography, an interactive
receipt-table demo (real component, canned data), pricing (one plan,
founding rate), security page (the receipt rule, rings, RLS, departure
rule — our actual posture, which *is* the trust section), FAQ, contact.
Restrained atmosphere per §2's rulings. *Exit:* Lighthouse ≥95 across the
board; reads like Stripe, loads like Vercel.

### Phase 5 — Brand & marketing assets
`docs/brand/` codifying what Docs 02/06 already imply: voice and
copywriting rules (the banned register included), logotype and icon usage,
illustration stance (abstract, evidentiary, never mascots), motion
language, screenshot standards; then the asset kit — demo flow script, VSL
structure honouring the honesty rules, launch/social templates, email
templates matching the weekly brief's plain-text calm. *Exit:* a designer
or agency could produce on-brand material without a meeting.

### Phase 6 — iOS foundation *(plan, not app)*
`docs/design/IOS_FOUNDATION.md`: SwiftUI + The Composable Architecture or
vanilla MVVM (ADR), navigation mirroring the web's four surfaces, the
generated-from-OpenAPI contract layer (AP5 satisfied by construction — no
rule reimplementation), auth per Phase 3's architecture, offline as
read-cache-only (teaching writes require the server's named effect —
offline queueing of corrections would fake the ten-second contract),
push for the Monday queue and outcome prompts (finally giving that audit
row its surface), widgets (this week's count + confidence words), Live
Activity candidacy assessed honestly (weekly cadence probably doesn't
merit one), HIG review checklist. *Exit:* an iOS engineer could start
Monday without an architecture meeting.

## 5. Prioritisation logic

Foundation before decoration (tokens unblock every later screen); the auth
experience outranks the marketing site (a beautiful site funnelling into a
token-paste box is a broken promise); the site outranks brand-asset volume
(one great surface beats ten templates); iOS is a foundation document only
until the web app has earned its polish. Backend work in this phase is
limited to what experience requires (revert endpoint, auth/session
surface) — the V1 scope-control rules still bind.

## 6. Governance

Doc 06 §8 and §12 are review law for every PR in this phase; the Design
System doc is their executable form. Any new dependency (fonts, icons,
site framework) is argued in an ADR against the ten-year question (AP8).
Nothing ships that makes the product louder.
