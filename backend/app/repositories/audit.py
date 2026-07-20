"""The audit stream's persistence — append-only, workspace-scoped.

No update or delete methods exist here, and the RLS policies on
`audit_entries` carry no UPDATE/DELETE clauses either, so mutation is
unrepresentable at both layers (Doc 08 §8).
"""

from uuid import UUID

from sqlalchemy import select

from app.domain.audit import AuditAction, AuditEntry
from app.repositories.base import WorkspaceScopedRepository
from app.repositories.orm import AuditEntryRow


def _to_entry(row: AuditEntryRow) -> AuditEntry:
    return AuditEntry(
        id=row.id,
        workspace_id=row.workspace_id,
        actor_user_id=row.actor_user_id,
        action=AuditAction(row.action),
        target_type=row.target_type,
        target_id=row.target_id,
        request_id=row.request_id,
        occurred_at=row.occurred_at,
    )


class SqlAuditEntryRepo(WorkspaceScopedRepository):
    """Implements the domain's AuditEntryRepo protocol."""

    def append(
        self,
        *,
        action: AuditAction,
        target_type: str,
        target_id: str,
        actor_user_id: UUID | None,
        request_id: str | None,
    ) -> AuditEntry:
        row = AuditEntryRow(
            workspace_id=self._workspace_id,
            actor_user_id=actor_user_id,
            action=action.value,
            target_type=target_type,
            target_id=target_id,
            request_id=request_id,
        )
        self._session.add(row)
        self._session.flush()
        return _to_entry(row)

    def list(self) -> list[AuditEntry]:
        rows = self._session.execute(
            select(AuditEntryRow)
            .where(AuditEntryRow.workspace_id == self._workspace_id)
            .order_by(AuditEntryRow.occurred_at)
        ).scalars()
        return [_to_entry(row) for row in rows]
