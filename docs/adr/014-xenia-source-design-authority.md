# ADR-014: xenia-source is the design source of truth

Status: Accepted
Date: 2026-07-21

## Context

The founder supplied the actual Xenia landing page (`xenia-source/`, PRD in
`xenia-source/memory/PRD.md`) with a **locked** design system: deep-space
black (`#030305`) with elevated charcoals, white/muted/faint foregrounds on
white-alpha hairlines, the royal-blue signature family (`#3a5cff` /
`#4c6cff` / `#1e3ad9` with soft and glow alphas), glass surfaces
(24–28px blur, saturated, inset-highlighted), Cabinet Grotesk display ·
IBM Plex Sans body · JetBrains Mono uppercase labels, density as a
principle, and the black-hole brand mark living everywhere. The directive:
base all UX and UI decisions on it.

This supersedes the interim warm-paper/serif system this repo derived in
V1.1 Phase 1, and the Doc 11 §2 rulings that confined glass and refused
gradients — those rulings existed precisely because the design language
was a pending founder decision (Doc 06 §14). It is now decided.

## Decision

1. `xenia-source/` is committed as reference material (its `.env` files,
   which carry live secrets, are gitignored) and is the design authority
   for the product and the site. `docs/design/DESIGN_SYSTEM.md` is
   re-derived from its tokens; the app re-skins to match.
2. **Dark-first, single theme** (`color-scheme: dark`), per the source.
   The light theme is retired until the brand defines one.
3. Glass, the royal gradient CTA, ambient royal washes, and the mono-label
   register are adopted as the product's own language — the XeniaOS frame
   in the source is the direct reference for application chrome.
4. **What does not travel:** the demo's fictional modules (Campaigns,
   Email sending, Pipeline, bulk Leads/Contacts) are marketing-demo
   surface only — Foundation N1, the never-automatic floor, and the V1
   ontology still govern real capabilities absolutely. Adopting the skin
   ratifies zero new features.
5. **Floors retained regardless of skin:** WCAG AA contrast (muted
   foregrounds are checked against the deep blacks), visible focus (royal
   ring), the reduced-motion law (present in the source, kept global),
   and motion-explains (M10) — the app takes the OS frame's restraint,
   not the landing hero's theatre (splash, cursor trail, ambient audio,
   grain remain marketing-surface only).

## Consequences

- Fonts load from Fontshare/Google CDNs as the source does; self-hosting
  is recorded in DEBT.md as a pre-GA task (privacy + latency).
- The brief's "typeset memo" voice is now carried by Cabinet Grotesk
  display + Plex reading text rather than a serif; Doc 06's *hierarchy
  through typography* principle is unchanged in force.
- The screens harness continues to run; light-scheme captures now render
  the single dark theme by design.
