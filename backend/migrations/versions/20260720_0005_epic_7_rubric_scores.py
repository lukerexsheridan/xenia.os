"""Epic 7 QA-delta dial: rubric scores (Ring 1, RLS).

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-20

Discipline: expand -> migrate -> contract. Reversible (Doc 10 SS6).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_WORKSPACE_MATCH = "workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid"


def upgrade() -> None:
    op.create_table(
        "rubric_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("brief_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("accuracy", sa.Integer(), nullable=False),
        sa.Column("evidence", sa.Integer(), nullable=False),
        sa.Column("insight", sa.Integer(), nullable=False),
        sa.Column("fit_reasoning", sa.Integer(), nullable=False),
        sa.Column("actionability", sa.Integer(), nullable=False),
        sa.Column(
            "scored_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rubric_scores")),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_rubric_scores_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["brief_id"],
            ["research_briefs.id"],
            name=op.f("fk_rubric_scores_brief_id_research_briefs"),
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("brief_id", name=op.f("uq_rubric_scores_brief_id")),
    )
    op.execute("ALTER TABLE rubric_scores ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE rubric_scores FORCE ROW LEVEL SECURITY")
    op.execute(
        f"CREATE POLICY rubric_scores_select ON rubric_scores FOR SELECT USING ({_WORKSPACE_MATCH})"
    )
    op.execute(
        f"CREATE POLICY rubric_scores_insert ON rubric_scores FOR INSERT "
        f"WITH CHECK ({_WORKSPACE_MATCH})"
    )
    op.execute(
        f"CREATE POLICY rubric_scores_update ON rubric_scores FOR UPDATE "
        f"USING ({_WORKSPACE_MATCH}) WITH CHECK ({_WORKSPACE_MATCH})"
    )


def downgrade() -> None:
    op.drop_table("rubric_scores")
