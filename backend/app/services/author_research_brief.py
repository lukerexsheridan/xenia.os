"""The brief-authoring use-cases: create, revise, finalise (Doc 10, Sprint 6).

At the concierge stage the founder authors sections; finalisation is the
moment the constitution bites: the structural floor must be clear (B1-B8
present, couldn't-see declared — Doc 04 §3), every cited receipt must
resolve to real Evidence, and the frozen receipt table plus the derivation
record are written so the brief is replayable (Doc 09 §6). A final brief is
never edited — regeneration is a new brief.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.core.errors import ConflictError, NotFoundError, XeniaError
from app.domain.audit import AuditAction, AuditEntryRepo
from app.domain.evidence import build_receipt_table
from app.domain.research_brief import (
    BriefSection,
    ResearchBrief,
    completeness_problems,
)
from app.repositories.evidence import SqlEvidenceRepo
from app.repositories.prospects import SqlProspectRepo
from app.repositories.research_briefs import (
    BriefStatus,
    SqlResearchBriefRepo,
    StoredResearchBrief,
)

# The concierge format starts at 1; revised weekly from feedback with each
# version logged so astonishment scores compare across versions (Doc 07 §3).
CURRENT_FORMAT_VERSION = 1


class CreateResearchBrief:
    def __init__(self, brief_repo: SqlResearchBriefRepo, prospect_repo: SqlProspectRepo) -> None:
        self._brief_repo = brief_repo
        self._prospect_repo = prospect_repo

    def execute(
        self,
        *,
        workspace_id: UUID,
        prospect_id: UUID,
        sections: list[BriefSection],
        couldnt_see: list[str],
        confidence_score: float,
    ) -> StoredResearchBrief:
        if self._prospect_repo.get(prospect_id) is None:
            raise NotFoundError("prospect not found in this workspace")
        brief = ResearchBrief(
            id=uuid4(),
            workspace_id=workspace_id,
            prospect_id=prospect_id,
            format_version=CURRENT_FORMAT_VERSION,
            sections=tuple(sections),
            couldnt_see=tuple(couldnt_see),
            confidence_score=confidence_score,
            created_at=datetime.now(UTC),
        )
        return self._brief_repo.add(brief)


class UpdateBriefSection:
    def __init__(self, brief_repo: SqlResearchBriefRepo) -> None:
        self._brief_repo = brief_repo

    def execute(self, *, brief_id: UUID, section: BriefSection) -> StoredResearchBrief:
        stored = _require_draft(self._brief_repo, brief_id)
        others = tuple(
            existing for existing in stored.brief.sections if existing.code is not section.code
        )
        revised = ResearchBrief(
            id=stored.brief.id,
            workspace_id=stored.brief.workspace_id,
            prospect_id=stored.brief.prospect_id,
            format_version=stored.brief.format_version,
            sections=(*others, section),
            couldnt_see=stored.brief.couldnt_see,
            confidence_score=stored.brief.confidence_score,
            created_at=stored.brief.created_at,
        )
        return self._brief_repo.update_content(revised)


class FinaliseResearchBrief:
    def __init__(
        self,
        brief_repo: SqlResearchBriefRepo,
        evidence_repo: SqlEvidenceRepo,
        audit_repo: AuditEntryRepo,
    ) -> None:
        self._brief_repo = brief_repo
        self._evidence_repo = evidence_repo
        self._audit_repo = audit_repo

    def execute(
        self, *, brief_id: UUID, finalised_by: str, request_id: str | None = None
    ) -> StoredResearchBrief:
        stored = _require_draft(self._brief_repo, brief_id)
        brief = stored.brief

        problems = completeness_problems(brief)
        if problems:
            raise XeniaError("brief is not complete: " + "; ".join(problems))

        cited_ids = brief.cited_evidence_ids()
        cited_evidence = self._evidence_repo.get_many(cited_ids)
        missing = set(cited_ids) - {item.id for item in cited_evidence}
        if missing:
            # No receipt, no claim (Doc 05 §3) — a citation must resolve.
            raise XeniaError(
                f"cited evidence does not resolve: {sorted(str(item) for item in missing)}"
            )

        receipt_table = build_receipt_table(cited_evidence)
        finalised_at = datetime.now(UTC)
        derivation = {
            "format_version": brief.format_version,
            "receipt_table_evidence_ids": [str(row.evidence_id) for row in receipt_table],
            "couldnt_see_count": len(brief.couldnt_see),
            "edit_log_entries": len(self._brief_repo.list_edits(brief_id)),
            "finalised_by": finalised_by,
            "finalised_at": finalised_at.isoformat(),
            "produced_by": "workbench-concierge/1",
        }
        result = self._brief_repo.finalise(
            brief_id,
            receipt_table=receipt_table,
            derivation=derivation,
            finalised_at=finalised_at,
        )
        self._audit_repo.append(
            action=AuditAction.RESEARCH_BRIEF_FINALISED,
            target_type="research_brief",
            target_id=str(brief_id),
            actor_user_id=None,
            request_id=request_id,
        )
        return result


def _require_draft(brief_repo: SqlResearchBriefRepo, brief_id: UUID) -> StoredResearchBrief:
    stored = brief_repo.get(brief_id)
    if stored is None:
        raise NotFoundError("research brief not found in this workspace")
    if stored.status is not BriefStatus.DRAFT:
        raise ConflictError("a final brief is never edited — regeneration is a new brief")
    return stored
