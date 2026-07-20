"""The DNA interview as a /v1 resource (Doc 10, Sprint 18).

Conversational and resumable: GET returns where the conversation stands,
POST records one answer. The final answer founds the DNA in the same
transaction; endorsement is its own moment on the DNA resource.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_authenticated_context, get_db_session
from app.core.logging import current_request_id
from app.domain.interview import INTERVIEW_SCRIPT
from app.repositories.audit import SqlAuditEntryRepo
from app.repositories.dna import SqlDnaRepo
from app.repositories.interview import SqlInterviewRepo
from app.services.authenticate_user import AuthenticatedContext
from app.services.run_interview import InterviewState, RunInterview

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_db_session)]
ContextDep = Annotated[AuthenticatedContext, Depends(get_authenticated_context)]


def _service(session: Session, workspace_id: UUID) -> RunInterview:
    return RunInterview(
        SqlInterviewRepo(session, workspace_id),
        SqlDnaRepo(session, workspace_id),
        SqlAuditEntryRepo(session, workspace_id),
    )


class AnsweredQuestionResponse(BaseModel):
    question_key: str
    prompt: str
    text: str
    one_per_line: bool


class InterviewStateResponse(BaseModel):
    question_key: str | None
    prompt: str | None
    one_per_line: bool
    answered: int
    total: int
    completed: bool
    dna_created: bool
    # The transcript so far: amendable in place while the interview is open
    # (Doc 13 I6 — the log begins where meaning begins).
    transcript: list[AnsweredQuestionResponse]


def _state_response(state: InterviewState) -> InterviewStateResponse:
    return InterviewStateResponse(
        question_key=state.question.key if state.question else None,
        prompt=state.question.prompt if state.question else None,
        one_per_line=bool(state.question and state.question.one_per_line),
        answered=state.answered,
        total=state.total,
        completed=state.completed,
        dna_created=state.dna_created,
        transcript=[
            AnsweredQuestionResponse(
                question_key=question.key,
                prompt=question.prompt,
                text=state.answers[question.key],
                one_per_line=question.one_per_line,
            )
            for question in INTERVIEW_SCRIPT
            if question.key in state.answers
        ],
    )


@router.get("/interview")
def interview_state(session: SessionDep, context: ContextDep) -> InterviewStateResponse:
    return _state_response(_service(session, context.workspace.id).state())


class AnswerRequest(BaseModel):
    question_key: str
    text: str = Field(max_length=4000)


@router.post("/interview/answers")
def record_interview_answer(
    request: AnswerRequest, session: SessionDep, context: ContextDep
) -> InterviewStateResponse:
    state = _service(session, context.workspace.id).answer(
        workspace_id=context.workspace.id,
        key=request.question_key,
        text=request.text,
        actor_user_id=context.user.id,
        request_id=current_request_id(),
    )
    return _state_response(state)
