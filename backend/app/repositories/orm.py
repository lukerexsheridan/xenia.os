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
    "rubric_scores",
    "recommendations",
    "decisions",
    "corrections",
    "outcomes",
    "dna_proposals",
)

# The shared world model: facts belong to nobody, judgments stay in Ring 1.
# The structural canary asserts none of these has a workspace column.
# (entity_binding_reviews and source_health_events are ops machinery rather
# than world model, but the same structural guarantee protects them.)
RING_2_TABLES = (
    "business_records",
    "source_snapshots",
    "evidence",
    "canonical_content",
    "entity_binding_reviews",
    "source_health_events",
    "signals",
    "ai_call_records",
)


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
    # Epic 5: the claim-type key relations group on, and the graph as columns
    # (Doc 09 §6/§13 — three columns, two queries, no graph database).
    claim_slot: Mapped[str] = mapped_column(String(100), server_default="general")
    corroborates_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("evidence.id", ondelete="SET NULL")
    )
    conflicts_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("evidence.id", ondelete="SET NULL")
    )
    supersedes_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("evidence.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SignalRow(Base):
    """Knowledge from evidence (Doc 09 §7): Ring 2, derivations stored."""

    __tablename__ = "signals"
    __table_args__ = (
        UniqueConstraint("business_record_id", "name", name="uq_signals_business_record_id_name"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    business_record_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("business_records.id", ondelete="CASCADE"), index=True
    )
    family: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(60))
    confidence: Mapped[float] = mapped_column(Float)
    supporting_evidence_ids: Mapped[list[str]] = mapped_column(JSONB)
    newest_observation_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    rule_version: Mapped[str] = mapped_column(String(30))
    derived_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AiCallRecordRow(Base):
    """The unit-cost ledger's raw material (Doc 08 §6): every model call."""

    __tablename__ = "ai_call_records"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    pipeline: Mapped[str] = mapped_column(String(60))
    prompt_version: Mapped[str] = mapped_column(String(60))
    model: Mapped[str] = mapped_column(String(60))
    input_tokens: Mapped[int] = mapped_column(Integer)
    output_tokens: Mapped[int] = mapped_column(Integer)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


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


class RubricScoreRow(Base):
    """The QA-delta dial's substrate (Doc 10 Sprint 13): one grading per brief."""

    __tablename__ = "rubric_scores"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE")
    )
    brief_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("research_briefs.id", ondelete="CASCADE"), unique=True
    )
    accuracy: Mapped[int] = mapped_column(Integer)
    evidence: Mapped[int] = mapped_column(Integer)
    insight: Mapped[int] = mapped_column(Integer)
    fit_reasoning: Mapped[int] = mapped_column(Integer)
    actionability: Mapped[int] = mapped_column(Integer)
    scored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


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


# ── Ring 2 / ops: acquisition machinery (Epic 4) ─────────────────────────────


class CanonicalContentRow(Base):
    """A canonical item (Doc 09 §5) referenced to its snapshot; deduplicated
    by content key at ingestion, where it is cheap. business_record_id stays
    NULL until entity binding resolves (ADR-008)."""

    __tablename__ = "canonical_content"
    __table_args__ = (
        UniqueConstraint("item_kind", "content_key", name="uq_canonical_content_item_kind"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    item_kind: Mapped[str] = mapped_column(String(20))
    content_key: Mapped[str] = mapped_column(String(64))
    source_family: Mapped[str] = mapped_column(String(30))
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    snapshot_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("source_snapshots.id", ondelete="RESTRICT")
    )
    business_record_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("business_records.id", ondelete="SET NULL"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EntityBindingReviewRow(Base):
    """The human floor queue (ADR-008): ambiguous bindings await the Editor."""

    __tablename__ = "entity_binding_reviews"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    candidate_name: Mapped[str] = mapped_column(String(300))
    website_domain: Mapped[str | None] = mapped_column(String(255))
    register_number: Mapped[str | None] = mapped_column(String(50))
    proposed_business_record_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("business_records.id", ondelete="SET NULL")
    )
    confidence: Mapped[float] = mapped_column(Float)
    canonical_item_ids: Mapped[list[str]] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(20))  # pending | bound | rejected
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class SourceHealthEventRow(Base):
    """Source-health telemetry (Doc 09 §10): per-family fetch/parse outcomes."""

    __tablename__ = "source_health_events"
    __table_args__ = (
        Index("ix_source_health_events_family_occurred", "source_family", "occurred_at"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    source_family: Mapped[str] = mapped_column(String(30))
    event: Mapped[str] = mapped_column(String(30))  # fetched|refused|parse_failed|items_emitted
    detail: Mapped[str] = mapped_column(String(500))
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class RecommendationRow(Base):
    """The accountable judgment persisted (Doc 08 §5): decomposed score,
    queue position, week, polarity — exclusions share the table and the
    audit trail."""

    __tablename__ = "recommendations"
    __table_args__ = (
        UniqueConstraint("workspace_id", "prospect_id", "week_key"),
        Index("ix_recommendations_workspace_week", "workspace_id", "week_key"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE")
    )
    prospect_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("prospects.id", ondelete="CASCADE")
    )
    week_key: Mapped[str] = mapped_column(String(10))  # e.g. "2026-W30"
    polarity: Mapped[str] = mapped_column(String(15))  # recommended | excluded
    rank: Mapped[int | None] = mapped_column(Integer)
    score_total: Mapped[float] = mapped_column(Float)
    confidence_band: Mapped[str] = mapped_column(String(10))  # the four words, as data
    components: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)  # the decomposition
    rank_reason: Mapped[str | None] = mapped_column(String(500))
    exclusion_reason: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DecisionRow(Base):
    """The founder's response — the teaching event (Doc 08 §5)."""

    __tablename__ = "decisions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE")
    )
    recommendation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("recommendations.id", ondelete="CASCADE"), unique=True
    )
    kind: Mapped[str] = mapped_column(String(10))  # accept | decline | pursue
    chip: Mapped[str | None] = mapped_column(String(30))  # the Doc 06 §6 taxonomy
    reason: Mapped[str | None] = mapped_column(String(1000))
    decided_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT")
    )
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CorrectionRow(Base):
    """The highest-intent teaching signal, recorded with its author
    (Doc 04 §5; Doc 08 §5)."""

    __tablename__ = "corrections"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE")
    )
    target_kind: Mapped[str] = mapped_column(String(20))
    target_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    reason: Mapped[str | None] = mapped_column(String(1000))
    effect_summary: Mapped[str] = mapped_column(String(500))  # the named effect, as said
    corrected_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT")
    )
    corrected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class OutcomeRow(Base):
    """Ground truth, append-only, always human-recorded (Doc 03 §7)."""

    __tablename__ = "outcomes"
    __table_args__ = (Index("ix_outcomes_workspace_prospect", "workspace_id", "prospect_id"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE")
    )
    prospect_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("prospects.id", ondelete="CASCADE")
    )
    kind: Mapped[str] = mapped_column(String(15))
    reason: Mapped[str | None] = mapped_column(String(1000))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    recorded_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT")
    )
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DnaProposalRow(Base):
    """A structural change awaiting the customer's signature (Doc 03 §8)."""

    __tablename__ = "dna_proposals"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE")
    )
    dna_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("dnas.id", ondelete="CASCADE")
    )
    element: Mapped[dict[str, Any]] = mapped_column(JSONB)  # as it would exist
    rationale: Mapped[str] = mapped_column(String(1000))  # proposed with reasoning (N4)
    proposed_by: Mapped[str] = mapped_column(String(20))  # customer | xenia
    status: Mapped[str] = mapped_column(String(15))  # proposed | endorsed | declined
    proposed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
