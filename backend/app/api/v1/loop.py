"""The loop's back half as /v1 resources (Doc 10, Epic 8).

The queue with its decomposed scores and visible exclusions, decisions,
corrections with the synchronous named effect, outcomes, and the proposal
signature moment. Everything a client renders — confidence words, rank
reasons, effect sentences, lesson narrations — arrives from here as data
(AP5): the frontend may be clever about latency, never about rules.
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_authenticated_context, get_db_session
from app.core.logging import current_request_id
from app.domain.correction import CorrectionTargetKind
from app.domain.decision import DecisionKind, DeclineChip
from app.domain.dna import ProposalStatus
from app.domain.outcome import OutcomeKind
from app.domain.recommendation import Recommendation, RecommendationPolarity
from app.repositories.audit import SqlAuditEntryRepo
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.dna import SqlDnaRepo
from app.repositories.jobs import JobQueue
from app.repositories.knowledge import SqlKnowledgeRepo
from app.repositories.prospects import SqlProspectRepo
from app.repositories.recommendations import SqlRecommendationRepo
from app.repositories.teaching import SqlTeachingRepo
from app.services.apply_correction import ApplyCorrection
from app.services.assemble_queue import AssembleQueue
from app.services.authenticate_user import AuthenticatedContext
from app.services.decide_dna_proposal import DecideDnaProposal
from app.services.record_decision import RecordDecision
from app.services.record_outcome import RecordOutcome

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_db_session)]
ContextDep = Annotated[AuthenticatedContext, Depends(get_authenticated_context)]


def _assembler(session: Session, workspace_id: UUID) -> AssembleQueue:
    return AssembleQueue(
        SqlDnaRepo(session, workspace_id),
        SqlProspectRepo(session, workspace_id),
        SqlBusinessRecordRepo(session),
        SqlKnowledgeRepo(session),
        SqlRecommendationRepo(session, workspace_id),
        SqlAuditEntryRepo(session, workspace_id),
    )


class ScoreComponentResponse(BaseModel):
    dna_statement: str
    signal_name: str
    signal_family: str
    supporting_evidence_ids: list[UUID]
    contribution: float


class QueueItemResponse(BaseModel):
    recommendation_id: UUID
    prospect_id: UUID
    polarity: RecommendationPolarity
    rank: int | None
    confidence_word: str  # one of the four, assigned by domain rule (AP5)
    components: list[ScoreComponentResponse]
    rank_reason: str | None
    exclusion_reason: str | None


class QueueResponse(BaseModel):
    week_key: str
    items: list[QueueItemResponse]


def _item_response(recommendation: Recommendation) -> QueueItemResponse:
    return QueueItemResponse(
        recommendation_id=recommendation.id,
        prospect_id=recommendation.prospect_id,
        polarity=recommendation.polarity,
        rank=recommendation.rank,
        confidence_word=recommendation.score.band.value,
        components=[
            ScoreComponentResponse(
                dna_statement=component.dna_statement,
                signal_name=component.signal_name,
                signal_family=component.signal_family.value,
                supporting_evidence_ids=list(component.supporting_evidence_ids),
                contribution=component.contribution,
            )
            for component in recommendation.score.components
        ],
        rank_reason=recommendation.rank_reason,
        exclusion_reason=recommendation.exclusion_reason,
    )


@router.get("/queue")
def get_queue(session: SessionDep, context: ContextDep) -> QueueResponse:
    """This week's bounded set — ranked items first, the visible exclusion
    at the queue's end (Doc 06 §7). An empty week is an honest week."""
    repo = SqlRecommendationRepo(session, context.workspace.id)
    week_key = repo.latest_week_key()
    if week_key is None:
        return QueueResponse(week_key="", items=[])
    return QueueResponse(
        week_key=week_key, items=[_item_response(item) for item in repo.list_week(week_key)]
    )


class DecisionRequest(BaseModel):
    kind: DecisionKind
    chip: DeclineChip | None = None
    reason: str | None = Field(default=None, max_length=1000)


class DecisionResponse(BaseModel):
    decision_id: UUID
    kind: DecisionKind
    lesson: str | None  # the teaching narration, rendered verbatim


@router.post("/recommendations/{recommendation_id}/decision")
def record_decision(
    recommendation_id: UUID,
    request: DecisionRequest,
    session: SessionDep,
    context: ContextDep,
) -> DecisionResponse:
    workspace_id = context.workspace.id
    result = RecordDecision(
        SqlRecommendationRepo(session, workspace_id),
        SqlTeachingRepo(session, workspace_id),
        SqlProspectRepo(session, workspace_id),
        SqlDnaRepo(session, workspace_id),
        JobQueue(session),
        SqlAuditEntryRepo(session, workspace_id),
    ).execute(
        workspace_id=workspace_id,
        recommendation_id=recommendation_id,
        kind=request.kind,
        chip=request.chip,
        reason=request.reason,
        decided_by=context.user.id,
        request_id=current_request_id(),
    )
    return DecisionResponse(
        decision_id=result.decision.id, kind=result.decision.kind, lesson=result.lesson
    )


class CorrectionRequest(BaseModel):
    target_kind: CorrectionTargetKind
    target_id: UUID
    reason: str | None = Field(default=None, max_length=1000)


class CorrectionResponse(BaseModel):
    correction_id: UUID
    # The named effect (Doc 08 §4): "removes two from this week's queue".
    effect_summary: str
    removed_prospect_ids: list[UUID]
    added_prospect_ids: list[UUID]
    reranked_count: int


@router.post("/corrections")
def apply_correction(
    request: CorrectionRequest, session: SessionDep, context: ContextDep
) -> CorrectionResponse:
    workspace_id = context.workspace.id
    result = ApplyCorrection(
        SqlDnaRepo(session, workspace_id),
        SqlRecommendationRepo(session, workspace_id),
        SqlTeachingRepo(session, workspace_id),
        _assembler(session, workspace_id),
        SqlAuditEntryRepo(session, workspace_id),
    ).execute(
        workspace_id=workspace_id,
        target_kind=request.target_kind,
        target_id=request.target_id,
        reason=request.reason,
        corrected_by=context.user.id,
        request_id=current_request_id(),
    )
    return CorrectionResponse(
        correction_id=result.correction.id,
        effect_summary=result.effect.summary,
        removed_prospect_ids=list(result.effect.removed_prospect_ids),
        added_prospect_ids=list(result.effect.added_prospect_ids),
        reranked_count=result.effect.reranked_count,
    )


class OutcomeRequest(BaseModel):
    kind: OutcomeKind
    occurred_at: datetime
    reason: str | None = Field(default=None, max_length=1000)


class OutcomeResponse(BaseModel):
    outcome_id: UUID
    kind: OutcomeKind
    reinforced_statements: list[str]  # "Xenia learned from our win", itemised


@router.post("/prospects/{prospect_id}/outcomes")
def record_outcome(
    prospect_id: UUID,
    request: OutcomeRequest,
    session: SessionDep,
    context: ContextDep,
) -> OutcomeResponse:
    workspace_id = context.workspace.id
    result = RecordOutcome(
        SqlProspectRepo(session, workspace_id),
        SqlTeachingRepo(session, workspace_id),
        SqlRecommendationRepo(session, workspace_id),
        SqlDnaRepo(session, workspace_id),
        SqlAuditEntryRepo(session, workspace_id),
    ).execute(
        workspace_id=workspace_id,
        prospect_id=prospect_id,
        kind=request.kind,
        occurred_at=request.occurred_at,
        reason=request.reason,
        recorded_by=context.user.id,
        request_id=current_request_id(),
    )
    return OutcomeResponse(
        outcome_id=result.outcome.id,
        kind=result.outcome.kind,
        reinforced_statements=list(result.reinforced_statements),
    )


class ProposalResponse(BaseModel):
    proposal_id: UUID
    statement: str
    rationale: str
    status: ProposalStatus


@router.get("/dna/proposals")
def list_proposals(session: SessionDep, context: ContextDep) -> list[ProposalResponse]:
    proposals = SqlDnaRepo(session, context.workspace.id).list_proposals()
    return [
        ProposalResponse(
            proposal_id=proposal.id,
            statement=proposal.element.statement,
            rationale=proposal.rationale,
            status=proposal.status,
        )
        for proposal in proposals
    ]


class ProposalDecisionRequest(BaseModel):
    endorse: bool


@router.post("/dna/proposals/{proposal_id}/decision")
def decide_proposal(
    proposal_id: UUID,
    request: ProposalDecisionRequest,
    session: SessionDep,
    context: ContextDep,
) -> ProposalResponse:
    result = DecideDnaProposal(SqlDnaRepo(session, context.workspace.id)).execute(
        proposal_id=proposal_id, endorse=request.endorse
    )
    return ProposalResponse(
        proposal_id=result.proposal.id,
        statement=result.proposal.element.statement,
        rationale=result.proposal.rationale,
        status=result.proposal.status,
    )
