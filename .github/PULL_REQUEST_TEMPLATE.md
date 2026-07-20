# What & why

<!-- One paragraph. Which document/ADR governs this change? -->

# Constitutional self-review (Doc 10 §1, principle 3 — actually performed)

- [ ] **AP2** — dependency direction holds; nothing new imports upward; `domain` stays pure
- [ ] **AP5** — no business logic entered the frontend (rules arrive from the API as data)
- [ ] **AP6** — AI calls (if any) live in `app/ai` pipelines with schemas, metering, eval hooks
- [ ] **Tenancy** — repositories remain workspace-scoped; new Ring-1 tables get RLS
- [ ] **Naming** — ubiquitous language only (`Workspace`, `Evidence`, `Recommendation`…)
- [ ] **API** — `/v1` changes are additive; internal endpoints stay out of the public schema
- [ ] **Migrations** — expand→migrate→contract; reversible or flagged with contraction plan
- [ ] **Tests** — required suites written; citable rules reference their document in test names
- [ ] **Docs** — package READMEs / ADRs / DEBT.md updated where touched

# High-risk touchpoints (full checklist mandatory regardless of scope — Doc 10 §8)

- [ ] Touches **money** (billing, Stripe)
- [ ] Touches **deletion** (customer data, retention)
- [ ] Touches **tenancy** (workspace scoping, RLS)
- [ ] Touches **prompts** (requires golden regression run)
- [ ] None of the above
