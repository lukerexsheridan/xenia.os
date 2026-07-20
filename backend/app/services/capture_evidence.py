"""CaptureEvidence — the workbench's manual capture path (Doc 10, Sprint 6).

The provenance contract enforced at entry (Doc 05 §3): the claim binds to a
verified BusinessRecord and cites a replayable snapshot, or it is refused.
The domain's own rules (type legality, the E5 ring rule, confidence bounds)
apply at construction.
"""

from datetime import datetime
from uuid import UUID, uuid4

from app.core.errors import NotFoundError
from app.domain.evidence import Evidence, EvidenceType, FreshnessClass
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.evidence import SqlEvidenceRepo
from app.repositories.snapshots import SqlSourceSnapshotRepo


class CaptureEvidence:
    def __init__(
        self,
        evidence_repo: SqlEvidenceRepo,
        business_repo: SqlBusinessRecordRepo,
        snapshot_repo: SqlSourceSnapshotRepo,
    ) -> None:
        self._evidence_repo = evidence_repo
        self._business_repo = business_repo
        self._snapshot_repo = snapshot_repo

    def execute(
        self,
        *,
        business_record_id: UUID,
        claim: str,
        evidence_type: EvidenceType,
        snapshot_id: UUID,
        observed_at: datetime,
        extraction_confidence: float,
        freshness_class: FreshnessClass,
    ) -> Evidence:
        if self._business_repo.get(business_record_id) is None:
            raise NotFoundError("business record not found — bind evidence to a verified entity")
        snapshot = self._snapshot_repo.get(snapshot_id)
        if snapshot is None:
            raise NotFoundError("snapshot not found — every receipt must be re-findable")
        evidence = Evidence(
            id=uuid4(),
            business_record_id=business_record_id,
            claim=claim,
            evidence_type=evidence_type,
            source_url=snapshot.url,
            snapshot_id=snapshot_id,
            observed_at=observed_at,
            extraction_confidence=extraction_confidence,
            freshness_class=freshness_class,
        )
        return self._evidence_repo.add(evidence)
