"""Epic 9 — golden-set membership (Ring 1, RLS enabled and forced).

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-20

Discipline: expand -> migrate -> contract. Reversible (Doc 10 SS6).
Curation is editable: entries may be removed, so a DELETE policy exists.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_WORKSPACE_MATCH = "workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid"


def upgrade() -> None:
    op.create_table(
        "golden_set_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("brief_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("note", sa.String(length=1000), nullable=False),
        sa.Column("added_by_subject", sa.String(length=255), nullable=False),
        sa.Column(
            "added_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_golden_set_entries")),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_golden_set_entries_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["brief_id"],
            ["research_briefs.id"],
            name=op.f("fk_golden_set_entries_brief_id_research_briefs"),
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("brief_id", name=op.f("uq_golden_set_entries_brief_id")),
    )
    op.execute("ALTER TABLE golden_set_entries ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE golden_set_entries FORCE ROW LEVEL SECURITY")
    for action, clause in (
        ("select", f"FOR SELECT USING ({_WORKSPACE_MATCH})"),
        ("insert", f"FOR INSERT WITH CHECK ({_WORKSPACE_MATCH})"),
        ("delete", f"FOR DELETE USING ({_WORKSPACE_MATCH})"),
    ):
        op.execute(f"CREATE POLICY golden_set_entries_{action} ON golden_set_entries {clause}")


def downgrade() -> None:
    op.drop_table("golden_set_entries")
