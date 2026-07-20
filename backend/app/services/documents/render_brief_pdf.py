"""RenderBriefPdf — B1-B8 as the shareable rendering (Docs 06 §7, 10 Sprint 6).

Verdict first: the confidence word leads, in the four-word vocabulary the
domain assigned. Sections follow the designed reading order; each section's
receipts appear as a quiet numbered line; the couldn't-see declaration is
always visible; the full receipt table closes the document, formatted for
audit. Deterministic for a given stored brief — the golden test holds the
bytes to that promise.
"""

from uuid import UUID

from app.core.errors import NotFoundError
from app.domain.evidence import ReceiptRow, build_receipt_table
from app.domain.research_brief import SECTION_TITLES, BriefSectionCode
from app.repositories.evidence import SqlEvidenceRepo
from app.repositories.research_briefs import SqlResearchBriefRepo, StoredResearchBrief
from app.services.documents.typeset import XeniaDocument


class RenderBriefPdf:
    def __init__(self, brief_repo: SqlResearchBriefRepo, evidence_repo: SqlEvidenceRepo) -> None:
        self._brief_repo = brief_repo
        self._evidence_repo = evidence_repo

    def execute(self, brief_id: UUID) -> bytes:
        stored = self._brief_repo.get(brief_id)
        if stored is None:
            raise NotFoundError("research brief not found in this workspace")
        receipt_table = stored.receipt_table
        if receipt_table is None:
            # Draft preview: assemble from current citations, deterministically.
            receipt_table = build_receipt_table(
                self._evidence_repo.get_many(stored.brief.cited_evidence_ids())
            )
        return _render(stored, receipt_table)


def _render(stored: StoredResearchBrief, receipt_table: tuple[ReceiptRow, ...]) -> bytes:
    brief = stored.brief
    receipt_numbers = {row.evidence_id: row.number for row in receipt_table}
    document = XeniaDocument(created_at=brief.created_at)

    document.add_title("Research brief")
    document.meta_line(
        f"Confidence: {brief.confidence_band.value}  ·  "
        f"format v{brief.format_version}  ·  "
        f"prepared {brief.created_at.date().isoformat()}"
        + ("" if stored.finalised_at is None else "  ·  final")
    )

    sections = {section.code: section for section in brief.sections}
    for code in BriefSectionCode:
        section = sections.get(code)
        if section is None:
            continue
        document.heading(SECTION_TITLES[code])
        document.body(section.content)
        numbers = sorted(
            receipt_numbers[evidence_id]
            for evidence_id in section.cited_evidence_ids
            if evidence_id in receipt_numbers
        )
        if numbers:
            document.quiet("Receipts: " + ", ".join(str(number) for number in numbers))

    document.heading("What I couldn't see")
    for entry in brief.couldnt_see:
        document.bullet(entry)

    if receipt_table:
        document.heading("Receipts")
        for row in receipt_table:
            document.body(f"{row.number}. {row.claim}")
            document.quiet(
                f"    {row.evidence_type.value}  ·  observed {row.observed_at.date().isoformat()}"
            )

    return document.render()
