"""The conflict hierarchy and the sovereignty rule (Doc 04 §4)."""

from app.domain.dna import SignalClass, resolve_conflict


def test_doc04_s4_the_hierarchy_ranks_six_signal_classes_in_order() -> None:
    assert [signal.value for signal in sorted(SignalClass)] == [1, 2, 3, 4, 5, 6]
    assert SignalClass.EXPLICIT_DISQUALIFIER < SignalClass.EXPLICIT_CORRECTION
    assert SignalClass.EXPLICIT_CORRECTION < SignalClass.RESOLVED_OUTCOME
    assert SignalClass.RESOLVED_OUTCOME < SignalClass.SUSTAINED_BEHAVIOUR
    assert SignalClass.SUSTAINED_BEHAVIOUR < SignalClass.INTERVIEW_STATEMENT
    assert SignalClass.INTERVIEW_STATEMENT < SignalClass.VERTICAL_PRIOR


def test_doc04_s4_disqualifiers_prevail_over_everything() -> None:
    for other in SignalClass:
        resolution = resolve_conflict(SignalClass.EXPLICIT_DISQUALIFIER, other)
        assert resolution.prevailing is SignalClass.EXPLICIT_DISQUALIFIER


def test_doc04_s4_outcomes_contradicting_a_disqualifier_surface_not_override() -> None:
    """The 3-versus-1 conflict: franchises keep converting, the no-franchise
    rule stands, and the tension is reported for the customer to rule on."""
    resolution = resolve_conflict(SignalClass.RESOLVED_OUTCOME, SignalClass.EXPLICIT_DISQUALIFIER)
    assert resolution.prevailing is SignalClass.EXPLICIT_DISQUALIFIER
    assert resolution.surfaced_to_customer is True


def test_doc04_s4_behaviour_contradicting_interview_proposes_the_reconciliation() -> None:
    """The 4-versus-5 conflict: behaviour outranks the old statement, but the
    reconciliation is proposed, never silently applied ("I've noticed…")."""
    resolution = resolve_conflict(SignalClass.SUSTAINED_BEHAVIOUR, SignalClass.INTERVIEW_STATEMENT)
    assert resolution.prevailing is SignalClass.SUSTAINED_BEHAVIOUR
    assert resolution.surfaced_to_customer is True

    inverse = resolve_conflict(SignalClass.INTERVIEW_STATEMENT, SignalClass.SUSTAINED_BEHAVIOUR)
    assert inverse == resolution  # order of arguments is irrelevant


def test_doc04_s4_statistics_never_silently_override_stated_intent() -> None:
    """Sovereignty: whenever a stated class prevails against evidence, the
    conflict is surfaced — quiet override in either direction is banned."""
    for stated in (
        SignalClass.EXPLICIT_DISQUALIFIER,
        SignalClass.EXPLICIT_CORRECTION,
    ):
        for evidence in (SignalClass.RESOLVED_OUTCOME, SignalClass.SUSTAINED_BEHAVIOUR):
            resolution = resolve_conflict(stated, evidence)
            assert resolution.prevailing is stated
            assert resolution.surfaced_to_customer is True


def test_doc04_s4_stated_versus_stated_needs_no_surfacing() -> None:
    """A recent correction beating an old interview answer is ordinary
    teaching, not a conflict the customer must adjudicate."""
    resolution = resolve_conflict(SignalClass.EXPLICIT_CORRECTION, SignalClass.INTERVIEW_STATEMENT)
    assert resolution.prevailing is SignalClass.EXPLICIT_CORRECTION
    assert resolution.surfaced_to_customer is False


def test_doc04_s4_vertical_priors_lose_to_everything() -> None:
    for other in SignalClass:
        if other is SignalClass.VERTICAL_PRIOR:
            continue
        assert resolve_conflict(other, SignalClass.VERTICAL_PRIOR).prevailing is other
