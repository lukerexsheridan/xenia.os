"""The golden set — curated exemplar briefs for regression (Doc 04 §6).

Golden entries are the evaluation harness's ground truth: briefs the Editor
has judged exemplary, frozen with a note on why. The membership rule is the
module's one law: only an approved (FINAL) brief may enter — an exemplar
that never passed the gate would calibrate the harness against unapproved
work. Evaluation objects observe the customer's world without entering it
(Doc 08 §5): an entry references a brief, it never copies or alters one.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.rules import DomainRuleViolation


@dataclass(frozen=True)
class GoldenSetEntry:
    id: UUID
    workspace_id: UUID
    brief_id: UUID
    note: str  # why this brief is exemplary — curation carries its reasoning
    added_by_subject: str  # the Editor who signed it in
    added_at: datetime

    def __post_init__(self) -> None:
        if not self.note.strip():
            raise DomainRuleViolation(
                "a golden entry carries its reasoning — an unexplained exemplar "
                "teaches the harness nothing (Doc 04 §6)"
            )


def require_approved(status_value: str) -> None:
    """The membership law: only gate-approved work calibrates the harness."""
    if status_value != "final":
        raise DomainRuleViolation(
            "only an approved (final) brief may enter the golden set (Doc 04 §6)"
        )
