"""ResolveBindingReview — the Editor closes a floor-queue entry (ADR-008).

Binding is misattribution-critical: only a human resolution attaches queued
canonical items to a BusinessRecord; a rejection leaves them unbound (and
therefore unusable as evidence — the queue SLA is structural).
"""

from datetime import UTC, datetime
from uuid import UUID

from app.core.errors import ConflictError, NotFoundError, XeniaError
from app.repositories.acquisition import (
    BindingReview,
    BindingReviewStatus,
    SqlCanonicalContentRepo,
    SqlEntityBindingReviewRepo,
)
from app.repositories.business_records import SqlBusinessRecordRepo


class ResolveBindingReview:
    def __init__(
        self,
        review_repo: SqlEntityBindingReviewRepo,
        canonical_repo: SqlCanonicalContentRepo,
        business_repo: SqlBusinessRecordRepo,
    ) -> None:
        self._review_repo = review_repo
        self._canonical_repo = canonical_repo
        self._business_repo = business_repo

    def execute(self, review_id: UUID, *, business_record_id: UUID | None) -> BindingReview:
        """Bind to the given business, or reject when business_record_id is None."""
        review = self._review_repo.get(review_id)
        if review is None:
            raise NotFoundError("binding review not found")
        if review.status is not BindingReviewStatus.PENDING:
            raise ConflictError("this binding review is already resolved")
        now = datetime.now(UTC)
        if business_record_id is None:
            return self._review_repo.resolve(
                review_id, status=BindingReviewStatus.REJECTED, now=now
            )
        if self._business_repo.get(business_record_id) is None:
            raise XeniaError("business record does not exist")
        self._canonical_repo.bind(list(review.canonical_item_ids), business_record_id)
        return self._review_repo.resolve(review_id, status=BindingReviewStatus.BOUND, now=now)
