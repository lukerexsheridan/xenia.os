"""Shared builders for the named-rule domain suite.

Every test in this package names the document and section of the rule it
enforces (Doc 10, Sprint 4: "every citable law from Documents 03-06 as a
test with the document reference in its name"). The suite is pure and must
stay milliseconds-fast — it is the second engineer (Doc 10 §1).
"""

from datetime import UTC, datetime
from uuid import uuid4

from app.domain.dna import (
    ChangeAuthor,
    DecayClass,
    Dna,
    DnaCategory,
    DnaElement,
    DnaProposal,
    ElementOrigin,
    ProposalStatus,
)

NOW = datetime(2026, 7, 20, 12, 0, tzinfo=UTC)


def make_element(
    *,
    category: DnaCategory = DnaCategory.BUSINESS_ATTRIBUTES,
    statement: str = "DTC e-commerce brands, £1-20m revenue",
    confidence: float = 0.7,
    decay_class: DecayClass = DecayClass.LEARNED_PREFERENCE,
    origin: ElementOrigin = ElementOrigin.BEHAVIOUR_PATTERN,
) -> DnaElement:
    return DnaElement(
        id=uuid4(),
        category=category,
        statement=statement,
        confidence=confidence,
        decay_class=decay_class,
        origin=origin,
        created_at=NOW,
        last_reinforced_at=NOW,
    )


def make_disqualifier(statement: str = "No franchise businesses") -> DnaElement:
    return make_element(
        category=DnaCategory.DISQUALIFIERS,
        statement=statement,
        confidence=1.0,
        decay_class=DecayClass.CUSTOMER_LAW,
        origin=ElementOrigin.INTERVIEW,
    )


def make_dna(*elements: DnaElement, endorsed: bool = True) -> Dna:
    return Dna(
        id=uuid4(),
        workspace_id=uuid4(),
        version=1,
        elements=elements,
        endorsed=endorsed,
    )


def make_proposal(
    dna: Dna, element: DnaElement, *, status: ProposalStatus = ProposalStatus.PROPOSED
) -> DnaProposal:
    return DnaProposal(
        id=uuid4(),
        dna_id=dna.id,
        element=element,
        rationale="three franchise pursuits went nowhere — proposing the rule",
        proposed_by=ChangeAuthor.XENIA,
        status=status,
        proposed_at=NOW,
    )
