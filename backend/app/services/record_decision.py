"""RecordDecision — the teaching event and what it teaches (Doc 10, Sprint 15).

The ten-second loop's server half: store the decision, act on its kind
(pursue advances the lifecycle and schedules the outcome prompt), and learn
from decline chips *synchronously* — a correction cycle that waits for a
nightly job is a correction visibly ignored for a day (Doc 04 §5:
corrections apply within one cycle; the cheapest cycle is "now"). Pattern
chips generalise at the minimum-occurrence threshold; the structural chip
raises a proposal, never a law (Doc 03 §8).
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from app.core.errors import ConflictError, NotFoundError, XeniaError
from app.domain.audit import AuditAction
from app.domain.decision import (
    NON_TEACHING_CHIPS,
    PATTERN_CHIP_LESSONS,
    STRUCTURAL_CHIPS,
    Decision,
    DecisionKind,
    DeclineChip,
)
from app.domain.dna import (
    LEARNED_INITIAL_CONFIDENCE,
    MINIMUM_PATTERN_OCCURRENCES,
    ChangeAuthor,
    DecayClass,
    Dna,
    DnaCategory,
    DnaElement,
    DnaProposal,
    ElementOrigin,
    ProposalStatus,
)
from app.domain.prospect import ProspectStatus
from app.repositories.audit import SqlAuditEntryRepo
from app.repositories.dna import SqlDnaRepo
from app.repositories.jobs import JobQueue
from app.repositories.prospects import SqlProspectRepo
from app.repositories.recommendations import SqlRecommendationRepo
from app.repositories.teaching import SqlTeachingRepo

# [calibrates] — when to nudge for ground truth after a pursue (Doc 03 §7:
# Xenia prompts, never assumes).
OUTCOME_PROMPT_DELAY = timedelta(days=14)


@dataclass(frozen=True)
class DecisionResult:
    decision: Decision
    # The teaching narration, when the decision taught something ("third
    # time — adjusting", Doc 04 §5) — shipped as data, rendered verbatim.
    lesson: str | None


class RecordDecision:
    def __init__(
        self,
        recommendation_repo: SqlRecommendationRepo,
        teaching_repo: SqlTeachingRepo,
        prospect_repo: SqlProspectRepo,
        dna_repo: SqlDnaRepo,
        job_repo: JobQueue,
        audit_repo: SqlAuditEntryRepo,
    ) -> None:
        self._recommendation_repo = recommendation_repo
        self._teaching_repo = teaching_repo
        self._prospect_repo = prospect_repo
        self._dna_repo = dna_repo
        self._job_repo = job_repo
        self._audit_repo = audit_repo

    def execute(
        self,
        *,
        workspace_id: UUID,
        recommendation_id: UUID,
        kind: DecisionKind,
        chip: DeclineChip | None,
        reason: str | None,
        decided_by: UUID,
        request_id: str | None = None,
        now: datetime | None = None,
    ) -> DecisionResult:
        current = now or datetime.now(UTC)
        recommendation = self._recommendation_repo.get(recommendation_id)
        if recommendation is None:
            raise NotFoundError("recommendation not found in this workspace")
        if self._teaching_repo.decision_for(recommendation_id) is not None:
            raise ConflictError("this recommendation is already resolved by a decision")
        if chip is not None and kind is not DecisionKind.DECLINE:
            raise XeniaError("reason chips belong to declines (Doc 06 §6)")

        decision = Decision(
            id=uuid4(),
            workspace_id=workspace_id,
            recommendation_id=recommendation_id,
            kind=kind,
            reason=reason,
            decided_by=decided_by,
            decided_at=current,
            chip=chip,
        )
        self._teaching_repo.add_decision(decision)
        self._audit_repo.append(
            action=AuditAction.DECISION_RECORDED,
            target_type="recommendation",
            target_id=str(recommendation_id),
            actor_user_id=decided_by,
            request_id=request_id,
        )

        if kind is DecisionKind.PURSUE:
            self._on_pursue(recommendation.prospect_id, workspace_id, current)
        lesson = self._learn(chip, current) if kind is DecisionKind.DECLINE else None
        return DecisionResult(decision=decision, lesson=lesson)

    def _on_pursue(self, prospect_id: UUID, workspace_id: UUID, now: datetime) -> None:
        prospect = self._prospect_repo.get(prospect_id)
        if prospect is not None and prospect.status < ProspectStatus.PURSUED:
            self._prospect_repo.save_status(prospect.advance(ProspectStatus.PURSUED))
        # The outcome prompt: scheduled now, asked later, never assumed
        # (Doc 03 §7). Idempotent per prospect — one nudge, not a drumbeat.
        self._job_repo.enqueue(
            "outcome_prompt",
            idempotency_key=f"outcome_prompt:{prospect_id}",
            payload={"prospect_id": str(prospect_id), "workspace_id": str(workspace_id)},
            run_at=now + OUTCOME_PROMPT_DELAY,
            workspace_id=workspace_id,
        )

    def _learn(self, chip: DeclineChip | None, now: datetime) -> str | None:
        """Chips teach by their taxonomy's rules — synchronously, so the
        next assembly already knows (Doc 04 §5's one-cycle promise)."""
        if chip is None or chip in NON_TEACHING_CHIPS:
            return None
        occurrences = self._teaching_repo.decline_chip_count(chip)
        if occurrences < MINIMUM_PATTERN_OCCURRENCES:
            return None
        dna = self._dna_repo.get()
        if dna is None:
            return None

        if chip in STRUCTURAL_CHIPS:
            return self._propose_disqualifier(dna, occurrences, now)

        category, statement = PATTERN_CHIP_LESSONS[chip]
        if any(element.statement == statement for element in dna.elements):
            return None  # this lesson is already in the DNA
        element = DnaElement(
            id=uuid4(),
            category=category,
            statement=statement,
            confidence=LEARNED_INITIAL_CONFIDENCE,
            decay_class=DecayClass.LEARNED_PREFERENCE,
            origin=ElementOrigin.BEHAVIOUR_PATTERN,
            created_at=now,
            last_reinforced_at=now,
        )
        evolved, event = dna.add_learned_element(element, occurrences=occurrences, now=now)
        self._dna_repo.save(evolved, (event,))
        return f"Third time — adjusting: {statement.lower()}"

    def _propose_disqualifier(self, dna: Dna, occurrences: int, now: datetime) -> str | None:
        statement = "Businesses of the kind repeatedly declined as 'not our kind of client'"
        if self._dna_repo.open_proposal_exists_for_statement(statement):
            return None
        proposal = DnaProposal(
            id=uuid4(),
            dna_id=dna.id,
            element=DnaElement(
                id=uuid4(),
                category=DnaCategory.DISQUALIFIERS,
                statement=statement,
                confidence=1.0,
                decay_class=DecayClass.CUSTOMER_LAW,
                origin=ElementOrigin.CORRECTION,
                created_at=now,
                last_reinforced_at=now,
            ),
            rationale=(
                f"{occurrences} declines cited 'not our kind of client' — a repeated "
                "not-our-kind smells like a missing disqualifier. Proposed for your "
                "endorsement; nothing changes until you sign it (Doc 03 §8)."
            ),
            proposed_by=ChangeAuthor.XENIA,
            status=ProposalStatus.PROPOSED,
            proposed_at=now,
        )
        self._dna_repo.add_proposal(proposal)
        return (
            "I've noticed a pattern in your declines — I've proposed a new "
            "disqualifier for your endorsement"
        )
