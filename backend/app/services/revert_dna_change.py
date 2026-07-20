"""RevertDnaChange — undo as revert-with-log, never erasure (Doc 13 I6).

The changelog is total and append-only: reverting restores the event's
before-state through a *new* logged event, so the DNA remembers being
corrected and remembers being un-corrected. The domain aggregate owns the
rules (only events with a before-state, only elements still present); this
service carries identities and persistence.
"""

from datetime import UTC, datetime
from uuid import UUID

from app.core.errors import NotFoundError
from app.domain.dna import Dna
from app.repositories.dna import SqlDnaRepo


class RevertDnaChange:
    def __init__(self, dna_repo: SqlDnaRepo) -> None:
        self._dna_repo = dna_repo

    def execute(self, *, event_id: UUID) -> Dna:
        dna = self._dna_repo.get()
        if dna is None:
            raise NotFoundError("no DNA yet — the interview founds it")
        event = next(
            (entry for entry in self._dna_repo.changelog(dna.id) if entry.id == event_id), None
        )
        if event is None:
            raise NotFoundError("no such change in this DNA's log")
        evolved, revert_event = dna.revert(event, now=datetime.now(UTC))
        self._dna_repo.save(evolved, (revert_event,))
        return evolved
