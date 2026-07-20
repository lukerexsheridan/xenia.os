"""Service tests against in-memory fakes of the domain protocols (Doc 08 §11)."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.audit import AuditAction, AuditEntry
from app.domain.user import User, WorkspaceRole
from app.domain.workspace import Workspace
from app.services.authenticate_user import AuthenticateUser


class FakeIdentityRepo:
    def __init__(self) -> None:
        self.workspaces: dict[UUID, Workspace] = {}
        self.users_by_subject: dict[str, User] = {}

    def find_user_by_subject(self, auth_subject: str) -> User | None:
        return self.users_by_subject.get(auth_subject)

    def get_workspace(self, workspace_id: UUID) -> Workspace:
        return self.workspaces[workspace_id]

    def provision_workspace(
        self, *, name: str, auth_subject: str, email: str | None
    ) -> tuple[Workspace, User]:
        workspace = Workspace(id=uuid4(), name=name, created_at=datetime.now(UTC))
        user = User(
            id=uuid4(),
            workspace_id=workspace.id,
            auth_subject=auth_subject,
            email=email,
            role=WorkspaceRole.OWNER,
            created_at=datetime.now(UTC),
        )
        self.workspaces[workspace.id] = workspace
        self.users_by_subject[auth_subject] = user
        return workspace, user


class FakeAuditRepo:
    def __init__(self, workspace_id: UUID) -> None:
        self.workspace_id = workspace_id
        self.entries: list[AuditEntry] = []

    def append(
        self,
        *,
        action: AuditAction,
        target_type: str,
        target_id: str,
        actor_user_id: UUID | None,
        request_id: str | None,
    ) -> AuditEntry:
        entry = AuditEntry(
            id=uuid4(),
            workspace_id=self.workspace_id,
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            request_id=request_id,
            occurred_at=datetime.now(UTC),
        )
        self.entries.append(entry)
        return entry


def make_service() -> tuple[AuthenticateUser, FakeIdentityRepo, list[FakeAuditRepo]]:
    identity_repo = FakeIdentityRepo()
    audit_repos: list[FakeAuditRepo] = []

    def audit_repo_for(workspace_id: UUID) -> FakeAuditRepo:
        repo = FakeAuditRepo(workspace_id)
        audit_repos.append(repo)
        return repo

    return AuthenticateUser(identity_repo, audit_repo_for), identity_repo, audit_repos


def test_first_seen_subject_provisions_workspace_with_owner() -> None:
    service, _, _ = make_service()
    context = service.execute(auth_subject="sub-new", email="jo@brightpath.example")
    assert context.user.role is WorkspaceRole.OWNER
    assert context.user.workspace_id == context.workspace.id
    assert context.workspace.name == "jo"  # provisional name from the email local part


def test_provisioning_writes_the_auth_audit_events() -> None:
    """Epic 1 exit criterion (Doc 10): audit entries written for auth events."""
    service, _, audit_repos = make_service()
    context = service.execute(auth_subject="sub-new", email=None, request_id="req-1")
    assert len(audit_repos) == 1
    actions = [entry.action for entry in audit_repos[0].entries]
    assert actions == [AuditAction.WORKSPACE_PROVISIONED, AuditAction.USER_PROVISIONED]
    assert all(entry.request_id == "req-1" for entry in audit_repos[0].entries)
    assert all(entry.actor_user_id == context.user.id for entry in audit_repos[0].entries)


def test_known_subject_resolves_without_new_provisioning_or_audit() -> None:
    service, identity_repo, audit_repos = make_service()
    first = service.execute(auth_subject="sub-1", email="a@b.example")
    second = service.execute(auth_subject="sub-1", email="a@b.example")
    assert second.user.id == first.user.id
    assert second.workspace.id == first.workspace.id
    assert len(identity_repo.workspaces) == 1
    assert len(audit_repos) == 1  # only the first call audited (provisioning)


def test_explicit_workspace_name_wins() -> None:
    service, _, _ = make_service()
    context = service.execute(auth_subject="sub-2", email=None, workspace_name="Brightpath Digital")
    assert context.workspace.name == "Brightpath Digital"


def test_default_name_without_email_derives_from_subject() -> None:
    service, _, _ = make_service()
    context = service.execute(auth_subject="abcdef1234567890", email=None)
    assert context.workspace.name == "workspace-abcdef12"
