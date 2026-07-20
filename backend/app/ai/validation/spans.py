"""Span-grounding — the anti-fabrication check at the extraction layer
(Doc 09 §6): before any reasoning model ever sees a claim, the quoted span
it rests on must actually exist in the source content. Deterministic code
holds this door; an AI guarding AI would be circular exactly where
circularity is fatal (Doc 09 §4)."""


def span_is_grounded(quoted_span: str, source_text: str) -> bool:
    """The quoted span must appear verbatim (whitespace-normalised) in the
    source. A claim citing a span that is not there is a fabrication and
    dies here."""
    if not quoted_span.strip():
        return False
    return _normalise(quoted_span) in _normalise(source_text)


def _normalise(text: str) -> str:
    return " ".join(text.split()).lower()
