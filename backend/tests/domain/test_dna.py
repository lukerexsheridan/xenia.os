"""The DNA's laws, one named test per citable rule (Doc 10, Sprint 4)."""

import pytest

from app.domain.dna import (
    ACTIVE_CATEGORIES_V1,
    MINIMUM_PATTERN_OCCURRENCES,
    NEUTRAL_CONFIDENCE,
    ChangeAuthor,
    ChangeCause,
    DecayClass,
    DnaCategory,
    ElementOrigin,
    excluded_by_disqualifier,
)
from app.domain.rules import DomainRuleViolation
from tests.domain.conftest import (
    NOW,
    make_disqualifier,
    make_dna,
    make_element,
    make_proposal,
)

# ── The schema (Doc 02 §7; Doc 10 Epic 2) ────────────────────────────────────


def test_doc02_s7_the_schema_has_exactly_ten_categories() -> None:
    assert len(DnaCategory) == 10


def test_doc10_epic2_four_categories_are_active_with_ten_slot_headroom() -> None:
    """The DNA ships with the four signal-consuming categories (Doc 09's cut)."""
    expected = {
        DnaCategory.BUSINESS_ATTRIBUTES,  # consumes: facts
        DnaCategory.SERVICE_NEED_EVIDENCE,  # consumes: ads/technology
        DnaCategory.BUYING_SIGNALS,  # consumes: hiring
        DnaCategory.DISQUALIFIERS,  # consumes: disqualifier triggers
    }
    assert expected == ACTIVE_CATEGORIES_V1
    assert set(DnaCategory) > ACTIVE_CATEGORIES_V1  # strict subset: headroom


# ── Disqualifier law (Doc 02 §7.10; Doc 04 §2.8) ─────────────────────────────


def test_doc02_s7_disqualifiers_are_constitutional_not_statistical() -> None:
    with pytest.raises(DomainRuleViolation, match="constitutional"):
        make_element(
            category=DnaCategory.DISQUALIFIERS,
            decay_class=DecayClass.LEARNED_PREFERENCE,
            origin=ElementOrigin.INTERVIEW,
        )


def test_doc02_s7_disqualifier_precedence_is_score_independent() -> None:
    """Absolute suppression, never overridden by score: the verdict function
    accepts no score at all — the signature is the rule."""
    assert excluded_by_disqualifier([make_disqualifier()]) is True
    assert excluded_by_disqualifier([make_element()]) is False
    assert excluded_by_disqualifier([]) is False


def test_doc04_s4_customer_laws_originate_only_from_the_customers_voice() -> None:
    with pytest.raises(DomainRuleViolation, match="customer's own voice"):
        make_element(
            decay_class=DecayClass.CUSTOMER_LAW,
            origin=ElementOrigin.OUTCOME_PATTERN,
        )


# ── Decay asymmetry (Doc 04 §4) ──────────────────────────────────────────────


def test_doc04_s4_customer_laws_never_decay_without_the_customer() -> None:
    disqualifier = make_disqualifier()
    stated_law = make_element(
        decay_class=DecayClass.CUSTOMER_LAW,
        origin=ElementOrigin.INTERVIEW,
        confidence=0.9,
    )
    dna = make_dna(disqualifier, stated_law)
    decayed, events = dna.decay_sweep(now=NOW)
    assert decayed.element(disqualifier.id).confidence == disqualifier.confidence
    assert decayed.element(stated_law.id).confidence == stated_law.confidence
    assert events == ()


def test_doc04_s4_learned_preferences_decay_toward_neutral() -> None:
    strong = make_element(confidence=0.9)
    weak = make_element(confidence=0.2)
    dna = make_dna(strong, weak)
    decayed, events = dna.decay_sweep(now=NOW)
    assert NEUTRAL_CONFIDENCE < decayed.element(strong.id).confidence < 0.9
    assert 0.2 < decayed.element(weak.id).confidence < NEUTRAL_CONFIDENCE
    assert len(events) == 2


def test_doc04_s4_decay_demotes_but_never_deletes() -> None:
    element = make_element(confidence=0.95)
    dna = make_dna(element)
    for _ in range(50):
        dna, _ = dna.decay_sweep(now=NOW)
    survivor = dna.element(element.id)
    assert survivor.confidence == pytest.approx(NEUTRAL_CONFIDENCE, abs=0.01)
    assert len(dna.elements) == 1


def test_doc04_s4_decay_writes_the_changelog() -> None:
    element = make_element(confidence=0.9)
    _, events = make_dna(element).decay_sweep(now=NOW)
    (event,) = events
    assert event.cause is ChangeCause.DECAY
    assert event.author is ChangeAuthor.XENIA
    assert event.before is not None and event.after is not None
    assert event.after.confidence < event.before.confidence


def test_doc04_s4_a_neutral_element_produces_no_decay_noise() -> None:
    element = make_element(confidence=NEUTRAL_CONFIDENCE)
    dna = make_dna(element)
    decayed, events = dna.decay_sweep(now=NOW)
    assert events == ()
    assert decayed.version == dna.version


# ── The changelog is total (Doc 04 §4; N4) ───────────────────────────────────


def test_doc04_s4_every_mutation_produces_a_change_event() -> None:
    dna = make_dna()
    element = make_element(origin=ElementOrigin.OUTCOME_PATTERN)
    dna, added = dna.add_learned_element(element, occurrences=3, now=NOW)
    assert added.after == element and added.before is None

    dna, reinforced = dna.reinforce_element(element.id, cause=ChangeCause.OUTCOME_PATTERN, now=NOW)
    assert reinforced.before is not None and reinforced.after is not None

    _, decay_events = dna.decay_sweep(now=NOW)
    assert decay_events  # even ambient decay is logged


def test_doc04_s4_reverted_changes_stay_in_the_log() -> None:
    """Revert restores the before-state via a NEW event — nothing is erased."""
    element = make_element(confidence=0.6)
    dna = make_dna(element)
    dna, change = dna.reinforce_element(element.id, cause=ChangeCause.CORRECTION, now=NOW)
    reverted_dna, reversion = dna.revert(change, now=NOW)
    assert reverted_dna.element(element.id).confidence == element.confidence
    assert reversion.cause is ChangeCause.REVERSION
    assert reversion.author is ChangeAuthor.CUSTOMER
    assert reversion.id != change.id  # a distinct log entry, not an erasure
    assert reverted_dna.version == dna.version + 1


def test_doc04_s4_an_event_without_a_before_state_cannot_revert() -> None:
    dna = make_dna()
    element = make_element(origin=ElementOrigin.INTERVIEW)
    dna, creation = dna.add_learned_element(element, occurrences=0, now=NOW)
    assert creation.reversible is False
    with pytest.raises(DomainRuleViolation, match="no before-state"):
        dna.revert(creation, now=NOW)


# ── Structural changes: proposed, never imposed (Doc 03 §8; Doc 08 §5) ───────


def test_doc03_s8_structural_changes_require_customer_endorsement() -> None:
    dna = make_dna()
    proposal = make_proposal(dna, make_disqualifier())
    with pytest.raises(DomainRuleViolation, match="endorsement"):
        dna.apply_endorsed_proposal(proposal, now=NOW)


def test_doc03_s8_an_endorsed_proposal_applies_with_the_customers_signature() -> None:
    dna = make_dna()
    new_disqualifier = make_disqualifier("No dropshipping businesses")
    endorsed = make_proposal(dna, new_disqualifier).endorse(now=NOW)
    evolved, event = dna.apply_endorsed_proposal(endorsed, now=NOW)
    assert evolved.element(new_disqualifier.id) == new_disqualifier
    assert event.cause is ChangeCause.ENDORSEMENT
    assert event.author is ChangeAuthor.CUSTOMER


def test_doc03_s8_a_declined_proposal_never_applies() -> None:
    dna = make_dna()
    declined = make_proposal(dna, make_disqualifier()).decline(now=NOW)
    with pytest.raises(DomainRuleViolation, match="declined"):
        dna.apply_endorsed_proposal(declined, now=NOW)


def test_doc03_s8_a_decided_proposal_is_not_decided_again() -> None:
    dna = make_dna()
    endorsed = make_proposal(dna, make_disqualifier()).endorse(now=NOW)
    with pytest.raises(DomainRuleViolation, match="not revisited"):
        endorsed.decline(now=NOW)
    with pytest.raises(DomainRuleViolation, match="not revisited"):
        endorsed.endorse(now=NOW)


def test_doc03_s8_xenia_cannot_self_apply_a_customer_law() -> None:
    dna = make_dna()
    stated_law = make_element(decay_class=DecayClass.CUSTOMER_LAW, origin=ElementOrigin.CORRECTION)
    with pytest.raises(DomainRuleViolation, match="proposed and endorsed"):
        dna.add_learned_element(stated_law, occurrences=99, now=NOW)


def test_doc08_s5_a_proposal_for_another_dna_is_rejected() -> None:
    dna = make_dna()
    other = make_dna()
    foreign = make_proposal(other, make_disqualifier()).endorse(now=NOW)
    with pytest.raises(DomainRuleViolation, match="different DNA"):
        dna.apply_endorsed_proposal(foreign, now=NOW)


# ── Pattern thresholds (Doc 04 §5) ───────────────────────────────────────────


def test_doc04_s5_one_event_never_becomes_law() -> None:
    dna = make_dna()
    lesson = make_element(origin=ElementOrigin.OUTCOME_PATTERN)
    with pytest.raises(DomainRuleViolation, match="one event never becomes law"):
        dna.add_learned_element(lesson, occurrences=1, now=NOW)


def test_doc04_s5_the_third_occurrence_adjusts() -> None:
    dna = make_dna()
    lesson = make_element(origin=ElementOrigin.BEHAVIOUR_PATTERN)
    evolved, _ = dna.add_learned_element(lesson, occurrences=MINIMUM_PATTERN_OCCURRENCES, now=NOW)
    assert evolved.element(lesson.id) == lesson


def test_doc04_s5_interview_statements_need_no_pattern() -> None:
    """The threshold guards generalisation from events, not the customer's
    own statements."""
    dna = make_dna()
    statement = make_element(origin=ElementOrigin.INTERVIEW)
    evolved, _ = dna.add_learned_element(statement, occurrences=0, now=NOW)
    assert evolved.element(statement.id) == statement


# ── Confidence evolution (Doc 09 §7) ─────────────────────────────────────────


def test_doc09_s7_corroboration_raises_confidence_within_bounds() -> None:
    element = make_element(confidence=0.99)
    dna = make_dna(element)
    for _ in range(20):
        dna, _ = dna.reinforce_element(element.id, cause=ChangeCause.OUTCOME_PATTERN, now=NOW)
    assert dna.element(element.id).confidence <= 1.0


def test_doc09_s7_reinforcement_resets_the_decay_clock() -> None:
    element = make_element(confidence=0.6)
    dna = make_dna(element)
    evolved, _ = dna.reinforce_element(element.id, cause=ChangeCause.CORRECTION, now=NOW)
    assert evolved.element(element.id).last_reinforced_at == NOW


# ── Aggregate hygiene ────────────────────────────────────────────────────────


def test_doc06_s5_element_confidence_is_bounded() -> None:
    with pytest.raises(DomainRuleViolation, match=r"\[0, 1\]"):
        make_element(confidence=1.2)


def test_doc03_s3_the_endorsement_moment_is_logged() -> None:
    dna = make_dna(endorsed=False)
    endorsed, event = dna.endorse(now=NOW)
    assert endorsed.endorsed is True
    assert event.cause is ChangeCause.ENDORSEMENT
    assert event.author is ChangeAuthor.CUSTOMER


def test_duplicate_element_ids_are_rejected() -> None:
    element = make_element(origin=ElementOrigin.INTERVIEW)
    dna = make_dna(element)
    with pytest.raises(DomainRuleViolation, match="already exists"):
        dna.add_learned_element(element, occurrences=0, now=NOW)


def test_unknown_element_lookup_fails_loudly() -> None:
    from uuid import uuid4

    with pytest.raises(DomainRuleViolation, match="no element"):
        make_dna().element(uuid4())


# ── The founding moment (Doc 03 C1/C2; Doc 07 §3) ────────────────────────────


def test_doc03_c1_the_founding_dna_logs_every_element_from_birth() -> None:
    from uuid import uuid4

    from app.domain.dna import Dna

    elements = (
        make_element(origin=ElementOrigin.INTERVIEW, decay_class=DecayClass.CUSTOMER_LAW),
        make_disqualifier(),
        make_element(origin=ElementOrigin.VERTICAL_PRIOR),
    )
    dna, events = Dna.create(workspace_id=uuid4(), elements=elements, now=NOW)
    assert dna.version == 1
    assert dna.endorsed is False  # endorsement is its own moment (Doc 03 §3)
    assert len(events) == 3
    by_element = {event.element_id: event for event in events}
    assert by_element[elements[0].id].author is ChangeAuthor.CUSTOMER
    assert by_element[elements[1].id].author is ChangeAuthor.CUSTOMER
    assert by_element[elements[2].id].author is ChangeAuthor.XENIA  # the template's voice
    assert by_element[elements[2].id].cause is ChangeCause.VERTICAL_PRIOR


def test_doc03_c1_the_founding_set_rejects_duplicate_ids() -> None:
    from uuid import uuid4

    from app.domain.dna import Dna

    element = make_element(origin=ElementOrigin.INTERVIEW)
    with pytest.raises(DomainRuleViolation, match="duplicate"):
        Dna.create(workspace_id=uuid4(), elements=(element, element), now=NOW)
