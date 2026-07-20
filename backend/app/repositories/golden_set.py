"""Golden-set persistence — Ring 1, workspace-scoped (Doc 04 §6).

The membership law (`require_approved`) runs at the write: an entry for an
unapproved brief cannot be stored through this repository.
"""

from uuid import UUID

from sqlalchemy import select

from app.domain.golden_set import GoldenSetEntry, require_approved
from app.repositories.base import WorkspaceScopedRepository
from app.repositories.orm import GoldenSetEntryRow, ResearchBriefRow


class SqlGoldenSetRepo(WorkspaceScopedRepository):
    def add(self, entry: GoldenSetEntry) -> GoldenSetEntry:
        brief_row = self._session.get(ResearchBriefRow, entry.brief_id)
        if brief_row is None or brief_row.workspace_id != self._workspace_id:
            raise LookupError(f"no research brief {entry.brief_id} in this workspace")
        require_approved(brief_row.status)
        self._session.add(
            GoldenSetEntryRow(
                id=entry.id,
                workspace_id=self._workspace_id,
                brief_id=entry.brief_id,
                note=entry.note,
                added_by_subject=entry.added_by_subject,
                added_at=entry.added_at,
            )
        )
        self._session.flush()
        return entry

    def remove(self, brief_id: UUID) -> bool:
        row = self._session.execute(
            select(GoldenSetEntryRow).where(
                GoldenSetEntryRow.workspace_id == self._workspace_id,
                GoldenSetEntryRow.brief_id == brief_id,
            )
        ).scalar_one_or_none()
        if row is None:
            return False
        self._session.delete(row)
        self._session.flush()
        return True

    def list(self) -> list[GoldenSetEntry]:
        rows = (
            self._session.execute(
                select(GoldenSetEntryRow)
                .where(GoldenSetEntryRow.workspace_id == self._workspace_id)
                .order_by(GoldenSetEntryRow.added_at, GoldenSetEntryRow.id)
            )
            .scalars()
            .all()
        )
        return [
            GoldenSetEntry(
                id=row.id,
                workspace_id=row.workspace_id,
                brief_id=row.brief_id,
                note=row.note,
                added_by_subject=row.added_by_subject,
                added_at=row.added_at,
            )
            for row in rows
        ]
