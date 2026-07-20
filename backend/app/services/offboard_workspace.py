"""OffboardWorkspace — the departure rule, exercised (Doc 10, Epic 12).

Leaving is a first-class act: the customer receives everything that is
theirs (a complete JSON export — their DNA and its history, their
relationships, their teaching, their briefs, their audit trail), and then
their Ring-1 world is deleted whole. Deletion rides the schema: every Ring-1
table cascades from the workspace row, so "provably gone" is a foreign-key
property, not a checklist. Ring-2 world facts remain — public facts belong
to nobody and were never theirs to take or ours to keep on their behalf
(Doc 05 §7).
"""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, XeniaError
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.dna import SqlDnaRepo, element_to_json
from app.repositories.interview import SqlInterviewRepo
from app.repositories.orm import RING_1_TABLES, WorkspaceRow
from app.repositories.prospects import SqlProspectRepo
from app.repositories.research_briefs import SqlResearchBriefRepo
from app.repositories.teaching import SqlTeachingRepo

EXPORT_FORMAT_VERSION = 1


@dataclass(frozen=True)
class DeletionReport:
    workspace_id: UUID
    rows_deleted_by_table: dict[str, int]


class OffboardWorkspace:
    def __init__(self, session: Session, workspace_id: UUID) -> None:
        self._session = session
        self._workspace_id = workspace_id

    def export(self) -> dict[str, Any]:
        """Everything that is theirs, in one readable bundle."""
        workspace = self._session.get(WorkspaceRow, self._workspace_id)
        if workspace is None:
            raise NotFoundError("workspace not found")
        dna_repo = SqlDnaRepo(self._session, self._workspace_id)
        prospect_repo = SqlProspectRepo(self._session, self._workspace_id)
        business_repo = SqlBusinessRecordRepo(self._session)
        brief_repo = SqlResearchBriefRepo(self._session, self._workspace_id)
        teaching_repo = SqlTeachingRepo(self._session, self._workspace_id)

        dna = dna_repo.get()
        prospects = prospect_repo.list()
        bundle: dict[str, Any] = {
            "export_format_version": EXPORT_FORMAT_VERSION,
            "workspace": {"id": str(workspace.id), "name": workspace.name},
            "interview_transcript": SqlInterviewRepo(
                self._session, self._workspace_id
            ).get_answers(),
            "dna": None,
            "dna_changelog": [],
            "prospects": [],
            "outcomes": [],
            "corrections": [
                {
                    "target_kind": correction.target_kind.value,
                    "reason": correction.reason,
                    "corrected_at": correction.corrected_at.isoformat(),
                }
                for correction in teaching_repo.corrections()
            ],
            "audit_trail": [
                {"action": action, "occurred_at": occurred_at.isoformat()}
                for action, occurred_at in self._session.execute(
                    text(
                        "SELECT action, occurred_at FROM audit_entries "
                        "WHERE workspace_id = :w ORDER BY occurred_at"
                    ),
                    {"w": str(self._workspace_id)},
                ).all()
            ],
        }
        if dna is not None:
            bundle["dna"] = {
                "version": dna.version,
                "endorsed": dna.endorsed,
                "elements": [element_to_json(element) for element in dna.elements],
            }
            bundle["dna_changelog"] = [
                {
                    "cause": event.cause.value,
                    "author": event.author.value,
                    "occurred_at": event.occurred_at.isoformat(),
                    "before": element_to_json(event.before) if event.before else None,
                    "after": element_to_json(event.after) if event.after else None,
                }
                for event in dna_repo.changelog(dna.id)
            ]
        for prospect in prospects:
            record = business_repo.get(prospect.business_record_id)
            stored = brief_repo.deliverable_for_prospect(prospect.id)
            bundle["prospects"].append(
                {
                    "business_name": record.canonical_name if record else None,
                    "status": prospect.status.name.lower(),
                    "surfaced_at": prospect.surfaced_at.isoformat(),
                    "approved_brief": (
                        {
                            "sections": [
                                {"code": s.code.value, "content": s.content}
                                for s in stored.brief.sections
                            ],
                            "couldnt_see": list(stored.brief.couldnt_see),
                            "receipts": [
                                {"number": r.number, "claim": r.claim}
                                for r in (stored.receipt_table or ())
                            ],
                        }
                        if stored
                        else None
                    ),
                }
            )
            for outcome in teaching_repo.outcomes_for_prospect(prospect.id):
                bundle["outcomes"].append(
                    {
                        "business_name": record.canonical_name if record else None,
                        "kind": outcome.kind.value,
                        "occurred_at": outcome.occurred_at.isoformat(),
                        "reason": outcome.reason,
                    }
                )
        return bundle

    def delete(self, *, confirm_name: str) -> DeletionReport:
        """Irreversible, so deliberately awkward: the workspace's exact name
        must be typed back. Deletion cascades from the workspace row — the
        schema is the guarantee that nothing Ring-1 survives."""
        workspace = self._session.get(WorkspaceRow, self._workspace_id)
        if workspace is None:
            raise NotFoundError("workspace not found")
        if confirm_name != workspace.name:
            raise XeniaError(
                "confirmation name does not match the workspace — deletion is "
                "irreversible, so the name must be typed exactly"
            )
        counts = {table: self._count(table) for table in RING_1_TABLES if table != "workspaces"}
        counts["workspaces"] = 1
        self._session.delete(workspace)
        self._session.flush()
        return DeletionReport(workspace_id=self._workspace_id, rows_deleted_by_table=counts)

    def _count(self, table: str) -> int:
        value = self._session.execute(
            text(f"SELECT count(*) FROM {table} WHERE workspace_id = :w"),
            {"w": str(self._workspace_id)},
        ).scalar_one()
        return int(value)
