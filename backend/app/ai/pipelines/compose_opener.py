"""ComposeOpener — the C6 draft pipeline, contained (AP6; Doc 03 C6).

The same shape as every pipeline here: versioned prompt, structured call,
deterministic validation, bounded regeneration. Validation is lighter than
the brief's L0 — a draft is the founder's raw material, not a delivered
claim — but the banned register and entity naming still gate absolutely.
"""

from dataclasses import dataclass
from typing import Any

from app.ai.prompts.compose_opener import PROMPT_VERSION, render_prompt
from app.ai.providers.base import ProviderUsage, StructuredProvider
from app.ai.validation.l0 import BANNED_VOCABULARY

PIPELINE_VERSION = "compose_opener/1"
MAX_ATTEMPTS = 2
_MAX_CHARS = 1400

_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["opener"],
    "properties": {"opener": {"type": "string"}},
}


@dataclass(frozen=True)
class OpenerResult:
    opener: str | None  # None -> every bounded attempt failed validation
    problems: tuple[str, ...]
    attempts: int
    usages: tuple[ProviderUsage, ...]
    pipeline_version: str = PIPELINE_VERSION
    prompt_version: str = PROMPT_VERSION


def _problems(opener: str, *, business_name: str) -> tuple[str, ...]:
    found: list[str] = []
    lowered = opener.lower()
    for phrase in BANNED_VOCABULARY:
        if phrase in lowered:
            found.append(f"banned register present: {phrase!r} (Doc 06 §2)")
    if business_name.lower() not in lowered:
        found.append("the opener never names the business — zero ambiguity, always")
    if "[" in opener or "]" in opener:
        found.append("placeholder brackets present — a draft is specific or it is nothing")
    if len(opener) > _MAX_CHARS:
        found.append("too long — the founder edits a note, not an essay")
    if not opener.strip():
        found.append("empty draft")
    return tuple(found)


class ComposeOpener:
    def __init__(self, provider: StructuredProvider) -> None:
        self._provider = provider

    def execute(self, *, business_name: str, voice_sample: str, receipts: str) -> OpenerResult:
        prompt = render_prompt(
            business_name=business_name, voice_sample=voice_sample, receipts=receipts
        )
        usages: list[ProviderUsage] = []
        problems: tuple[str, ...] = ("no attempt made",)
        for attempt in range(1, MAX_ATTEMPTS + 1):
            parsed, usage = self._provider.structured(
                prompt=prompt, schema=_SCHEMA, schema_name="opener_draft"
            )
            usages.append(usage)
            opener = str(parsed.get("opener", ""))
            problems = _problems(opener, business_name=business_name)
            if not problems:
                return OpenerResult(
                    opener=opener, problems=(), attempts=attempt, usages=tuple(usages)
                )
            prompt = (
                prompt
                + "\n\nYour previous attempt failed validation:\n- "
                + "\n- ".join(problems)
                + "\nCorrect these and respond again."
            )
        return OpenerResult(
            opener=None, problems=problems, attempts=MAX_ATTEMPTS, usages=tuple(usages)
        )
