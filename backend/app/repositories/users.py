"""Users within one workspace — workspace-scoped by constructor (Doc 08 §8)."""

from uuid import UUID

from sqlalchemy import select

from app.domain.user import User, WorkspaceRole
from app.repositories.base import WorkspaceScopedRepository
from app.repositories.orm import UserRow


def _to_user(row: UserRow) -> User:
    return User(
        id=row.id,
        workspace_id=row.workspace_id,
        auth_subject=row.auth_subject,
        email=row.email,
        role=WorkspaceRole(row.role),
        created_at=row.created_at,
    )


class SqlUserRepo(WorkspaceScopedRepository):
    def get(self, user_id: UUID) -> User | None:
        row = self._session.execute(
            select(UserRow).where(UserRow.workspace_id == self._workspace_id, UserRow.id == user_id)
        ).scalar_one_or_none()
        return _to_user(row) if row else None

    def list(self) -> list[User]:
        rows = self._session.execute(
            select(UserRow)
            .where(UserRow.workspace_id == self._workspace_id)
            .order_by(UserRow.created_at)
        ).scalars()
        return [_to_user(row) for row in rows]
