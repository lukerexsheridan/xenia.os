"""The confidence vocabulary and its banding rule (Doc 06 §5).

Exactly four words — confident / likely / possible / uncertain — used with
dictionary discipline across every surface forever. The band is assigned by
this deterministic rule, never by the model (Doc 09 §4: "the model proposes
nothing here"), and never rendered as a percentage in customer-facing prose.

The thresholds are pre-registered hypotheses [calibrates]: measured
calibration data (Doc 04 §5's quarterly reviews) re-maps the presentation
bands before the reasoning layer ever retrains. "When I say likely, I'm right
about it roughly four times in five" is the published meaning the LIKELY band
is centred on.
"""

from enum import StrEnum

from app.domain.rules import DomainRuleViolation


class ConfidenceBand(StrEnum):
    CONFIDENT = "confident"
    LIKELY = "likely"
    POSSIBLE = "possible"
    UNCERTAIN = "uncertain"


# [calibrates] — band floors, inclusive. LIKELY spans ~0.8 ± the width the
# published sentence promises; adjusted only from measured calibration curves.
CONFIDENT_FLOOR = 0.85
LIKELY_FLOOR = 0.65
POSSIBLE_FLOOR = 0.35


def band_for(score: float) -> ConfidenceBand:
    """Deterministic score → vocabulary mapping; the same bands everywhere."""
    if not 0.0 <= score <= 1.0:
        raise DomainRuleViolation(f"confidence score must be within [0, 1], got {score}")
    if score >= CONFIDENT_FLOOR:
        return ConfidenceBand.CONFIDENT
    if score >= LIKELY_FLOOR:
        return ConfidenceBand.LIKELY
    if score >= POSSIBLE_FLOOR:
        return ConfidenceBand.POSSIBLE
    return ConfidenceBand.UNCERTAIN
