"""Recommendations — Ring 1, workspace-scoped; replace-by-week assembly.

The decomposition is stored verbatim (every component names its DNA element,
signal, and evidence — Doc 04 §2's explainability persisted), so a stored
recommendation can always answer "why" without recomputation.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import delete, select

from app.domain.recommendation import (
    Recommendation,
    RecommendationPolarity,
    ScoreBreakdown,
    ScoreComponent,
)
from app.domain.signal import SignalFamily
from app.repositories.base import WorkspaceScopedRepository
from app.repositories.orm import RecommendationRow


def _component_to_json(component: ScoreComponent) -> dict[str, Any]:
    return {
        "dna_element_id": str(component.dna_element_id),
        "dna_statement": component.dna_statement,
        "dna_confidence": component.dna_confidence,
        "signal_id": str(component.signal_id),
        "signal_name": component.signal_name,
        "signal_family": component.signal_family.value,
        "signal_confidence": component.signal_confidence,
        "supporting_evidence_ids": [str(item) for item in component.supporting_evidence_ids],
        "contribution": component.contribution,
    }


def _component_from_json(payload: dict[str, Any]) -> ScoreComponent:
    return ScoreComponent(
        dna_element_id=UUID(payload["dna_element_id"]),
        dna_statement=payload["dna_statement"],
        dna_confidence=payload["dna_confidence"],
        signal_id=UUID(payload["signal_id"]),
        signal_name=payload["signal_name"],
        signal_family=SignalFamily(payload["signal_family"]),
        signal_confidence=payload["signal_confidence"],
        supporting_evidence_ids=tuple(UUID(item) for item in payload["supporting_evidence_ids"]),
        contribution=payload["contribution"],
    )


def _to_domain(row: RecommendationRow) -> Recommendation:
    return Recommendation(
        id=row.id,
        workspace_id=row.workspace_id,
        prospect_id=row.prospect_id,
        week_key=row.week_key,
        polarity=RecommendationPolarity(row.polarity),
        rank=row.rank,
        score=ScoreBreakdown(
            components=tuple(_component_from_json(item) for item in row.components)
        ),
        rank_reason=row.rank_reason,
        exclusion_reason=row.exclusion_reason,
        created_at=row.created_at,
    )


class SqlRecommendationRepo(WorkspaceScopedRepository):
    def replace_week(self, week_key: str, recommendations: list[Recommendation]) -> None:
        """Idempotent weekly assembly: the week's set is replaced whole, so
        re-running assembly converges instead of duplicating."""
        self._session.execute(
            delete(RecommendationRow).where(
                RecommendationRow.workspace_id == self._workspace_id,
                RecommendationRow.week_key == week_key,
            )
        )
        for recommendation in recommendations:
            self._session.add(
                RecommendationRow(
                    id=recommendation.id,
                    workspace_id=self._workspace_id,
                    prospect_id=recommendation.prospect_id,
                    week_key=recommendation.week_key,
                    polarity=recommendation.polarity.value,
                    rank=recommendation.rank,
                    score_total=recommendation.score.total,
                    confidence_band=recommendation.score.band.value,
                    components=[
                        _component_to_json(component)
                        for component in recommendation.score.components
                    ],
                    rank_reason=recommendation.rank_reason,
                    exclusion_reason=recommendation.exclusion_reason,
                )
            )
        self._session.flush()

    def list_week(self, week_key: str) -> list[Recommendation]:
        rows = (
            self._session.execute(
                select(RecommendationRow)
                .where(
                    RecommendationRow.workspace_id == self._workspace_id,
                    RecommendationRow.week_key == week_key,
                )
                # Exclusions (rank NULL) sort last: the queue's end (Doc 06 §7).
                .order_by(RecommendationRow.rank.nulls_last(), RecommendationRow.prospect_id)
            )
            .scalars()
            .all()
        )
        return [_to_domain(row) for row in rows]

    def latest_week_key(self) -> str | None:
        row = self._session.execute(
            select(RecommendationRow.week_key)
            .where(RecommendationRow.workspace_id == self._workspace_id)
            .order_by(RecommendationRow.week_key.desc())
            .limit(1)
        ).scalar_one_or_none()
        return row

    def get(self, recommendation_id: UUID) -> Recommendation | None:
        row = self._session.get(RecommendationRow, recommendation_id)
        if row is None or row.workspace_id != self._workspace_id:
            return None
        return _to_domain(row)
