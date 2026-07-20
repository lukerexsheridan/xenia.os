"""Opener drafts (Doc 03 C6): composed on request, always editable, never
sent — no send path exists anywhere in this system (N1/N3)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai.pipelines.compose_opener import ComposeOpener
from app.ai.providers.openai_responses import OpenAIResponsesProvider
from app.api.deps import get_authenticated_context, get_db_session
from app.core.config import get_settings
from app.core.errors import NotFoundError
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.drafts import SqlDraftRepo
from app.repositories.interview import SqlInterviewRepo
from app.repositories.knowledge import SqlKnowledgeRepo
from app.repositories.prospects import SqlProspectRepo
from app.repositories.research_briefs import SqlResearchBriefRepo
from app.services.authenticate_user import AuthenticatedContext
from app.services.compose_draft import ComposeDraft

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_db_session)]
ContextDep = Annotated[AuthenticatedContext, Depends(get_authenticated_context)]


def get_opener_pipeline() -> ComposeOpener | None:
    settings = get_settings()
    if not settings.openai_api_key:
        return None
    return ComposeOpener(
        OpenAIResponsesProvider(api_key=settings.openai_api_key, model=settings.openai_model)
    )


class DraftResponse(BaseModel):
    body: str | None
    problems: list[str]


@router.post("/prospects/{prospect_id}/draft")
def compose_draft(
    prospect_id: UUID,
    session: SessionDep,
    context: ContextDep,
    pipeline: Annotated[ComposeOpener | None, Depends(get_opener_pipeline)],
) -> DraftResponse:
    workspace_id = context.workspace.id
    result = ComposeDraft(
        pipeline,
        SqlResearchBriefRepo(session, workspace_id),
        SqlProspectRepo(session, workspace_id),
        SqlBusinessRecordRepo(session),
        SqlInterviewRepo(session, workspace_id),
        SqlDraftRepo(session, workspace_id),
        SqlKnowledgeRepo(session),
    ).execute(prospect_id=prospect_id)
    return DraftResponse(body=result.body, problems=list(result.problems))


@router.get("/prospects/{prospect_id}/draft")
def get_draft(prospect_id: UUID, session: SessionDep, context: ContextDep) -> DraftResponse:
    body = SqlDraftRepo(session, context.workspace.id).get_for_prospect(prospect_id)
    if body is None:
        raise NotFoundError("no draft yet — compose one from the approved brief")
    return DraftResponse(body=body, problems=[])


class DraftEditRequest(BaseModel):
    body: str = Field(min_length=1, max_length=5000)


@router.put("/prospects/{prospect_id}/draft")
def edit_draft(
    prospect_id: UUID, request: DraftEditRequest, session: SessionDep, context: ContextDep
) -> DraftResponse:
    """Always-editable: the founder's edit is the final word (and a voice
    signal for later — recorded by the save, judged by nobody)."""
    SqlDraftRepo(session, context.workspace.id).save(prospect_id, request.body)
    return DraftResponse(body=request.body, problems=[])
