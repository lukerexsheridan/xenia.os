"""CreateDna — the workbench intake's output (Doc 07 §3).

The scripted-human interview, transcribed into the founding DNA: every
element logged from birth by the aggregate's founding operation, persisted
with its changelog in one transaction. One DNA per workspace at V1.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.core.errors import ConflictError
from app.domain.audit import AuditAction, AuditEntryRepo
from app.domain.dna import DecayClass, Dna, DnaCategory, DnaElement, ElementOrigin
from app.repositories.dna import SqlDnaRepo


@dataclass(frozen=True)
class DnaElementInput:
    category: DnaCategory
    statement: str
    confidence: float
    decay_class: DecayClass
    origin: ElementOrigin


class CreateDna:
    def __init__(self, dna_repo: SqlDnaRepo, audit_repo: AuditEntryRepo) -> None:
        self._dna_repo = dna_repo
        self._audit_repo = audit_repo

    def execute(
        self,
        *,
        workspace_id: UUID,
        elements: list[DnaElementInput],
        request_id: str | None = None,
    ) -> Dna:
        if self._dna_repo.get() is not None:
            raise ConflictError("this workspace already has a DNA (one per workspace at V1)")
        now = datetime.now(UTC)
        dna, events = Dna.create(
            workspace_id=workspace_id,
            elements=tuple(
                DnaElement(
                    id=uuid4(),
                    category=item.category,
                    statement=item.statement,
                    confidence=item.confidence,
                    decay_class=item.decay_class,
                    origin=item.origin,
                    created_at=now,
                    last_reinforced_at=now,
                )
                for item in elements
            ),
            now=now,
        )
        self._dna_repo.save(dna, events)
        self._audit_repo.append(
            action=AuditAction.DNA_CREATED,
            target_type="dna",
            target_id=str(dna.id),
            actor_user_id=None,
            request_id=request_id,
        )
        return dna
