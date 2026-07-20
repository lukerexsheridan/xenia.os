"""Persistence for the knowledge layer (Epic 5): signals and the AI-call
ledger. Ring 2/ops — deliberately not workspace-scoped (Doc 05 §7)."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.signal import Signal, SignalFamily
from app.repositories.orm import (
    AiCallRecordRow,
    CanonicalContentRow,
    SignalRow,
    SourceSnapshotRow,
)


@dataclass(frozen=True)
class StoredCanonicalItem:
    id: UUID
    item_kind: str
    payload: dict[str, object]
    snapshot_id: UUID
    source_url: str
    fetched_at: datetime


class SqlKnowledgeRepo:
    def __init__(self, session: Session) -> None:
        self._session = session

    # ── canonical inputs to extraction ───────────────────────────────────

    def canonical_items_for_business(self, business_record_id: UUID) -> list[StoredCanonicalItem]:
        rows = self._session.execute(
            select(CanonicalContentRow, SourceSnapshotRow)
            .join(SourceSnapshotRow, CanonicalContentRow.snapshot_id == SourceSnapshotRow.id)
            .where(CanonicalContentRow.business_record_id == business_record_id)
            .order_by(CanonicalContentRow.created_at, CanonicalContentRow.id)
        ).all()
        return [
            StoredCanonicalItem(
                id=content.id,
                item_kind=content.item_kind,
                payload=dict(content.payload),
                snapshot_id=content.snapshot_id,
                source_url=snapshot.url,
                fetched_at=snapshot.fetched_at,
            )
            for content, snapshot in rows
        ]

    # ── signals ──────────────────────────────────────────────────────────

    def upsert_signal(self, signal: Signal) -> None:
        existing = self._session.execute(
            select(SignalRow).where(
                SignalRow.business_record_id == signal.business_record_id,
                SignalRow.name == signal.name,
            )
        ).scalar_one_or_none()
        if existing is None:
            existing = SignalRow(
                id=signal.id,
                business_record_id=signal.business_record_id,
                family=signal.family.value,
                name=signal.name,
                confidence=signal.confidence,
                supporting_evidence_ids=[str(item) for item in signal.supporting_evidence_ids],
                newest_observation_at=signal.newest_observation_at,
                rule_version=signal.rule_version,
                derived_at=signal.derived_at,
            )
            self._session.add(existing)
        else:
            existing.family = signal.family.value
            existing.confidence = signal.confidence
            existing.supporting_evidence_ids = [
                str(item) for item in signal.supporting_evidence_ids
            ]
            existing.newest_observation_at = signal.newest_observation_at
            existing.rule_version = signal.rule_version
            existing.derived_at = signal.derived_at
        self._session.flush()

    def signals_for_business(self, business_record_id: UUID) -> list[Signal]:
        rows = self._session.execute(
            select(SignalRow)
            .where(SignalRow.business_record_id == business_record_id)
            .order_by(SignalRow.name)
        ).scalars()
        return [
            Signal(
                id=row.id,
                business_record_id=row.business_record_id,
                family=SignalFamily(row.family),
                name=row.name,
                confidence=row.confidence,
                supporting_evidence_ids=tuple(UUID(item) for item in row.supporting_evidence_ids),
                newest_observation_at=row.newest_observation_at,
                rule_version=row.rule_version,
                derived_at=row.derived_at,
            )
            for row in rows
        ]

    def businesses_with_signals(self) -> list[UUID]:
        rows = self._session.execute(select(SignalRow.business_record_id).distinct()).scalars()
        return list(rows)

    # ── the AI-call ledger ───────────────────────────────────────────────

    def record_ai_call(
        self,
        *,
        pipeline: str,
        prompt_version: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> None:
        self._session.add(
            AiCallRecordRow(
                pipeline=pipeline,
                prompt_version=prompt_version,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
        )
        self._session.flush()

    def ai_usage_totals(self) -> dict[str, int]:
        """Token totals and composition counts from the ledger (Doc 08 SS8):
        the unit-cost dial's raw numbers, honest tokens rather than guessed
        prices."""
        rows = self._session.execute(
            select(
                AiCallRecordRow.pipeline,
                func.count(),
                func.coalesce(func.sum(AiCallRecordRow.input_tokens), 0),
                func.coalesce(func.sum(AiCallRecordRow.output_tokens), 0),
            ).group_by(AiCallRecordRow.pipeline)
        ).all()
        total_tokens = 0
        brief_compositions = 0
        for pipeline, count, input_tokens, output_tokens in rows:
            total_tokens += int(input_tokens) + int(output_tokens)
            if str(pipeline).startswith("compose_brief"):
                brief_compositions += int(count)
        return {"total_tokens": total_tokens, "brief_compositions": brief_compositions}
