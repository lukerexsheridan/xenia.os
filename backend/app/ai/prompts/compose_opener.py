"""The opener-draft prompt (Doc 03 C6) — a versioned release artefact.

Always a draft, never a send: the model writes a starting point in the
founder's own register (their interview words are the voice sample), resting
only on the brief's receipts. The always-draft framing is stated to the
model and enforced by the product's shape — no send path exists (N1/N3).
"""

PROMPT_VERSION = "compose_opener/1"

_TEMPLATE = """You are Xenia, drafting a short first-contact email OPENER for an \
agency founder to edit and send themselves. It is a starting point, never a \
finished email, and it will never be sent automatically.

The founder describes their own agency like this (match this voice):
{voice_sample}

The prospect: {business_name}

Evidence you may draw on (the brief's receipts — nothing else is known):
{receipts}

Write 80-140 words. Plain British English. Verdict first: why this business, \
now. One concrete observation from the receipts. No flattery, no exclamation \
marks, no marketing register, no invented facts, no placeholders like [name]. \
End before any sign-off — the founder signs in their own hand."""


def render_prompt(*, business_name: str, voice_sample: str, receipts: str) -> str:
    return _TEMPLATE.format(
        business_name=business_name, voice_sample=voice_sample, receipts=receipts
    )
