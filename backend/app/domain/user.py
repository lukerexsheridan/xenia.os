"""User — a human within a workspace (Doc 08 §5).

Identity comes from the auth vendor (the opaque ``auth_subject``); attribution
and the flat-role model of Doc 03 (owner/member) live here. Authority nuance
belongs to the delegation ladder (Epic 2), not to roles.

``IdentityRepo`` is the domain-defined protocol (AP2) for the sub → User →
Workspace mapping of Doc 08 §8, implemented by ``app.repositories``.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID

from app.domain.workspace import Workspace


class WorkspaceRole(StrEnum):
    OWNER = "owner"
    MEMBER = "member"


@dataclass(frozen=True)
class User:
    id: UUID
    workspace_id: UUID
    auth_subject: str
    email: str | None
    role: WorkspaceRole
    created_at: datetime


class IdentityRepo(Protocol):
    """Maps verified identities to Users and Workspaces (Doc 08 §8)."""

    def find_user_by_subject(self, auth_subject: str) -> User | None: ...

    def get_workspace(self, workspace_id: UUID) -> Workspace: ...

    def provision_workspace(
        self, *, name: str, auth_subject: str, email: str | None
    ) -> tuple[Workspace, User]:
        """Create a new Workspace with its owner User, atomically."""
        ...
