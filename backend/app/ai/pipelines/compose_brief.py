"""ComposeBrief — B1-B8 against a frozen receipt table (Doc 08 §6 step 4;
Doc 10 Sprint 12).

The pipeline shape: context assembly is the caller's deterministic job (the
receipt table arrives frozen); prompt assembly is versioned; the model call
is structured; L0 validation is inline and blocking; regeneration is bounded
with the failures fed back; repeated failure surfaces to the Editor, never
to a customer.
"""

from dataclasses import dataclass
from typing import Any

from app.ai.prompts.compose_brief import PROMPT_VERSION, render_prompt
from app.ai.providers.base import ProviderUsage, StructuredProvider
from app.ai.validation.l0 import ComposedBrief, ComposedSection, L0Report, validate_composition
from app.domain.evidence import ReceiptRow
from app.domain.research_brief import BriefSectionCode

PIPELINE_VERSION = "compose_brief/1"
MAX_ATTEMPTS = 2  # bounded regeneration (Doc 08 §6): retries are not a loop

_SECTION_CODES = [code.value for code in BriefSectionCode]

_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["sections", "couldnt_see", "confidence_proposal"],
    "properties": {
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["code", "content", "cited_receipts"],
                "properties": {
                    "code": {"type": "string", "enum": _SECTION_CODES},
                    "content": {"type": "string"},
                    "cited_receipts": {"type": "array", "items": {"type": "integer"}},
                },
            },
        },
        "couldnt_see": {"type": "array", "items": {"type": "string"}},
        "confidence_proposal": {"type": "number", "minimum": 0, "maximum": 1},
    },
}


@dataclass(frozen=True)
class CompositionResult:
    composed: ComposedBrief | None  # None when every bounded attempt failed L0
    l0_report: L0Report
    attempts: int
    usages: tuple[ProviderUsage, ...]
    pipeline_version: str = PIPELINE_VERSION
    prompt_version: str = PROMPT_VERSION


class ComposeBrief:
    def __init__(self, provider: StructuredProvider) -> None:
        self._provider = provider

    def execute(
        self,
        *,
        business_name: str,
        dna_summary: str,
        receipt_table: tuple[ReceiptRow, ...],
    ) -> CompositionResult:
        receipt_numbers = frozenset(row.number for row in receipt_table)
        rendered_receipts = "\n".join(
            f"[{row.number}] ({row.evidence_type.value}, observed "
            f"{row.observed_at.date().isoformat()}) {row.claim}"
            for row in receipt_table
        )
        prompt = render_prompt(
            business_name=business_name,
            dna_summary=dna_summary,
            receipt_table=rendered_receipts or "(no receipts — say so)",
        )

        usages: list[ProviderUsage] = []
        report = L0Report(problems=("no attempt made",))
        for attempt in range(1, MAX_ATTEMPTS + 1):
            parsed, usage = self._provider.structured(
                prompt=prompt, schema=_SCHEMA, schema_name="research_brief_composition"
            )
            usages.append(usage)
            composed = _parse(parsed)
            report = validate_composition(
                composed, receipt_numbers=receipt_numbers, business_name=business_name
            )
            if report.passed:
                return CompositionResult(
                    composed=composed, l0_report=report, attempts=attempt, usages=tuple(usages)
                )
            # Bounded regeneration: the failures are fed back, once.
            prompt = (
                prompt
                + "\n\nYour previous attempt failed validation:\n- "
                + "\n- ".join(report.problems)
                + "\nCorrect these and respond again."
            )
        return CompositionResult(
            composed=None, l0_report=report, attempts=MAX_ATTEMPTS, usages=tuple(usages)
        )


def _parse(parsed: dict[str, Any]) -> ComposedBrief:
    sections = tuple(
        ComposedSection(
            code=BriefSectionCode(str(raw.get("code"))),
            content=str(raw.get("content", "")),
            cited_receipts=tuple(int(n) for n in raw.get("cited_receipts", [])),
        )
        for raw in parsed.get("sections", [])
        if isinstance(raw, dict) and str(raw.get("code")) in _SECTION_CODES
    )
    couldnt_see = tuple(str(item) for item in parsed.get("couldnt_see", []))
    proposal = parsed.get("confidence_proposal", 0.0)
    return ComposedBrief(
        sections=sections,
        couldnt_see=couldnt_see,
        confidence_proposal=float(proposal) if isinstance(proposal, int | float) else -1.0,
    )
