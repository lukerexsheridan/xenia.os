# Xenia Design System

*The executable form of Doc 06 §8. Tokens are law: a feature component
that reaches for a raw palette utility instead of a semantic token is a
review failure, exactly as hand-written fetch code outside the API client
is. Source of truth in code: `frontend/src/styles/globals.css`.*

## 1. Colour — ink, paper, one accent, semantic meaning

Two neutrals and one accent carry the whole interface; every additional
colour must *mean* something (confidence, risk) and never decorates.

| Token | Light | Dark | Role |
|---|---|---|---|
| `paper` | `#faf9f7` | `#141312` | The page. Warm, not clinical white / not dead black. |
| `surface` | `#ffffff` | `#1c1a18` | Cards, the typeset sheet. |
| `ink` | `#211e1a` | `#e9e6e0` | Primary text. Warm near-black — a document, not a terminal. |
| `ink-muted` | `#6d675e` | `#9d968b` | Secondary text. AA against its paper. |
| `ink-faint` | `#98918a` | `#6d675f` | Tertiary/metadata. AA-large only; never for reading text. |
| `hairline` | `#e6e2db` | `#2e2b27` | Borders. One weight; boxes never carry hierarchy. |
| `accent` | `#3a5bc7` | `#93aaf5` | The one accent: links, primary actions, focus. Stripe-authority blue, warmed. |
| `accent-ink` | `#ffffff` | `#10131f` | Text on accent. |

Semantic colour (meaning only, word always present — colour never sole
carrier):

| Token | Light bg/fg | Dark bg/fg | Meaning |
|---|---|---|---|
| `confident` | `#e7f2ec` / `#1d5c3f` | `#16241d` / `#84c7a3` | Confidence: confident |
| `likely` | `#e8f0f7` / `#1e4e79` | `#16202a` / `#8cb8dd` | Confidence: likely |
| `possible` | `#f7efe0` / `#755619` | `#262015` / `#d3b578` | Confidence: possible |
| `uncertain` | `#efedea` / `#5f594f` | `#232120` / `#a29a8f` | Confidence: uncertain |
| `danger` | `#f8ecea` / `#8c2f24` | `#271a18` / `#e09287` | Errors, hard lines, destructive intent |

All pairs meet WCAG AA for normal text against their own background and
against `paper`.

## 2. Typography — hierarchy through type, not chrome

- **Reading/display face:** `ui-serif, Georgia, Cambria, 'Times New Roman',
  serif` — the brief is a typeset memo; page titles, brief sections, DNA
  statements, and Xenia's longer voice moments are serif.
- **Interface face:** `ui-sans-serif, system-ui, -apple-system, sans-serif`
  — controls, metadata, tables. System stacks are a deliberate AP8 choice:
  zero payload, native rendering, revisit via ADR only if a licensed face
  earns its bytes.
- **Scale (rem):** 0.75 (meta) · 0.8125 (ui-small) · 0.9375 (ui) · 1.0625
  (reading, line-height 1.65) · 1.25 (section) · 1.5 (title) · 2.0 (display,
  marketing only). No font size outside the scale.
- Reading measure ≤ `65ch`. Numbers in tables `tabular-nums`.

## 3. Space, radius, elevation, blur

- **Spacing:** the 4px grid via Tailwind's default scale; sections breathe
  at 24–48px; density only where scanning demands it (queues, tables).
- **Radius:** `6px` controls · `10px` cards/sheets · `999px` chips. Nothing
  else.
- **Elevation:** two shadows only. `shadow-card` (barely-there lift for the
  sheet on paper) and `shadow-raised` (transient surfaces). Hierarchy is
  typographic; shadows whisper.
- **Blur (the entire glass budget):** `backdrop-blur` at one strength
  (12px) on *transient elevated surfaces only* — dialogs, palettes, sheets
  — over a translucent `surface`. Never on resting content. (Plan §2.)

## 4. Motion — explains, never performs

| Token | Value | Use |
|---|---|---|
| `--duration-fast` | 120ms | Hover, focus, chip press |
| `--duration-base` | 200ms | State changes: resolution replacing buttons, skeleton→content |
| `--duration-slow` | 320ms | Spatial: sheet entry, the named effect surfacing |
| `--ease-settle` | `cubic-bezier(0.2, 0, 0, 1)` | Everything entering or changing — fast start, settled end |
| `--ease-exit` | `cubic-bezier(0.4, 0, 1, 1)` | Everything leaving |

Laws: no bounce, no spring overshoot, no confetti, no looping attention
animation, no loading theatre. Motion communicates causality (the
correction's effect appearing; the card resolving) or it does not exist.
`prefers-reduced-motion: reduce` collapses all durations to 0 — globally,
in one rule, not per component.

## 5. UX states — every async surface, four states

Every data surface renders exactly one of: **skeleton** (shape-true
placeholders, `--duration-base` fade to content, no spinners anywhere),
**content**, **empty** (designed and in-voice — the empty week is
integrity, not failure), **error** (plain voice: what happened, whose
fault it isn't, what to do). Primitives: `<Skeleton>`, `<EmptyState>`,
`<ErrorNotice>` — feature components compose these, never re-invent them.

## 6. Focus & accessibility

- `:focus-visible` everywhere: 2px `accent` ring, 2px offset, never
  removed, never colour-only.
- AA contrast floor (checked in both themes); reading text targets AAA
  where the palette allows.
- Confidence words always rendered as text with `role="status"` and an
  accessible name; colour underlines, never carries.
- Hit targets ≥ 40px on touch surfaces; keyboard reachability is a
  release gate for every new interaction.

## 7. Dark mode

Automatic via `prefers-color-scheme` — no toggle at V1.1 (calm products
don't ask questions the OS already answered; a toggle is an ADR away if
partners ask). Both themes are first-class: every token defined in both,
every screen reviewed in both, AA in both. Dark is warm (brown-blacks, not
blue-blacks) — midnight reading, per the ICP, is the design case.

## 8. Iconography & illustration (Phase 2+)

One line-icon family (Lucide, via ADR when introduced), 1.5px stroke,
16/20px sizes, `ink-muted` default. No emoji in product UI. Illustration
stance: abstract and evidentiary (documents, threads, marks on paper) —
never mascots, never stock-3D. Until then: typography does the work.
