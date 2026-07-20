"""The brief-quality rubric's dimensions (Doc 04 §3).

Five dimensions, 0-4 each; the harness's nouns are first-class domain
vocabulary (Doc 08 §5). Epic 3 uses the dimensions to categorise the edit
log — every founder edit to machine-assisted output tagged by the dimension
it repaired, which is the QA-delta measurement operating from the first
brief (Doc 07 §3). Scoring machinery arrives with the harness epics.
"""

from dataclasses import dataclass
from enum import StrEnum

from app.domain.rules import DomainRuleViolation


class RubricDimension(StrEnum):
    ACCURACY = "accuracy"
    EVIDENCE = "evidence"
    INSIGHT = "insight"
    FIT_REASONING = "fit_reasoning"
    ACTIONABILITY = "actionability"


# ── The ship bar (Doc 04 §3) ─────────────────────────────────────────────────

SHIP_BAR_TOTAL = 16  # [calibrates] — total >= 16/20
SHIP_BAR_DIMENSION_FLOOR = 2  # no dimension below 2
DIMENSION_MAX = 4


@dataclass(frozen=True)
class RubricScore:
    """One grading of one brief, 0-4 per dimension. An Accuracy zero zeroes
    the brief (fabrication/misattribution is an automatic fail)."""

    accuracy: int
    evidence: int
    insight: int
    fit_reasoning: int
    actionability: int

    def __post_init__(self) -> None:
        for name, value in self.by_dimension().items():
            if not 0 <= value <= DIMENSION_MAX:
                raise DomainRuleViolation(f"{name} must be within 0-4, got {value}")

    def by_dimension(self) -> dict[str, int]:
        return {
            RubricDimension.ACCURACY.value: self.accuracy,
            RubricDimension.EVIDENCE.value: self.evidence,
            RubricDimension.INSIGHT.value: self.insight,
            RubricDimension.FIT_REASONING.value: self.fit_reasoning,
            RubricDimension.ACTIONABILITY.value: self.actionability,
        }

    @property
    def total(self) -> int:
        return sum(self.by_dimension().values())

    @property
    def meets_ship_bar(self) -> bool:
        """Total >= 16/20 with no dimension below 2 — and a zero on Accuracy
        zeroes the brief regardless (Doc 04 §3)."""
        if self.accuracy == 0:
            return False
        return self.total >= SHIP_BAR_TOTAL and all(
            value >= SHIP_BAR_DIMENSION_FLOOR for value in self.by_dimension().values()
        )
