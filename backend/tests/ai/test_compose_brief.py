"""Composition: bounded regeneration, receipts-bound, prompt as a release
artefact (golden-locked)."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from app.ai.pipelines.compose_brief import MAX_ATTEMPTS, ComposeBrief
from app.ai.prompts.compose_brief import render_prompt
from app.ai.providers.base import ProviderUsage
from app.domain.evidence import EvidenceType, ReceiptRow
from app.domain.research_brief import BriefSectionCode

GOLDEN = Path(__file__).parent.parent / "golden"
NOW = datetime(2026, 7, 13, 9, 0, tzinfo=UTC)


def receipt_table() -> tuple[ReceiptRow, ...]:
    return tuple(
        ReceiptRow(
            number=index + 1,
            evidence_id=UUID(f"00000000-0000-0000-0000-00000000000{index + 1}"),
            claim=claim,
            evidence_type=EvidenceType.MEASURED_OBSERVATION,
            observed_at=NOW,
            extraction_confidence=0.9,
        )
        for index, claim in enumerate(
            [
                "Running ads on facebook, instagram (active at observation)",
                "Hiring: Marketing Manager (Manchester), posted 2026-07-01",
                "Companies House (12345678): Status active; incorporated 2019-03-01",
            ]
        )
    )


def valid_payload() -> dict[str, Any]:
    material = {
        "b3_trajectory": [3],
        "b4_marketing_gap": [1],
        "b5_fit_thesis": [2],
    }
    return {
        "sections": [
            {
                "code": code.value,
                "content": (
                    "Brightpath Ltd sells DTC skincare."
                    if code is BriefSectionCode.B1_IDENTITY_SNAPSHOT
                    else f"Analyst content for {code.value}."
                ),
                "cited_receipts": material.get(code.value, []),
            }
            for code in BriefSectionCode
        ],
        "couldnt_see": ["Their ad spend levels"],
        "confidence_proposal": 0.72,
    }


class ScriptedProvider:
    def __init__(self, payloads: list[dict[str, Any]]) -> None:
        self._payloads = payloads
        self.calls = 0

    def structured(
        self, *, prompt: str, schema: dict[str, Any], schema_name: str
    ) -> tuple[dict[str, Any], ProviderUsage]:
        payload = self._payloads[min(self.calls, len(self._payloads) - 1)]
        self.calls += 1
        return payload, ProviderUsage(model="fixture", input_tokens=500, output_tokens=400)


def compose(payloads: list[dict[str, Any]]):  # type: ignore[no-untyped-def]
    return ComposeBrief(ScriptedProvider(payloads)).execute(
        business_name="Brightpath Ltd",
        dna_summary="- [LAW] No franchise businesses",
        receipt_table=receipt_table(),
    )


def test_doc10_sprint12_a_valid_composition_passes_l0_first_time() -> None:
    result = compose([valid_payload()])
    assert result.composed is not None
    assert result.l0_report.passed
    assert result.attempts == 1


def test_doc08_s6_regeneration_is_bounded_with_failures_fed_back() -> None:
    bad = valid_payload()
    bad["sections"][3]["cited_receipts"] = [99]  # fabricated citation
    result = compose([bad, valid_payload()])
    assert result.composed is not None
    assert result.attempts == 2  # one regeneration, failures fed back


def test_doc08_s6_repeated_failure_never_reaches_a_customer() -> None:
    bad = valid_payload()
    bad["sections"][3]["cited_receipts"] = [99]
    result = compose([bad, bad])
    assert result.composed is None  # the Editor queue's case, not the customer's
    assert result.attempts == MAX_ATTEMPTS
    assert result.l0_report.problems


def test_doc08_s6_the_prompt_is_a_release_artefact() -> None:
    """A prompt change is a diff, a review, and a regression run — locked by
    golden file; regenerate deliberately via tests/golden/regenerate.py."""
    rendered = render_prompt(
        business_name="Brightpath Ltd",
        dna_summary="- [LAW] No franchise businesses",
        receipt_table="[1] (e1) Running ads",
    )
    golden_path = GOLDEN / "compose_brief_prompt_v1.txt"
    assert golden_path.exists(), "regenerate the prompt golden deliberately"
    assert rendered + "\n" == golden_path.read_text()
