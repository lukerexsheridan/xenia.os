"""Evidence and the receipt table — named rules (Docs 05 §3, 09 §6)."""

import dataclasses
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.domain.evidence import (
    Evidence,
    EvidenceType,
    FreshnessClass,
    build_receipt_table,
)
from app.domain.rules import DomainRuleViolation

NOW = datetime(2026, 7, 20, 12, 0, tzinfo=UTC)


def make_evidence(
    *,
    claim: str = "Running paid social on two platforms",
    evidence_type: EvidenceType = EvidenceType.MEASURED_OBSERVATION,
    observed_at: datetime = NOW,
    confidence: float = 0.9,
) -> Evidence:
    return Evidence(
        id=uuid4(),
        business_record_id=uuid4(),
        claim=claim,
        evidence_type=evidence_type,
        source_url="https://brightpath.example/about",
        snapshot_id=uuid4(),
        observed_at=observed_at,
        extraction_confidence=confidence,
        freshness_class=FreshnessClass.WEEKS,
    )


def test_doc05_s3_the_taxonomy_has_five_types_by_epistemic_strength() -> None:
    assert [item.value for item in EvidenceType] == [
        "e1_measured_observation",
        "e2_third_party_attestation",
        "e3_self_declaration",
        "e4_market_behavioural",
        "e5_customer_attested",
    ]


def test_doc09_s3_customer_attested_evidence_never_enters_ring_2() -> None:
    with pytest.raises(DomainRuleViolation, match="Ring 1"):
        make_evidence(evidence_type=EvidenceType.CUSTOMER_ATTESTED)


def test_doc05_s7_evidence_is_structurally_workspace_agnostic() -> None:
    names = {field.name for field in dataclasses.fields(Evidence)}
    assert not any("workspace" in name for name in names)


def test_doc05_s3_no_receipt_no_claim() -> None:
    with pytest.raises(DomainRuleViolation, match="claim"):
        make_evidence(claim="   ")
    with pytest.raises(DomainRuleViolation, match=r"\[0, 1\]"):
        make_evidence(confidence=1.4)


def test_doc09_s6_the_receipt_table_is_numbered_and_deterministic() -> None:
    early = make_evidence(observed_at=NOW - timedelta(days=3))
    middle = make_evidence(observed_at=NOW - timedelta(days=1))
    late = make_evidence(observed_at=NOW)

    forwards = build_receipt_table([early, middle, late])
    backwards = build_receipt_table([late, middle, early])
    assert forwards == backwards  # order of input is irrelevant
    assert [row.number for row in forwards] == [1, 2, 3]
    assert [row.evidence_id for row in forwards] == [early.id, middle.id, late.id]


def test_doc09_s6_duplicate_evidence_collapses_to_one_receipt() -> None:
    item = make_evidence()
    table = build_receipt_table([item, item, item])
    assert len(table) == 1
    assert table[0].number == 1


def test_doc09_s6_receipt_rows_carry_the_citable_facts() -> None:
    item = make_evidence()
    (row,) = build_receipt_table([item])
    assert row.claim == item.claim
    assert row.evidence_type is item.evidence_type
    assert row.observed_at == item.observed_at
    assert row.extraction_confidence == item.extraction_confidence
