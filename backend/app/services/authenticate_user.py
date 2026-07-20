"""AuthenticateUser — map a verified identity to its User and Workspace.

The use-case behind every authenticated request (Doc 08 §8): a known subject
resolves to its existing User; a first-seen subject provisions a new
Workspace with an owner User, and the provisioning is written to the audit
stream (the auth events Epic 1's exit criteria require). Workspace naming is
provisional — the agency names itself properly during onboarding (Epic 10).
"""

from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from app.domain.audit import AuditAction, AuditEntryRepo
from app.domain.user import IdentityRepo, User
from app.domain.workspace import Workspace

AuditRepoFactory = Callable[[UUID], AuditEntryRepo]


@dataclass(frozen=True)
class AuthenticatedContext:
    user: User
    workspace: Workspace


def _default_workspace_name(email: str | None, auth_subject: str) -> str:
    if email and "@" in email:
        return email.split("@", 1)[0]
    return f"workspace-{auth_subject[:8]}"


class AuthenticateUser:
    def __init__(self, identity_repo: IdentityRepo, audit_repo_for: AuditRepoFactory) -> None:
        self._identity_repo = identity_repo
        self._audit_repo_for = audit_repo_for

    def execute(
        self,
        *,
        auth_subject: str,
        email: str | None,
        request_id: str | None = None,
        workspace_name: str | None = None,
    ) -> AuthenticatedContext:
        user = self._identity_repo.find_user_by_subject(auth_subject)
        if user is not None:
            workspace = self._identity_repo.get_workspace(user.workspace_id)
            return AuthenticatedContext(user=user, workspace=workspace)

        workspace, user = self._identity_repo.provision_workspace(
            name=workspace_name or _default_workspace_name(email, auth_subject),
            auth_subject=auth_subject,
            email=email,
        )
        audit = self._audit_repo_for(workspace.id)
        audit.append(
            action=AuditAction.WORKSPACE_PROVISIONED,
            target_type="workspace",
            target_id=str(workspace.id),
            actor_user_id=user.id,
            request_id=request_id,
        )
        audit.append(
            action=AuditAction.USER_PROVISIONED,
            target_type="user",
            target_id=str(user.id),
            actor_user_id=user.id,
            request_id=request_id,
        )
        return AuthenticatedContext(user=user, workspace=workspace)
