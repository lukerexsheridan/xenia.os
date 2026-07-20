"""Prospects — Ring 1, workspace-scoped by constructor (Doc 08 §8)."""

from uuid import UUID

from app.domain.prospect import Prospect, ProspectStatus
from app.repositories.base import WorkspaceScopedRepository
from app.repositories.orm import ProspectRow


def _to_domain(row: ProspectRow) -> Prospect:
    return Prospect(
        id=row.id,
        workspace_id=row.workspace_id,
        business_record_id=row.business_record_id,
        binding_confidence=row.binding_confidence,
        status=ProspectStatus[row.status.upper()],
        surfaced_at=row.surfaced_at,
    )


class SqlProspectRepo(WorkspaceScopedRepository):
    def add(self, prospect: Prospect) -> Prospect:
        row = ProspectRow(
            id=prospect.id,
            workspace_id=self._workspace_id,
            business_record_id=prospect.business_record_id,
            binding_confidence=prospect.binding_confidence,
            status=prospect.status.name.lower(),
        )
        self._session.add(row)
        self._session.flush()
        return _to_domain(row)

    def get(self, prospect_id: UUID) -> Prospect | None:
        row = self._session.get(ProspectRow, prospect_id)
        if row is None or row.workspace_id != self._workspace_id:
            return None
        return _to_domain(row)
