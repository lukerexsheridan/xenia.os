"""Decision — the founder's response to a Recommendation (Doc 08 §5).

Accept, decline, or pursue, with a one-tap reason chip and free text always
available, never required (Doc 06 §6 — the ten-second loop). The chip
taxonomy is ratified here per Doc 10 Sprint 15 as the launch teaching
vocabulary, together with what each chip may teach:

- pattern chips generalise into learned preferences only at the
  minimum-occurrence threshold ("third time — adjusting", Doc 04 §5);
- the structural chip (not-our-kind) travels the proposal road — a repeated
  "not our kind of client" smells like a missing disqualifier, and
  disqualifiers are proposed, never self-applied (Doc 03 §8);
- relationship and evidence chips teach the DNA nothing: "we know them" is
  a fact about this prospect, and "evidence is wrong" routes to the Editor
  (a quality event, not a preference).
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.domain.dna import DnaCategory


class DecisionKind(StrEnum):
    ACCEPT = "accept"
    DECLINE = "decline"
    PURSUE = "pursue"


class DeclineChip(StrEnum):
    """The reason chips, verbatim from Doc 06 §6 — the chips *are* the
    teaching vocabulary."""

    WRONG_INDUSTRY = "wrong_industry"
    TOO_SMALL = "too_small"
    BAD_TIMING = "bad_timing"
    WE_KNOW_THEM = "we_know_them"
    EVIDENCE_WRONG = "evidence_is_wrong"
    NOT_OUR_KIND = "not_our_kind_of_client"


# Pattern chips: the learned-preference blueprint each one generalises into
# once the pattern threshold is met. Statements are plain language, always
# customer-readable (N4), and narrate their own origin.
PATTERN_CHIP_LESSONS: dict[DeclineChip, tuple[DnaCategory, str]] = {
    DeclineChip.WRONG_INDUSTRY: (
        DnaCategory.BUSINESS_ATTRIBUTES,
        "Declines keep citing 'wrong industry' — narrowing the industries I surface",
    ),
    DeclineChip.TOO_SMALL: (
        DnaCategory.BUSINESS_ATTRIBUTES,
        "Declines keep citing 'too small' — weighting company scale higher",
    ),
    DeclineChip.BAD_TIMING: (
        DnaCategory.BUYING_SIGNALS,
        "Declines keep citing 'bad timing' — demanding fresher buying signals",
    ),
}

# The structural chip: repeated occurrences propose a disqualifier, applied
# only on endorsement (Doc 03 §8's human-in-the-loop zone).
STRUCTURAL_CHIPS = frozenset({DeclineChip.NOT_OUR_KIND})

# Chips that never touch the DNA (see the module charter).
NON_TEACHING_CHIPS = frozenset({DeclineChip.WE_KNOW_THEM, DeclineChip.EVIDENCE_WRONG})


@dataclass(frozen=True)
class Decision:
    id: UUID
    workspace_id: UUID
    recommendation_id: UUID
    kind: DecisionKind
    reason: str | None  # decline-with-reason is the teaching gold (Doc 04 §5)
    decided_by: UUID  # attribution: who taught what (Doc 08 §5)
    decided_at: datetime
    chip: DeclineChip | None = None  # one tap; free text stays in `reason`
