"""Signal decay — knowledge demotes toward unknown (Doc 09 §7)."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.domain.signal import (
    HALF_LIFE_BY_FAMILY,
    Signal,
    SignalFamily,
    decayed_confidence,
    is_stale,
)

NOW = datetime(2026, 7, 20, 12, 0, tzinfo=UTC)


def test_doc09_s7_the_four_alpha_families() -> None:
    assert {family.value for family in SignalFamily} == {
        "facts",
        "hiring",
        "ads_technology",
        "disqualifier_triggers",
    }
    assert set(HALF_LIFE_BY_FAMILY) == set(SignalFamily)


def test_doc09_s7_fresh_evidence_keeps_full_confidence() -> None:
    value = decayed_confidence(
        0.9, family=SignalFamily.ADS_TECHNOLOGY, newest_observation_at=NOW, now=NOW
    )
    assert value == 0.9


def test_doc05_s3_confidence_halves_at_the_half_life() -> None:
    half_life = HALF_LIFE_BY_FAMILY[SignalFamily.ADS_TECHNOLOGY]
    value = decayed_confidence(
        0.9,
        family=SignalFamily.ADS_TECHNOLOGY,
        newest_observation_at=NOW - half_life,
        now=NOW,
    )
    assert value == pytest.approx(0.45)


def test_doc09_s7_stale_signals_demote_to_research_prompts() -> None:
    signal = Signal(
        id=uuid4(),
        business_record_id=uuid4(),
        family=SignalFamily.ADS_TECHNOLOGY,
        name="active_paid_media",
        confidence=0.9,
        supporting_evidence_ids=(uuid4(),),
        newest_observation_at=NOW - timedelta(days=120),
        rule_version="signals/1",
        derived_at=NOW,
    )
    assert is_stale(signal, now=NOW)
    fresh = Signal(
        id=uuid4(),
        business_record_id=signal.business_record_id,
        family=SignalFamily.ADS_TECHNOLOGY,
        name="active_paid_media",
        confidence=0.9,
        supporting_evidence_ids=(uuid4(),),
        newest_observation_at=NOW,
        rule_version="signals/1",
        derived_at=NOW,
    )
    assert not is_stale(fresh, now=NOW)
