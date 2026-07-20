"""The consumer loop's semantics, with handlers faked at the registry seam."""

from datetime import UTC, datetime, time
from uuid import uuid4

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.repositories.jobs import Job, JobQueue, JobStatus
from app.repositories.orm import JobRow
from app.workers.main import process_next_job
from app.workers.schedules import HEARTBEAT_JOB_TYPE, enqueue_due_schedules


def enqueue(db: Engine, job_type: str, *, max_attempts: int = 5) -> None:
    with Session(db) as session:
        JobQueue(session).enqueue(
            job_type, idempotency_key=f"{job_type}:{uuid4()}", max_attempts=max_attempts
        )
        session.commit()


def job_states(db: Engine) -> list[tuple[str, str, int]]:
    with Session(db) as session:
        rows = session.query(JobRow).order_by(JobRow.created_at).all()
        return [(row.job_type, row.status, row.attempts) for row in rows]


def test_successful_job_is_marked_succeeded(db: Engine) -> None:
    handled: list[str] = []

    def handler(session: Session, job: Job) -> None:
        handled.append(job.job_type)

    enqueue(db, "greet")
    assert process_next_job({"greet": handler}) is True
    assert handled == ["greet"]
    assert job_states(db) == [("greet", JobStatus.SUCCEEDED.value, 1)]
    assert process_next_job({"greet": handler}) is False  # queue idle


def test_failing_handler_books_the_attempt_and_backs_off(db: Engine) -> None:
    def handler(session: Session, job: Job) -> None:
        raise RuntimeError("transient failure")

    enqueue(db, "flaky")
    assert process_next_job({"flaky": handler}) is True
    assert job_states(db) == [("flaky", JobStatus.PENDING.value, 1)]


def test_poison_job_dead_letters_after_max_attempts(db: Engine) -> None:
    def handler(session: Session, job: Job) -> None:
        raise RuntimeError("always broken")

    enqueue(db, "poison", max_attempts=1)
    assert process_next_job({"poison": handler}) is True
    assert job_states(db) == [("poison", JobStatus.DEAD.value, 1)]


def test_unregistered_job_type_takes_the_failure_path(db: Engine) -> None:
    enqueue(db, "unknown", max_attempts=1)
    assert process_next_job({}) is True
    assert job_states(db) == [("unknown", JobStatus.DEAD.value, 1)]


def test_failed_handler_writes_roll_back(db: Engine) -> None:
    """Handler side-effects and job completion commit together, or not at all."""

    def handler(session: Session, job: Job) -> None:
        JobQueue(session).enqueue("side-effect", idempotency_key=f"side:{uuid4()}")
        raise RuntimeError("fail after writing")

    enqueue(db, "writer", max_attempts=1)
    process_next_job({"writer": handler})
    states = job_states(db)
    assert ("side-effect", JobStatus.PENDING.value, 0) not in states
    assert states == [("writer", JobStatus.DEAD.value, 1)]


def test_daily_schedule_enqueues_exactly_once_per_day(db: Engine) -> None:
    from app.workers.schedules import SCHEDULES

    after_due = datetime.combine(datetime.now(UTC).date(), time(23, 59), tzinfo=UTC)
    with Session(db) as session:
        enqueue_due_schedules(session, now=after_due)
        enqueue_due_schedules(session, now=after_due)
        session.commit()
        counts = JobQueue(session).counts_by_status()
    assert counts == {"pending": len(SCHEDULES)}


def test_schedule_not_due_enqueues_nothing(db: Engine) -> None:
    before_due = datetime.combine(datetime.now(UTC).date(), time(0, 0), tzinfo=UTC)
    with Session(db) as session:
        enqueue_due_schedules(session, now=before_due)
        session.commit()
        assert JobQueue(session).counts_by_status() == {}


def test_heartbeat_schedule_is_registered() -> None:
    from app.workers.handlers import JOB_HANDLERS
    from app.workers.schedules import SCHEDULES

    scheduled_types = {schedule.job_type for schedule in SCHEDULES}
    assert HEARTBEAT_JOB_TYPE in scheduled_types
    assert scheduled_types <= set(JOB_HANDLERS)  # every schedule has a handler
