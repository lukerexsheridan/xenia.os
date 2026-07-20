"""DeriveSignals — the four families as rules (Doc 10, Sprint 10; Doc 09 §7).

Predominantly rules over typed evidence: a signal exists only when its
evidence basis meets its type's threshold, stores its derivation, and its
confidence is the deterministic decay function of its newest supporting
observation's age — so re-deriving *is* the decay sweep, and a stale signal
demotes toward unknown, never toward false.
"""

import re
from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.evidence import Evidence, EvidenceType
from app.domain.signal import Signal, SignalFamily, decayed_confidence
from app.repositories.evidence import SqlEvidenceRepo
from app.repositories.knowledge import SqlKnowledgeRepo

RULE_VERSION = "signals/1"

_MARKETING_HIRE = re.compile(
    r"\b(marketing|growth|performance|paid (social|search|media)|ppc|seo|ecommerce)\b", re.I
)
_IN_HOUSE_SENIOR = re.compile(r"\b(head of marketing|marketing director|cmo)\b", re.I)


def _company_active(item: Evidence) -> bool:
    return (
        item.claim_slot == "register:company-profile"
        and item.evidence_type is EvidenceType.THIRD_PARTY_ATTESTATION
        and "status active" in item.claim.lower()
    )


def _active_paid_media(item: Evidence) -> bool:
    return (
        item.claim_slot == "ad_activity"
        and item.evidence_type is EvidenceType.MEASURED_OBSERVATION
        and "running ads" in item.claim.lower()
    )


def _hiring_marketing(item: Evidence) -> bool:
    return (
        item.claim_slot.startswith("hiring:")
        and item.evidence_type is EvidenceType.MARKET_BEHAVIOURAL
        and _MARKETING_HIRE.search(item.claim) is not None
        and _IN_HOUSE_SENIOR.search(item.claim) is None
    )


def _in_house_marketing_team(item: Evidence) -> bool:
    return item.claim_slot.startswith("hiring:") and _IN_HOUSE_SENIOR.search(item.claim) is not None


# The rule table (Doc 09 §7): family, name, base confidence, and the
# evidence-basis threshold expressed as the matcher itself. Promotion
# requires at least one matching item of the required type — e.g.
# active_paid_media requires E1 ad-library evidence, never a self-declared
# "we advertise".
_RULES: tuple[tuple[SignalFamily, str, float, Callable[[Evidence], bool]], ...] = (
    (SignalFamily.FACTS, "company_active", 0.95, _company_active),
    (SignalFamily.ADS_TECHNOLOGY, "active_paid_media", 0.9, _active_paid_media),
    (SignalFamily.HIRING, "hiring_marketing_role", 0.85, _hiring_marketing),
    (SignalFamily.DISQUALIFIER_TRIGGERS, "in_house_marketing_team", 0.8, _in_house_marketing_team),
)


class DeriveSignals:
    def __init__(self, evidence_repo: SqlEvidenceRepo, knowledge_repo: SqlKnowledgeRepo) -> None:
        self._evidence_repo = evidence_repo
        self._knowledge_repo = knowledge_repo

    def execute(self, business_record_id: UUID, *, now: datetime | None = None) -> list[Signal]:
        """Derive (or re-derive) the business's signals. Re-running with a
        later `now` is the decay sweep: confidence falls deterministically
        with the newest observation's age."""
        current = now or datetime.now(UTC)
        evidence = self._evidence_repo.list_for_business(business_record_id)
        signals: list[Signal] = []
        for family, name, base, matcher in _RULES:
            matching = [item for item in evidence if matcher(item)]
            if not matching:
                continue
            newest = max(item.observed_at for item in matching)
            signal = Signal(
                id=uuid4(),
                business_record_id=business_record_id,
                family=family,
                name=name,
                confidence=decayed_confidence(
                    base, family=family, newest_observation_at=newest, now=current
                ),
                supporting_evidence_ids=tuple(sorted((item.id for item in matching), key=str)),
                newest_observation_at=newest,
                rule_version=RULE_VERSION,
                derived_at=current,
            )
            self._knowledge_repo.upsert_signal(signal)
            signals.append(signal)
        return signals
