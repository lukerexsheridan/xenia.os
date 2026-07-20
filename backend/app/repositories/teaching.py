"""The teaching events — decisions, corrections, outcomes (Ring 1).

Append-only by contract *and* by policy: the repository exposes no update or
delete, and the tables carry no UPDATE/DELETE RLS policy — ground truth and
teaching history are never rewritten (Doc 03 §7; Doc 04 §5).
"""

from uuid import UUID

from sqlalchemy import func, select

from app.domain.correction import Correction, CorrectionTargetKind
from app.domain.decision import Decision, DecisionKind, DeclineChip
from app.domain.outcome import Outcome, OutcomeKind
from app.repositories.base import WorkspaceScopedRepository
from app.repositories.orm import CorrectionRow, DecisionRow, OutcomeRow


class SqlTeachingRepo(WorkspaceScopedRepository):
    def add_decision(self, decision: Decision) -> None:
        self._session.add(
            DecisionRow(
                id=decision.id,
                workspace_id=self._workspace_id,
                recommendation_id=decision.recommendation_id,
                kind=decision.kind.value,
                chip=decision.chip.value if decision.chip else None,
                reason=decision.reason,
                decided_by=decision.decided_by,
                decided_at=decision.decided_at,
            )
        )
        self._session.flush()

    def decision_for(self, recommendation_id: UUID) -> Decision | None:
        row = self._session.execute(
            select(DecisionRow).where(
                DecisionRow.workspace_id == self._workspace_id,
                DecisionRow.recommendation_id == recommendation_id,
            )
        ).scalar_one_or_none()
        if row is None:
            return None
        return Decision(
            id=row.id,
            workspace_id=row.workspace_id,
            recommendation_id=row.recommendation_id,
            kind=DecisionKind(row.kind),
            reason=row.reason,
            decided_by=row.decided_by,
            decided_at=row.decided_at,
            chip=DeclineChip(row.chip) if row.chip else None,
        )

    def decline_chip_count(self, chip: DeclineChip) -> int:
        """How often this chip has been tapped — the pattern threshold's
        input (Doc 04 §5: 'third time — adjusting')."""
        count = self._session.execute(
            select(func.count())
            .select_from(DecisionRow)
            .where(
                DecisionRow.workspace_id == self._workspace_id,
                DecisionRow.kind == DecisionKind.DECLINE.value,
                DecisionRow.chip == chip.value,
            )
        ).scalar_one()
        return int(count)

    def add_correction(self, correction: Correction, *, effect_summary: str) -> None:
        self._session.add(
            CorrectionRow(
                id=correction.id,
                workspace_id=self._workspace_id,
                target_kind=correction.target_kind.value,
                target_id=correction.target_id,
                reason=correction.reason,
                effect_summary=effect_summary,
                corrected_by=correction.corrected_by,
                corrected_at=correction.corrected_at,
            )
        )
        self._session.flush()

    def corrections(self) -> list[Correction]:
        rows = (
            self._session.execute(
                select(CorrectionRow)
                .where(CorrectionRow.workspace_id == self._workspace_id)
                .order_by(CorrectionRow.corrected_at, CorrectionRow.id)
            )
            .scalars()
            .all()
        )
        return [
            Correction(
                id=row.id,
                workspace_id=row.workspace_id,
                target_kind=CorrectionTargetKind(row.target_kind),
                target_id=row.target_id,
                reason=row.reason,
                corrected_by=row.corrected_by,
                corrected_at=row.corrected_at,
            )
            for row in rows
        ]

    def add_outcome(self, outcome: Outcome) -> None:
        self._session.add(
            OutcomeRow(
                id=outcome.id,
                workspace_id=self._workspace_id,
                prospect_id=outcome.prospect_id,
                kind=outcome.kind.value,
                reason=outcome.reason,
                occurred_at=outcome.occurred_at,
                recorded_by=outcome.recorded_by,
                recorded_at=outcome.recorded_at,
            )
        )
        self._session.flush()

    def outcomes_for_prospect(self, prospect_id: UUID) -> list[Outcome]:
        rows = (
            self._session.execute(
                select(OutcomeRow)
                .where(
                    OutcomeRow.workspace_id == self._workspace_id,
                    OutcomeRow.prospect_id == prospect_id,
                )
                .order_by(OutcomeRow.occurred_at, OutcomeRow.id)
            )
            .scalars()
            .all()
        )
        return [
            Outcome(
                id=row.id,
                workspace_id=row.workspace_id,
                prospect_id=row.prospect_id,
                kind=OutcomeKind(row.kind),
                occurred_at=row.occurred_at,
                recorded_by=row.recorded_by,
                recorded_at=row.recorded_at,
                reason=row.reason,
            )
            for row in rows
        ]

    def decision_counts(self) -> dict[str, int]:
        rows = self._session.execute(
            select(DecisionRow.kind, func.count())
            .where(DecisionRow.workspace_id == self._workspace_id)
            .group_by(DecisionRow.kind)
        ).all()
        return {str(kind): int(count) for kind, count in rows}

    def correction_count(self) -> int:
        count = self._session.execute(
            select(func.count())
            .select_from(CorrectionRow)
            .where(CorrectionRow.workspace_id == self._workspace_id)
        ).scalar_one()
        return int(count)

    def prospects_with_outcomes(self) -> set[UUID]:
        rows = self._session.execute(
            select(OutcomeRow.prospect_id)
            .where(OutcomeRow.workspace_id == self._workspace_id)
            .distinct()
        ).all()
        return {row[0] for row in rows}
