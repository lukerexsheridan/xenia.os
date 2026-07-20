"""RecordOutcome — ground truth arrives, and the win teaches (Doc 03 §7).

Outcomes are always human-recorded (the domain type has no machine-author
affordance) and append-only. A terminal outcome resolves the prospect's
lifecycle; a WON outcome reinforces exactly the DNA elements that argued for
the recommendation — the decomposition stored at assembly time is the list
of elements that earned the credit, so "Xenia learned from our win" is a
statement about named elements, not vibes (Doc 04 §5: outcomes are the
strongest signal).
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.core.errors import NotFoundError
from app.domain.audit import AuditAction
from app.domain.dna import ChangeCause, DnaChangeEvent
from app.domain.outcome import Outcome, OutcomeKind
from app.domain.prospect import ProspectStatus
from app.domain.recommendation import RecommendationPolarity
from app.repositories.audit import SqlAuditEntryRepo
from app.repositories.dna import SqlDnaRepo
from app.repositories.prospects import SqlProspectRepo
from app.repositories.recommendations import SqlRecommendationRepo
from app.repositories.teaching import SqlTeachingRepo

_TERMINAL = frozenset({OutcomeKind.WON, OutcomeKind.LOST, OutcomeKind.DISQUALIFIED})


@dataclass(frozen=True)
class OutcomeResult:
    outcome: Outcome
    # Which DNA elements a win reinforced, by statement — the learning
    # narration's raw material ("Xenia learned from our win").
    reinforced_statements: tuple[str, ...]


class RecordOutcome:
    def __init__(
        self,
        prospect_repo: SqlProspectRepo,
        teaching_repo: SqlTeachingRepo,
        recommendation_repo: SqlRecommendationRepo,
        dna_repo: SqlDnaRepo,
        audit_repo: SqlAuditEntryRepo,
    ) -> None:
        self._prospect_repo = prospect_repo
        self._teaching_repo = teaching_repo
        self._recommendation_repo = recommendation_repo
        self._dna_repo = dna_repo
        self._audit_repo = audit_repo

    def execute(
        self,
        *,
        workspace_id: UUID,
        prospect_id: UUID,
        kind: OutcomeKind,
        occurred_at: datetime,
        reason: str | None,
        recorded_by: UUID,
        request_id: str | None = None,
        now: datetime | None = None,
    ) -> OutcomeResult:
        current = now or datetime.now(UTC)
        prospect = self._prospect_repo.get(prospect_id)
        if prospect is None:
            raise NotFoundError("prospect not found in this workspace")

        outcome = Outcome(
            id=uuid4(),
            workspace_id=workspace_id,
            prospect_id=prospect_id,
            kind=kind,
            occurred_at=occurred_at,
            recorded_by=recorded_by,
            recorded_at=current,
            reason=reason,
        )
        self._teaching_repo.add_outcome(outcome)
        if kind in _TERMINAL and prospect.status < ProspectStatus.RESOLVED:
            self._prospect_repo.save_status(prospect.advance(ProspectStatus.RESOLVED))

        reinforced = self._reinforce_on_win(prospect_id, current) if kind is OutcomeKind.WON else ()
        self._audit_repo.append(
            action=AuditAction.OUTCOME_RECORDED,
            target_type="prospect",
            target_id=str(prospect_id),
            actor_user_id=recorded_by,
            request_id=request_id,
        )
        return OutcomeResult(outcome=outcome, reinforced_statements=reinforced)

    def _reinforce_on_win(self, prospect_id: UUID, now: datetime) -> tuple[str, ...]:
        """Credit assignment by receipt: the elements that scored this
        prospect are the elements the win corroborates."""
        dna = self._dna_repo.get()
        week_key = self._recommendation_repo.latest_week_key()
        if dna is None or week_key is None:
            return ()
        recommendation = next(
            (
                item
                for item in self._recommendation_repo.list_week(week_key)
                if item.prospect_id == prospect_id
                and item.polarity is RecommendationPolarity.RECOMMENDED
            ),
            None,
        )
        if recommendation is None:
            return ()
        element_ids: list[UUID] = []
        for component in recommendation.score.components:
            if component.dna_element_id not in element_ids:
                element_ids.append(component.dna_element_id)
        events: list[DnaChangeEvent] = []
        statements: list[str] = []
        current = dna
        for element_id in element_ids:
            if all(element.id != element_id for element in current.elements):
                continue  # withdrawn since the recommendation was assembled
            current, event = current.reinforce_element(
                element_id, cause=ChangeCause.OUTCOME_PATTERN, now=now
            )
            events.append(event)
            statements.append(current.element(element_id).statement)
        if events:
            self._dna_repo.save(current, tuple(events))
        return tuple(statements)
