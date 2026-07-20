"""The Prospect/BusinessRecord split and the ring boundary (Docs 05 §7, 08 §5)."""

import dataclasses
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain.business_record import BusinessRecord
from app.domain.prospect import Prospect, ProspectStatus
from app.domain.rules import DomainRuleViolation

NOW = datetime(2026, 7, 20, 12, 0, tzinfo=UTC)


def make_prospect(status: ProspectStatus = ProspectStatus.SURFACED) -> Prospect:
    return Prospect(
        id=uuid4(),
        workspace_id=uuid4(),
        business_record_id=uuid4(),
        binding_confidence=0.9,
        status=status,
        surfaced_at=NOW,
    )


def field_names(cls: type) -> set[str]:
    return {field.name for field in dataclasses.fields(cls)}


def test_doc05_s7_business_record_is_structurally_workspace_agnostic() -> None:
    """Ring 2 carries no workspace column at all — incapable of leaking
    tenancy (Doc 08 §8)."""
    assert not any("workspace" in name for name in field_names(BusinessRecord))


def test_doc08_s5_a_prospect_references_a_business_record_and_adds_the_relational() -> None:
    prospect = make_prospect()
    assert prospect.business_record_id is not None
    assert prospect.workspace_id is not None  # Ring 1: exists within one workspace


def test_doc08_s5_identity_binding_carries_confidence() -> None:
    """A Prospect *is* a claim that name/domain/register are one company —
    the misattribution defence starts here."""
    with pytest.raises(DomainRuleViolation, match=r"\[0, 1\]"):
        Prospect(
            id=uuid4(),
            workspace_id=uuid4(),
            business_record_id=uuid4(),
            binding_confidence=1.7,
            status=ProspectStatus.SURFACED,
            surfaced_at=NOW,
        )


def test_doc08_s5_the_lifecycle_moves_forward_only() -> None:
    prospect = make_prospect()
    recommended = prospect.advance(ProspectStatus.RECOMMENDED)
    pursued = recommended.advance(ProspectStatus.PURSUED)
    resolved = pursued.advance(ProspectStatus.RESOLVED)
    assert resolved.status is ProspectStatus.RESOLVED

    with pytest.raises(DomainRuleViolation, match="forward-only"):
        resolved.advance(ProspectStatus.SURFACED)
    with pytest.raises(DomainRuleViolation, match="forward-only"):
        pursued.advance(ProspectStatus.PURSUED)


def test_doc08_s5_a_declined_prospect_may_resolve_without_pursuit() -> None:
    """Forward-only, not step-by-step: a decline resolves straight from
    recommended."""
    recommended = make_prospect(ProspectStatus.RECOMMENDED)
    assert recommended.advance(ProspectStatus.RESOLVED).status is ProspectStatus.RESOLVED


def test_doc03_s7_prospects_carry_no_deal_semantics() -> None:
    """Deliberately not a deal: no value, stage, or probability — the refused
    pipeline board (Doc 03 §5)."""
    names = field_names(Prospect)
    assert not names & {"value", "deal_value", "stage", "probability", "pipeline_stage"}
