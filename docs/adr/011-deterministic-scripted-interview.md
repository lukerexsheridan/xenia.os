# ADR-011: Deterministic scripted interview at alpha

Status: Accepted
Date: 2026-07-20

## Context

Doc 03 C1 describes the DNA interview as "AI-led, conversational". Epic 10
shipped a fixed five-question script (`app/domain/interview.py`):
conversational in shape, resumable, homework-first — but deterministic, with
the customer's answers becoming the founding DNA verbatim.

## Decision

Keep the deterministic script for the design-partner alpha. The AI
Philosophy (CLAUDE.md) prefers deterministic software wherever possible;
onboarding is the single highest-stakes trust moment, and a model
paraphrasing a founder's own targeting into the founding DNA risks
misstating it at the exact point the endorsement moment is supposed to
create a shared agreement. Verbatim answers are maximally N4-compliant.

## Consequences

- The interview cannot probe or follow up; rambling answers become rambling
  elements. Mitigation: the correction loop is the editor.
- An AI distillation step (assistive, shown side-by-side with the verbatim
  answer, customer picks) is the intended upgrade path, gated on concierge
  feedback — not on this ADR.
- One-per-line answers are bounded (20 elements) to keep paste accidents
  from flooding the DNA with laws.
