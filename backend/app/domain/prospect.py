"""Prospect — a verified business entity in relationship to one workspace.

Ring 1: distinct from the Ring-2 BusinessRecord (the world's facts); a
Prospect *references* a BusinessRecord and adds everything relational
(Doc 08 §5). A Prospect is itself a claim — "this name, this domain, this
register entry are one company" — carried with binding confidence (the
misattribution defence).

Deliberately absent, forever at V1: deal semantics. No value, no stage, no
probability — that is the refused pipeline board (Doc 03 §5/§7); Xenia tracks
outcomes as learning data, not deals as workflow objects.
"""

from dataclasses import dataclass, replace
from datetime import datetime
from enum import IntEnum
from uuid import UUID

from app.domain.rules import DomainRuleViolation


class ProspectStatus(IntEnum):
    """The lifecycle (Doc 08 §5): surfaced → recommended → pursued → resolved.
    Forward-only — a relationship's history never rewinds."""

    SURFACED = 1
    RECOMMENDED = 2
    PURSUED = 3
    RESOLVED = 4


@dataclass(frozen=True)
class Prospect:
    id: UUID
    workspace_id: UUID
    business_record_id: UUID
    binding_confidence: float  # confidence that the identity claim holds
    status: ProspectStatus
    surfaced_at: datetime

    def __post_init__(self) -> None:
        if not 0.0 <= self.binding_confidence <= 1.0:
            raise DomainRuleViolation(
                f"binding confidence must be within [0, 1], got {self.binding_confidence}"
            )

    def advance(self, to: ProspectStatus) -> "Prospect":
        if to <= self.status:
            raise DomainRuleViolation(
                f"lifecycle is forward-only: cannot move from "
                f"{self.status.name.lower()} to {to.name.lower()}"
            )
        return replace(self, status=to)
