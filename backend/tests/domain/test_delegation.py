"""The delegation ladder and the never-automatic floor (Doc 06 §3; N3)."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain.delegation import (
    UNGRANTED_RUNG,
    V1_GRANTABLE_CEILING,
    DelegationGrant,
    DelegationRung,
    NeverAutomatic,
    never_automatic_permits,
    rung_for,
)
from app.domain.rules import DomainRuleViolation

NOW = datetime(2026, 7, 20, 12, 0, tzinfo=UTC)


def make_grant(
    activity: str = "outreach_drafting", rung: DelegationRung = DelegationRung.DRAFT
) -> DelegationGrant:
    return DelegationGrant(
        id=uuid4(),
        workspace_id=uuid4(),
        activity=activity,
        rung=rung,
        granted_by=uuid4(),
        granted_at=NOW,
    )


def test_doc06_s3_the_ladder_has_six_rungs_and_no_l6() -> None:
    assert [rung.value for rung in DelegationRung] == [0, 1, 2, 3, 4, 5]
    assert max(DelegationRung) is DelegationRung.ACT_AND_REPORT


def test_doc06_s3_the_never_automatic_floor_defeats_any_grant() -> None:
    """No grant, role, or bug in an upper layer authorises the floor — at any
    delegation level, regardless of feature requests."""
    maximal_grant = make_grant(rung=DelegationRung.DRAFT)
    for act in NeverAutomatic:
        assert never_automatic_permits(act, [maximal_grant]) is False
        assert never_automatic_permits(act, []) is False


def test_doc06_s3_the_floor_names_the_constitutional_acts() -> None:
    assert {act.value for act in NeverAutomatic} == {
        "send_external_communication",
        "override_disqualifier",
        "structural_dna_change_without_endorsement",
        "delete_customer_data",
        "spend_money",
        "irreversible_action_without_a_human",
    }


def test_doc03_s2_v1_grants_cap_at_draft() -> None:
    """P4: V1's delegation configuration is one meaningful trust decision —
    the ladder above draft is visible but earned later."""
    assert V1_GRANTABLE_CEILING is DelegationRung.DRAFT
    for rung in (DelegationRung.PREPARE, DelegationRung.ACT_AND_REPORT):
        with pytest.raises(DomainRuleViolation, match="not grantable at V1"):
            make_grant(rung=rung)


def test_doc03_s8_the_ungranted_default_is_the_accountable_analysis_posture() -> None:
    """Doc 03 §8's autonomous zone is brain acts: without a grant Xenia
    recommends, and nothing action-shaped happens."""
    assert UNGRANTED_RUNG is DelegationRung.RECOMMEND
    assert rung_for("anything_at_all", grants=[]) is DelegationRung.RECOMMEND


def test_doc06_s3_grants_are_per_activity() -> None:
    drafting_grant = make_grant(activity="outreach_drafting", rung=DelegationRung.DRAFT)
    assert rung_for("outreach_drafting", [drafting_grant]) is DelegationRung.DRAFT
    # The grant confers nothing on any other activity.
    assert rung_for("research", [drafting_grant]) is DelegationRung.RECOMMEND


def test_doc06_s3_a_grant_below_the_default_is_meaningless_and_rejected() -> None:
    with pytest.raises(DomainRuleViolation, match="needs no grant"):
        make_grant(rung=DelegationRung.SUGGEST)


def test_doc06_s3_grants_carry_the_human_who_made_the_trust_decision() -> None:
    grant = make_grant()
    assert grant.granted_by is not None
    assert grant.granted_at == NOW
