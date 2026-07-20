"""Evidence identity and graph relations — named rules (ADR-009; Doc 09 §6)."""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from app.domain.evidence import (
    Evidence,
    EvidenceType,
    FreshnessClass,
    derive_evidence_id,
    relate,
)

NOW = datetime(2026, 7, 20, 12, 0, tzinfo=UTC)
BUSINESS = uuid4()


def make(
    claim: str = "Running ads on facebook (active at observation)",
    *,
    slot: str = "ad_activity",
    source_url: str = "https://graph.facebook.com/ads",
    observed_at: datetime = NOW,
    snapshot: UUID | None = None,
) -> Evidence:
    snapshot_id = snapshot or uuid4()
    return Evidence(
        id=derive_evidence_id(
            business_record_id=BUSINESS,
            evidence_type=EvidenceType.MEASURED_OBSERVATION,
            claim_slot=slot,
            claim=claim,
            snapshot_id=snapshot_id,
        ),
        business_record_id=BUSINESS,
        claim=claim,
        evidence_type=EvidenceType.MEASURED_OBSERVATION,
        source_url=source_url,
        snapshot_id=snapshot_id,
        observed_at=observed_at,
        extraction_confidence=0.9,
        freshness_class=FreshnessClass.WEEKS,
        claim_slot=slot,
    )


def test_adr009_the_same_observation_yields_the_same_id() -> None:
    snapshot = uuid4()
    first = make(snapshot=snapshot)
    second = make(snapshot=snapshot)
    assert first.id == second.id  # re-extraction is idempotent
    assert first.id != make(snapshot=uuid4()).id  # a new observation is new


def test_doc05_s3_reobservation_from_the_same_source_supersedes() -> None:
    prior = make(observed_at=NOW - timedelta(days=30))
    fresh = make(observed_at=NOW)
    relations = relate(fresh, [prior])
    assert relations.supersedes_id == prior.id
    assert relations.corroborates_id is None


def test_doc05_s3_independent_agreement_corroborates() -> None:
    prior = make(source_url="https://other-library.example/ads")
    fresh = make()
    relations = relate(fresh, [prior])
    assert relations.corroborates_id == prior.id


def test_doc05_s3_same_domain_repetition_never_corroborates() -> None:
    """Twenty sightings on one domain are one source wearing twenty hats."""
    prior = make()
    fresh = make(observed_at=NOW + timedelta(days=1))
    relations = relate(fresh, [prior])
    assert relations.corroborates_id is None
    assert relations.supersedes_id == prior.id


def test_doc05_s3_conflicts_are_reported_not_resolved() -> None:
    prior = make("Ran ads on facebook until 2026-06-01")
    fresh = make("Running ads on facebook (active at observation)")
    relations = relate(fresh, [prior])
    assert relations.conflicts_id == prior.id


def test_relations_stay_within_the_claim_slot() -> None:
    other_slot = make("Hiring: Marketing Manager", slot="hiring:marketing manager")
    fresh = make()
    assert relate(fresh, [other_slot]) == relate(fresh, [])
