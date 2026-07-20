"""AssembleQueue — the bounded weekly set, accountably (Doc 10, Sprint 14).

Deterministic end to end: score every live prospect against the DNA and its
business's fresh signals, run the disqualifier gate before ranking exists,
rank what remains, bound the set, explain every adjacency, and persist the
week whole (replace-by-week, so re-assembly converges). A thin week ships
thin — padding is structurally impossible because nothing here can invent a
candidate (Doc 03 P3).
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.domain.audit import AuditAction
from app.domain.dna import Dna
from app.domain.prospect import Prospect, ProspectStatus
from app.domain.recommendation import (
    AssembledQueue,
    Candidate,
    Recommendation,
    RecommendationPolarity,
    assemble_queue,
    exclusion_reason,
    find_disqualifier_matches,
    rank_reason,
    score_against_dna,
    week_key_for,
)
from app.repositories.audit import SqlAuditEntryRepo
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.dna import SqlDnaRepo
from app.repositories.knowledge import SqlKnowledgeRepo
from app.repositories.prospects import SqlProspectRepo
from app.repositories.recommendations import SqlRecommendationRepo

# Prospects still in play: resolved relationships and already-pursued
# prospects are not re-recommended (Doc 08 §5's lifecycle).
_LIVE_STATUSES = frozenset({ProspectStatus.SURFACED, ProspectStatus.RECOMMENDED})


@dataclass(frozen=True)
class AssemblyResult:
    week_key: str
    recommended: int
    excluded: int


class AssembleQueue:
    def __init__(
        self,
        dna_repo: SqlDnaRepo,
        prospect_repo: SqlProspectRepo,
        business_record_repo: SqlBusinessRecordRepo,
        knowledge_repo: SqlKnowledgeRepo,
        recommendation_repo: SqlRecommendationRepo,
        audit_repo: SqlAuditEntryRepo,
    ) -> None:
        self._dna_repo = dna_repo
        self._prospect_repo = prospect_repo
        self._business_record_repo = business_record_repo
        self._knowledge_repo = knowledge_repo
        self._recommendation_repo = recommendation_repo
        self._audit_repo = audit_repo

    def execute(
        self, *, workspace_id: UUID, actor_user_id: UUID | None = None, now: datetime | None = None
    ) -> AssemblyResult:
        current = now or datetime.now(UTC)
        week_key = week_key_for(current)
        dna = self._dna_repo.get()
        if dna is None:
            # No DNA, no judgment: an empty week, honestly (Doc 03 P3).
            self._recommendation_repo.replace_week(week_key, [])
            return AssemblyResult(week_key=week_key, recommended=0, excluded=0)

        prospects = [
            prospect for prospect in self._prospect_repo.list() if prospect.status in _LIVE_STATUSES
        ]
        candidates = tuple(self._candidate(prospect, dna, current) for prospect in prospects)
        assembled = assemble_queue(candidates, week_key=week_key)

        records = self._records(assembled, workspace_id, current)
        self._recommendation_repo.replace_week(week_key, records)
        self._advance_surfaced(assembled, prospects)
        self._audit_repo.append(
            action=AuditAction.QUEUE_ASSEMBLED,
            target_type="week",
            target_id=week_key,
            actor_user_id=actor_user_id,
            request_id=None,
        )
        return AssemblyResult(
            week_key=week_key,
            recommended=len(assembled.ranked),
            excluded=len(assembled.excluded),
        )

    def _candidate(self, prospect: Prospect, dna: Dna, now: datetime) -> Candidate:
        record = self._business_record_repo.get(prospect.business_record_id)
        signals = tuple(self._knowledge_repo.signals_for_business(prospect.business_record_id))
        return Candidate(
            prospect_id=prospect.id,
            business_name=record.canonical_name if record else "this business",
            score=score_against_dna(dna, signals, now=now),
            disqualified_by=find_disqualifier_matches(dna, signals, now=now),
        )

    def _records(
        self,
        assembled: AssembledQueue,
        workspace_id: UUID,
        now: datetime,
    ) -> list[Recommendation]:
        records: list[Recommendation] = []
        ranked = assembled.ranked
        for index, candidate in enumerate(ranked):
            below = ranked[index + 1] if index + 1 < len(ranked) else None
            records.append(
                Recommendation(
                    id=uuid4(),
                    workspace_id=workspace_id,
                    prospect_id=candidate.prospect_id,
                    week_key=assembled.week_key,
                    polarity=RecommendationPolarity.RECOMMENDED,
                    rank=index + 1,
                    score=candidate.score,
                    rank_reason=None if below is None else rank_reason(candidate, below),
                    exclusion_reason=None,
                    created_at=now,
                )
            )
        for candidate in assembled.excluded:
            records.append(
                Recommendation(
                    id=uuid4(),
                    workspace_id=workspace_id,
                    prospect_id=candidate.prospect_id,
                    week_key=assembled.week_key,
                    polarity=RecommendationPolarity.EXCLUDED,
                    rank=None,
                    score=candidate.score,
                    rank_reason=None,
                    exclusion_reason=exclusion_reason(candidate),
                    created_at=now,
                )
            )
        return records

    def _advance_surfaced(self, assembled: AssembledQueue, prospects: list[Prospect]) -> None:
        ranked_ids = {candidate.prospect_id for candidate in assembled.ranked}
        for prospect in prospects:
            if prospect.id in ranked_ids and prospect.status is ProspectStatus.SURFACED:
                self._prospect_repo.save_status(prospect.advance(ProspectStatus.RECOMMENDED))


def build_assemble_queue(session: Session, workspace_id: UUID) -> AssembleQueue:
    """The one composition root for assembly. Three call sites (the /v1
    correction path, the internal workbench trigger, the Monday job) must
    wire identical dependencies; a drifted copy would mean 'the same queue'
    assembled differently depending on who asked."""
    return AssembleQueue(
        SqlDnaRepo(session, workspace_id),
        SqlProspectRepo(session, workspace_id),
        SqlBusinessRecordRepo(session),
        SqlKnowledgeRepo(session),
        SqlRecommendationRepo(session, workspace_id),
        SqlAuditEntryRepo(session, workspace_id),
    )
