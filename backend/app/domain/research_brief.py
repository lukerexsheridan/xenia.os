"""ResearchBrief — the analyst's note, B1-B8 (Docs 04 §3, 08 §5).

The composed artefact: eight sections in a designed reading order, each claim
linked to Evidence, the couldn't-see declaration mandatory (declared
blindness is the cheapest trust-builder we own), overall confidence assigned
by the banding rule — never by a model — and a format version so quality
metrics compare like with like (Doc 07's revision loop).

At the workbench stage (Epic 3) the sections are authored by the founder;
the completeness rule below is the structural floor every brief must clear
before it is finalised. The full L0 validator battery (citation binding,
vocabulary, entity-consistency) arrives with machine composition in Epic 7.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.domain.confidence import ConfidenceBand, band_for


class BriefSectionCode(StrEnum):
    """B1-B8, verbatim from Doc 04 §3 — designed as a reading order."""

    B1_IDENTITY_SNAPSHOT = "b1_identity_snapshot"
    B2_WHAT_THEY_DO = "b2_what_they_do"
    B3_TRAJECTORY = "b3_trajectory"
    B4_MARKETING_GAP = "b4_marketing_gap"
    B5_FIT_THESIS = "b5_fit_thesis"
    B6_COUNTER_EVIDENCE = "b6_counter_evidence"
    B7_SUGGESTED_APPROACH = "b7_suggested_approach"
    B8_CONFIDENCE_FRESHNESS = "b8_confidence_freshness"


SECTION_TITLES: dict[BriefSectionCode, str] = {
    BriefSectionCode.B1_IDENTITY_SNAPSHOT: "Identity & snapshot",
    BriefSectionCode.B2_WHAT_THEY_DO: "What they do and for whom",
    BriefSectionCode.B3_TRAJECTORY: "Trajectory",
    BriefSectionCode.B4_MARKETING_GAP: "Marketing state & gap analysis",
    BriefSectionCode.B5_FIT_THESIS: "Fit thesis",
    BriefSectionCode.B6_COUNTER_EVIDENCE: "Counter-evidence & risks",
    BriefSectionCode.B7_SUGGESTED_APPROACH: "Suggested approach",
    BriefSectionCode.B8_CONFIDENCE_FRESHNESS: "Confidence & freshness",
}


@dataclass(frozen=True)
class BriefSection:
    code: BriefSectionCode
    content: str
    cited_evidence_ids: tuple[UUID, ...]


@dataclass(frozen=True)
class ResearchBrief:
    id: UUID
    workspace_id: UUID
    prospect_id: UUID
    format_version: int  # astonishment scores compare across versions (Doc 07)
    sections: tuple[BriefSection, ...]
    couldnt_see: tuple[str, ...]  # the mandatory declared-blindness list (B8 bar)
    confidence_score: float
    created_at: datetime

    @property
    def confidence_band(self) -> ConfidenceBand:
        """The four-word vocabulary, assigned by domain rule (Doc 06 §5)."""
        return band_for(self.confidence_score)

    def cited_evidence_ids(self) -> tuple[UUID, ...]:
        """Every evidence id any section cites, deduplicated, order-stable."""
        seen: dict[UUID, None] = {}
        for section in self.sections:
            for evidence_id in section.cited_evidence_ids:
                seen.setdefault(evidence_id, None)
        return tuple(seen)


def completeness_problems(brief: ResearchBrief) -> tuple[str, ...]:
    """The structural floor (Doc 04 §3): B1-B8 each present exactly once and
    non-empty; the couldn't-see declaration present. A brief failing any of
    these cannot be finalised — regardless of other merit."""
    problems: list[str] = []
    present = [section.code for section in brief.sections]
    for code in BriefSectionCode:
        count = present.count(code)
        if count == 0:
            problems.append(f"missing section {code.value}")
        elif count > 1:
            problems.append(f"duplicate section {code.value}")
    for section in brief.sections:
        if not section.content.strip():
            problems.append(f"empty section {section.code.value}")
    if not any(entry.strip() for entry in brief.couldnt_see):
        problems.append("the couldn't-see declaration is mandatory (Doc 04 §3, B8)")
    return tuple(problems)
