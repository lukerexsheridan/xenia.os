"""Job semantics (Doc 10, Sprint 3 DoD): idempotency, SKIP LOCKED, backoff,
dead-lettering, and killed-worker resume."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from app.repositories.jobs import JobQueue, JobStatus, backoff_delay
from app.repositories.orm import JobRow


def unique_key(prefix: str) -> str:
    return f"{prefix}:{uuid4()}"


def test_enqueue_is_idempotent_by_key(db: Engine) -> None:
    key = unique_key("idem")
    with Session(db) as session:
        queue = JobQueue(session)
        first = queue.enqueue("noop", idempotency_key=key)
        second = queue.enqueue("noop", idempotency_key=key)
        session.commit()
        count = session.execute(select(JobRow).where(JobRow.idempotency_key == key)).scalars().all()
    assert first is not None
    assert second is None
    assert len(count) == 1


def test_claim_returns_due_jobs_in_priority_then_time_order(db: Engine) -> None:
    now = datetime.now(UTC)
    with Session(db) as session:
        queue = JobQueue(session)
        queue.enqueue("later", idempotency_key=unique_key("later"), run_at=now + timedelta(hours=1))
        queue.enqueue("low", idempotency_key=unique_key("low"), priority=0, run_at=now)
        queue.enqueue("high", idempotency_key=unique_key("high"), priority=10, run_at=now)
        session.commit()

        first = queue.claim_next()
        assert first is not None and first.job_type == "high"
        queue.mark_succeeded(first.id)
        session.commit()

        second = queue.claim_next()
        assert second is not None and second.job_type == "low"
        queue.mark_succeeded(second.id)
        session.commit()

        assert queue.claim_next() is None  # "later" is not due yet


def test_claimed_job_is_skipped_by_a_second_worker(db: Engine) -> None:
    key = unique_key("locked")
    with Session(db) as session_one, Session(db) as session_two:
        JobQueue(session_one).enqueue("only", idempotency_key=key)
        session_one.commit()

        claimed = JobQueue(session_one).claim_next()
        assert claimed is not None
        # Second worker, concurrent transaction: FOR UPDATE SKIP LOCKED
        # must pass over the held row rather than block or double-claim.
        assert JobQueue(session_two).claim_next() is None
        session_one.rollback()


def test_killed_worker_resumes_cleanly(db: Engine) -> None:
    """A crash mid-job aborts the claim transaction; the job is pending again."""
    key = unique_key("crash")
    with Session(db) as session:
        JobQueue(session).enqueue("crashy", idempotency_key=key)
        session.commit()

    with Session(db) as session:
        assert JobQueue(session).claim_next() is not None
        session.rollback()  # the "kill"

    with Session(db) as session:
        resumed = JobQueue(session).claim_next()
        assert resumed is not None and resumed.idempotency_key == key
        assert resumed.attempts == 0


def test_failure_backs_off_then_dead_letters(db: Engine) -> None:
    now = datetime.now(UTC)
    with Session(db) as session:
        queue = JobQueue(session)
        job_id = queue.enqueue(
            "poison", idempotency_key=unique_key("poison"), max_attempts=2, run_at=now
        )
        assert job_id is not None
        session.commit()

        first_failure = queue.record_failure(job_id, error="boom", now=now)
        session.commit()
        assert first_failure.status is JobStatus.PENDING
        assert first_failure.attempts == 1
        assert first_failure.run_at >= now + backoff_delay(1)
        assert first_failure.last_error == "boom"

        second_failure = queue.record_failure(job_id, error="boom again", now=now)
        session.commit()
        assert second_failure.status is JobStatus.DEAD
        assert second_failure.attempts == 2


def test_counts_by_status(db: Engine) -> None:
    with Session(db) as session:
        queue = JobQueue(session)
        queue.enqueue("a", idempotency_key=unique_key("a"))
        queue.enqueue("b", idempotency_key=unique_key("b"))
        session.commit()
        assert queue.counts_by_status() == {"pending": 2}
