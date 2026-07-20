"""The ship bar (Doc 04 §3) as named rules."""

import pytest

from app.domain.rubric import RubricScore
from app.domain.rules import DomainRuleViolation


def test_doc04_s3_the_ship_bar_is_16_of_20_with_no_dimension_below_2() -> None:
    assert RubricScore(4, 4, 3, 3, 2).meets_ship_bar
    assert not RubricScore(4, 4, 4, 4, 1).meets_ship_bar  # dimension floor
    assert not RubricScore(3, 3, 3, 3, 3).meets_ship_bar  # 15 < 16


def test_doc04_s3_an_accuracy_zero_zeroes_the_brief() -> None:
    assert not RubricScore(0, 4, 4, 4, 4).meets_ship_bar


def test_doc04_s3_dimensions_are_bounded() -> None:
    with pytest.raises(DomainRuleViolation, match="0-4"):
        RubricScore(5, 4, 4, 4, 4)
