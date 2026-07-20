"""Epic 3 research workbench: Ring-2 world model + Ring-1 workbench tables with RLS.

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-20

Discipline: expand -> migrate -> contract. Reversible (Doc 10 SS6).

Ring 2 (business_records, source_snapshots, evidence): the shared world model
(Doc 05 SS7) — no workspace column, no RLS; structurally incapable of leaking
tenancy. Ring 1 (prospects, dnas, dna_change_events, research_briefs,
edit_log_entries): RLS ENABLED and FORCED, policies keyed to the
transaction-local `app.workspace_id` setting. dna_change_events and
edit_log_entries carry no UPDATE/DELETE policy — append-only at the database,
like audit_entries (the changelog is total, Doc 04 SS4).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_WORKSPACE_MATCH = "workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid"


def _created_at() -> sa.Column[sa.types.DateTime]:
    return sa.Column(
        "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
    )


def upgrade() -> None:
    # ── Ring 2 ───────────────────────────────────────────────────────────
    op.create_table(
        "business_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("canonical_name", sa.String(length=300), nullable=False),
        sa.Column("website_domain", sa.String(length=255), nullable=True),
        sa.Column("register_number", sa.String(length=50), nullable=True),
        _created_at(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_business_records")),
        sa.UniqueConstraint("website_domain", name=op.f("uq_business_records_website_domain")),
        sa.UniqueConstraint("register_number", name=op.f("uq_business_records_register_number")),
    )

    op.create_table(
        "source_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("content_type", sa.String(length=200), nullable=False),
        sa.Column("http_status", sa.Integer(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("fetcher_version", sa.String(length=50), nullable=False),
        sa.Column(
            "fetched_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_source_snapshots")),
    )
    op.create_index(
        op.f("ix_source_snapshots_content_sha256"), "source_snapshots", ["content_sha256"]
    )

    op.create_table(
        "evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("claim", sa.Text(), nullable=False),
        sa.Column("evidence_type", sa.String(length=40), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("extraction_confidence", sa.Float(), nullable=False),
        sa.Column("freshness_class", sa.String(length=20), nullable=False),
        _created_at(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_evidence")),
        sa.ForeignKeyConstraint(
            ["business_record_id"],
            ["business_records.id"],
            name=op.f("fk_evidence_business_record_id_business_records"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["snapshot_id"],
            ["source_snapshots.id"],
            name=op.f("fk_evidence_snapshot_id_source_snapshots"),
            ondelete="RESTRICT",
        ),
    )
    op.create_index(op.f("ix_evidence_business_record_id"), "evidence", ["business_record_id"])

    # ── Ring 1 ───────────────────────────────────────────────────────────
    op.create_table(
        "prospects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("binding_confidence", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "surfaced_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_prospects")),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_prospects_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["business_record_id"],
            ["business_records.id"],
            name=op.f("fk_prospects_business_record_id_business_records"),
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "workspace_id",
            "business_record_id",
            name="uq_prospects_workspace_id_business_record_id",
        ),
    )
    op.create_index(op.f("ix_prospects_workspace_id"), "prospects", ["workspace_id"])

    op.create_table(
        "dnas",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("endorsed", sa.Boolean(), nullable=False),
        sa.Column("elements", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        _created_at(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_dnas")),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_dnas_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("workspace_id", name=op.f("uq_dnas_workspace_id")),
    )

    op.create_table(
        "dna_change_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dna_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("element_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cause", sa.String(length=30), nullable=False),
        sa.Column("author", sa.String(length=20), nullable=False),
        sa.Column("before", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("after", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_dna_change_events")),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_dna_change_events_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["dna_id"],
            ["dnas.id"],
            name=op.f("fk_dna_change_events_dna_id_dnas"),
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_dna_change_events_dna_id_occurred_at", "dna_change_events", ["dna_id", "occurred_at"]
    )

    op.create_table(
        "research_briefs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prospect_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("format_version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("sections", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("couldnt_see", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("receipt_table", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("derivation", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        _created_at(),
        sa.Column("finalised_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_research_briefs")),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_research_briefs_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["prospect_id"],
            ["prospects.id"],
            name=op.f("fk_research_briefs_prospect_id_prospects"),
            ondelete="CASCADE",
        ),
    )
    op.create_index(op.f("ix_research_briefs_workspace_id"), "research_briefs", ["workspace_id"])

    op.create_table(
        "edit_log_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("brief_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rubric_dimension", sa.String(length=30), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        _created_at(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_edit_log_entries")),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_edit_log_entries_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["brief_id"],
            ["research_briefs.id"],
            name=op.f("fk_edit_log_entries_brief_id_research_briefs"),
            ondelete="CASCADE",
        ),
    )
    op.create_index(op.f("ix_edit_log_entries_brief_id"), "edit_log_entries", ["brief_id"])

    # ── Ring-1 row-level security (Doc 08 §8) ────────────────────────────
    ring_1 = ("prospects", "dnas", "dna_change_events", "research_briefs", "edit_log_entries")
    for table in ring_1:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(f"CREATE POLICY {table}_select ON {table} FOR SELECT USING ({_WORKSPACE_MATCH})")
        op.execute(
            f"CREATE POLICY {table}_insert ON {table} FOR INSERT WITH CHECK ({_WORKSPACE_MATCH})"
        )

    # Mutable Ring-1 tables get UPDATE; the changelog and edit log do not —
    # append-only is a database property, not an application convention.
    for table in ("prospects", "dnas", "research_briefs"):
        op.execute(
            f"CREATE POLICY {table}_update ON {table} FOR UPDATE "
            f"USING ({_WORKSPACE_MATCH}) WITH CHECK ({_WORKSPACE_MATCH})"
        )


def downgrade() -> None:
    # Policies drop with their tables.
    op.drop_index(op.f("ix_edit_log_entries_brief_id"), table_name="edit_log_entries")
    op.drop_table("edit_log_entries")
    op.drop_index(op.f("ix_research_briefs_workspace_id"), table_name="research_briefs")
    op.drop_table("research_briefs")
    op.drop_index("ix_dna_change_events_dna_id_occurred_at", table_name="dna_change_events")
    op.drop_table("dna_change_events")
    op.drop_table("dnas")
    op.drop_index(op.f("ix_prospects_workspace_id"), table_name="prospects")
    op.drop_table("prospects")
    op.drop_index(op.f("ix_evidence_business_record_id"), table_name="evidence")
    op.drop_table("evidence")
    op.drop_index(op.f("ix_source_snapshots_content_sha256"), table_name="source_snapshots")
    op.drop_table("source_snapshots")
    op.drop_table("business_records")
