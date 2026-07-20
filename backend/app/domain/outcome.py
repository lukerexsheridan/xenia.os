"""Outcome — ground truth: what actually happened with a pursued prospect.

Append-only and **never inferred** (Doc 03 §8: Xenia prompts, never assumes —
a guessed outcome would poison ground truth). Structurally: `recorded_by` is
a human User id and the type has no machine-author affordance at all; the
dataclass is frozen and no revision operation exists. The scarcest, most
valuable object in the system (Doc 03 §7) — the flywheel's title deeds.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class OutcomeKind(StrEnum):
    """The C7 vocabulary (Doc 03): contacted → replied → meeting → won/lost/
    disqualified."""

    CONTACTED = "contacted"
    REPLIED = "replied"
    MEETING = "meeting"
    WON = "won"
    LOST = "lost"
    DISQUALIFIED = "disqualified"


@dataclass(frozen=True)
class Outcome:
    id: UUID
    workspace_id: UUID
    prospect_id: UUID
    kind: OutcomeKind
    occurred_at: datetime
    recorded_by: UUID  # always a human user — outcome truth is theirs alone
    recorded_at: datetime
    reason: str | None = None  # the optional why (Doc 03 §7)
