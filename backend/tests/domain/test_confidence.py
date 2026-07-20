"""The confidence vocabulary and banding rule (Doc 06 §5)."""

import pytest

from app.domain.confidence import (
    CONFIDENT_FLOOR,
    LIKELY_FLOOR,
    POSSIBLE_FLOOR,
    ConfidenceBand,
    band_for,
)
from app.domain.rules import DomainRuleViolation


def test_doc06_s5_the_vocabulary_is_exactly_four_words() -> None:
    assert [band.value for band in ConfidenceBand] == [
        "confident",
        "likely",
        "possible",
        "uncertain",
    ]


def test_doc06_s5_banding_is_deterministic_and_exhaustive() -> None:
    """Every score in [0, 1] maps to exactly one of the four words, and the
    mapping never moves between calls — dictionary discipline."""
    for hundredths in range(101):
        score = hundredths / 100
        band = band_for(score)
        assert band is band_for(score)
        assert band in ConfidenceBand


def test_doc06_s5_bands_are_monotonic_in_score() -> None:
    ordering = [
        ConfidenceBand.UNCERTAIN,
        ConfidenceBand.POSSIBLE,
        ConfidenceBand.LIKELY,
        ConfidenceBand.CONFIDENT,
    ]
    previous_rank = 0
    for hundredths in range(101):
        rank = ordering.index(band_for(hundredths / 100))
        assert rank >= previous_rank
        previous_rank = rank


def test_doc06_s5_band_floors_are_inclusive() -> None:
    assert band_for(CONFIDENT_FLOOR) is ConfidenceBand.CONFIDENT
    assert band_for(LIKELY_FLOOR) is ConfidenceBand.LIKELY
    assert band_for(POSSIBLE_FLOOR) is ConfidenceBand.POSSIBLE
    assert band_for(0.0) is ConfidenceBand.UNCERTAIN


def test_doc09_s4_the_model_cannot_smuggle_a_score_outside_the_range() -> None:
    with pytest.raises(DomainRuleViolation, match=r"\[0, 1\]"):
        band_for(1.5)
    with pytest.raises(DomainRuleViolation, match=r"\[0, 1\]"):
        band_for(-0.1)
