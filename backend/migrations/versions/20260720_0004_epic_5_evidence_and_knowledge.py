"""Epic 5 evidence & knowledge: evidence slots + relations, signals, AI ledger.

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-20

Discipline: expand -> migrate -> contract; the evidence additions are pure
expansion (server default carries existing rows). All Ring-2/ops — no
workspace columns, no RLS (Doc 05 §7).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "evidence",
        sa.Column("claim_slot", sa.String(length=100), server_default="general", nullable=False),
    )
    for relation in ("corroborates_id", "conflicts_id", "supersedes_id"):
        op.add_column("evidence", sa.Column(relation, postgresql.UUID(as_uuid=True), nullable=True))
        op.create_foreign_key(
            op.f(f"fk_evidence_{relation}_evidence"),
            "evidence",
            "evidence",
            [relation],
            ["id"],
            ondelete="SET NULL",
        )

    op.create_table(
        "signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("family", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column(
            "supporting_evidence_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("newest_observation_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("rule_version", sa.String(length=30), nullable=False),
        sa.Column("derived_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_signals")),
        sa.ForeignKeyConstraint(
            ["business_record_id"],
            ["business_records.id"],
            name=op.f("fk_signals_business_record_id_business_records"),
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "business_record_id", "name", name="uq_signals_business_record_id_name"
        ),
    )
    op.create_index(op.f("ix_signals_business_record_id"), "signals", ["business_record_id"])

    op.create_table(
        "ai_call_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pipeline", sa.String(length=60), nullable=False),
        sa.Column("prompt_version", sa.String(length=60), nullable=False),
        sa.Column("model", sa.String(length=60), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False),
        sa.Column("output_tokens", sa.Integer(), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ai_call_records")),
    )


def downgrade() -> None:
    op.drop_table("ai_call_records")
    op.drop_index(op.f("ix_signals_business_record_id"), table_name="signals")
    op.drop_table("signals")
    for relation in ("supersedes_id", "conflicts_id", "corroborates_id"):
        op.drop_constraint(op.f(f"fk_evidence_{relation}_evidence"), "evidence")
        op.drop_column("evidence", relation)
    op.drop_column("evidence", "claim_slot")
