"""The research workbench — the concierge kit's API (Doc 10, Sprints 5-6).

Ugly-but-honest by decree; its users number exactly one. The internal
sub-application's Swagger UI is the "UI-lite": every operation the concierge
needs — snapshot, register, capture, brief, finalise, render — as documented
endpoints behind Editor authorisation. Ring-1 operations name their target
workspace in the path; Ring-2 operations (world facts) have no workspace at
all.
"""

import time
from datetime import UTC, datetime
from functools import lru_cache
from typing import Annotated, Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai.pipelines.compose_brief import ComposeBrief
from app.ai.pipelines.extract_page_evidence import ExtractPageEvidence
from app.ai.providers.openai_responses import OpenAIResponsesProvider
from app.api.deps import get_db_session
from app.api.internal.deps import EditorContext, get_editor_context, get_workspace_session
from app.core.config import get_settings
from app.core.errors import NotFoundError
from app.core.logging import current_request_id
from app.domain.confidence import ConfidenceBand, band_for
from app.domain.dna import DecayClass, DnaCategory, ElementOrigin
from app.domain.evidence import EvidenceType, FreshnessClass
from app.domain.golden_set import GoldenSetEntry
from app.domain.research_brief import BriefSection, BriefSectionCode, completeness_problems
from app.domain.rubric import RubricDimension, RubricScore
from app.domain.signal import Signal
from app.integrations.object_storage import S3ObjectStore
from app.integrations.sources.http_transport import HttpxTransport
from app.integrations.sources.politeness import PolitenessEngine
from app.repositories.acquisition import (
    BindingReview,
    SqlCanonicalContentRepo,
    SqlEntityBindingReviewRepo,
    SqlSourceHealthRepo,
)
from app.repositories.audit import SqlAuditEntryRepo
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.dna import SqlDnaRepo
from app.repositories.evidence import SqlEvidenceRepo
from app.repositories.golden_set import SqlGoldenSetRepo
from app.repositories.identity import SqlIdentityRepo
from app.repositories.knowledge import SqlKnowledgeRepo
from app.repositories.prospects import SqlProspectRepo
from app.repositories.research_briefs import SqlResearchBriefRepo, StoredResearchBrief
from app.repositories.snapshots import SqlSourceSnapshotRepo
from app.services.acquire_footprint import AcquireFootprint
from app.services.assemble_queue import build_assemble_queue
from app.services.author_research_brief import (
    CreateResearchBrief,
    FinaliseResearchBrief,
    UpdateBriefSection,
)
from app.services.capture_evidence import CaptureEvidence
from app.services.capture_snapshot import CaptureSnapshot
from app.services.compose_research_brief import ComposeResearchBrief
from app.services.compute_metrics import ComputeMetrics
from app.services.create_dna import CreateDna, DnaElementInput
from app.services.create_prospect import CreateProspect
from app.services.derive_signals import DeriveSignals
from app.services.documents import RenderBriefPdf, RenderDnaDocument
from app.services.extract_evidence import ExtractEvidence
from app.services.offboard_workspace import OffboardWorkspace
from app.services.research_run import RunResearch
from app.services.resolve_binding_review import ResolveBindingReview
from app.services.resolve_entity import ResolveEntity

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_db_session)]
WorkspaceSessionDep = Annotated[Session, Depends(get_workspace_session)]
EditorDep = Annotated[EditorContext, Depends(get_editor_context)]


@lru_cache
def _politeness_engine() -> PolitenessEngine:
    return PolitenessEngine(
        HttpxTransport(),
        user_agent=get_settings().politeness_user_agent,
        clock=time.monotonic,
        sleeper=time.sleep,
    )


@lru_cache
def _object_store() -> S3ObjectStore:
    settings = get_settings()
    store = S3ObjectStore(
        endpoint_url=settings.object_storage_endpoint,
        access_key=settings.object_storage_access_key,
        secret_key=settings.object_storage_secret_key,
        bucket=settings.object_storage_bucket,
    )
    store.ensure_bucket()
    return store


def get_capture_snapshot(session: SessionDep) -> CaptureSnapshot:
    return CaptureSnapshot(_politeness_engine(), _object_store(), SqlSourceSnapshotRepo(session))


# ── Ring 2: snapshots, business records, evidence ────────────────────────────


class SnapshotRequest(BaseModel):
    url: str


class SnapshotResponse(BaseModel):
    id: UUID
    url: str
    content_sha256: str
    http_status: int
    size_bytes: int
    fetched_at: datetime


@router.post("/snapshots")
def capture_snapshot(
    body: SnapshotRequest,
    capture: Annotated[CaptureSnapshot, Depends(get_capture_snapshot)],
) -> SnapshotResponse:
    snapshot = capture.execute(body.url)
    return SnapshotResponse(
        id=snapshot.id,
        url=snapshot.url,
        content_sha256=snapshot.content_sha256,
        http_status=snapshot.http_status,
        size_bytes=snapshot.size_bytes,
        fetched_at=snapshot.fetched_at,
    )


class BusinessRecordRequest(BaseModel):
    canonical_name: str
    website_domain: str | None = None
    register_number: str | None = None


class BusinessRecordResponse(BaseModel):
    id: UUID
    canonical_name: str
    website_domain: str | None
    register_number: str | None


@router.post("/business-records")
def register_business_record(
    body: BusinessRecordRequest, session: SessionDep
) -> BusinessRecordResponse:
    record = SqlBusinessRecordRepo(session).find_or_create(
        canonical_name=body.canonical_name,
        website_domain=body.website_domain,
        register_number=body.register_number,
    )
    return BusinessRecordResponse(
        id=record.id,
        canonical_name=record.canonical_name,
        website_domain=record.website_domain,
        register_number=record.register_number,
    )


class EvidenceRequest(BaseModel):
    business_record_id: UUID
    claim: str
    evidence_type: EvidenceType
    snapshot_id: UUID
    observed_at: datetime
    extraction_confidence: float = Field(ge=0.0, le=1.0)
    freshness_class: FreshnessClass


class EvidenceResponse(BaseModel):
    id: UUID
    business_record_id: UUID
    claim: str
    evidence_type: EvidenceType
    source_url: str
    observed_at: datetime


@router.post("/evidence")
def capture_evidence(body: EvidenceRequest, session: SessionDep) -> EvidenceResponse:
    evidence = CaptureEvidence(
        SqlEvidenceRepo(session), SqlBusinessRecordRepo(session), SqlSourceSnapshotRepo(session)
    ).execute(
        business_record_id=body.business_record_id,
        claim=body.claim,
        evidence_type=body.evidence_type,
        snapshot_id=body.snapshot_id,
        observed_at=body.observed_at,
        extraction_confidence=body.extraction_confidence,
        freshness_class=body.freshness_class,
    )
    return EvidenceResponse(
        id=evidence.id,
        business_record_id=evidence.business_record_id,
        claim=evidence.claim,
        evidence_type=evidence.evidence_type,
        source_url=evidence.source_url,
        observed_at=evidence.observed_at,
    )


@router.get("/business-records/{business_record_id}/evidence")
def list_evidence(business_record_id: UUID, session: SessionDep) -> list[EvidenceResponse]:
    return [
        EvidenceResponse(
            id=item.id,
            business_record_id=item.business_record_id,
            claim=item.claim,
            evidence_type=item.evidence_type,
            source_url=item.source_url,
            observed_at=item.observed_at,
        )
        for item in SqlEvidenceRepo(session).list_for_business(business_record_id)
    ]


# ── Ring 1: prospects, DNA, briefs (workspace named in the path) ─────────────


class ProspectRequest(BaseModel):
    business_record_id: UUID
    binding_confidence: float = Field(ge=0.0, le=1.0)


class ProspectResponse(BaseModel):
    id: UUID
    business_record_id: UUID
    binding_confidence: float
    status: str


@router.post("/workspaces/{workspace_id}/prospects")
def create_prospect(
    workspace_id: UUID, body: ProspectRequest, session: WorkspaceSessionDep
) -> ProspectResponse:
    prospect = CreateProspect(
        SqlProspectRepo(session, workspace_id),
        SqlBusinessRecordRepo(session),
        SqlAuditEntryRepo(session, workspace_id),
    ).execute(
        workspace_id=workspace_id,
        business_record_id=body.business_record_id,
        binding_confidence=body.binding_confidence,
        request_id=current_request_id(),
    )
    return ProspectResponse(
        id=prospect.id,
        business_record_id=prospect.business_record_id,
        binding_confidence=prospect.binding_confidence,
        status=prospect.status.name.lower(),
    )


class DnaElementRequest(BaseModel):
    category: DnaCategory
    statement: str
    confidence: float = Field(ge=0.0, le=1.0)
    decay_class: DecayClass
    origin: ElementOrigin


class DnaRequest(BaseModel):
    elements: list[DnaElementRequest]


class DnaResponse(BaseModel):
    id: UUID
    version: int
    endorsed: bool
    element_count: int


@router.post("/workspaces/{workspace_id}/dna")
def create_dna(workspace_id: UUID, body: DnaRequest, session: WorkspaceSessionDep) -> DnaResponse:
    dna = CreateDna(
        SqlDnaRepo(session, workspace_id), SqlAuditEntryRepo(session, workspace_id)
    ).execute(
        workspace_id=workspace_id,
        elements=[
            DnaElementInput(
                category=item.category,
                statement=item.statement,
                confidence=item.confidence,
                decay_class=item.decay_class,
                origin=item.origin,
            )
            for item in body.elements
        ],
        request_id=current_request_id(),
    )
    return DnaResponse(
        id=dna.id, version=dna.version, endorsed=dna.endorsed, element_count=len(dna.elements)
    )


@router.get("/workspaces/{workspace_id}/dna/document.pdf")
def render_dna_document(workspace_id: UUID, session: WorkspaceSessionDep) -> Response:
    workspace = SqlIdentityRepo(session).get_workspace(workspace_id)
    pdf = RenderDnaDocument(SqlDnaRepo(session, workspace_id)).execute(
        workspace_name=workspace.name
    )
    return Response(content=pdf, media_type="application/pdf")


class BriefSectionRequest(BaseModel):
    code: BriefSectionCode
    content: str
    cited_evidence_ids: list[UUID] = Field(default_factory=list)

    def to_domain(self) -> BriefSection:
        return BriefSection(
            code=self.code,
            content=self.content,
            cited_evidence_ids=tuple(self.cited_evidence_ids),
        )


class BriefRequest(BaseModel):
    prospect_id: UUID
    sections: list[BriefSectionRequest] = Field(default_factory=list)
    couldnt_see: list[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)


class BriefResponse(BaseModel):
    id: UUID
    prospect_id: UUID
    status: str
    format_version: int
    confidence_band: ConfidenceBand
    completeness_problems: list[str]
    receipt_count: int | None


@router.post("/workspaces/{workspace_id}/briefs")
def create_brief(
    workspace_id: UUID, body: BriefRequest, session: WorkspaceSessionDep
) -> BriefResponse:
    stored = CreateResearchBrief(
        SqlResearchBriefRepo(session, workspace_id), SqlProspectRepo(session, workspace_id)
    ).execute(
        workspace_id=workspace_id,
        prospect_id=body.prospect_id,
        sections=[section.to_domain() for section in body.sections],
        couldnt_see=body.couldnt_see,
        confidence_score=body.confidence_score,
    )
    return _brief_response(stored)


@router.get("/workspaces/{workspace_id}/briefs/{brief_id}")
def get_brief(workspace_id: UUID, brief_id: UUID, session: WorkspaceSessionDep) -> BriefResponse:
    stored = SqlResearchBriefRepo(session, workspace_id).get(brief_id)
    if stored is None:
        raise NotFoundError("research brief not found in this workspace")
    return _brief_response(stored)


@router.put("/workspaces/{workspace_id}/briefs/{brief_id}/sections")
def update_brief_section(
    workspace_id: UUID,
    brief_id: UUID,
    body: BriefSectionRequest,
    session: WorkspaceSessionDep,
) -> BriefResponse:
    stored = UpdateBriefSection(SqlResearchBriefRepo(session, workspace_id)).execute(
        brief_id=brief_id, section=body.to_domain()
    )
    return _brief_response(stored)


@router.post("/workspaces/{workspace_id}/briefs/{brief_id}/finalise")
def finalise_brief(
    workspace_id: UUID,
    brief_id: UUID,
    session: WorkspaceSessionDep,
    editor: EditorDep,
) -> BriefResponse:
    stored = FinaliseResearchBrief(
        SqlResearchBriefRepo(session, workspace_id),
        SqlEvidenceRepo(session),
        SqlAuditEntryRepo(session, workspace_id),
    ).execute(
        brief_id=brief_id,
        finalised_by=editor.auth_subject,
        request_id=current_request_id(),
    )
    return _brief_response(stored)


class BriefEditRequest(BaseModel):
    rubric_dimension: RubricDimension
    note: str


@router.post("/workspaces/{workspace_id}/briefs/{brief_id}/edits", status_code=201)
def record_brief_edit(
    workspace_id: UUID,
    brief_id: UUID,
    body: BriefEditRequest,
    session: WorkspaceSessionDep,
) -> dict[str, str]:
    entry_id = SqlResearchBriefRepo(session, workspace_id).add_edit(
        brief_id, dimension=body.rubric_dimension, note=body.note
    )
    return {"id": str(entry_id)}


@router.get("/workspaces/{workspace_id}/briefs/{brief_id}/document.pdf")
def render_brief_document(
    workspace_id: UUID, brief_id: UUID, session: WorkspaceSessionDep
) -> Response:
    pdf = RenderBriefPdf(
        SqlResearchBriefRepo(session, workspace_id), SqlEvidenceRepo(session)
    ).execute(brief_id)
    return Response(content=pdf, media_type="application/pdf")


def _brief_response(stored: StoredResearchBrief) -> BriefResponse:
    return BriefResponse(
        id=stored.brief.id,
        prospect_id=stored.brief.prospect_id,
        status=stored.status.value,
        format_version=stored.brief.format_version,
        confidence_band=stored.brief.confidence_band,
        completeness_problems=list(completeness_problems(stored.brief)),
        receipt_count=len(stored.receipt_table) if stored.receipt_table is not None else None,
    )


# ── Epic 4: acquisition, the binding floor queue, source health ──────────────


def get_acquire_footprint(session: SessionDep) -> AcquireFootprint:
    settings = get_settings()
    return AcquireFootprint(
        get_capture_snapshot(session),
        SqlBusinessRecordRepo(session),
        SqlCanonicalContentRepo(session),
        SqlSourceHealthRepo(session),
        ResolveEntity(SqlBusinessRecordRepo(session), SqlEntityBindingReviewRepo(session)),
        ad_library_access_token=settings.ad_library_access_token,
    )


class FamilyResultResponse(BaseModel):
    family: str
    items_stored: int
    duplicates_collapsed: int
    queued_for_binding: int
    couldnt_see: list[str]


class FootprintResponse(BaseModel):
    business_record_id: UUID
    families: list[FamilyResultResponse]
    canonical_counts: dict[str, int]


@router.post("/business-records/{business_record_id}/acquire")
def acquire_footprint(
    business_record_id: UUID,
    session: SessionDep,
    acquire: Annotated[AcquireFootprint, Depends(get_acquire_footprint)],
) -> FootprintResponse:
    report = acquire.execute(business_record_id)
    return FootprintResponse(
        business_record_id=report.business_record_id,
        families=[
            FamilyResultResponse(
                family=result.family,
                items_stored=result.items_stored,
                duplicates_collapsed=result.duplicates_collapsed,
                queued_for_binding=result.queued_for_binding,
                couldnt_see=result.couldnt_see,
            )
            for result in report.families
        ],
        canonical_counts=SqlCanonicalContentRepo(session).count_for_business(business_record_id),
    )


class BindingReviewResponse(BaseModel):
    id: UUID
    candidate_name: str
    website_domain: str | None
    register_number: str | None
    confidence: float
    canonical_item_count: int
    status: str


def _review_response(review: BindingReview) -> BindingReviewResponse:
    return BindingReviewResponse(
        id=review.id,
        candidate_name=review.candidate_name,
        website_domain=review.website_domain,
        register_number=review.register_number,
        confidence=review.confidence,
        canonical_item_count=len(review.canonical_item_ids),
        status=review.status.value,
    )


@router.get("/binding-reviews")
def list_binding_reviews(session: SessionDep) -> list[BindingReviewResponse]:
    return [
        _review_response(review) for review in SqlEntityBindingReviewRepo(session).list_pending()
    ]


class BindingResolutionRequest(BaseModel):
    business_record_id: UUID | None  # None rejects the binding


@router.post("/binding-reviews/{review_id}/resolve")
def resolve_binding_review(
    review_id: UUID, body: BindingResolutionRequest, session: SessionDep
) -> BindingReviewResponse:
    review = ResolveBindingReview(
        SqlEntityBindingReviewRepo(session),
        SqlCanonicalContentRepo(session),
        SqlBusinessRecordRepo(session),
    ).execute(review_id, business_record_id=body.business_record_id)
    return _review_response(review)


@router.get("/source-health")
def source_health(session: SessionDep) -> dict[str, dict[str, int]]:
    """Per-family fetch/parse outcome counts (Doc 09 §10's Steward view)."""
    return SqlSourceHealthRepo(session).counts()


# ── Epic 5: extraction and signals ───────────────────────────────────────────


def get_extract_evidence(session: SessionDep) -> ExtractEvidence:
    settings = get_settings()
    pipeline = None
    if settings.openai_api_key:
        pipeline = ExtractPageEvidence(
            OpenAIResponsesProvider(api_key=settings.openai_api_key, model=settings.openai_model)
        )
    return ExtractEvidence(
        SqlKnowledgeRepo(session),
        SqlEvidenceRepo(session),
        SqlBusinessRecordRepo(session),
        SqlSourceHealthRepo(session),
        pipeline,
    )


class ExtractionResponse(BaseModel):
    business_record_id: UUID
    stored: int
    already_known: int
    dropped: int
    couldnt_see: list[str]


@router.post("/business-records/{business_record_id}/extract")
def extract_evidence(
    business_record_id: UUID,
    extract: Annotated[ExtractEvidence, Depends(get_extract_evidence)],
) -> ExtractionResponse:
    report = extract.execute(business_record_id)
    return ExtractionResponse(
        business_record_id=report.business_record_id,
        stored=report.stored,
        already_known=report.already_known,
        dropped=report.dropped,
        couldnt_see=report.couldnt_see,
    )


class SignalResponse(BaseModel):
    family: str
    name: str
    confidence: float
    confidence_band: ConfidenceBand
    supporting_evidence_count: int
    newest_observation_at: datetime
    rule_version: str


@router.post("/business-records/{business_record_id}/signals")
def derive_signals(business_record_id: UUID, session: SessionDep) -> list[SignalResponse]:
    signals = DeriveSignals(SqlEvidenceRepo(session), SqlKnowledgeRepo(session)).execute(
        business_record_id
    )
    return [_signal_response(signal) for signal in signals]


@router.get("/business-records/{business_record_id}/signals")
def list_signals(business_record_id: UUID, session: SessionDep) -> list[SignalResponse]:
    return [
        _signal_response(signal)
        for signal in SqlKnowledgeRepo(session).signals_for_business(business_record_id)
    ]


def _signal_response(signal: Signal) -> SignalResponse:
    return SignalResponse(
        family=signal.family.value,
        name=signal.name,
        confidence=signal.confidence,
        confidence_band=band_for(signal.confidence),
        supporting_evidence_count=len(signal.supporting_evidence_ids),
        newest_observation_at=signal.newest_observation_at,
        rule_version=signal.rule_version,
    )


# ── Epic 6: the orchestrated research run ────────────────────────────────────


class ResearchRequest(BaseModel):
    force_refresh: bool = False


class CoverageResponse(BaseModel):
    source_family: str
    achieved: bool
    couldnt_see: list[str]


class ResearchRunResponse(BaseModel):
    business_record_id: UUID
    trigger: str
    source_families: list[str]
    max_fetches: int
    coverage: list[CoverageResponse]
    couldnt_see: list[str]
    signals: list[SignalResponse]
    ledger: dict[str, int]


@router.post("/business-records/{business_record_id}/research")
def run_research(
    business_record_id: UUID,
    body: ResearchRequest,
    session: SessionDep,
    acquire: Annotated[AcquireFootprint, Depends(get_acquire_footprint)],
    extract: Annotated[ExtractEvidence, Depends(get_extract_evidence)],
) -> ResearchRunResponse:
    report = RunResearch(
        acquire,
        extract,
        DeriveSignals(SqlEvidenceRepo(session), SqlKnowledgeRepo(session)),
        SqlKnowledgeRepo(session),
    ).execute(business_record_id, force_refresh=body.force_refresh)
    return ResearchRunResponse(
        business_record_id=report.business_record_id,
        trigger=report.recipe.trigger.value,
        source_families=sorted(report.recipe.source_families),
        max_fetches=report.recipe.max_fetches,
        coverage=[
            CoverageResponse(
                source_family=entry.source_family,
                achieved=entry.achieved,
                couldnt_see=list(entry.couldnt_see),
            )
            for entry in report.coverage
        ],
        couldnt_see=report.couldnt_see,
        signals=[_signal_response(signal) for signal in report.signals],
        ledger=report.ledger,
    )


# ── Epic 7: machine composition behind the wall, and the QA-delta dial ───────


def get_compose_pipeline() -> ComposeBrief | None:
    settings = get_settings()
    if not settings.openai_api_key:
        return None
    return ComposeBrief(
        OpenAIResponsesProvider(api_key=settings.openai_api_key, model=settings.openai_model)
    )


class CompositionResponse(BaseModel):
    brief: BriefResponse | None
    l0_problems: list[str]
    attempts: int


@router.post("/workspaces/{workspace_id}/prospects/{prospect_id}/compose-brief")
def compose_brief(
    workspace_id: UUID,
    prospect_id: UUID,
    session: WorkspaceSessionDep,
    pipeline: Annotated[ComposeBrief | None, Depends(get_compose_pipeline)],
) -> CompositionResponse:
    if pipeline is None:
        raise NotFoundError("AI composition is not configured (no provider key)")
    prospect = SqlProspectRepo(session, workspace_id).get(prospect_id)
    if prospect is None:
        raise NotFoundError("prospect not found in this workspace")
    business = SqlBusinessRecordRepo(session).get(prospect.business_record_id)
    outcome = ComposeResearchBrief(
        pipeline,
        SqlResearchBriefRepo(session, workspace_id),
        SqlProspectRepo(session, workspace_id),
        SqlEvidenceRepo(session),
        SqlDnaRepo(session, workspace_id),
        SqlKnowledgeRepo(session),
    ).execute(
        workspace_id=workspace_id,
        prospect_id=prospect_id,
        business_name=business.canonical_name if business else "",
    )
    return CompositionResponse(
        brief=_brief_response(outcome.stored) if outcome.stored else None,
        l0_problems=list(outcome.l0_problems),
        attempts=outcome.attempts,
    )


class RubricScoreRequest(BaseModel):
    accuracy: int = Field(ge=0, le=4)
    evidence: int = Field(ge=0, le=4)
    insight: int = Field(ge=0, le=4)
    fit_reasoning: int = Field(ge=0, le=4)
    actionability: int = Field(ge=0, le=4)


class RubricScoreResponse(BaseModel):
    total: int
    meets_ship_bar: bool


@router.post("/workspaces/{workspace_id}/briefs/{brief_id}/rubric-score")
def record_rubric_score(
    workspace_id: UUID,
    brief_id: UUID,
    body: RubricScoreRequest,
    session: WorkspaceSessionDep,
) -> RubricScoreResponse:
    repo = SqlResearchBriefRepo(session, workspace_id)
    if repo.get(brief_id) is None:
        raise NotFoundError("research brief not found in this workspace")
    score = RubricScore(
        accuracy=body.accuracy,
        evidence=body.evidence,
        insight=body.insight,
        fit_reasoning=body.fit_reasoning,
        actionability=body.actionability,
    )
    repo.record_rubric_score(brief_id, score)
    return RubricScoreResponse(total=score.total, meets_ship_bar=score.meets_ship_bar)


@router.get("/workspaces/{workspace_id}/quality-report")
def quality_report(workspace_id: UUID, session: WorkspaceSessionDep) -> dict[str, float | int]:
    """The QA-delta dial (Doc 10, Sprint 13): the unedited-pass rate."""
    return SqlResearchBriefRepo(session, workspace_id).quality_report()


class AssemblyResponse(BaseModel):
    week_key: str
    recommended: int
    excluded: int


@router.post("/workspaces/{workspace_id}/assemble-queue")
def assemble_queue_now(workspace_id: UUID, session: WorkspaceSessionDep) -> AssemblyResponse:
    """Assemble this workspace's week on demand (Doc 10, Sprint 14's staging
    deploy); the Monday job runs the identical service."""
    result = build_assemble_queue(session, workspace_id).execute(workspace_id=workspace_id)
    return AssemblyResponse(
        week_key=result.week_key, recommended=result.recommended, excluded=result.excluded
    )


# ── Epic 9: the Editor console's data surfaces (Doc 10, Sprint 16) ───────────


class GradingQueueItemResponse(BaseModel):
    brief_id: UUID
    prospect_id: UUID
    status: str
    created_sections: int
    couldnt_see: list[str]
    l0: str | None  # from the stored derivation, when machine-composed
    edits: int


@router.get("/workspaces/{workspace_id}/grading-queue")
def grading_queue(
    workspace_id: UUID, session: WorkspaceSessionDep
) -> list[GradingQueueItemResponse]:
    """Everything awaiting a rubric score, oldest first (MVP samples 100%)."""
    repo = SqlResearchBriefRepo(session, workspace_id)
    items = []
    for stored in repo.grading_queue():
        derivation = stored.derivation or {}
        items.append(
            GradingQueueItemResponse(
                brief_id=stored.brief.id,
                prospect_id=stored.brief.prospect_id,
                status=stored.status.value,
                created_sections=len(stored.brief.sections),
                couldnt_see=list(stored.brief.couldnt_see),
                l0=derivation.get("l0"),
                edits=len(repo.list_edits(stored.brief.id)),
            )
        )
    return items


class ApprovalQueueItemResponse(BaseModel):
    brief_id: UUID
    prospect_id: UUID
    scored: bool
    meets_ship_bar: bool | None


@router.get("/workspaces/{workspace_id}/approval-queue")
def approval_queue(
    workspace_id: UUID, session: WorkspaceSessionDep
) -> list[ApprovalQueueItemResponse]:
    """The gate's inbox: every DRAFT, with its grading state alongside —
    approval without a score is possible but visibly flagged."""
    repo = SqlResearchBriefRepo(session, workspace_id)
    items = []
    for stored in repo.awaiting_approval():
        score = repo.rubric_score_for(stored.brief.id)
        items.append(
            ApprovalQueueItemResponse(
                brief_id=stored.brief.id,
                prospect_id=stored.brief.prospect_id,
                scored=score is not None,
                meets_ship_bar=score.meets_ship_bar if score else None,
            )
        )
    return items


class GoldenEntryRequest(BaseModel):
    note: str


class GoldenEntryResponse(BaseModel):
    brief_id: UUID
    note: str
    added_by: str


@router.post("/workspaces/{workspace_id}/briefs/{brief_id}/golden", status_code=201)
def add_golden_entry(
    workspace_id: UUID,
    brief_id: UUID,
    body: GoldenEntryRequest,
    session: WorkspaceSessionDep,
    editor: EditorDep,
) -> GoldenEntryResponse:
    if SqlResearchBriefRepo(session, workspace_id).get(brief_id) is None:
        raise NotFoundError("no research brief with this id in this workspace")
    entry = SqlGoldenSetRepo(session, workspace_id).add(
        GoldenSetEntry(
            id=uuid4(),
            workspace_id=workspace_id,
            brief_id=brief_id,
            note=body.note,
            added_by_subject=editor.auth_subject,
            added_at=datetime.now(UTC),
        )
    )
    return GoldenEntryResponse(
        brief_id=entry.brief_id, note=entry.note, added_by=entry.added_by_subject
    )


@router.delete("/workspaces/{workspace_id}/briefs/{brief_id}/golden", status_code=204)
def remove_golden_entry(workspace_id: UUID, brief_id: UUID, session: WorkspaceSessionDep) -> None:
    if not SqlGoldenSetRepo(session, workspace_id).remove(brief_id):
        raise NotFoundError("this brief is not in the golden set")


@router.get("/workspaces/{workspace_id}/golden-set")
def list_golden_set(workspace_id: UUID, session: WorkspaceSessionDep) -> list[GoldenEntryResponse]:
    return [
        GoldenEntryResponse(
            brief_id=entry.brief_id, note=entry.note, added_by=entry.added_by_subject
        )
        for entry in SqlGoldenSetRepo(session, workspace_id).list()
    ]


class FiveMetricsResponse(BaseModel):
    acceptance_rate: float
    teaching_events: int
    unedited_pass_rate: float
    capture_rate: float
    tokens_per_brief: float


@router.get("/metrics")
def five_metrics(session: SessionDep) -> FiveMetricsResponse:
    """The five numbers on one page (Doc 10, Sprint 20)."""
    metrics = ComputeMetrics(session).cohort()
    return FiveMetricsResponse(
        acceptance_rate=metrics.acceptance_rate,
        teaching_events=metrics.teaching_events,
        unedited_pass_rate=metrics.unedited_pass_rate,
        capture_rate=metrics.capture_rate,
        tokens_per_brief=metrics.tokens_per_brief,
    )


# ── Epic 12: the departure rule (Doc 10, Sprint 21-22) ───────────────────────


@router.get("/workspaces/{workspace_id}/offboarding-export")
def offboarding_export(workspace_id: UUID, session: WorkspaceSessionDep) -> dict[str, Any]:
    """Everything that is theirs, in one bundle — the access-request answer
    and the departure export are the same artefact."""
    return OffboardWorkspace(session, workspace_id).export()


class OffboardRequest(BaseModel):
    confirm_name: str


class DeletionReportResponse(BaseModel):
    workspace_id: UUID
    rows_deleted_by_table: dict[str, int]


@router.post("/workspaces/{workspace_id}/offboard")
def offboard_workspace(
    workspace_id: UUID, body: OffboardRequest, session: WorkspaceSessionDep
) -> DeletionReportResponse:
    """Irreversible: export first, then delete. The exact workspace name is
    the confirmation — deliberate friction for a deliberate act."""
    report = OffboardWorkspace(session, workspace_id).delete(confirm_name=body.confirm_name)
    return DeletionReportResponse(
        workspace_id=report.workspace_id, rows_deleted_by_table=report.rows_deleted_by_table
    )
