"""PDF golden-file snapshots (Doc 10, Sprint 6 DoD).

Fixed IDs and timestamps in, byte-identical PDFs out — rendering is
deterministic, so a format change is always a conscious diff against the
golden file, never an accident. Compression is off, so content assertions
read the bytes directly.
"""

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from app.domain.dna import DecayClass, Dna, DnaCategory, DnaElement, ElementOrigin
from app.domain.evidence import EvidenceType, ReceiptRow
from app.domain.research_brief import BriefSectionCode
from app.repositories.orm import ResearchBriefRow
from app.repositories.research_briefs import StoredResearchBrief
from app.services.documents.render_brief_pdf import _render as render_brief
from app.services.documents.render_dna_document import _render as render_dna

GOLDEN_DIR = Path(__file__).parent.parent / "golden"
CREATED_AT = datetime(2026, 7, 13, 9, 0, tzinfo=UTC)
EVIDENCE_ID = UUID("00000000-0000-0000-0000-00000000e001")


def fixture_stored_brief() -> StoredResearchBrief:
    sections = [
        {
            "code": code.value,
            "content": f"Fixture content for {code.value}, written as an analyst would.",
            "cited_evidence_ids": (
                [str(EVIDENCE_ID)] if code is BriefSectionCode.B4_MARKETING_GAP else []
            ),
        }
        for code in BriefSectionCode
    ]
    row = ResearchBriefRow(
        id=UUID("00000000-0000-0000-0000-0000000000b1"),
        workspace_id=UUID("00000000-0000-0000-0000-0000000000a1"),
        prospect_id=UUID("00000000-0000-0000-0000-0000000000c1"),
        format_version=1,
        status="final",
        sections=sections,
        couldnt_see=["Their ad spend levels — the library shows presence only"],
        confidence_score=0.72,
        receipt_table=None,
        derivation=None,
    )
    row.created_at = CREATED_AT
    row.finalised_at = CREATED_AT
    return StoredResearchBrief(row)


def fixture_receipt_table() -> tuple[ReceiptRow, ...]:
    return (
        ReceiptRow(
            number=1,
            evidence_id=EVIDENCE_ID,
            claim="They sell DTC skincare with active paid social",
            evidence_type=EvidenceType.MEASURED_OBSERVATION,
            observed_at=CREATED_AT,
            extraction_confidence=0.9,
        ),
    )


def fixture_dna() -> Dna:
    def element(suffix: int, **overrides: object) -> DnaElement:
        defaults: dict[str, object] = {
            "id": UUID(f"00000000-0000-0000-0000-0000000000d{suffix}"),
            "category": DnaCategory.BUSINESS_ATTRIBUTES,
            "statement": "DTC e-commerce brands, £1-20m revenue",
            "confidence": 0.8,
            "decay_class": DecayClass.CUSTOMER_LAW,
            "origin": ElementOrigin.INTERVIEW,
            "created_at": CREATED_AT,
            "last_reinforced_at": CREATED_AT,
        }
        defaults.update(overrides)
        return DnaElement(**defaults)  # type: ignore[arg-type]

    return Dna(
        id=UUID("00000000-0000-0000-0000-0000000000e1"),
        workspace_id=UUID("00000000-0000-0000-0000-0000000000a1"),
        version=1,
        elements=(
            element(1),
            element(
                2,
                category=DnaCategory.DISQUALIFIERS,
                statement="No franchise businesses",
                confidence=1.0,
            ),
            element(
                3,
                category=DnaCategory.BUYING_SIGNALS,
                statement="Hiring a first marketing manager",
                confidence=0.6,
                decay_class=DecayClass.LEARNED_PREFERENCE,
                origin=ElementOrigin.VERTICAL_PRIOR,
            ),
        ),
        endorsed=True,
    )


def assert_matches_golden(rendered: bytes, name: str) -> None:
    golden_path = GOLDEN_DIR / name
    assert golden_path.exists(), (
        f"golden file {name} missing — regenerate deliberately with "
        f"tests/golden/regenerate.py and review the diff"
    )
    assert rendered == golden_path.read_bytes(), (
        f"{name} changed — a format change must be a conscious decision: "
        f"review, then regenerate the golden file"
    )


def test_doc10_sprint6_brief_pdf_matches_the_golden_file() -> None:
    rendered = render_brief(fixture_stored_brief(), fixture_receipt_table())
    assert rendered == render_brief(fixture_stored_brief(), fixture_receipt_table())
    assert_matches_golden(rendered, "brief_v1.pdf")


def test_doc10_sprint6_dna_document_matches_the_golden_file() -> None:
    rendered = render_dna(fixture_dna(), "Brightpath Digital")
    assert rendered == render_dna(fixture_dna(), "Brightpath Digital")
    assert_matches_golden(rendered, "dna_document_v1.pdf")


def test_doc06_s7_the_brief_reads_verdict_first_with_receipts_quiet() -> None:
    rendered = render_brief(fixture_stored_brief(), fixture_receipt_table())
    assert b"Research brief" in rendered
    assert b"Confidence: likely" in rendered  # the four-word vocabulary leads
    identity = rendered.index(b"(Identity & snapshot)")
    receipts = rendered.index(b"(Receipts)")  # the appendix heading, exactly
    couldnt_see = rendered.index(b"(What I couldn't see)")
    assert identity < couldnt_see < receipts  # the designed reading order


def test_doc06_s7_the_dna_document_labels_stated_laws() -> None:
    rendered = render_dna(fixture_dna(), "Brightpath Digital")
    assert b"Ideal Client DNA" in rendered
    assert b"your stated rule" in rendered
    assert b"learned preference" in rendered
    assert b"Disqualifiers" in rendered
