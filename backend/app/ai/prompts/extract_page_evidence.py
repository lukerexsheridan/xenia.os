"""The extraction prompt — a versioned release artefact (Doc 08 §6).

A prompt change is a diff, a review, and a regression run. The couldn't-see
discipline is built in: the model is told to omit, never invent — the
span-grounding validator enforces it regardless of obedience.
"""

PROMPT_VERSION = "extract_page_evidence/1"

_TEMPLATE = """You are extracting factual claims about a business from one \
page of its public website.

Business: {business_name}

Rules:
- Extract only claims supported by an exact quote from the page text below.
- For each claim, copy the supporting passage VERBATIM into quoted_span.
- Classify each claim: e1_measured_observation (machine-verifiable states), \
e3_self_declaration (what the company says about itself), \
e4_market_behavioural (actions implying states, e.g. hiring or expansion).
- Confidence reflects how clearly the passage supports the claim.
- If the page supports no claims, return an empty list. Never invent.

Page text:
{page_text}"""


def render_prompt(*, page_text: str, business_name: str) -> str:
    return _TEMPLATE.format(business_name=business_name, page_text=page_text[:12000])
