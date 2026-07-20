"""ResearchBrief persistence + the edit log — Ring 1, workspace-scoped.

A brief is draft until finalisation freezes its receipt table and derivation
record (Doc 09 §6); the edit log (the QA-delta measurement, Doc 07 §3) is
append-only like the audit stream.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select

from app.domain.evidence import EvidenceType, ReceiptRow
from app.domain.research_brief import BriefSection, BriefSectionCode, ResearchBrief
from app.domain.rubric import RubricDimension
from app.repositories.base import WorkspaceScopedRepository
from app.repositories.orm import EditLogEntryRow, ResearchBriefRow


class BriefStatus(StrEnum):
    DRAFT = "draft"
    FINAL = "final"


def _section_to_json(section: BriefSection) -> dict[str, Any]:
    return {
        "code": section.code.value,
        "content": section.content,
        "cited_evidence_ids": [str(item) for item in section.cited_evidence_ids],
    }


def _section_from_json(payload: dict[str, Any]) -> BriefSection:
    return BriefSection(
        code=BriefSectionCode(payload["code"]),
        content=payload["content"],
        cited_evidence_ids=tuple(UUID(item) for item in payload["cited_evidence_ids"]),
    )


def _receipt_row_to_json(row: ReceiptRow) -> dict[str, Any]:
    return {
        "number": row.number,
        "evidence_id": str(row.evidence_id),
        "claim": row.claim,
        "evidence_type": row.evidence_type.value,
        "observed_at": row.observed_at.isoformat(),
        "extraction_confidence": row.extraction_confidence,
    }


def _receipt_row_from_json(payload: dict[str, Any]) -> ReceiptRow:
    return ReceiptRow(
        number=payload["number"],
        evidence_id=UUID(payload["evidence_id"]),
        claim=payload["claim"],
        evidence_type=EvidenceType(payload["evidence_type"]),
        observed_at=datetime.fromisoformat(payload["observed_at"]),
        extraction_confidence=payload["extraction_confidence"],
    )


def _to_domain(row: ResearchBriefRow) -> ResearchBrief:
    return ResearchBrief(
        id=row.id,
        workspace_id=row.workspace_id,
        prospect_id=row.prospect_id,
        format_version=row.format_version,
        sections=tuple(_section_from_json(item) for item in row.sections),
        couldnt_see=tuple(row.couldnt_see),
        confidence_score=row.confidence_score,
        created_at=row.created_at,
    )


class StoredResearchBrief:
    """The brief plus its persistence lifecycle and frozen artefacts."""

    def __init__(self, row: ResearchBriefRow) -> None:
        self.brief = _to_domain(row)
        self.status = BriefStatus(row.status)
        self.receipt_table = (
            tuple(_receipt_row_from_json(item) for item in row.receipt_table)
            if row.receipt_table is not None
            else None
        )
        self.derivation: dict[str, Any] | None = row.derivation
        self.finalised_at = row.finalised_at


class SqlResearchBriefRepo(WorkspaceScopedRepository):
    def add(self, brief: ResearchBrief) -> StoredResearchBrief:
        row = ResearchBriefRow(
            id=brief.id,
            workspace_id=self._workspace_id,
            prospect_id=brief.prospect_id,
            format_version=brief.format_version,
            status=BriefStatus.DRAFT.value,
            sections=[_section_to_json(section) for section in brief.sections],
            couldnt_see=list(brief.couldnt_see),
            confidence_score=brief.confidence_score,
        )
        self._session.add(row)
        self._session.flush()
        return StoredResearchBrief(row)

    def get(self, brief_id: UUID) -> StoredResearchBrief | None:
        row = self._row(brief_id)
        return StoredResearchBrief(row) if row else None

    def update_content(self, brief: ResearchBrief) -> StoredResearchBrief:
        row = self._require_row(brief.id)
        row.sections = [_section_to_json(section) for section in brief.sections]
        row.couldnt_see = list(brief.couldnt_see)
        row.confidence_score = brief.confidence_score
        self._session.flush()
        return StoredResearchBrief(row)

    def finalise(
        self,
        brief_id: UUID,
        *,
        receipt_table: tuple[ReceiptRow, ...],
        derivation: dict[str, Any],
        finalised_at: datetime,
    ) -> StoredResearchBrief:
        row = self._require_row(brief_id)
        row.status = BriefStatus.FINAL.value
        row.receipt_table = [_receipt_row_to_json(item) for item in receipt_table]
        row.derivation = derivation
        row.finalised_at = finalised_at
        self._session.flush()
        return StoredResearchBrief(row)

    def add_edit(self, brief_id: UUID, *, dimension: RubricDimension, note: str) -> UUID:
        row = EditLogEntryRow(
            id=uuid4(),
            workspace_id=self._workspace_id,
            brief_id=brief_id,
            rubric_dimension=dimension.value,
            note=note,
        )
        self._session.add(row)
        self._session.flush()
        return row.id

    def list_edits(self, brief_id: UUID) -> list[tuple[RubricDimension, str]]:
        rows = self._session.execute(
            select(EditLogEntryRow)
            .where(
                EditLogEntryRow.workspace_id == self._workspace_id,
                EditLogEntryRow.brief_id == brief_id,
            )
            .order_by(EditLogEntryRow.created_at, EditLogEntryRow.id)
        ).scalars()
        return [(RubricDimension(row.rubric_dimension), row.note) for row in rows]

    def _row(self, brief_id: UUID) -> ResearchBriefRow | None:
        row = self._session.get(ResearchBriefRow, brief_id)
        if row is None or row.workspace_id != self._workspace_id:
            return None
        return row

    def _require_row(self, brief_id: UUID) -> ResearchBriefRow:
        row = self._row(brief_id)
        if row is None:
            raise LookupError(f"no research brief {brief_id} in this workspace")
        return row
