"""ResolveEntity — entity binding v1 (Doc 10 Sprint 7; ADR-008).

Deterministic strong keys bind automatically (domain, register number —
attestation-grade identity); everything weaker queues for the Editor, because
same-name-different-company is the Class-A misattribution vector (Doc 04 §8
A2). The decision is always recorded with its method and confidence
(Doc 09 §4).
"""

import re
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.domain.business_record import BusinessRecord
from app.repositories.acquisition import BindingReview, SqlEntityBindingReviewRepo
from app.repositories.business_records import SqlBusinessRecordRepo

# ADR-008: the auto-binding floor [calibrates]. Strong keys sit above it;
# the only current heuristic (normalised-name equality) sits below it.
BINDING_CONFIDENCE_FLOOR = 0.85
STRONG_KEY_CONFIDENCE = 1.0
NAME_MATCH_CONFIDENCE = 0.7

_LEGAL_SUFFIXES = re.compile(
    r"\b(ltd|limited|plc|llp|llc|inc|incorporated|co|company)\b\.?", re.IGNORECASE
)


def normalise_company_name(name: str) -> str:
    stripped = _LEGAL_SUFFIXES.sub("", name.lower())
    return re.sub(r"[^a-z0-9]+", " ", stripped).strip()


class BindingMethod(StrEnum):
    DOMAIN = "domain"
    REGISTER_NUMBER = "register_number"
    QUEUED_FOR_REVIEW = "queued_for_review"


@dataclass(frozen=True)
class BindingDecision:
    method: BindingMethod
    confidence: float
    business_record: BusinessRecord | None  # None while the queue holds it
    review: BindingReview | None


class ResolveEntity:
    def __init__(
        self,
        business_repo: SqlBusinessRecordRepo,
        review_repo: SqlEntityBindingReviewRepo,
    ) -> None:
        self._business_repo = business_repo
        self._review_repo = review_repo

    def execute(
        self,
        *,
        candidate_name: str,
        website_domain: str | None = None,
        register_number: str | None = None,
        canonical_item_ids: list[UUID] | None = None,
    ) -> BindingDecision:
        if website_domain:
            record = self._business_repo.find_or_create(
                canonical_name=candidate_name,
                website_domain=website_domain,
                register_number=register_number,
            )
            return BindingDecision(
                method=BindingMethod.DOMAIN,
                confidence=STRONG_KEY_CONFIDENCE,
                business_record=record,
                review=None,
            )
        if register_number:
            record = self._business_repo.find_or_create(
                canonical_name=candidate_name,
                website_domain=None,
                register_number=register_number,
            )
            return BindingDecision(
                method=BindingMethod.REGISTER_NUMBER,
                confidence=STRONG_KEY_CONFIDENCE,
                business_record=record,
                review=None,
            )
        # No strong key: the name heuristic scores below the floor by design
        # (ADR-008) — the human floor holds it, never a guess.
        review = self._review_repo.enqueue(
            candidate_name=candidate_name,
            website_domain=None,
            register_number=None,
            confidence=NAME_MATCH_CONFIDENCE,
            canonical_item_ids=canonical_item_ids or [],
        )
        return BindingDecision(
            method=BindingMethod.QUEUED_FOR_REVIEW,
            confidence=NAME_MATCH_CONFIDENCE,
            business_record=None,
            review=review,
        )
