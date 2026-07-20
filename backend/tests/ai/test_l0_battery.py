"""The L0 battery, validator by validator, with pass/fail fixtures (Doc 10
Sprint 12): any L0 failure blocks; fabrication cannot pass."""

from app.ai.validation.l0 import (
    ComposedBrief,
    ComposedSection,
    validate_composition,
)
from app.domain.research_brief import BriefSectionCode

RECEIPTS = frozenset({1, 2, 3})
BUSINESS = "Brightpath Ltd"


def valid_sections() -> tuple[ComposedSection, ...]:
    def section(code: BriefSectionCode, cited: tuple[int, ...] = ()) -> ComposedSection:
        content = f"Analyst content for {code.value}."
        if code is BriefSectionCode.B1_IDENTITY_SNAPSHOT:
            content = f"{BUSINESS} sells DTC skincare across the UK."
        return ComposedSection(code=code, content=content, cited_receipts=cited)

    material = {
        BriefSectionCode.B3_TRAJECTORY: (1,),
        BriefSectionCode.B4_MARKETING_GAP: (2,),
        BriefSectionCode.B5_FIT_THESIS: (3,),
    }
    return tuple(section(code, material.get(code, ())) for code in BriefSectionCode)


def composed(
    sections: tuple[ComposedSection, ...] | None = None,
    couldnt_see: tuple[str, ...] = ("Their ad spend levels",),
    confidence: float = 0.7,
) -> ComposedBrief:
    return ComposedBrief(
        sections=sections if sections is not None else valid_sections(),
        couldnt_see=couldnt_see,
        confidence_proposal=confidence,
    )


def problems(brief: ComposedBrief) -> tuple[str, ...]:
    return validate_composition(brief, receipt_numbers=RECEIPTS, business_name=BUSINESS).problems


def test_doc04_s6_a_valid_composition_passes_every_validator() -> None:
    assert problems(composed()) == ()


def test_doc09_s6_citing_a_nonexistent_receipt_is_fabrication_and_blocks() -> None:
    sections = tuple(
        ComposedSection(s.code, s.content, (99,))
        if s.code is BriefSectionCode.B4_MARKETING_GAP
        else s
        for s in valid_sections()
    )
    found = problems(composed(sections))
    assert any("do not exist" in p and "fabrication" in p for p in found)


def test_doc04_s3_material_sections_without_receipts_block() -> None:
    sections = tuple(
        ComposedSection(s.code, s.content, ()) if s.code is BriefSectionCode.B5_FIT_THESIS else s
        for s in valid_sections()
    )
    assert any("without receipts" in p for p in problems(composed(sections)))


def test_doc06_s2_the_banned_register_blocks() -> None:
    sections = tuple(
        ComposedSection(s.code, s.content + " We can 10x your pipeline.", s.cited_receipts)
        if s.code is BriefSectionCode.B7_SUGGESTED_APPROACH
        else s
        for s in valid_sections()
    )
    assert any("banned register" in p for p in problems(composed(sections)))


def test_doc06_s5_percentage_confidence_blocks() -> None:
    sections = tuple(
        ComposedSection(s.code, s.content + " An 87% fit overall.", s.cited_receipts)
        if s.code is BriefSectionCode.B5_FIT_THESIS
        else s
        for s in valid_sections()
    )
    assert any("percentage-precision" in p for p in problems(composed(sections)))


def test_doc04_s8_entity_consistency_blocks_the_wrong_company() -> None:
    sections = tuple(
        ComposedSection(s.code, "Northline Studio makes films.", s.cited_receipts)
        if s.code is BriefSectionCode.B1_IDENTITY_SNAPSHOT
        else s
        for s in valid_sections()
    )
    assert any("B1 does not name" in p for p in problems(composed(sections)))


def test_doc04_s3_missing_couldnt_see_blocks() -> None:
    assert any("couldn't-see" in p for p in problems(composed(couldnt_see=())))


def test_doc04_s3_missing_sections_block() -> None:
    assert any("missing section" in p for p in problems(composed(sections=valid_sections()[:-1])))
