# Golden fixtures

The golden dataset (Doc 04 §6, L1): hand-graded briefs and DNAs at the quality
bar, seeded from concierge-phase artefacts (Doc 09 §12), refreshed quarterly,
with a **held-out portion never used in development**.

Rules:

- Every AI-touching merge runs the golden regression suite; ship gates per
  Doc 04 §6 are enforced mechanically in CI once pipelines exist.
- Stale gold is a named failure mode — refresh status is reviewed monthly.
- Fixtures contain synthetic or public business information only (ADR-006);
  never customer data.

Empty until the concierge phase produces its first artefacts, by design.
