"""The DNA as a /v1 resource: the living document, its changelog, the
endorsement moment, and the exports (Doc 03 C2; Doc 10 Sprint 18-19).

The changelog arrives with the document — an unexplainable DNA change
violates N4, so the explanation ships by default. Export is the customer's
own model as a PDF (shareable with their team, Doc 03 §7); the prospect CSV
carries business names and lifecycle only — no contacts exist in the system
to export, and none ever will (Foundation N1).
"""

import csv
import io
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_authenticated_context, get_db_session
from app.core.errors import NotFoundError
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.dna import SqlDnaRepo
from app.repositories.evidence import SqlEvidenceRepo
from app.repositories.prospects import SqlProspectRepo
from app.repositories.research_briefs import SqlResearchBriefRepo
from app.services.authenticate_user import AuthenticatedContext
from app.services.documents import RenderBriefPdf, RenderDnaDocument

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_db_session)]
ContextDep = Annotated[AuthenticatedContext, Depends(get_authenticated_context)]


class DnaElementResponse(BaseModel):
    element_id: UUID
    category: str
    statement: str
    decay_class: str
    origin: str


class ChangelogEntryResponse(BaseModel):
    cause: str
    author: str
    element_statement: str | None
    occurred_at: str


class ProposalSummaryResponse(BaseModel):
    proposal_id: UUID
    statement: str
    rationale: str
    status: str


class DnaResponse(BaseModel):
    dna_id: UUID
    version: int
    endorsed: bool
    elements: list[DnaElementResponse]
    changelog: list[ChangelogEntryResponse]
    proposals: list[ProposalSummaryResponse]


@router.get("/dna")
def get_dna(session: SessionDep, context: ContextDep) -> DnaResponse:
    repo = SqlDnaRepo(session, context.workspace.id)
    dna = repo.get()
    if dna is None:
        raise NotFoundError("no DNA yet — the interview founds it")
    return DnaResponse(
        dna_id=dna.id,
        version=dna.version,
        endorsed=dna.endorsed,
        elements=[
            DnaElementResponse(
                element_id=element.id,
                category=element.category.value,
                statement=element.statement,
                decay_class=element.decay_class.value,
                origin=element.origin.value,
            )
            for element in dna.elements
        ],
        changelog=[
            ChangelogEntryResponse(
                cause=event.cause.value,
                author=event.author.value,
                element_statement=(
                    event.after.statement
                    if event.after
                    else event.before.statement
                    if event.before
                    else None
                ),
                occurred_at=event.occurred_at.isoformat(),
            )
            for event in repo.changelog(dna.id)
        ],
        proposals=[
            ProposalSummaryResponse(
                proposal_id=proposal.id,
                statement=proposal.element.statement,
                rationale=proposal.rationale,
                status=proposal.status.value,
            )
            for proposal in repo.list_proposals()
        ],
    )


@router.post("/dna/endorse")
def endorse_dna(session: SessionDep, context: ContextDep) -> DnaResponse:
    """The C2 endorsement moment: the customer converts Xenia's model into a
    shared agreement (Doc 03 §3)."""
    repo = SqlDnaRepo(session, context.workspace.id)
    dna = repo.get()
    if dna is None:
        raise NotFoundError("no DNA yet — the interview founds it")
    evolved, event = dna.endorse(now=datetime.now(UTC))
    repo.save(evolved, (event,))
    return get_dna(session, context)


@router.get("/dna/document.pdf")
def export_dna_document(session: SessionDep, context: ContextDep) -> Response:
    pdf = RenderDnaDocument(SqlDnaRepo(session, context.workspace.id)).execute(
        workspace_name=context.workspace.name
    )
    return Response(content=pdf, media_type="application/pdf")


@router.get("/prospects/{prospect_id}/brief.pdf")
def export_brief_pdf(prospect_id: UUID, session: SessionDep, context: ContextDep) -> Response:
    """The shareable artefact — approved briefs only (the Editor gate is the
    only door, Doc 10 Epic 9)."""
    brief_repo = SqlResearchBriefRepo(session, context.workspace.id)
    stored = brief_repo.deliverable_for_prospect(prospect_id)
    if stored is None:
        raise NotFoundError("no approved brief for this prospect")
    pdf = RenderBriefPdf(brief_repo, SqlEvidenceRepo(session)).execute(stored.brief.id)
    return Response(content=pdf, media_type="application/pdf")


@router.get("/prospects/export.csv")
def export_prospects_csv(session: SessionDep, context: ContextDep) -> Response:
    """Lifecycle export: business names and statuses. No contacts exist in
    this system to export, and none ever will (Foundation N1)."""
    prospects = SqlProspectRepo(session, context.workspace.id).list()
    business_repo = SqlBusinessRecordRepo(session)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["business_name", "status", "surfaced_at"])
    for prospect in prospects:
        record = business_repo.get(prospect.business_record_id)
        writer.writerow(
            [
                record.canonical_name if record else "",
                prospect.status.name.lower(),
                prospect.surfaced_at.isoformat(),
            ]
        )
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="prospects.csv"'},
    )
