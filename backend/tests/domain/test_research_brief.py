"""The brief's structural floor — named rules (Doc 04 §3)."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.confidence import ConfidenceBand
from app.domain.research_brief import (
    SECTION_TITLES,
    BriefSection,
    BriefSectionCode,
    ResearchBrief,
    completeness_problems,
)

NOW = datetime(2026, 7, 20, 12, 0, tzinfo=UTC)


def full_sections(cited: tuple[UUID, ...] = ()) -> tuple[BriefSection, ...]:
    return tuple(
        BriefSection(code=code, content=f"Content for {code.value}.", cited_evidence_ids=cited)
        for code in BriefSectionCode
    )


def make_brief(
    sections: tuple[BriefSection, ...] | None = None,
    couldnt_see: tuple[str, ...] = ("Their ad spend levels — the library shows presence only",),
) -> ResearchBrief:
    return ResearchBrief(
        id=uuid4(),
        workspace_id=uuid4(),
        prospect_id=uuid4(),
        format_version=1,
        sections=sections if sections is not None else full_sections(),
        couldnt_see=couldnt_see,
        confidence_score=0.7,
        created_at=NOW,
    )


def test_doc04_s3_the_brief_has_eight_sections_in_reading_order() -> None:
    assert len(BriefSectionCode) == 8
    assert set(SECTION_TITLES) == set(BriefSectionCode)


def test_doc04_s3_a_complete_brief_clears_the_floor() -> None:
    assert completeness_problems(make_brief()) == ()


def test_doc04_s3_a_missing_section_fails_the_floor() -> None:
    incomplete = tuple(
        section
        for section in full_sections()
        if section.code is not BriefSectionCode.B6_COUNTER_EVIDENCE
    )
    problems = completeness_problems(make_brief(sections=incomplete))
    assert any("missing section b6_counter_evidence" in problem for problem in problems)


def test_doc04_s3_the_couldnt_see_declaration_is_mandatory() -> None:
    problems = completeness_problems(make_brief(couldnt_see=()))
    assert any("couldn't-see" in problem for problem in problems)
    problems = completeness_problems(make_brief(couldnt_see=("  ",)))
    assert any("couldn't-see" in problem for problem in problems)


def test_doc04_s3_an_empty_section_fails_the_floor() -> None:
    sections = tuple(
        BriefSection(code=section.code, content=" ", cited_evidence_ids=())
        if section.code is BriefSectionCode.B4_MARKETING_GAP
        else section
        for section in full_sections()
    )
    problems = completeness_problems(make_brief(sections=sections))
    assert any("empty section b4_marketing_gap" in problem for problem in problems)


def test_doc04_s3_duplicate_sections_fail_the_floor() -> None:
    duplicated = (*full_sections(), full_sections()[0])
    problems = completeness_problems(make_brief(sections=duplicated))
    assert any("duplicate section" in problem for problem in problems)


def test_doc06_s5_the_confidence_band_is_assigned_by_rule() -> None:
    assert make_brief().confidence_band is ConfidenceBand.LIKELY


def test_cited_evidence_ids_deduplicate_stably() -> None:
    shared = uuid4()
    brief = make_brief(sections=full_sections(cited=(shared,)))
    assert brief.cited_evidence_ids() == (shared,)
