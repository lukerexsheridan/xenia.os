"""Workspace — the aggregate root of tenancy and of Ring 1 (Doc 08 §5).

One agency, its people, its DNA, its prospects-in-relationship, its memory,
its grants. Every domain operation executes within a workspace context;
nothing meaningful exists outside one except Ring-2 knowledge.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Workspace:
    id: UUID
    name: str
    created_at: datetime
