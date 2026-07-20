"""Epic 11 — MVP mode: delivery scheduling, billing state, drafts.

Revision ID: 0009
Revises: 0008
Create Date: 2026-07-20

Discipline: expand -> migrate -> contract. Reversible (Doc 10 SS6).
Workspace columns are additive with server defaults (expand-safe). Drafts
are Ring 1 with RLS; they update in place (always-editable, Doc 03 C6).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_WORKSPACE_MATCH = "workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid"


def upgrade() -> None:
    op.add_column(
        "workspaces",
        sa.Column(
            "delivery_timezone",
            sa.String(length=50),
            server_default="Europe/London",
            nullable=False,
        ),
    )
    op.add_column(
        "workspaces", sa.Column("stripe_customer_id", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "workspaces",
        sa.Column(
            "subscription_status", sa.String(length=20), server_default="none", nullable=False
        ),
    )

    op.create_table(
        "drafts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prospect_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_drafts")),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_drafts_workspace_id_workspaces"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["prospect_id"],
            ["prospects.id"],
            name=op.f("fk_drafts_prospect_id_prospects"),
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("prospect_id", name=op.f("uq_drafts_prospect_id")),
    )
    op.execute("ALTER TABLE drafts ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE drafts FORCE ROW LEVEL SECURITY")
    for action, clause in (
        ("select", f"FOR SELECT USING ({_WORKSPACE_MATCH})"),
        ("insert", f"FOR INSERT WITH CHECK ({_WORKSPACE_MATCH})"),
        ("update", f"FOR UPDATE USING ({_WORKSPACE_MATCH}) WITH CHECK ({_WORKSPACE_MATCH})"),
    ):
        op.execute(f"CREATE POLICY drafts_{action} ON drafts {clause}")


def downgrade() -> None:
    op.drop_table("drafts")
    op.drop_column("workspaces", "subscription_status")
    op.drop_column("workspaces", "stripe_customer_id")
    op.drop_column("workspaces", "delivery_timezone")
