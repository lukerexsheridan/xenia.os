"""The Postgres-backed job queue (Doc 08 §7): transactional enqueue, `FOR
UPDATE SKIP LOCKED` consumption, exponential backoff, dead-lettering.

Claim-and-process happen inside one transaction: a killed worker's transaction
aborts, the row lock releases, and the job is simply pending again — resume is
a property of the design, not a recovery procedure. No broker until the
queue's measured profile demands one (AP8).
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.repositories.orm import JobRow

logger = logging.getLogger(__name__)

DEFAULT_MAX_ATTEMPTS = 5
BACKOFF_BASE_SECONDS = 30
BACKOFF_CAP_SECONDS = 3600


class JobStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    # Poison jobs land here after max_attempts; a dead job is an ops signal
    # (ERROR log — "error pages someone", Doc 08 §9) and stays queryable.
    DEAD = "dead"


@dataclass(frozen=True)
class Job:
    id: UUID
    job_type: str
    idempotency_key: str
    payload: dict[str, Any]
    status: JobStatus
    attempts: int
    max_attempts: int
    run_at: datetime
    workspace_id: UUID | None
    last_error: str | None


def _to_job(row: JobRow) -> Job:
    return Job(
        id=row.id,
        job_type=row.job_type,
        idempotency_key=row.idempotency_key,
        payload=row.payload,
        status=JobStatus(row.status),
        attempts=row.attempts,
        max_attempts=row.max_attempts,
        run_at=row.run_at,
        workspace_id=row.workspace_id,
        last_error=row.last_error,
    )


def backoff_delay(attempts: int) -> timedelta:
    """Exponential: 30s, 60s, 120s… capped at an hour."""
    seconds = BACKOFF_BASE_SECONDS * 2 ** max(attempts - 1, 0)
    return timedelta(seconds=min(seconds, BACKOFF_CAP_SECONDS))


class JobQueue:
    def __init__(self, session: Session) -> None:
        self._session = session

    def enqueue(
        self,
        job_type: str,
        *,
        idempotency_key: str,
        payload: dict[str, Any] | None = None,
        run_at: datetime | None = None,
        priority: int = 0,
        workspace_id: UUID | None = None,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    ) -> UUID | None:
        """Insert a job; a duplicate idempotency key is a silent no-op.

        Enqueue shares the caller's transaction, so a job and the state change
        that triggered it commit together — no lost work, no phantom work.
        Returns the new job id, or None when the key already existed.
        """
        statement = (
            insert(JobRow)
            .values(
                job_type=job_type,
                idempotency_key=idempotency_key,
                payload=payload or {},
                status=JobStatus.PENDING.value,
                priority=priority,
                run_at=run_at or datetime.now(UTC),
                attempts=0,
                max_attempts=max_attempts,
                workspace_id=workspace_id,
            )
            .on_conflict_do_nothing(index_elements=[JobRow.idempotency_key])
            .returning(JobRow.id)
        )
        return self._session.execute(statement).scalar_one_or_none()

    def claim_next(self, *, now: datetime | None = None) -> Job | None:
        """Lock and return the next due job, skipping rows other workers hold.

        The lock lives until the caller's transaction ends; process the job in
        the same transaction and the queue semantics do the rest.
        """
        row = self._session.execute(
            select(JobRow)
            .where(
                JobRow.status == JobStatus.PENDING.value,
                JobRow.run_at <= (now or datetime.now(UTC)),
            )
            .order_by(JobRow.priority.desc(), JobRow.run_at)
            .limit(1)
            .with_for_update(skip_locked=True)
        ).scalar_one_or_none()
        return _to_job(row) if row else None

    def mark_succeeded(self, job_id: UUID) -> None:
        row = self._session.get_one(JobRow, job_id)
        row.status = JobStatus.SUCCEEDED.value
        row.attempts += 1
        self._session.flush()

    def record_failure(self, job_id: UUID, *, error: str, now: datetime | None = None) -> Job:
        """Book a failed attempt: retry with backoff, or dead-letter."""
        row = self._session.execute(
            select(JobRow).where(JobRow.id == job_id).with_for_update()
        ).scalar_one()
        row.attempts += 1
        row.last_error = error
        if row.attempts >= row.max_attempts:
            row.status = JobStatus.DEAD.value
            logger.error("job dead-lettered after %s attempts: %s", row.attempts, row.job_type)
        else:
            row.run_at = (now or datetime.now(UTC)) + backoff_delay(row.attempts)
        self._session.flush()
        return _to_job(row)

    def counts_by_status(self) -> dict[str, int]:
        rows = self._session.execute(
            select(JobRow.status, func.count()).group_by(JobRow.status)
        ).all()
        return {str(job_status): int(count) for job_status, count in rows}
