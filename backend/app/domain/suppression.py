"""SuppressionEntry — the prospect-rights machinery (Doc 05 §8).

A business or person who objected or requested erasure, suppressed from all
customers' discovery: one request, honoured everywhere, permanently. This is
**the one record class that deliberately spans tenancy** (Doc 08 §5) —
rights-handling outranks ring symmetry, and its uniqueness is documented
here, where it lives. Nothing else may copy this shape.

Entries are permanent by design: the type offers no lift/expire operation.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class SuppressedSubjectKind(StrEnum):
    BUSINESS = "business"
    PERSON = "person"


class SuppressionReason(StrEnum):
    ERASURE_REQUEST = "erasure_request"
    OBJECTION = "objection"


@dataclass(frozen=True)
class SuppressionEntry:
    id: UUID
    subject_kind: SuppressedSubjectKind
    # Specific enough to match at discovery time: a domain, a register
    # number, or a professional contact route — IDs and identifiers only.
    subject_reference: str
    reason: SuppressionReason
    created_at: datetime
