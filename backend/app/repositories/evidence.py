"""Evidence persistence — Ring 2, immutable once written (Doc 08 §5).

No update or delete methods exist: evidence is superseded, never edited.
Deliberately not workspace-scoped — public facts are shared (Doc 05 §7).
"""

from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.evidence import Evidence, EvidenceType, FreshnessClass
from app.repositories.orm import EvidenceRow


def _to_domain(row: EvidenceRow) -> Evidence:
    return Evidence(
        id=row.id,
        business_record_id=row.business_record_id,
        claim=row.claim,
        evidence_type=EvidenceType(row.evidence_type),
        source_url=row.source_url,
        snapshot_id=row.snapshot_id,
        observed_at=row.observed_at,
        extraction_confidence=row.extraction_confidence,
        freshness_class=FreshnessClass(row.freshness_class),
    )


class SqlEvidenceRepo:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, evidence: Evidence) -> Evidence:
        row = EvidenceRow(
            id=evidence.id,
            business_record_id=evidence.business_record_id,
            claim=evidence.claim,
            evidence_type=evidence.evidence_type.value,
            source_url=evidence.source_url,
            snapshot_id=evidence.snapshot_id,
            observed_at=evidence.observed_at,
            extraction_confidence=evidence.extraction_confidence,
            freshness_class=evidence.freshness_class.value,
        )
        self._session.add(row)
        self._session.flush()
        return _to_domain(row)

    def get(self, evidence_id: UUID) -> Evidence | None:
        row = self._session.get(EvidenceRow, evidence_id)
        return _to_domain(row) if row else None

    def get_many(self, evidence_ids: Iterable[UUID]) -> list[Evidence]:
        ids = list(evidence_ids)
        if not ids:
            return []
        rows = self._session.execute(select(EvidenceRow).where(EvidenceRow.id.in_(ids))).scalars()
        return [_to_domain(row) for row in rows]

    def list_for_business(self, business_record_id: UUID) -> list[Evidence]:
        rows = self._session.execute(
            select(EvidenceRow)
            .where(EvidenceRow.business_record_id == business_record_id)
            .order_by(EvidenceRow.observed_at, EvidenceRow.id)
        ).scalars()
        return [_to_domain(row) for row in rows]
