"""The tenancy canary (Doc 10 §5): permanent, and loud when RLS weakens.

Two layers of assertion:
- the catalogue check — every Ring-1 table has RLS enabled AND forced; a
  migration that drops either fails this immediately;
- the behavioural check — under a non-superuser role, one workspace's rows are
  invisible to another, invisible without a context, and audit entries cannot
  be updated or deleted at all.

The probe role exists because local/CI database users are superusers, which
bypass RLS by definition; staging/production connect as the table owner,
which FORCE covers.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID, uuid4

import pytest
from sqlalchemy import Connection, Engine, text

from app.repositories.orm import RING_1_TABLES


@pytest.fixture
def two_workspaces(db: Engine) -> tuple[UUID, UUID]:
    """Two workspaces, each with one user — created as the privileged test user."""
    ids = (uuid4(), uuid4())
    with db.begin() as connection:
        for index, workspace_id in enumerate(ids):
            connection.execute(
                text("INSERT INTO workspaces (id, name) VALUES (:id, :name)"),
                {"id": workspace_id, "name": f"agency-{index}"},
            )
            connection.execute(
                text(
                    "INSERT INTO users (id, workspace_id, auth_subject, email, role) "
                    "VALUES (:id, :workspace_id, :subject, :email, 'owner')"
                ),
                {
                    "id": uuid4(),
                    "workspace_id": workspace_id,
                    "subject": f"subject-{index}-{workspace_id}",
                    "email": None,
                },
            )
            connection.execute(
                text(
                    "INSERT INTO audit_entries "
                    "(id, workspace_id, action, target_type, target_id) "
                    "VALUES (:id, :workspace_id, 'workspace.provisioned', 'workspace', :target)"
                ),
                {"id": uuid4(), "workspace_id": workspace_id, "target": str(workspace_id)},
            )
    return ids


@contextmanager
def probe_transaction(
    db: Engine, rls_probe: str, *, workspace_id: UUID | None = None, auth_subject: str | None = None
) -> Iterator[Connection]:
    """A transaction running as the non-superuser probe with a tenancy context."""
    with db.connect() as connection:
        connection.execute(text(f"SET ROLE {rls_probe}"))
        if workspace_id is not None:
            connection.execute(
                text("SELECT set_config('app.workspace_id', :value, true)"),
                {"value": str(workspace_id)},
            )
        if auth_subject is not None:
            connection.execute(
                text("SELECT set_config('app.auth_subject', :value, true)"),
                {"value": auth_subject},
            )
        yield connection
        connection.rollback()


def test_every_ring_1_table_has_rls_enabled_and_forced(db: Engine) -> None:
    """The catalogue canary: fails loudly the day a migration weakens RLS."""
    with db.connect() as connection:
        for table in RING_1_TABLES:
            row = connection.execute(
                text(
                    "SELECT relrowsecurity, relforcerowsecurity FROM pg_class "
                    "WHERE relname = :table AND relkind = 'r'"
                ),
                {"table": table},
            ).one()
            assert row.relrowsecurity, f"RLS is not enabled on Ring-1 table {table!r}"
            assert row.relforcerowsecurity, f"RLS is not forced on Ring-1 table {table!r}"


def test_workspace_context_sees_only_its_own_rows(
    db: Engine, rls_probe: str, two_workspaces: tuple[UUID, UUID]
) -> None:
    workspace_a, workspace_b = two_workspaces
    with probe_transaction(db, rls_probe, workspace_id=workspace_a) as connection:
        visible_workspaces = connection.execute(text("SELECT id FROM workspaces")).scalars().all()
        visible_users = connection.execute(text("SELECT workspace_id FROM users")).scalars().all()
        visible_audit = (
            connection.execute(text("SELECT workspace_id FROM audit_entries")).scalars().all()
        )
    assert visible_workspaces == [workspace_a]
    assert visible_users == [workspace_a]
    assert visible_audit == [workspace_a]
    assert workspace_b not in visible_workspaces


def test_no_context_sees_nothing(
    db: Engine, rls_probe: str, two_workspaces: tuple[UUID, UUID]
) -> None:
    with probe_transaction(db, rls_probe) as connection:
        assert connection.execute(text("SELECT count(*) FROM workspaces")).scalar_one() == 0
        assert connection.execute(text("SELECT count(*) FROM users")).scalar_one() == 0
        assert connection.execute(text("SELECT count(*) FROM audit_entries")).scalar_one() == 0


def test_auth_subject_context_sees_only_itself(
    db: Engine, rls_probe: str, two_workspaces: tuple[UUID, UUID]
) -> None:
    """The pre-tenancy identity lookup can only ever resolve its own row."""
    workspace_a, _ = two_workspaces
    with db.connect() as connection:
        subject = connection.execute(
            text("SELECT auth_subject FROM users WHERE workspace_id = :id"),
            {"id": workspace_a},
        ).scalar_one()
    with probe_transaction(db, rls_probe, auth_subject=subject) as connection:
        rows = connection.execute(text("SELECT auth_subject FROM users")).scalars().all()
    assert rows == [subject]


def test_audit_entries_are_append_only_under_rls(
    db: Engine, rls_probe: str, two_workspaces: tuple[UUID, UUID]
) -> None:
    """No UPDATE/DELETE policy exists: mutation affects zero rows even in-tenant."""
    workspace_a, _ = two_workspaces
    with probe_transaction(db, rls_probe, workspace_id=workspace_a) as connection:
        updated = connection.execute(text("UPDATE audit_entries SET action = 'tampered'")).rowcount
        deleted = connection.execute(text("DELETE FROM audit_entries")).rowcount
    assert updated == 0
    assert deleted == 0


def test_cross_tenant_write_is_rejected(
    db: Engine, rls_probe: str, two_workspaces: tuple[UUID, UUID]
) -> None:
    workspace_a, workspace_b = two_workspaces
    with (
        probe_transaction(db, rls_probe, workspace_id=workspace_a) as connection,
        pytest.raises(Exception, match="row-level security"),
    ):
        connection.execute(
            text(
                "INSERT INTO audit_entries "
                "(id, workspace_id, action, target_type, target_id) "
                "VALUES (:id, :workspace_id, 'workspace.provisioned', 'workspace', 'x')"
            ),
            {"id": uuid4(), "workspace_id": workspace_b},
        )
