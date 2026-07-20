"""Epic 8 — the loop's back half: recommendations, decisions, corrections,
outcomes (all Ring 1, RLS enabled and forced).

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-20

Discipline: expand -> migrate -> contract. Reversible (Doc 10 SS6).
Policy notes: `recommendations` carries a DELETE policy because weekly
assembly is replace-by-week (idempotent); `decisions`, `corrections` and
`outcomes` are append-only, so no UPDATE or DELETE policy exists at all —
the absence is the enforcement.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_WORKSPACE_MATCH = "workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid"

_TABLES = ("recommendations", "decisions", "corrections", "outcomes", "dna_proposals")


def _workspace_column() -> sa.Column[postgresql.UUID]:
    return sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False)


def upgrade() -> None:
    op.create_table(
        "recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        _workspace_column(),
        sa.Column("prospect_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("week_key", sa.String(length=10), nullable=False),
        sa.Column("polarity", sa.String(length=15), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("score_total", sa.Float(), nullable=False),
        sa.Column("confidence_band", sa.String(length=10), nullable=False),
        sa.Column("components", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("rank_reason", sa.String(length=500), nullable=True),
        sa.Column("exclusion_reason", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_recommendations")),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_recommendations_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["prospect_id"],
            ["prospects.id"],
            name=op.f("fk_recommendations_prospect_id_prospects"),
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "workspace_id",
            "prospect_id",
            "week_key",
            name=op.f("uq_recommendations_workspace_id"),
        ),
    )
    op.create_index(
        "ix_recommendations_workspace_week", "recommendations", ["workspace_id", "week_key"]
    )

    op.create_table(
        "decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        _workspace_column(),
        sa.Column("recommendation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kind", sa.String(length=10), nullable=False),
        sa.Column("chip", sa.String(length=30), nullable=True),
        sa.Column("reason", sa.String(length=1000), nullable=True),
        sa.Column("decided_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_decisions")),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_decisions_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["recommendation_id"],
            ["recommendations.id"],
            name=op.f("fk_decisions_recommendation_id_recommendations"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["decided_by"],
            ["users.id"],
            name=op.f("fk_decisions_decided_by_users"),
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("recommendation_id", name=op.f("uq_decisions_recommendation_id")),
    )

    op.create_table(
        "corrections",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        _workspace_column(),
        sa.Column("target_kind", sa.String(length=20), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.String(length=1000), nullable=True),
        sa.Column("effect_summary", sa.String(length=500), nullable=False),
        sa.Column("corrected_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("corrected_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_corrections")),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_corrections_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["corrected_by"],
            ["users.id"],
            name=op.f("fk_corrections_corrected_by_users"),
            ondelete="RESTRICT",
        ),
    )

    op.create_table(
        "outcomes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        _workspace_column(),
        sa.Column("prospect_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kind", sa.String(length=15), nullable=False),
        sa.Column("reason", sa.String(length=1000), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recorded_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_outcomes")),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_outcomes_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["prospect_id"],
            ["prospects.id"],
            name=op.f("fk_outcomes_prospect_id_prospects"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["recorded_by"],
            ["users.id"],
            name=op.f("fk_outcomes_recorded_by_users"),
            ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_outcomes_workspace_prospect", "outcomes", ["workspace_id", "prospect_id"])

    op.create_table(
        "dna_proposals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        _workspace_column(),
        sa.Column("dna_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("element", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("rationale", sa.String(length=1000), nullable=False),
        sa.Column("proposed_by", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=15), nullable=False),
        sa.Column("proposed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_dna_proposals")),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_dna_proposals_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["dna_id"],
            ["dnas.id"],
            name=op.f("fk_dna_proposals_dna_id_dnas"),
            ondelete="CASCADE",
        ),
    )

    for table in _TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(f"CREATE POLICY {table}_select ON {table} FOR SELECT USING ({_WORKSPACE_MATCH})")
        op.execute(
            f"CREATE POLICY {table}_insert ON {table} FOR INSERT WITH CHECK ({_WORKSPACE_MATCH})"
        )
    # Weekly assembly is replace-by-week; only recommendations may be deleted.
    op.execute(
        f"CREATE POLICY recommendations_delete ON recommendations "
        f"FOR DELETE USING ({_WORKSPACE_MATCH})"
    )
    # A proposal's status changes exactly once (the state machine enforces
    # the sequence); the row itself is never deleted.
    op.execute(
        f"CREATE POLICY dna_proposals_update ON dna_proposals "
        f"FOR UPDATE USING ({_WORKSPACE_MATCH}) WITH CHECK ({_WORKSPACE_MATCH})"
    )


def downgrade() -> None:
    op.drop_table("dna_proposals")
    op.drop_table("outcomes")
    op.drop_table("corrections")
    op.drop_table("decisions")
    op.drop_table("recommendations")
