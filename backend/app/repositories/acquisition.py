"""Persistence for the acquisition layer (Epic 4): canonical content, the
entity-binding review queue, and source-health telemetry. All Ring-2/ops —
deliberately not workspace-scoped."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.repositories.orm import (
    CanonicalContentRow,
    EntityBindingReviewRow,
    SourceHealthEventRow,
)


class SqlCanonicalContentRepo:
    def __init__(self, session: Session) -> None:
        self._session = session

    def store(
        self,
        *,
        item_kind: str,
        content_key: str,
        payload: dict[str, Any],
        source_family: str,
        snapshot_id: UUID,
        business_record_id: UUID | None,
    ) -> UUID | None:
        """Insert unless the same substance is already known (near-dup
        collapse at ingestion, Doc 09 §5). Returns the row id, or None when
        the content was a duplicate. Serialisation is the caller's job — this
        layer never imports the integrations' shapes (AP2 siblings)."""
        statement = (
            insert(CanonicalContentRow)
            .values(
                item_kind=item_kind,
                content_key=content_key,
                source_family=source_family,
                payload=payload,
                snapshot_id=snapshot_id,
                business_record_id=business_record_id,
            )
            .on_conflict_do_nothing(
                index_elements=[CanonicalContentRow.item_kind, CanonicalContentRow.content_key]
            )
            .returning(CanonicalContentRow.id)
        )
        return self._session.execute(statement).scalar_one_or_none()

    def bind(self, canonical_ids: list[UUID], business_record_id: UUID) -> int:
        rows = self._session.execute(
            select(CanonicalContentRow).where(CanonicalContentRow.id.in_(canonical_ids))
        ).scalars()
        count = 0
        for row in rows:
            row.business_record_id = business_record_id
            count += 1
        self._session.flush()
        return count

    def count_for_business(self, business_record_id: UUID) -> dict[str, int]:
        rows = self._session.execute(
            select(CanonicalContentRow.item_kind, func.count())
            .where(CanonicalContentRow.business_record_id == business_record_id)
            .group_by(CanonicalContentRow.item_kind)
        ).all()
        return {str(kind): int(count) for kind, count in rows}


class BindingReviewStatus(StrEnum):
    PENDING = "pending"
    BOUND = "bound"
    REJECTED = "rejected"


@dataclass(frozen=True)
class BindingReview:
    id: UUID
    candidate_name: str
    website_domain: str | None
    register_number: str | None
    confidence: float
    canonical_item_ids: tuple[UUID, ...]
    status: BindingReviewStatus


def _to_review(row: EntityBindingReviewRow) -> BindingReview:
    return BindingReview(
        id=row.id,
        candidate_name=row.candidate_name,
        website_domain=row.website_domain,
        register_number=row.register_number,
        confidence=row.confidence,
        canonical_item_ids=tuple(UUID(item) for item in row.canonical_item_ids),
        status=BindingReviewStatus(row.status),
    )


class SqlEntityBindingReviewRepo:
    def __init__(self, session: Session) -> None:
        self._session = session

    def enqueue(
        self,
        *,
        candidate_name: str,
        website_domain: str | None,
        register_number: str | None,
        confidence: float,
        canonical_item_ids: list[UUID],
    ) -> BindingReview:
        row = EntityBindingReviewRow(
            candidate_name=candidate_name,
            website_domain=website_domain,
            register_number=register_number,
            confidence=confidence,
            canonical_item_ids=[str(item) for item in canonical_item_ids],
            status=BindingReviewStatus.PENDING.value,
        )
        self._session.add(row)
        self._session.flush()
        return _to_review(row)

    def get(self, review_id: UUID) -> BindingReview | None:
        row = self._session.get(EntityBindingReviewRow, review_id)
        return _to_review(row) if row else None

    def list_pending(self) -> list[BindingReview]:
        rows = self._session.execute(
            select(EntityBindingReviewRow)
            .where(EntityBindingReviewRow.status == BindingReviewStatus.PENDING.value)
            .order_by(EntityBindingReviewRow.created_at)
        ).scalars()
        return [_to_review(row) for row in rows]

    def resolve(
        self, review_id: UUID, *, status: BindingReviewStatus, now: datetime
    ) -> BindingReview:
        row = self._session.get_one(EntityBindingReviewRow, review_id)
        row.status = status.value
        row.resolved_at = now
        self._session.flush()
        return _to_review(row)


class SqlSourceHealthRepo:
    def __init__(self, session: Session) -> None:
        self._session = session

    def record(self, *, source_family: str, event: str, detail: str = "") -> None:
        self._session.add(
            SourceHealthEventRow(source_family=source_family, event=event, detail=detail[:500])
        )
        self._session.flush()

    def counts(self) -> dict[str, dict[str, int]]:
        rows = self._session.execute(
            select(
                SourceHealthEventRow.source_family, SourceHealthEventRow.event, func.count()
            ).group_by(SourceHealthEventRow.source_family, SourceHealthEventRow.event)
        ).all()
        summary: dict[str, dict[str, int]] = {}
        for family, event, count in rows:
            summary.setdefault(str(family), {})[str(event)] = int(count)
        return summary
