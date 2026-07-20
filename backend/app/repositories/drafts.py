"""Draft persistence — Ring 1, workspace-scoped; always-editable (Doc 03 C6)."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select

from app.repositories.base import WorkspaceScopedRepository
from app.repositories.orm import DraftRow


class SqlDraftRepo(WorkspaceScopedRepository):
    def get_for_prospect(self, prospect_id: UUID) -> str | None:
        row = self._row(prospect_id)
        return row.body if row else None

    def save(self, prospect_id: UUID, body: str) -> None:
        row = self._row(prospect_id)
        if row is None:
            self._session.add(
                DraftRow(workspace_id=self._workspace_id, prospect_id=prospect_id, body=body)
            )
        else:
            row.body = body
            row.updated_at = datetime.now(UTC)
        self._session.flush()

    def _row(self, prospect_id: UUID) -> DraftRow | None:
        return self._session.execute(
            select(DraftRow).where(
                DraftRow.workspace_id == self._workspace_id,
                DraftRow.prospect_id == prospect_id,
            )
        ).scalar_one_or_none()
