"""Signals — knowledge from evidence (Doc 09 §7).

Evidence is what was observed; a signal is what it means, derived
predominantly by rules. Four families at V1 — exactly the ones the active
DNA categories consume (Doc 09 §13's cut). A signal exists only when its
evidence basis meets its type's threshold, stores its derivation (which
evidence, which rule version — knowledge is as auditable as evidence, one
level up), and decays toward *unknown*, never toward false (absence-of-
evidence semantics, Doc 05 §3): confidence is a deterministic function of
the newest supporting observation's age against the family's half-life
[calibrates].
"""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from uuid import UUID


class SignalFamily(StrEnum):
    """The four alpha families (Doc 09 §13)."""

    FACTS = "facts"
    HIRING = "hiring"
    ADS_TECHNOLOGY = "ads_technology"
    DISQUALIFIER_TRIGGERS = "disqualifier_triggers"


# [calibrates] — the freshness half-lives per family (Doc 05 §3: ad activity
# decays in weeks, staffing in months, register facts in years).
HALF_LIFE_BY_FAMILY: dict[SignalFamily, timedelta] = {
    SignalFamily.FACTS: timedelta(days=365),
    SignalFamily.HIRING: timedelta(days=60),
    SignalFamily.ADS_TECHNOLOGY: timedelta(days=28),
    SignalFamily.DISQUALIFIER_TRIGGERS: timedelta(days=90),
}

# Below this, a signal has demoted from scoring input to research prompt
# (Doc 09 §7: decayed knowledge is what refresh recipes re-verify).
STALE_SIGNAL_FLOOR = 0.25


@dataclass(frozen=True)
class Signal:
    id: UUID
    business_record_id: UUID
    family: SignalFamily
    name: str  # e.g. "active_paid_media", "hiring_marketing_role"
    confidence: float
    supporting_evidence_ids: tuple[UUID, ...]
    newest_observation_at: datetime
    rule_version: str
    derived_at: datetime


def decayed_confidence(
    base_confidence: float,
    *,
    family: SignalFamily,
    newest_observation_at: datetime,
    now: datetime,
) -> float:
    """Exponential decay toward unknown on the family's half-life. Fresh
    evidence keeps full confidence; each half-life halves it. Deterministic:
    the same inputs always yield the same number."""
    age = now - newest_observation_at
    if age <= timedelta(0):
        return base_confidence
    half_life = HALF_LIFE_BY_FAMILY[family]
    return base_confidence * math.pow(0.5, age / half_life)


def is_stale(signal: Signal, *, now: datetime) -> bool:
    """A stale signal prompts re-observation rather than underwriting scores."""
    return (
        decayed_confidence(
            signal.confidence,
            family=signal.family,
            newest_observation_at=signal.newest_observation_at,
            now=now,
        )
        < STALE_SIGNAL_FLOOR
    )
