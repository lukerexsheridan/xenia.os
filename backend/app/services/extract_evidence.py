"""ExtractEvidence — canonical content into Evidence with receipts
(Doc 10, Sprint 9; Doc 09 §6).

Structured shapes (Filing, AdRecord, Posting) extract deterministically —
schema in, evidence out, zero tokens (Doc 09 §4). Page prose goes through
the AI pipeline, span-grounded before anything downstream sees a claim; an
absent provider degrades to a declared couldn't-see, never a guess.

Evidence IDs are content-derived (ADR-009), so extraction is idempotent:
the receipt table for a business assembles deterministically twice
identically — the Sprint 9 DoD, and a named test holds it.
"""

from dataclasses import dataclass, field
from uuid import UUID

from app.ai.pipelines.extract_page_evidence import ExtractedCandidate, ExtractPageEvidence
from app.core.errors import NotFoundError
from app.domain.evidence import (
    Evidence,
    EvidenceType,
    FreshnessClass,
    derive_evidence_id,
    relate,
)
from app.repositories.acquisition import SqlSourceHealthRepo
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.evidence import SqlEvidenceRepo
from app.repositories.knowledge import SqlKnowledgeRepo, StoredCanonicalItem

EXTRACTION_FAMILY = "extraction"


@dataclass
class ExtractionReport:
    business_record_id: UUID
    stored: int = 0
    already_known: int = 0
    dropped: int = 0
    couldnt_see: list[str] = field(default_factory=list)


class ExtractEvidence:
    def __init__(
        self,
        knowledge_repo: SqlKnowledgeRepo,
        evidence_repo: SqlEvidenceRepo,
        business_repo: SqlBusinessRecordRepo,
        health_repo: SqlSourceHealthRepo,
        page_pipeline: ExtractPageEvidence | None,
    ) -> None:
        self._knowledge_repo = knowledge_repo
        self._evidence_repo = evidence_repo
        self._business_repo = business_repo
        self._health_repo = health_repo
        self._page_pipeline = page_pipeline

    def execute(self, business_record_id: UUID) -> ExtractionReport:
        business = self._business_repo.get(business_record_id)
        if business is None:
            raise NotFoundError("business record not found")
        report = ExtractionReport(business_record_id=business_record_id)
        items = self._knowledge_repo.canonical_items_for_business(business_record_id)
        existing = self._evidence_repo.list_for_business(business_record_id)

        for item in items:
            if item.item_kind == "page":
                candidates = self._extract_page(item, business.canonical_name, report)
            else:
                candidates = _deterministic_extract(item, business_record_id)
            for candidate in candidates:
                relations = relate(candidate, existing)
                if self._evidence_repo.add_if_new(candidate, relations):
                    report.stored += 1
                    existing.append(candidate)
                else:
                    report.already_known += 1
        return report

    def _extract_page(
        self, item: StoredCanonicalItem, business_name: str, report: ExtractionReport
    ) -> list[Evidence]:
        if self._page_pipeline is None:
            note = "AI extraction not configured — page prose unread (declared, not guessed)"
            if note not in report.couldnt_see:
                report.couldnt_see.append(note)
            return []
        text = str(item.payload.get("text", ""))
        extraction = self._page_pipeline.execute(page_text=text, business_name=business_name)
        self._knowledge_repo.record_ai_call(
            pipeline=extraction.pipeline_version,
            prompt_version=extraction.prompt_version,
            model=extraction.usage.model,
            input_tokens=extraction.usage.input_tokens,
            output_tokens=extraction.usage.output_tokens,
        )
        if extraction.dropped_ungrounded:
            report.dropped += extraction.dropped_ungrounded
            self._health_repo.record(
                source_family=EXTRACTION_FAMILY,
                event="candidate_dropped",
                detail=f"{extraction.dropped_ungrounded} ungrounded from {item.source_url}",
            )
        return [
            _page_candidate(item, candidate, business_id=report.business_record_id)
            for candidate in extraction.candidates
        ]


def _page_candidate(
    item: StoredCanonicalItem, candidate: ExtractedCandidate, *, business_id: UUID
) -> Evidence:
    evidence_type = EvidenceType(candidate.evidence_type)
    slot = "page_prose"
    return Evidence(
        id=derive_evidence_id(
            business_record_id=business_id,
            evidence_type=evidence_type,
            claim_slot=slot,
            claim=candidate.claim,
            snapshot_id=item.snapshot_id,
        ),
        business_record_id=business_id,
        claim=candidate.claim,
        evidence_type=evidence_type,
        source_url=item.source_url,
        snapshot_id=item.snapshot_id,
        observed_at=item.fetched_at,
        extraction_confidence=candidate.confidence,
        freshness_class=FreshnessClass.MONTHS,
        claim_slot=slot,
    )


def _deterministic_extract(item: StoredCanonicalItem, business_record_id: UUID) -> list[Evidence]:
    """Doc 09 §4's ruling: structured sources extract with zero tokens."""
    payload = item.payload
    if item.item_kind == "filing":
        slot = f"register:{payload.get('category', 'unknown')}"
        claim = (
            f"Companies House ({payload.get('register_number', '')}): "
            f"{payload.get('description', '')}"
        )
        return [
            _build(
                item,
                business_record_id,
                claim=claim,
                evidence_type=EvidenceType.THIRD_PARTY_ATTESTATION,
                slot=slot,
                confidence=0.95,
                freshness=FreshnessClass.YEARS
                if payload.get("category") == "company-profile"
                else FreshnessClass.MONTHS,
            )
        ]
    if item.item_kind == "ad_record":
        stopped = payload.get("stopped_at")
        platforms = ", ".join(payload.get("platforms", []) or [])  # type: ignore[arg-type]
        claim = (
            f"Ran ads on {platforms} until {stopped}"
            if stopped
            else f"Running ads on {platforms} (active at observation)"
        )
        return [
            _build(
                item,
                business_record_id,
                claim=claim,
                evidence_type=EvidenceType.MEASURED_OBSERVATION,
                slot="ad_activity",
                confidence=0.95,
                freshness=FreshnessClass.WEEKS,
            )
        ]
    if item.item_kind == "posting":
        title = str(payload.get("title", ""))
        location = payload.get("location")
        claim = f"Hiring: {title}" + (f" ({location})" if location else "")
        if payload.get("posted_at"):
            claim += f", posted {payload['posted_at']}"
        return [
            _build(
                item,
                business_record_id,
                claim=claim,
                evidence_type=EvidenceType.MARKET_BEHAVIOURAL,
                slot=f"hiring:{' '.join(title.lower().split())}",
                confidence=0.9,
                freshness=FreshnessClass.MONTHS,
            )
        ]
    return []


def _build(
    item: StoredCanonicalItem,
    business_record_id: UUID,
    *,
    claim: str,
    evidence_type: EvidenceType,
    slot: str,
    confidence: float,
    freshness: FreshnessClass,
) -> Evidence:
    return Evidence(
        id=derive_evidence_id(
            business_record_id=business_record_id,
            evidence_type=evidence_type,
            claim_slot=slot,
            claim=claim,
            snapshot_id=item.snapshot_id,
        ),
        business_record_id=business_record_id,
        claim=claim,
        evidence_type=evidence_type,
        source_url=item.source_url,
        snapshot_id=item.snapshot_id,
        observed_at=item.fetched_at,
        extraction_confidence=confidence,
        freshness_class=freshness,
        claim_slot=slot,
    )
