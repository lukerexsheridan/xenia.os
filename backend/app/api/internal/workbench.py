"""The research workbench — the concierge kit's API (Doc 10, Sprints 5-6).

Ugly-but-honest by decree; its users number exactly one. The internal
sub-application's Swagger UI is the "UI-lite": every operation the concierge
needs — snapshot, register, capture, brief, finalise, render — as documented
endpoints behind Editor authorisation. Ring-1 operations name their target
workspace in the path; Ring-2 operations (world facts) have no workspace at
all.
"""

import time
from datetime import datetime
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.api.internal.deps import EditorContext, get_editor_context, get_workspace_session
from app.core.config import get_settings
from app.core.errors import NotFoundError
from app.core.logging import current_request_id
from app.domain.confidence import ConfidenceBand
from app.domain.dna import DecayClass, DnaCategory, ElementOrigin
from app.domain.evidence import EvidenceType, FreshnessClass
from app.domain.research_brief import BriefSection, BriefSectionCode, completeness_problems
from app.domain.rubric import RubricDimension
from app.integrations.object_storage import S3ObjectStore
from app.integrations.sources.http_transport import HttpxTransport
from app.integrations.sources.politeness import PolitenessEngine
from app.repositories.audit import SqlAuditEntryRepo
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.dna import SqlDnaRepo
from app.repositories.evidence import SqlEvidenceRepo
from app.repositories.identity import SqlIdentityRepo
from app.repositories.prospects import SqlProspectRepo
from app.repositories.research_briefs import SqlResearchBriefRepo, StoredResearchBrief
from app.repositories.snapshots import SqlSourceSnapshotRepo
from app.services.author_research_brief import (
    CreateResearchBrief,
    FinaliseResearchBrief,
    UpdateBriefSection,
)
from app.services.capture_evidence import CaptureEvidence
from app.services.capture_snapshot import CaptureSnapshot
from app.services.create_dna import CreateDna, DnaElementInput
from app.services.create_prospect import CreateProspect
from app.services.documents import RenderBriefPdf, RenderDnaDocument

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
