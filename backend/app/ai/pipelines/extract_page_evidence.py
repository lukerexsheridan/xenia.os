"""ExtractPageEvidence — schema-constrained AI extraction for prose
(Doc 09 §4's one extraction ruling where AI earns its place: the input has
no schema).

The pipeline shape of Doc 08 §6: context in, versioned prompt, structured
output against a declared schema, deterministic L0 validation (span
grounding) before anything downstream sees a claim, usage returned for the
metering the calling service records. Candidates whose quoted span is not in
the page are fabrications and are dropped, never patched (Doc 09 §6).
"""

from dataclasses import dataclass
from typing import Any

from app.ai.prompts.extract_page_evidence import PROMPT_VERSION, render_prompt
from app.ai.providers.base import ProviderUsage, StructuredProvider
from app.ai.validation.spans import span_is_grounded

PIPELINE_VERSION = "extract_page_evidence/1"

_ALLOWED_TYPES = ("e1_measured_observation", "e3_self_declaration", "e4_market_behavioural")

_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["claims"],
    "properties": {
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["claim", "evidence_type", "quoted_span", "confidence"],
                "properties": {
                    "claim": {"type": "string"},
                    "evidence_type": {"type": "string", "enum": list(_ALLOWED_TYPES)},
                    "quoted_span": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
            },
        }
    },
}


@dataclass(frozen=True)
class ExtractedCandidate:
    claim: str
    evidence_type: str
    quoted_span: str
    confidence: float


@dataclass(frozen=True)
class PageExtraction:
    candidates: tuple[ExtractedCandidate, ...]
    dropped_ungrounded: int  # fabrications that died at the door
    usage: ProviderUsage
    pipeline_version: str = PIPELINE_VERSION
    prompt_version: str = PROMPT_VERSION


class ExtractPageEvidence:
    def __init__(self, provider: StructuredProvider) -> None:
        self._provider = provider

    def execute(self, *, page_text: str, business_name: str) -> PageExtraction:
        parsed, usage = self._provider.structured(
            prompt=render_prompt(page_text=page_text, business_name=business_name),
            schema=_SCHEMA,
            schema_name="page_evidence_claims",
        )
        grounded: list[ExtractedCandidate] = []
        dropped = 0
        for raw in parsed.get("claims", []):
            candidate = _parse_candidate(raw)
            if candidate is None:
                dropped += 1
                continue
            if not span_is_grounded(candidate.quoted_span, page_text):
                dropped += 1  # the receipt rule's first door (Doc 09 §6)
                continue
            grounded.append(candidate)
        return PageExtraction(candidates=tuple(grounded), dropped_ungrounded=dropped, usage=usage)


def _parse_candidate(raw: Any) -> ExtractedCandidate | None:
    if not isinstance(raw, dict):
        return None
    claim = raw.get("claim")
    evidence_type = raw.get("evidence_type")
    quoted_span = raw.get("quoted_span")
    confidence = raw.get("confidence")
    if (
        not isinstance(claim, str)
        or not claim.strip()
        or evidence_type not in _ALLOWED_TYPES
        or not isinstance(quoted_span, str)
        or not isinstance(confidence, int | float)
        or not 0 <= float(confidence) <= 1
    ):
        return None
    return ExtractedCandidate(
        claim=claim.strip(),
        evidence_type=str(evidence_type),
        quoted_span=quoted_span,
        confidence=float(confidence),
    )
