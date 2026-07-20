"""Correction — the highest-intent routine teaching signal (Doc 04 §5).

A correction targets an element — an evidence item, a score factor, or a DNA
element (Doc 08 §5) — and is applied first, never argued with at the point of
teaching (Doc 06 §6). The named-effect computation it triggers is Epic 8's
work; the shape records the teaching itself.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class CorrectionTargetKind(StrEnum):
    EVIDENCE_ITEM = "evidence_item"
    SCORE_FACTOR = "score_factor"
    DNA_ELEMENT = "dna_element"


@dataclass(frozen=True)
class Correction:
    id: UUID
    workspace_id: UUID
    target_kind: CorrectionTargetKind
    target_id: UUID
    reason: str | None  # chips arrive with the ratified taxonomy (Doc 10 §12)
    corrected_by: UUID  # corrections carry their author (Doc 08 §5)
    corrected_at: datetime
