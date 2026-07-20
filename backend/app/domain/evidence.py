"""Evidence — knowledge with a receipt (Doc 05 §3).

An observation bound to a claim, carrying the full provenance contract:
source specific enough to re-find (the snapshot), observation timestamp,
evidence type E1-E5, extraction confidence, entity binding (which verified
company), and freshness class. An observation missing any of these may inform
working hypotheses but may not underwrite a customer-facing claim — no
receipt, no claim.

Evidence about the public business world is Ring 2 (Doc 05 §7): the type
carries no workspace reference, structurally. Customer-attested evidence (E5)
belongs to Ring 1 and arrives with customer-side ingestion (Doc 09 §3) —
constructing it here is refused rather than mis-ringed.

The receipt table (Doc 09 §6) is the pipeline's most important artefact: a
numbered, frozen, deterministically-assembled table of validated Evidence.
The same evidence in any order yields byte-identical tables — that stability
is what makes citations replayable.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.domain.rules import DomainRuleViolation


class EvidenceType(StrEnum):
    """E1-E5 by epistemic strength (Doc 05 §3, verbatim taxonomy)."""

    MEASURED_OBSERVATION = "e1_measured_observation"
    THIRD_PARTY_ATTESTATION = "e2_third_party_attestation"
    SELF_DECLARATION = "e3_self_declaration"
    MARKET_BEHAVIOURAL = "e4_market_behavioural"
    CUSTOMER_ATTESTED = "e5_customer_attested"


class FreshnessClass(StrEnum):
    """Per-claim-type half-life families [calibrates] (Doc 05 §3): ad
    activity decays in weeks, staffing in months, location in years."""

    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"


@dataclass(frozen=True)
class Evidence:
    """Immutable once written; superseded, never edited (Doc 08 §5)."""

    id: UUID
    business_record_id: UUID  # entity binding — the misattribution defence
    claim: str
    evidence_type: EvidenceType
    source_url: str  # specific enough to re-find
    snapshot_id: UUID  # the replayable observation this claim was read from
    observed_at: datetime
    extraction_confidence: float
    freshness_class: FreshnessClass

    def __post_init__(self) -> None:
        if self.evidence_type is EvidenceType.CUSTOMER_ATTESTED:
            raise DomainRuleViolation(
                "customer-attested evidence (E5) is Ring 1 and arrives with "
                "customer-side ingestion (Doc 09 §3) — it never enters the "
                "shared Ring-2 store"
            )
        if not 0.0 <= self.extraction_confidence <= 1.0:
            raise DomainRuleViolation(
                f"extraction confidence must be within [0, 1], got {self.extraction_confidence}"
            )
        if not self.claim.strip():
            raise DomainRuleViolation("evidence must bind an observation to a claim")


@dataclass(frozen=True)
class ReceiptRow:
    """One numbered row of a frozen receipt table (Doc 09 §6)."""

    number: int
    evidence_id: UUID
    claim: str
    evidence_type: EvidenceType
    observed_at: datetime
    extraction_confidence: float


def build_receipt_table(evidence: Iterable[Evidence]) -> tuple[ReceiptRow, ...]:
    """Assemble the numbered, frozen receipt table — deterministically.

    Duplicates collapse; ordering is (observed_at, id), so the same evidence
    set yields the identical table regardless of input order. Generating
    models may only cite these numbers; the table snapshot lives in the
    brief's derivation record (Doc 09 §6).
    """
    unique = {item.id: item for item in evidence}
    ordered = sorted(unique.values(), key=lambda item: (item.observed_at, str(item.id)))
    return tuple(
        ReceiptRow(
            number=index + 1,
            evidence_id=item.id,
            claim=item.claim,
            evidence_type=item.evidence_type,
            observed_at=item.observed_at,
            extraction_confidence=item.extraction_confidence,
        )
        for index, item in enumerate(ordered)
    )
