"""Epic 10 — the resumable interview transcript (Ring 1, RLS).

Revision ID: 0008
Revises: 0007
Create Date: 2026-07-20

Discipline: expand -> migrate -> contract. Reversible (Doc 10 SS6).
The transcript updates in place as answers arrive, so an UPDATE policy
exists; the row is never deleted by the application.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_WORKSPACE_MATCH = "workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid"


def upgrade() -> None:
    op.create_table(
        "interview_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("answers", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_interview_states")),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_interview_states_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("workspace_id", name=op.f("uq_interview_states_workspace_id")),
    )
    op.execute("ALTER TABLE interview_states ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE interview_states FORCE ROW LEVEL SECURITY")
    for action, clause in (
        ("select", f"FOR SELECT USING ({_WORKSPACE_MATCH})"),
        ("insert", f"FOR INSERT WITH CHECK ({_WORKSPACE_MATCH})"),
        ("update", f"FOR UPDATE USING ({_WORKSPACE_MATCH}) WITH CHECK ({_WORKSPACE_MATCH})"),
    ):
        op.execute(f"CREATE POLICY interview_states_{action} ON interview_states {clause}")


def downgrade() -> None:
    op.drop_table("interview_states")
