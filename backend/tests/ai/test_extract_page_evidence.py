"""The first AI pipeline, tested in recorded-fixture mode (Doc 08 §11):
span-grounding rejects seeded fabrications (Sprint 9 DoD)."""

from typing import Any

from app.ai.pipelines.extract_page_evidence import ExtractPageEvidence
from app.ai.providers.base import ProviderUsage
from app.ai.validation.spans import span_is_grounded

PAGE = (
    "Brightpath — DTC skincare that works. We sell direct-to-consumer skincare "
    "for sensitive skin, shipped across the UK. Founded in Manchester, we now "
    "serve over 40,000 customers."
)


class FakeProvider:
    def __init__(self, claims: list[dict[str, Any]]) -> None:
        self._claims = claims
        self.prompts: list[str] = []

    def structured(
        self, *, prompt: str, schema: dict[str, Any], schema_name: str
    ) -> tuple[dict[str, Any], ProviderUsage]:
        self.prompts.append(prompt)
        return {"claims": self._claims}, ProviderUsage(
            model="fixture", input_tokens=100, output_tokens=50
        )


def grounded_claim() -> dict[str, Any]:
    return {
        "claim": "They serve over 40,000 customers",
        "evidence_type": "e3_self_declaration",
        "quoted_span": "we now serve over 40,000 customers",
        "confidence": 0.8,
    }


def fabricated_claim() -> dict[str, Any]:
    return {
        "claim": "They raised a £2m funding round",
        "evidence_type": "e1_measured_observation",
        "quoted_span": "raised a £2m funding round",  # not on the page
        "confidence": 0.9,
    }


def test_doc09_s6_span_grounding_rejects_seeded_fabrications() -> None:
    pipeline = ExtractPageEvidence(FakeProvider([grounded_claim(), fabricated_claim()]))
    extraction = pipeline.execute(page_text=PAGE, business_name="Brightpath Ltd")
    assert len(extraction.candidates) == 1
    assert extraction.candidates[0].claim == "They serve over 40,000 customers"
    assert extraction.dropped_ungrounded == 1  # the fabrication died at the door


def test_doc09_s6_malformed_candidates_are_dropped_never_patched() -> None:
    pipeline = ExtractPageEvidence(
        FakeProvider(
            [
                {
                    "claim": "",
                    "evidence_type": "e3_self_declaration",
                    "quoted_span": "x",
                    "confidence": 0.5,
                },
                {
                    "claim": "ok",
                    "evidence_type": "e2_third_party_attestation",
                    "quoted_span": "x",
                    "confidence": 0.5,
                },
                {
                    "claim": "ok",
                    "evidence_type": "e3_self_declaration",
                    "quoted_span": "x",
                    "confidence": 2.0,
                },
            ]
        )
    )
    extraction = pipeline.execute(page_text=PAGE, business_name="Brightpath Ltd")
    assert extraction.candidates == ()
    assert extraction.dropped_ungrounded == 3


def test_doc08_s6_usage_and_versions_travel_with_the_extraction() -> None:
    provider = FakeProvider([grounded_claim()])
    extraction = ExtractPageEvidence(provider).execute(
        page_text=PAGE, business_name="Brightpath Ltd"
    )
    assert extraction.usage.input_tokens == 100
    assert extraction.pipeline_version == "extract_page_evidence/1"
    assert extraction.prompt_version == "extract_page_evidence/1"
    assert "Never invent" in provider.prompts[0]  # the prompt's honesty clause


def test_span_grounding_is_whitespace_and_case_tolerant_only() -> None:
    assert span_is_grounded("WE NOW   SERVE over 40,000 customers", PAGE)
    assert not span_is_grounded("we serve 90,000 customers", PAGE)
    assert not span_is_grounded("   ", PAGE)
