# Xenia — Product-first AI OS for modern agencies

## Original problem statement
Xenia is an AI-native lead-generation platform for modern agencies. **PIVOT (2026-02-21)**: the landing page shifts entirely from a cinematic scroll-driven 3D unveiling to a product-first flagship-store experience. The interactive XeniaOS is the hero. The black hole becomes Xenia's permanent, timeless brand mark (nav logo, splash, loading, AI processing indicator).

## Design principles (locked)
- **Product first.** Every animation supports the product; nothing competes with it.
- **Density.** Reduce whitespace; components sit close together; premium and minimalist, never sparse.
- **Colour system.** Deep black · charcoal · white · glass transparency, with **royal blue** (`#3a5cff`) as the signature accent — used sparingly on active nav, primary CTAs, hover/selected states, charts, AI highlights, progress fills, glowing edges.
- **Brand mark.** A Gargantua-style photoreal black hole (`BlackHoleMark`) lives everywhere: top-left of the floating glass nav, splash, page-transition placeholder, AI processing indicator inside the OS.
- **Floating glass nav** is preserved.

## Architecture
- **Frontend**: React 19 · React Router · framer-motion · Lenis · Tailwind + custom CSS · Sonner toasts · Craco `@` alias. NO more @react-three/fiber on the landing page.
- **Backend**: FastAPI + MongoDB. `access_requests` collection. `POST /api/email/generate` streams Claude Sonnet 4.6 via `emergentintegrations` (SSE).

## Brand mark — BlackHoleMark
`/app/frontend/src/components/BlackHoleMark.{jsx,css}` — pure CSS/SVG so it renders identically at any scale (18px topbar → 200px splash) with negligible cost. Layers back→front:
1. Warm ambient halo (bloom)
2. Near edge-on accretion disc — warm conic gradient extending beyond bounds for horizontal streaks; slow rotation
3. Faster inner streak layer for density
4. Gravitationally-lensed arch — untilted warm ring showing the disc curving over/under the horizon (the signature "vertical arch")
5. Photon ring — razor-thin bright edge hugging the event horizon
6. Event horizon — perfect black core
Fixed 8° axial tilt so it reads as a real, oriented object.

## Layout (`Experience.jsx`)
- **SplashLoader** (1.2s black hole reveal) → **Nav** (floating glass with BlackHoleMark) → **ProductHero** (compact headline + live XeniaOS) → **ValueStrip** (3 dense cards) → **RequestAccess** (tightened) → **Footer** (condensed).
- Fixed ambient royal-blue backdrop + subtle CSS star field replaces the old fullscreen R3F scene.
- CursorTrail + AmbientAudio retained.

## Interactive product — XeniaOS (`/app/frontend/src/os/`)
Unchanged features but re-styled with royal blue: active sidebar item now has a `linear-gradient(90deg, rgba(76,108,255,.18) → transparent)` background with a 2px blue left rail; `.os-cta` is a royal-blue gradient pill; `.os-bar-fill` is a royal-blue progress bar with glow.
- 18 modules (Dashboard, Leads, Companies, Contacts, AI Research, Buying Signals, Campaigns, Email Writer, AI Chat, Tasks, Pipeline, Analytics, Reports, Team, Integrations, Notifications, Activity, Settings)
- ⌘K command palette · Company detail side panel with "Draft outreach" deep-link
- Email Writer streams real Claude Sonnet 4.6; BlackHoleMark spins as the AI processing indicator

## Endpoints
- `GET  /api/` — health
- `POST /api/access` `{ email, role?, company? }` — idempotent lead capture
- `GET  /api/access` — list
- `POST /api/email/generate` — SSE stream (Claude Sonnet 4.6 via emergentintegrations)

## Changelog
- **2026-02-20** — Initial cinematic 3D unveiling (Aperture, then Cosmic Reverse-Evolution)
- **2026-02-21** — **Direction pivot**: product-first landing. Removed the fullscreen R3F scene and the 6-act scroll narrative. Introduced royal blue tokens. Created `BlackHoleMark` + `SplashLoader` + `ProductHero` + `ValueStrip`. Rewired Nav/Footer/Sidebar/EmailWriter/RequestAccess. Testing agent (iteration 3): backend 5/5, frontend all flows green.
- **2026-02-21 (later)** — BlackHoleMark visual upgrade to Gargantua-style: warm cream/gold conic-gradient disc extending as horizontal streaks + gravitationally-lensed vertical arch wrapping the horizon + brighter photon ring + fixed 8° axial tilt + slow spin.
- **2026-02-21 (final)** — Shipped four requested features. Iteration 4: backend 12/12 pytest, frontend 100% acceptance.
  1. **AI Chat Live** — `POST /api/chat/stream` (Claude Sonnet 4.6 via emergentintegrations LlmChat, SSE). Multi-turn context via stable `session_id` stored in localStorage.
  2. **Loading Transitions** — `ModuleTransition.jsx` overlay flashes the BlackHoleMark + module label whenever `activeModule` changes; ~520ms in/out.
  3. **Waitlist Dashboard** — `/admin` route with single-password gate (`ADMIN_PASSWORD` env + PyJWT HS256, 24h TTL). Table + refresh + logout.
  4. **OS Memory** — `OSContext` persists `{activeModule, paletteRecents}` to localStorage; palette shows "Recents" section on empty query.

- **2026-02-21 (v5)** — Shipped three follow-up features. Iteration 5: backend 12/12 pytest regression pass, frontend all acceptance checks, zero bugs.
  1. **Route Transitions** — full-page BlackHoleMark overlay on pathname change.
  2. **CSV Export** — one-click download from Admin dashboard.
  3. **Chat Memory Panel** — entity + topic sidebar in AI Chat.

- **2026-02-21 (v6)** — Shipped three more follow-up features. Iteration 6: backend 15/15 pytest, frontend all flows green, zero bugs.
  1. **Faster Logo Spin** — BlackHoleMark disc rotation reduced from 14s/9s to 7s/4.5s, `rotateX` lifted from 78° to 72° so the streaming accretion pattern is visibly animated at every scale.
  2. **Memory Highlights** — new `POST /api/chat/summarise` (fresh LlmChat session with a summarisation system prompt, Claude Sonnet 4.6, non-streaming JSON response). `MemorySummary.jsx` inside the AI Chat memory sidebar with a royal-blue "Summarise session" button, Copy/Share/Regenerate actions, and a spinning BlackHoleMark loader.
  3. **Palette Autopilot** — new `os/paletteAutopilot.js` interpreter with five regex patterns (`draft outreach to X`, `signals from X`, `research X`, `call/meet X`, `open/show/view/go to X`). Matches against known companies, contacts, and modules and surfaces a prominent royal-blue action at the top of the ⌘K palette. Enter runs the autopilot, or the first filtered result when no autopilot matches. New `.kind-autopilot` style tokens in `os.css`.

## Backlog (P1)
- Rate-limit / lockout on admin login attempts (non-blocking suggestion from reviewer)
- Route-level transitions using SplashLoader between `/` and `/admin`
- Full a11y pass on the OS + Admin (focus rings on shadcn / royal-blue focus tokens)
- Real charts library on Analytics module (currently SVG on mock data)

## Backlog (P2)
- Multi-tenant workspace concept
- Pre-stream error surface in /api/chat/stream when the model key/permissions fail
- Optional export CSV of admin leads

## Test credentials
See `/app/memory/test_credentials.md`. Admin password: `xenia-admin-2026`.
