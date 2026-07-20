"""The delivered brief — behind the Editor gate, always (Doc 10, Epic 9).

The one delivery read model is `deliverable_for_prospect`, whose query bakes
in FINAL and whose signature takes no status: this surface structurally
cannot serve an unapproved brief. A draft is a 404 here, indistinguishable
from absence — the gate is the only door.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_authenticated_context, get_db_session
from app.core.errors import NotFoundError
from app.domain.confidence import band_for
from app.domain.research_brief import SECTION_TITLES
from app.repositories.research_briefs import SqlResearchBriefRepo
from app.services.authenticate_user import AuthenticatedContext

router = APIRouter()


class BriefSectionResponse(BaseModel):
    code: str
    title: str
    content: str
    cited_evidence_ids: list[UUID]


class ReceiptResponse(BaseModel):
    number: int
    claim: str
    evidence_type: str
    observed_at: str


class DeliveredBriefResponse(BaseModel):
    brief_id: UUID
    prospect_id: UUID
    sections: list[BriefSectionResponse]
    couldnt_see: list[str]
    confidence_word: str  # assigned by domain rule, rendered verbatim (AP5)
    receipts: list[ReceiptResponse]
    finalised_at: str


@router.get("/prospects/{prospect_id}/brief")
def get_delivered_brief(
    prospect_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    context: Annotated[AuthenticatedContext, Depends(get_authenticated_context)],
) -> DeliveredBriefResponse:
    stored = SqlResearchBriefRepo(session, context.workspace.id).deliverable_for_prospect(
        prospect_id
    )
    if stored is None or stored.finalised_at is None:
        raise NotFoundError("no approved brief for this prospect")
    return DeliveredBriefResponse(
        brief_id=stored.brief.id,
        prospect_id=stored.brief.prospect_id,
        sections=[
            BriefSectionResponse(
                code=section.code.value,
                title=SECTION_TITLES[section.code],
                content=section.content,
                cited_evidence_ids=list(section.cited_evidence_ids),
            )
            for section in stored.brief.sections
        ],
        couldnt_see=list(stored.brief.couldnt_see),
        confidence_word=band_for(stored.brief.confidence_score).value,
        receipts=[
            ReceiptResponse(
                number=row.number,
                claim=row.claim,
                evidence_type=row.evidence_type.value,
                observed_at=row.observed_at.isoformat(),
            )
            for row in (stored.receipt_table or ())
        ],
        finalised_at=stored.finalised_at.isoformat(),
    )
