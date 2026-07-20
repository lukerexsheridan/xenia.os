"""RenderDnaDocument — the DNA as a readable document (Docs 02 §7, 06 §7).

The customer can always *see* their DNA in plain language: elements grouped
by schema category, each carrying its confidence word (the four-word
vocabulary, assigned by rule) and its nature — the customer's stated rule
versus Xenia's learned preference (the decay asymmetry, made legible).
"""

from app.core.errors import NotFoundError
from app.domain.confidence import band_for
from app.domain.dna import DecayClass, Dna, DnaCategory
from app.repositories.dna import SqlDnaRepo
from app.services.documents.typeset import XeniaDocument

_CATEGORY_TITLES: dict[DnaCategory, str] = {
    DnaCategory.BUSINESS_ATTRIBUTES: "Business attributes",
    DnaCategory.FOUNDER_LEADERSHIP: "Founder & leadership",
    DnaCategory.SERVICE_NEED_EVIDENCE: "Service-need evidence",
    DnaCategory.MARKET_TRAJECTORY: "Market maturity & trajectory",
    DnaCategory.BUYING_SIGNALS: "Buying signals",
    DnaCategory.BUDGET_INDICATORS: "Budget indicators",
    DnaCategory.NEGATIVE_SIGNALS: "Negative signals",
    DnaCategory.RISK_INDICATORS: "Risk indicators",
    DnaCategory.RELATIONSHIP_INDICATORS: "Relationship indicators",
    DnaCategory.DISQUALIFIERS: "Disqualifiers — your stated laws",
}


class RenderDnaDocument:
    def __init__(self, dna_repo: SqlDnaRepo) -> None:
        self._dna_repo = dna_repo

    def execute(self, *, workspace_name: str) -> bytes:
        dna = self._dna_repo.get()
        if dna is None:
            raise NotFoundError("this workspace has no DNA yet")
        return _render(dna, workspace_name)


def _render(dna: Dna, workspace_name: str) -> bytes:
    if not dna.elements:
        raise NotFoundError("this workspace's DNA has no elements yet")
    newest = max(element.created_at for element in dna.elements)
    document = XeniaDocument(created_at=newest)

    document.add_title(f"Ideal Client DNA — {workspace_name}")
    document.meta_line(
        f"version {dna.version}  ·  "
        + ("endorsed" if dna.endorsed else "awaiting your endorsement")
    )

    for category in DnaCategory:
        elements = [element for element in dna.elements if element.category is category]
        if not elements:
            continue
        document.heading(_CATEGORY_TITLES[category])
        for element in elements:
            document.body(element.statement)
            nature = (
                "your stated rule"
                if element.decay_class is DecayClass.CUSTOMER_LAW
                else "learned preference"
            )
            document.quiet(f"    {band_for(element.confidence).value}  ·  {nature}")

    return document.render()
