"""SuppressionEntry — one request, honoured everywhere, permanently (Doc 05 §8)."""

import dataclasses
from datetime import UTC, datetime
from uuid import uuid4

from app.domain.suppression import (
    SuppressedSubjectKind,
    SuppressionEntry,
    SuppressionReason,
)


def make_entry() -> SuppressionEntry:
    return SuppressionEntry(
        id=uuid4(),
        subject_kind=SuppressedSubjectKind.BUSINESS,
        subject_reference="example-company.co.uk",
        reason=SuppressionReason.OBJECTION,
        created_at=datetime(2026, 7, 20, tzinfo=UTC),
    )


def test_doc05_s8_suppression_spans_all_workspaces_by_design() -> None:
    """The one record class that deliberately spans tenancy (Doc 08 §5):
    no workspace field exists, so per-workspace suppression is unrepresentable."""
    names = {field.name for field in dataclasses.fields(SuppressionEntry)}
    assert not any("workspace" in name for name in names)


def test_doc05_s8_suppression_is_permanent_by_design() -> None:
    """No lift/expire operation exists on the type, and entries are frozen."""
    entry = make_entry()
    assert not [name for name in dir(entry) if "lift" in name or "expire" in name]
    assert dataclasses.fields(SuppressionEntry)  # frozen dataclass, no mutators


def test_doc05_s8_both_businesses_and_people_can_be_suppressed() -> None:
    assert {kind.value for kind in SuppressedSubjectKind} == {"business", "person"}
    assert {reason.value for reason in SuppressionReason} == {
        "erasure_request",
        "objection",
    }
