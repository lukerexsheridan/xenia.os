"""Decision, Correction, Outcome — the teaching shapes (Docs 03, 04 §5, 08 §5)."""

import dataclasses
from datetime import UTC, datetime
from uuid import uuid4

from app.domain.correction import Correction, CorrectionTargetKind
from app.domain.decision import Decision, DecisionKind
from app.domain.outcome import Outcome, OutcomeKind

NOW = datetime(2026, 7, 20, 12, 0, tzinfo=UTC)


def test_doc03_c5_decisions_are_accept_decline_pursue_with_optional_reason() -> None:
    assert {kind.value for kind in DecisionKind} == {"accept", "decline", "pursue"}
    decision = Decision(
        id=uuid4(),
        workspace_id=uuid4(),
        recommendation_id=uuid4(),
        kind=DecisionKind.DECLINE,
        reason="too small for our retainer floor",
        decided_by=uuid4(),
        decided_at=NOW,
    )
    assert decision.reason is not None  # decline-with-reason is the teaching gold


def test_doc08_s5_corrections_target_an_element() -> None:
    """Corrections target an evidence item, a score factor, or a DNA element."""
    assert {kind.value for kind in CorrectionTargetKind} == {
        "evidence_item",
        "score_factor",
        "dna_element",
    }
    correction = Correction(
        id=uuid4(),
        workspace_id=uuid4(),
        target_kind=CorrectionTargetKind.DNA_ELEMENT,
        target_id=uuid4(),
        reason=None,  # free text optional, never required (Doc 06 §6)
        corrected_by=uuid4(),
        corrected_at=NOW,
    )
    assert correction.corrected_by is not None  # corrections carry their author


def test_doc03_c7_outcome_vocabulary_matches_the_capture_design() -> None:
    assert {kind.value for kind in OutcomeKind} == {
        "contacted",
        "replied",
        "meeting",
        "won",
        "lost",
        "disqualified",
    }


def test_doc03_s8_outcomes_are_recorded_never_inferred() -> None:
    """Outcome truth belongs to humans exclusively: `recorded_by` is a human
    user id with no default and the type has no machine-author affordance."""
    field_by_name = {field.name: field for field in dataclasses.fields(Outcome)}
    assert field_by_name["recorded_by"].default is dataclasses.MISSING
    assert "author" not in field_by_name  # no CUSTOMER/XENIA switch exists here


def test_doc03_s8_outcomes_are_append_only() -> None:
    """Frozen shape, no revision operation — ground truth is never edited."""
    outcome = Outcome(
        id=uuid4(),
        workspace_id=uuid4(),
        prospect_id=uuid4(),
        kind=OutcomeKind.WON,
        occurred_at=NOW,
        recorded_by=uuid4(),
        recorded_at=NOW,
    )
    assert dataclasses.fields(Outcome)
    try:
        outcome.kind = OutcomeKind.LOST  # type: ignore[misc]
        raise AssertionError("Outcome must be immutable")
    except dataclasses.FrozenInstanceError:
        pass
    assert outcome.reason is None  # the optional why defaults to absent
