"""Epic 1 foundations: workspaces, users, audit_entries, feature_flags, jobs — with RLS.

Revision ID: 0001
Revises:
Create Date: 2026-07-20

Discipline: expand -> migrate -> contract. Reversible, or the downgrade states
its contraction plan explicitly (Doc 10 SS6).

Tenancy is never retrofitted (Doc 10, Epic 1): the Ring-1 tables (workspaces,
users, audit_entries) get row-level security ENABLED and FORCED from this
first migration. FORCE matters because the application connects as the table
owner in staging/production; without it, owner connections would bypass every
policy. Policies key on transaction-local settings (`app.workspace_id`,
`app.auth_subject`) set by app.core.db.set_app_context. Note: a Postgres
*superuser* connection (the local docker-compose default) bypasses RLS by
definition — the tenancy canary tests therefore run under a dedicated
non-superuser probe role.

audit_entries carries no UPDATE or DELETE policy: append-only, enforced by the
database, not by convention.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_WORKSPACE_MATCH = "workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid"
_SUBJECT_MATCH = "auth_subject = NULLIF(current_setting('app.auth_subject', true), '')"


def upgrade() -> None:
    op.create_table(
        "workspaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workspaces")),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("auth_subject", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_users_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("auth_subject", name=op.f("uq_users_auth_subject")),
    )
    op.create_index(op.f("ix_users_workspace_id"), "users", ["workspace_id"])

    op.create_table(
        "audit_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column("target_id", sa.String(length=64), nullable=False),
        sa.Column("request_id", sa.String(length=64), nullable=True),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_entries")),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_audit_entries_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name=op.f("fk_audit_entries_actor_user_id_users"),
            ondelete="SET NULL",
        ),
    )
    op.create_index(
        "ix_audit_entries_workspace_id_occurred_at",
        "audit_entries",
        ["workspace_id", "occurred_at"],
    )

    op.create_table(
        "feature_flags",
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("removal_date", sa.Date(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("key", name=op.f("pk_feature_flags")),
    )

    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_type", sa.String(length=100), nullable=False),
        sa.Column("idempotency_key", sa.String(length=200), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column(
            "run_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_jobs")),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_jobs_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("idempotency_key", name=op.f("uq_jobs_idempotency_key")),
    )
    op.create_index("ix_jobs_status_run_at", "jobs", ["status", "run_at"])

    # ── Ring-1 row-level security: the braces of belt-and-braces (Doc 08 §8) ──
    for table in ("workspaces", "users", "audit_entries"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")

    # workspaces: readable/updatable only as the current workspace. INSERT is
    # open — creating a new workspace is how a tenancy context is born
    # (provisioning), and it exposes nothing across tenants.
    workspace_row_match = "id = NULLIF(current_setting('app.workspace_id', true), '')::uuid"
    op.execute(
        f"CREATE POLICY workspaces_select ON workspaces FOR SELECT USING ({workspace_row_match})"
    )
    op.execute("CREATE POLICY workspaces_insert ON workspaces FOR INSERT WITH CHECK (true)")
    op.execute(
        f"CREATE POLICY workspaces_update ON workspaces FOR UPDATE "
        f"USING ({workspace_row_match}) WITH CHECK ({workspace_row_match})"
    )

    # users: visible within the workspace, or to the matching auth subject —
    # the pre-tenancy identity lookup (sub -> User -> Workspace, Doc 08 §8)
    # can only ever see itself.
    user_match = f"({_WORKSPACE_MATCH} OR {_SUBJECT_MATCH})"
    op.execute(f"CREATE POLICY users_select ON users FOR SELECT USING {user_match}")
    op.execute(f"CREATE POLICY users_insert ON users FOR INSERT WITH CHECK {user_match}")
    op.execute(
        f"CREATE POLICY users_update ON users FOR UPDATE "
        f"USING ({_WORKSPACE_MATCH}) WITH CHECK ({_WORKSPACE_MATCH})"
    )

    # audit_entries: SELECT and INSERT only — append-only is a database
    # property, not an application convention.
    op.execute(
        f"CREATE POLICY audit_entries_select ON audit_entries FOR SELECT USING ({_WORKSPACE_MATCH})"
    )
    op.execute(
        f"CREATE POLICY audit_entries_insert ON audit_entries FOR INSERT "
        f"WITH CHECK ({_WORKSPACE_MATCH})"
    )


def downgrade() -> None:
    # Policies drop with their tables.
    op.drop_index("ix_jobs_status_run_at", table_name="jobs")
    op.drop_table("jobs")
    op.drop_table("feature_flags")
    op.drop_index("ix_audit_entries_workspace_id_occurred_at", table_name="audit_entries")
    op.drop_table("audit_entries")
    op.drop_index(op.f("ix_users_workspace_id"), table_name="users")
    op.drop_table("users")
    op.drop_table("workspaces")
