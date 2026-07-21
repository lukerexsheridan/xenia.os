# Xenia Design System

*Derived from `xenia-source/` — the founder-locked design authority
(ADR-014). Tokens are law: a feature component that reaches for a raw
palette utility instead of a semantic token is a review failure. Source of
truth in code: `frontend/src/styles/globals.css`; visual reference: the
XeniaOS frame in `xenia-source/frontend/src/os/`.*

## 1. Colour — deep space, white ink, one royal signature

Dark-first, single theme (`color-scheme: dark`). Two families carry the
interface — the blacks and the whites — plus the royal-blue signature used
sparingly, and semantic colour that always means something.

| Token | Value | Role |
|---|---|---|
| `paper` | `#030305` | The page. Deep space, not grey. |
| `surface` | `#0a0a0c` | Elevated panels. |
| `surface-2` | `#121216` | Second elevation, inputs, wells. |
| `panel` | `rgba(255,255,255,0.02)` | The card wash over paper (the os-card material). |
| `ink` | `#ffffff` | Primary text. |
| `ink-muted` | `#a1a1a8` | Secondary text. AA on the blacks. |
| `ink-faint` | `#666670` | Tertiary/metadata. Large/label use only. |
| `hairline` | `rgba(255,255,255,0.08)` | Borders at rest. |
| `hairline-hover` | `rgba(255,255,255,0.15)` | Borders under attention. |
| `royal` | `#3a5cff` | The signature. Active nav, primary CTAs, AI moments, progress. Sparingly. |
| `royal-bright` | `#4c6cff` | Gradient top, hover. |
| `royal-deep` | `#1e3ad9` | Gradient base. |
| `royal-soft` | `rgba(76,108,255,0.18)` | Selected/active fills. |
| `royal-glow` | `rgba(76,108,255,0.42)` | Glow shadows. Never on body text. |

Semantic colour (meaning only; the word is always present — colour never
sole carrier). Foregrounds AA against the blacks:

| Token | fg on dark | Meaning |
|---|---|---|
| `confident` | `#7fd0a5` on `rgba(60,190,120,0.10)` | Confidence: confident |
| `likely` | `#8fb7ff` on `rgba(76,108,255,0.12)` | Confidence: likely |
| `possible` | `#e0bd7d` on `rgba(220,170,80,0.10)` | Confidence: possible |
| `uncertain` | `#a1a1a8` on `rgba(255,255,255,0.06)` | Confidence: uncertain |
| `danger` | `#f09a8e` on `rgba(220,80,60,0.10)` | Errors, hard lines |

## 2. Typography — the three voices

- **Display:** Cabinet Grotesk 300, `-0.03em` — page titles, brief section
  headings, the hero register. Light weight is the premium signal.
- **Body:** IBM Plex Sans 300/400, `-0.005em` — reading text, controls.
  Reading text at `1.0625rem/1.65`, measure ≤ `65ch`.
- **Label:** JetBrains Mono, uppercase, `0.14em` tracking, 10.5–11px —
  metadata, category headers, week keys, the "RESEARCH BRIEF" register.
  The mono label is a brand signature; use it wherever the old system
  used small-caps meta.
- Loaded from Fontshare/Google per the source (self-hosting: DEBT, pre-GA).
- Scale (rem): 0.6875 mono-label · 0.8125 ui-small · 0.9375 ui · 1.0625
  reading · 1.25 section · 1.5 title · 2.25+ display (marketing).

## 3. Surfaces — glass, panels, hairlines

- **Glass** (`.glass` / `.glass-strong`): blur 24–28px + saturate(140%),
  white-alpha border, inset top highlight, deep shadow. Roles: application
  chrome (the frame, the topbar), transient surfaces (palette, dialogs,
  sheets). *Not* per-card — cards are **panels**.
- **Panel** (cards, list items): `panel` wash + `hairline` border +
  `radius-card`; hover raises border to `hairline-hover`. No per-card
  blur (GPU honesty), no per-card glow.
- **Royal glow** reserved for: the primary CTA, the active/AI moment, the
  OS frame's ambient. Never ambient on content.
- **Radius:** 8px controls/inputs · 12px cards/panels · 999px pills &
  chips (the CTA is a pill).
- **Ambient:** the shell may carry one subtle royal radial wash
  (`ambient-royal`, heavily dimmed) behind content. Vignette, grain, star
  field, splash, cursor trail: marketing surfaces only (ADR-014 §5).

## 4. Motion — explains, never performs (unchanged in law)

Durations 120/200/320ms; `--ease-settle: cubic-bezier(0.2,0,0,1)`;
settle-in entrances; the pulse-dot is the only permitted looping element
and only as a live/AI indicator (it is the heartbeat, not decoration).
`prefers-reduced-motion` collapses everything, globally. The black-hole
mark's slow disc rotation counts as the brand's one ambient motion and
respects the same law.

## 5. UX states, focus, accessibility (unchanged in law)

Four states per async surface (skeleton/content/empty/error) via the
shared primitives; skeletons breathe with white-alpha, never spin. Focus:
2px royal ring, visible always. AA floor on every fg/bg pair above;
`ink-faint` never carries reading text. Confidence words remain text with
`role="status"`. Hit targets ≥ 40px on touch.

## 6. The brand mark

`BlackHoleMark` (pure CSS/SVG, ported from the source) is the product
mark: topbar at 18–24px, loading and AI-processing moments at larger
sizes. It is never decorated further and never duplicated per-card.
