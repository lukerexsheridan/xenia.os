"""Decision — the founder's response to a Recommendation (Doc 08 §5).

Accept, decline, or pursue, with an optional reason — the teaching event.
The reason vocabulary (the chip taxonomy) is a research-phase output ratified
at Sprint 15 (Doc 10 §12); until then reasons are free text. The
Recommendation object itself arrives with Epic 8; a Decision references it
by id.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class DecisionKind(StrEnum):
    ACCEPT = "accept"
    DECLINE = "decline"
    PURSUE = "pursue"


@dataclass(frozen=True)
class Decision:
    id: UUID
    workspace_id: UUID
    recommendation_id: UUID
    kind: DecisionKind
    reason: str | None  # decline-with-reason is the teaching gold (Doc 04 §5)
    decided_by: UUID  # attribution: who taught what (Doc 08 §5)
    decided_at: datetime
