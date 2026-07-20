"""The L0 validator battery (Doc 08 §6; Doc 04 §6) — deterministic, blocking.

The receipt rule as architecture: the generating model received a closed
world (the frozen, numbered receipt table) and may only make material claims
that cite it. These validators are pure code holding the only door
(Doc 09 §4: "an AI guarding AI is circular at the exact point circularity is
fatal"). Any L0 failure blocks the output from ever reaching a customer —
mechanical failures are never quality-judgment calls.
"""

import re
from dataclasses import dataclass

from app.domain.research_brief import BriefSectionCode

# The scar-tissue register, banned in product copy as absolutely as in
# marketing (Doc 06 §2; Doc 02 §5's language rules).
BANNED_VOCABULARY = (
    "leads at scale",
    "blast",
    "sequences",
    "10x",
    "booked meetings on autopilot",
    "growth hacking",
    "spray",
    "ai sdr",
)

# Percentages presented as fit/confidence are false precision wearing a lab
# coat (Doc 06 §5): no "87/100" and no "73% fit" in customer-facing prose.
_FALSE_PRECISION = re.compile(r"\b\d{1,3}\s*(/\s*100|%)\s*(fit|confiden)", re.IGNORECASE)

# Sections whose claims are material: they must rest on receipts (Doc 04 §3).
_MATERIAL_SECTIONS = (
    BriefSectionCode.B3_TRAJECTORY,
    BriefSectionCode.B4_MARKETING_GAP,
    BriefSectionCode.B5_FIT_THESIS,
)


@dataclass(frozen=True)
class ComposedSection:
    code: BriefSectionCode
    content: str
    cited_receipts: tuple[int, ...]


@dataclass(frozen=True)
class ComposedBrief:
    sections: tuple[ComposedSection, ...]
    couldnt_see: tuple[str, ...]
    confidence_proposal: float


@dataclass(frozen=True)
class L0Report:
    problems: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.problems


def _structure_problems(composed: ComposedBrief) -> list[str]:
    """Structure completeness: B1-B8 exactly once, non-empty, couldn't-see present."""
    problems: list[str] = []
    present = [section.code for section in composed.sections]
    for code in BriefSectionCode:
        if present.count(code) == 0:
            problems.append(f"missing section {code.value}")
        elif present.count(code) > 1:
            problems.append(f"duplicate section {code.value}")
    for section in composed.sections:
        if not section.content.strip():
            problems.append(f"empty section {section.code.value}")
    if not any(entry.strip() for entry in composed.couldnt_see):
        problems.append("couldn't-see declaration missing (Doc 04 §3 B8)")
    return problems


def validate_composition(
    composed: ComposedBrief, *, receipt_numbers: frozenset[int], business_name: str
) -> L0Report:
    problems: list[str] = _structure_problems(composed)

    # Citation binding: cited numbers must exist; material sections must cite.
    for section in composed.sections:
        invented = [n for n in section.cited_receipts if n not in receipt_numbers]
        if invented:
            problems.append(
                f"{section.code.value} cites receipts that do not exist: {invented} "
                f"— fabrication dies here (the receipt rule)"
            )
        if section.code in _MATERIAL_SECTIONS and not section.cited_receipts:
            problems.append(f"{section.code.value} makes material claims without receipts")

    # Vocabulary legality and false precision.
    all_text = " ".join(section.content for section in composed.sections).lower()
    for phrase in BANNED_VOCABULARY:
        if phrase in all_text:
            problems.append(f"banned register present: {phrase!r} (Doc 06 §2)")
    if _FALSE_PRECISION.search(all_text):
        problems.append("percentage-precision confidence in prose (Doc 06 §5)")

    # Entity consistency: the brief is about exactly this business (Doc 04 §8 A2).
    b1 = next(
        (s for s in composed.sections if s.code is BriefSectionCode.B1_IDENTITY_SNAPSHOT), None
    )
    if b1 is not None and business_name.lower() not in b1.content.lower():
        problems.append(
            f"B1 does not name {business_name!r} — zero ambiguity about which "
            f"company this is (Doc 04 §3 B1)"
        )

    if not 0.0 <= composed.confidence_proposal <= 1.0:
        problems.append("confidence proposal outside [0, 1]")

    return L0Report(problems=tuple(problems))
