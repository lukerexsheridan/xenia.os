"""DecideDnaProposal — the customer signs, or doesn't (Doc 03 §8).

Structural changes exist first as proposals and apply only on endorsement;
declining is recorded and honoured with equal weight. Either way the
proposal's status changes exactly once — the domain state machine enforces
the sequence, this service only carries identities and persistence.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from app.core.errors import NotFoundError
from app.domain.dna import Dna, DnaProposal
from app.repositories.dna import SqlDnaRepo


@dataclass(frozen=True)
class ProposalDecisionResult:
    proposal: DnaProposal
    dna: Dna | None  # the evolved DNA when endorsed; None on decline


class DecideDnaProposal:
    def __init__(self, dna_repo: SqlDnaRepo) -> None:
        self._dna_repo = dna_repo

    def execute(
        self, *, proposal_id: UUID, endorse: bool, now: datetime | None = None
    ) -> ProposalDecisionResult:
        current = now or datetime.now(UTC)
        proposal = self._dna_repo.get_proposal(proposal_id)
        if proposal is None:
            raise NotFoundError("proposal not found in this workspace")

        if not endorse:
            declined = proposal.decline(now=current)
            self._dna_repo.save_proposal_decision(declined)
            return ProposalDecisionResult(proposal=declined, dna=None)

        endorsed = proposal.endorse(now=current)
        dna = self._dna_repo.get()
        if dna is None:
            raise NotFoundError("no DNA exists in this workspace")
        evolved, event = dna.apply_endorsed_proposal(endorsed, now=current)
        self._dna_repo.save(evolved, (event,))
        self._dna_repo.save_proposal_decision(endorsed)
        return ProposalDecisionResult(proposal=endorsed, dna=evolved)
