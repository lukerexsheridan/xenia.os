"""SQLAlchemy table mappings — the persistence shape, private to this package.

Ring-1 tables (`RING_1_TABLES`) carry a workspace column and Postgres RLS
(enabled AND forced in the migration; the tenancy canary in
tests/repositories/test_rls.py fails loudly if either is ever dropped).
Ring-2 tables (`RING_2_TABLES`) are the shared world model (Doc 05 §7): they
carry no workspace column at all — structurally incapable of leaking tenancy.
`jobs` and `feature_flags` are infrastructure, not customer data: job payloads
carry IDs only (Doc 05), and flags are global by design (Doc 08 §9).
"""

from datetime import date, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.repositories.base import Base

# The tables whose rows belong to exactly one workspace (Ring 1, Doc 05 §7).
# Every table named here must have RLS enabled and forced; the canary asserts it.
RING_1_TABLES = (
    "workspaces",
    "users",
    "audit_entries",
    "prospects",
    "dnas",
    "dna_change_events",
    "research_briefs",
    "edit_log_entries",
)

# The shared world model: facts belong to nobody, judgments stay in Ring 1.
# The structural canary asserts none of these has a workspace column.
RING_2_TABLES = ("business_records", "source_snapshots", "evidence")


class WorkspaceRow(Base):
    __tablename__ = "workspaces"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    auth_subject: Mapped[str] = mapped_column(String(255), unique=True)
    email: Mapped[str | None] = mapped_column(String(320))
    role: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditEntryRow(Base):
    __tablename__ = "audit_entries"
    __table_args__ = (
        Index("ix_audit_entries_workspace_id_occurred_at", "workspace_id", "occurred_at"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE")
    )
    actor_user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    action: Mapped[str] = mapped_column(String(100))
    target_type: Mapped[str] = mapped_column(String(50))
    target_id: Mapped[str] = mapped_column(String(64))
    request_id: Mapped[str | None] = mapped_column(String(64))
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class FeatureFlagRow(Base):
    __tablename__ = "feature_flags"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str] = mapped_column(String(500))
    # Every flag has a removal date at creation (Doc 10 §6) — not nullable.
    removal_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class JobRow(Base):
    __tablename__ = "jobs"
    __table_args__ = (Index("ix_jobs_status_run_at", "status", "run_at"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    job_type: Mapped[str] = mapped_column(String(100))
    # Keyed on natural identity ("compose brief for prospect X, week W") so
    # running twice is harmless (Doc 08 §7). Required: unkeyed jobs are how
    # phantom work happens.
    idempotency_key: Mapped[str] = mapped_column(String(200), unique=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    priority: Mapped[int] = mapped_column(Integer, default=0)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=5)
    last_error: Mapped[str | None] = mapped_column(Text)
    workspace_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ── Ring 2: the shared world model (Epic 3) ──────────────────────────────────


class BusinessRecordRow(Base):
    __tablename__ = "business_records"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    canonical_name: Mapped[str] = mapped_column(String(300))
    website_domain: Mapped[str | None] = mapped_column(String(255), unique=True)
    register_number: Mapped[str | None] = mapped_column(String(50), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SourceSnapshotRow(Base):
    """One observation event. Content lives in object storage keyed by its
    SHA-256; identical content re-fetched later is a new row, one blob."""

    __tablename__ = "source_snapshots"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    url: Mapped[str] = mapped_column(Text)
    content_sha256: Mapped[str] = mapped_column(String(64), index=True)
    content_type: Mapped[str] = mapped_column(String(200))
    http_status: Mapped[int] = mapped_column(Integer)
    size_bytes: Mapped[int] = mapped_column(Integer)
    fetcher_version: Mapped[str] = mapped_column(String(50))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EvidenceRow(Base):
    __tablename__ = "evidence"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    business_record_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("business_records.id", ondelete="CASCADE"), index=True
    )
    claim: Mapped[str] = mapped_column(Text)
    evidence_type: Mapped[str] = mapped_column(String(40))
    source_url: Mapped[str] = mapped_column(Text)
    # RESTRICT: provenance must not vanish from under a receipt (Doc 05 §3).
    snapshot_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("source_snapshots.id", ondelete="RESTRICT")
    )
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    extraction_confidence: Mapped[float] = mapped_column(Float)
    freshness_class: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ── Ring 1: the workbench's customer-side records (Epic 3) ───────────────────


class ProspectRow(Base):
    __tablename__ = "prospects"
    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "business_record_id",
            name="uq_prospects_workspace_id_business_record_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    business_record_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("business_records.id", ondelete="RESTRICT")
    )
    binding_confidence: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20))
    surfaced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DnaRow(Base):
    __tablename__ = "dnas"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    # One DNA per workspace at V1 (Doc 03 §7; a second DNA is a V1.5 trigger).
    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), unique=True
    )
    version: Mapped[int] = mapped_column(Integer)
    endorsed: Mapped[bool] = mapped_column(Boolean)
    elements: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DnaChangeEventRow(Base):
    """Append-only: no update/delete path in code, none in the RLS policies."""

    __tablename__ = "dna_change_events"
    __table_args__ = (Index("ix_dna_change_events_dna_id_occurred_at", "dna_id", "occurred_at"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE")
    )
    dna_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("dnas.id", ondelete="CASCADE")
    )
    element_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    cause: Mapped[str] = mapped_column(String(30))
    author: Mapped[str] = mapped_column(String(20))
    before: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    after: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ResearchBriefRow(Base):
    __tablename__ = "research_briefs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    prospect_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("prospects.id", ondelete="CASCADE")
    )
    format_version: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20))
    sections: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
    couldnt_see: Mapped[list[str]] = mapped_column(JSONB)
    confidence_score: Mapped[float] = mapped_column(Float)
    # Frozen at finalisation: the numbered receipt table (Doc 09 §6) and the
    # derivation record that makes the brief replayable.
    receipt_table: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB)
    derivation: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finalised_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class EditLogEntryRow(Base):
    """The QA-delta measurement (Doc 07 §3): append-only, like the changelog."""

    __tablename__ = "edit_log_entries"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE")
    )
    brief_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("research_briefs.id", ondelete="CASCADE"), index=True
    )
    rubric_dimension: Mapped[str] = mapped_column(String(30))
    note: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
