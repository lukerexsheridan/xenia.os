"""DNA persistence — the aggregate as a document, its changelog append-only.

Workspace-scoped by constructor; one DNA per workspace at V1 (unique at the
database). `save` writes the evolved aggregate together with the change
events that explain it — a DNA row never moves without its changelog entries
in the same transaction (Doc 04 §4: the changelog is total).
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select

from app.domain.dna import (
    ChangeAuthor,
    ChangeCause,
    DecayClass,
    Dna,
    DnaCategory,
    DnaChangeEvent,
    DnaElement,
    DnaProposal,
    ElementOrigin,
    ProposalStatus,
)
from app.repositories.base import WorkspaceScopedRepository
from app.repositories.orm import DnaChangeEventRow, DnaProposalRow, DnaRow


def element_to_json(element: DnaElement) -> dict[str, Any]:
    return {
        "id": str(element.id),
        "category": element.category.value,
        "statement": element.statement,
        "confidence": element.confidence,
        "decay_class": element.decay_class.value,
        "origin": element.origin.value,
        "created_at": element.created_at.isoformat(),
        "last_reinforced_at": element.last_reinforced_at.isoformat(),
    }


def element_from_json(payload: dict[str, Any]) -> DnaElement:
    return DnaElement(
        id=UUID(payload["id"]),
        category=DnaCategory(payload["category"]),
        statement=payload["statement"],
        confidence=payload["confidence"],
        decay_class=DecayClass(payload["decay_class"]),
        origin=ElementOrigin(payload["origin"]),
        created_at=datetime.fromisoformat(payload["created_at"]),
        last_reinforced_at=datetime.fromisoformat(payload["last_reinforced_at"]),
    )


def _to_domain(row: DnaRow) -> Dna:
    return Dna(
        id=row.id,
        workspace_id=row.workspace_id,
        version=row.version,
        elements=tuple(element_from_json(item) for item in row.elements),
        endorsed=row.endorsed,
    )


def _event_to_json(element: DnaElement | None) -> dict[str, Any] | None:
    return element_to_json(element) if element is not None else None


class SqlDnaRepo(WorkspaceScopedRepository):
    def get(self) -> Dna | None:
        row = self._session.execute(
            select(DnaRow).where(DnaRow.workspace_id == self._workspace_id)
        ).scalar_one_or_none()
        return _to_domain(row) if row else None

    def save(self, dna: Dna, events: tuple[DnaChangeEvent, ...]) -> None:
        """Upsert the aggregate and append its change events, atomically."""
        row = self._session.get(DnaRow, dna.id)
        if row is None:
            row = DnaRow(
                id=dna.id,
                workspace_id=self._workspace_id,
                version=dna.version,
                endorsed=dna.endorsed,
                elements=[element_to_json(element) for element in dna.elements],
            )
            self._session.add(row)
        else:
            row.version = dna.version
            row.endorsed = dna.endorsed
            row.elements = [element_to_json(element) for element in dna.elements]
        # The aggregate row must exist before its events reference it: without
        # ORM relationships the unit of work won't order the two tables.
        self._session.flush()
        for event in events:
            self._session.add(
                DnaChangeEventRow(
                    id=event.id,
                    workspace_id=self._workspace_id,
                    dna_id=event.dna_id,
                    element_id=event.element_id,
                    cause=event.cause.value,
                    author=event.author.value,
                    before=_event_to_json(event.before),
                    after=_event_to_json(event.after),
                    occurred_at=event.occurred_at,
                )
            )
        self._session.flush()

    def changelog(self, dna_id: UUID) -> list[DnaChangeEvent]:
        rows = self._session.execute(
            select(DnaChangeEventRow)
            .where(
                DnaChangeEventRow.workspace_id == self._workspace_id,
                DnaChangeEventRow.dna_id == dna_id,
            )
            .order_by(DnaChangeEventRow.occurred_at, DnaChangeEventRow.id)
        ).scalars()
        return [
            DnaChangeEvent(
                id=row.id,
                dna_id=row.dna_id,
                element_id=row.element_id,
                cause=ChangeCause(row.cause),
                author=ChangeAuthor(row.author),
                before=element_from_json(row.before) if row.before else None,
                after=element_from_json(row.after) if row.after else None,
                occurred_at=row.occurred_at,
            )
            for row in rows
        ]

    def add_proposal(self, proposal: DnaProposal) -> None:
        self._session.add(
            DnaProposalRow(
                id=proposal.id,
                workspace_id=self._workspace_id,
                dna_id=proposal.dna_id,
                element=element_to_json(proposal.element),
                rationale=proposal.rationale,
                proposed_by=proposal.proposed_by.value,
                status=proposal.status.value,
                proposed_at=proposal.proposed_at,
                decided_at=proposal.decided_at,
            )
        )
        self._session.flush()

    def get_proposal(self, proposal_id: UUID) -> DnaProposal | None:
        row = self._session.get(DnaProposalRow, proposal_id)
        if row is None or row.workspace_id != self._workspace_id:
            return None
        return _proposal_to_domain(row)

    def list_proposals(self, *, status: ProposalStatus | None = None) -> list[DnaProposal]:
        query = select(DnaProposalRow).where(DnaProposalRow.workspace_id == self._workspace_id)
        if status is not None:
            query = query.where(DnaProposalRow.status == status.value)
        rows = (
            self._session.execute(query.order_by(DnaProposalRow.proposed_at, DnaProposalRow.id))
            .scalars()
            .all()
        )
        return [_proposal_to_domain(row) for row in rows]

    def open_proposal_exists_for_statement(self, statement: str) -> bool:
        """Idempotence for pattern-born proposals: the same lesson is
        proposed once, not on every occurrence past the threshold."""
        rows = self.list_proposals(status=ProposalStatus.PROPOSED)
        return any(row.element.statement == statement for row in rows)

    def save_proposal_decision(self, proposal: DnaProposal) -> None:
        row = self._session.get(DnaProposalRow, proposal.id)
        if row is None or row.workspace_id != self._workspace_id:
            return
        row.status = proposal.status.value
        row.decided_at = proposal.decided_at
        self._session.flush()


def _proposal_to_domain(row: DnaProposalRow) -> DnaProposal:
    return DnaProposal(
        id=row.id,
        dna_id=row.dna_id,
        element=element_from_json(row.element),
        rationale=row.rationale,
        proposed_by=ChangeAuthor(row.proposed_by),
        status=ProposalStatus(row.status),
        proposed_at=row.proposed_at,
        decided_at=row.decided_at,
    )
