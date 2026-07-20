"""BusinessRecord — the world's facts about a company, workspace-agnostic.

Ring 2 (Doc 05 §7): public facts belong to nobody and are shared across all
customers by design. The type carries no workspace reference at all —
structurally incapable of leaking tenancy (Doc 08 §8). Everything relational
lives on the Prospect that references this record.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class BusinessRecord:
    id: UUID
    canonical_name: str
    website_domain: str | None
    register_number: str | None  # Companies House (or equivalent) — a strong key
    created_at: datetime
