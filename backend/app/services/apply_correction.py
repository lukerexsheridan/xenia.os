"""ApplyCorrection — applied first, named effect returned, never argued with
(Doc 06 §6; Doc 08 §4).

The contract: the correction lands on the DNA immediately (withdraw for
"this element is wrong", demote for "this weighs too much"), the week's
queue is re-assembled in the same transaction, and the response *names the
consequence* — a deterministic diff of the queue before and after. Evidence
corrections are a quality event, not a preference: they are logged for the
Editor and touch nothing, and the effect summary says exactly that.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.core.errors import NotFoundError
from app.domain.audit import AuditAction
from app.domain.correction import Correction, CorrectionTargetKind
from app.domain.recommendation import (
    AssembledQueue,
    Candidate,
    NamedEffect,
    Recommendation,
    RecommendationPolarity,
    ScoreBreakdown,
    named_effect,
    week_key_for,
)
from app.repositories.audit import SqlAuditEntryRepo
from app.repositories.dna import SqlDnaRepo
from app.repositories.recommendations import SqlRecommendationRepo
from app.repositories.teaching import SqlTeachingRepo
from app.services.assemble_queue import AssembleQueue

_EVIDENCE_EFFECT = "Logged for the Editor's review this week — no change to this week's queue"


@dataclass(frozen=True)
class CorrectionResult:
    correction: Correction
    effect: NamedEffect


class ApplyCorrection:
    def __init__(
        self,
        dna_repo: SqlDnaRepo,
        recommendation_repo: SqlRecommendationRepo,
        teaching_repo: SqlTeachingRepo,
        assemble_queue: AssembleQueue,
        audit_repo: SqlAuditEntryRepo,
    ) -> None:
        self._dna_repo = dna_repo
        self._recommendation_repo = recommendation_repo
        self._teaching_repo = teaching_repo
        self._assemble_queue = assemble_queue
        self._audit_repo = audit_repo

    def execute(
        self,
        *,
        workspace_id: UUID,
        target_kind: CorrectionTargetKind,
        target_id: UUID,
        reason: str | None,
        corrected_by: UUID,
        request_id: str | None = None,
        now: datetime | None = None,
    ) -> CorrectionResult:
        current = now or datetime.now(UTC)
        if target_kind is CorrectionTargetKind.EVIDENCE_ITEM:
            effect = NamedEffect(
                summary=_EVIDENCE_EFFECT,
                removed_prospect_ids=(),
                added_prospect_ids=(),
                reranked_count=0,
            )
        else:
            effect = self._apply_to_dna(workspace_id, target_kind, target_id, current)

        correction = Correction(
            id=uuid4(),
            workspace_id=workspace_id,
            target_kind=target_kind,
            target_id=target_id,
            reason=reason,
            corrected_by=corrected_by,
            corrected_at=current,
        )
        self._teaching_repo.add_correction(correction, effect_summary=effect.summary)
        self._audit_repo.append(
            action=AuditAction.CORRECTION_APPLIED,
            target_type=target_kind.value,
            target_id=str(target_id),
            actor_user_id=corrected_by,
            request_id=request_id,
        )
        return CorrectionResult(correction=correction, effect=effect)

    def _apply_to_dna(
        self,
        workspace_id: UUID,
        target_kind: CorrectionTargetKind,
        element_id: UUID,
        now: datetime,
    ) -> NamedEffect:
        dna = self._dna_repo.get()
        if dna is None:
            raise NotFoundError("no DNA exists in this workspace")
        before = self._stored_queue(week_key_for(now))

        if target_kind is CorrectionTargetKind.DNA_ELEMENT:
            evolved, event = dna.withdraw_element(element_id, now=now)
        else:  # SCORE_FACTOR: the weight is questioned, not the truth
            evolved, event = dna.demote_element(element_id, now=now)
        self._dna_repo.save(evolved, (event,))

        # The one-cycle promise, honoured in the same transaction: the next
        # queue is *this* queue, re-assembled.
        self._assemble_queue.execute(workspace_id=workspace_id, now=now)
        after = self._stored_queue(week_key_for(now))
        return named_effect(before, after)

    def _stored_queue(self, week_key: str) -> AssembledQueue:
        """The stored week as a comparable queue: the diff needs identity and
        order, which the persisted set carries."""
        stored = self._recommendation_repo.list_week(week_key)
        return AssembledQueue(
            week_key=week_key,
            ranked=tuple(
                _as_candidate(item)
                for item in stored
                if item.polarity is RecommendationPolarity.RECOMMENDED
            ),
            excluded=tuple(
                _as_candidate(item)
                for item in stored
                if item.polarity is RecommendationPolarity.EXCLUDED
            ),
        )


def _as_candidate(recommendation: Recommendation) -> Candidate:
    return Candidate(
        prospect_id=recommendation.prospect_id,
        business_name="",
        score=ScoreBreakdown(components=recommendation.score.components),
        disqualified_by=(),
    )
