"""Identity resolution: sub → User → Workspace (Doc 08 §8).

Deliberately not workspace-scoped: it runs before a workspace context exists.
The RLS policies still constrain it — `users` is readable pre-tenancy only via
the row whose `auth_subject` matches the transaction's `app.auth_subject`
setting, so an identity can only ever resolve itself.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import set_app_context
from app.domain.user import User, WorkspaceRole
from app.domain.workspace import Workspace
from app.repositories.orm import UserRow, WorkspaceRow


def _to_workspace(row: WorkspaceRow) -> Workspace:
    return Workspace(id=row.id, name=row.name, created_at=row.created_at)


def _to_user(row: UserRow) -> User:
    return User(
        id=row.id,
        workspace_id=row.workspace_id,
        auth_subject=row.auth_subject,
        email=row.email,
        role=WorkspaceRole(row.role),
        created_at=row.created_at,
    )


class SqlIdentityRepo:
    """Implements the domain's IdentityRepo protocol."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def find_user_by_subject(self, auth_subject: str) -> User | None:
        row = self._session.execute(
            select(UserRow).where(UserRow.auth_subject == auth_subject)
        ).scalar_one_or_none()
        if row is None:
            return None
        # Resolution establishes the transaction's tenancy context, so the
        # workspace row (and everything Ring-1 after it) becomes readable.
        set_app_context(self._session, workspace_id=row.workspace_id)
        return _to_user(row)

    def get_workspace(self, workspace_id: UUID) -> Workspace:
        row = self._session.execute(
            select(WorkspaceRow).where(WorkspaceRow.id == workspace_id)
        ).scalar_one()
        return _to_workspace(row)

    def find_workspace(self, workspace_id: UUID) -> Workspace | None:
        row = self._session.execute(
            select(WorkspaceRow).where(WorkspaceRow.id == workspace_id)
        ).scalar_one_or_none()
        return _to_workspace(row) if row else None

    def provision_workspace(
        self, *, name: str, auth_subject: str, email: str | None
    ) -> tuple[Workspace, User]:
        workspace_row = WorkspaceRow(name=name)
        self._session.add(workspace_row)
        self._session.flush()
        # A new tenancy context is born exactly here: attach it to the
        # transaction so the rest of the provisioning writes (user, audit)
        # pass the Ring-1 RLS policies.
        set_app_context(self._session, workspace_id=workspace_row.id)
        user_row = UserRow(
            workspace_id=workspace_row.id,
            auth_subject=auth_subject,
            email=email,
            role=WorkspaceRole.OWNER.value,
        )
        self._session.add(user_row)
        self._session.flush()
        return _to_workspace(workspace_row), _to_user(user_row)
