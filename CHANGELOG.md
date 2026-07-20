# Changelog

Format: keep-a-changelog-ish; one entry per released state, newest first.

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
