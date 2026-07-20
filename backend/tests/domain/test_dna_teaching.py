"""The Epic 8 DNA teaching paths: withdrawal and demotion (Doc 06 §6)."""

from datetime import UTC, datetime
from uuid import uuid4

from app.domain.dna import (
    NEUTRAL_CONFIDENCE,
    ChangeAuthor,
    ChangeCause,
    DecayClass,
    Dna,
    DnaCategory,
    DnaElement,
    ElementOrigin,
)

NOW = datetime(2026, 7, 20, tzinfo=UTC)


def founded_dna() -> tuple[Dna, DnaElement]:
    element = DnaElement(
        id=uuid4(),
        category=DnaCategory.BUYING_SIGNALS,
        statement="Hiring for marketing roles",
        confidence=0.9,
        decay_class=DecayClass.LEARNED_PREFERENCE,
        origin=ElementOrigin.BEHAVIOUR_PATTERN,
        created_at=NOW,
        last_reinforced_at=NOW,
    )
    dna, _ = Dna.create(workspace_id=uuid4(), elements=(element,), now=NOW)
    return dna, element


def test_doc06_s6_a_correction_withdraws_immediately_and_without_argument() -> None:
    dna, element = founded_dna()
    evolved, event = dna.withdraw_element(element.id, now=NOW)
    assert evolved.elements == ()
    assert evolved.version == dna.version + 1
    assert event.cause is ChangeCause.CORRECTION
    assert event.author is ChangeAuthor.CUSTOMER
    assert event.before == element  # the log remembers what was withdrawn
    assert event.after is None


def test_doc04_s5_a_score_factor_correction_demotes_weight_not_truth() -> None:
    dna, element = founded_dna()
    evolved, event = dna.demote_element(element.id, now=NOW)
    demoted = evolved.element(element.id)
    assert NEUTRAL_CONFIDENCE < demoted.confidence < element.confidence
    assert demoted.statement == element.statement  # the element stays
    assert event.cause is ChangeCause.CORRECTION
    assert event.author is ChangeAuthor.CUSTOMER
