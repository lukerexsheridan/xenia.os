"""The audit stream — append-only records of consequential acts (Doc 08 §8).

Who, what, when, from-where; queryable; retained per policy. This is
simultaneously Doc 05's inspectability, the Sev1 forensics substrate, and the
future SOC 2 down-payment. Entries are never updated or deleted by
application code (and RLS carries no update/delete policies for them).

Details carry IDs only — never names, prospect content, or PII (Doc 05).
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class AuditAction(StrEnum):
    """Grows one member per consequential act as epics land — never reworded."""

    WORKSPACE_PROVISIONED = "workspace.provisioned"
    USER_PROVISIONED = "user.provisioned"


@dataclass(frozen=True)
class AuditEntry:
    id: UUID
    workspace_id: UUID
    actor_user_id: UUID | None
    action: AuditAction
    target_type: str
    target_id: str
    request_id: str | None
    occurred_at: datetime


class AuditEntryRepo(Protocol):
    """Append-only by contract: the protocol offers no update or delete."""

    def append(
        self,
        *,
        action: AuditAction,
        target_type: str,
        target_id: str,
        actor_user_id: UUID | None,
        request_id: str | None,
    ) -> AuditEntry: ...
