"""Epic 4 source ingestion: canonical content, binding reviews, source health.

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-20

Discipline: expand -> migrate -> contract. Reversible (Doc 10 SS6).
All three tables are Ring-2/ops (no workspace column, no RLS): canonical
content is the shared world model's normalised layer (Doc 09 SS5); binding
reviews are the human floor queue (ADR-008); source-health events are the
Steward's telemetry (Doc 09 SS10).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "canonical_content",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("item_kind", sa.String(length=20), nullable=False),
        sa.Column("content_key", sa.String(length=64), nullable=False),
        sa.Column("source_family", sa.String(length=30), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_record_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_canonical_content")),
        sa.ForeignKeyConstraint(
            ["snapshot_id"],
            ["source_snapshots.id"],
            name=op.f("fk_canonical_content_snapshot_id_source_snapshots"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["business_record_id"],
            ["business_records.id"],
            name=op.f("fk_canonical_content_business_record_id_business_records"),
            ondelete="SET NULL",
        ),
        sa.UniqueConstraint("item_kind", "content_key", name="uq_canonical_content_item_kind"),
    )
    op.create_index(
        op.f("ix_canonical_content_business_record_id"),
        "canonical_content",
        ["business_record_id"],
    )

    op.create_table(
        "entity_binding_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("candidate_name", sa.String(length=300), nullable=False),
        sa.Column("website_domain", sa.String(length=255), nullable=True),
        sa.Column("register_number", sa.String(length=50), nullable=True),
        sa.Column("proposed_business_record_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("canonical_item_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_entity_binding_reviews")),
        sa.ForeignKeyConstraint(
            ["proposed_business_record_id"],
            ["business_records.id"],
            name=op.f("fk_entity_binding_reviews_proposed_business_record_id_business_records"),
            ondelete="SET NULL",
        ),
    )

    op.create_table(
        "source_health_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_family", sa.String(length=30), nullable=False),
        sa.Column("event", sa.String(length=30), nullable=False),
        sa.Column("detail", sa.String(length=500), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_source_health_events")),
    )
    op.create_index(
        "ix_source_health_events_family_occurred",
        "source_health_events",
        ["source_family", "occurred_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_source_health_events_family_occurred", table_name="source_health_events")
    op.drop_table("source_health_events")
    op.drop_table("entity_binding_reviews")
    op.drop_index(op.f("ix_canonical_content_business_record_id"), table_name="canonical_content")
    op.drop_table("canonical_content")
