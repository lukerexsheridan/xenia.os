"""Schedule definitions in code — the worker's clock (Doc 08 §7).

A daily schedule enqueues its job once per day: the idempotency key is
`{job_type}:{date}`, so every tick past the due time is a no-op after the
first. Workspace-local scheduling (Monday 08:00 *their* time) arrives with
the delivery epics; ops schedules run in UTC.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, time

from sqlalchemy.orm import Session

from app.repositories.jobs import JobQueue

HEARTBEAT_JOB_TYPE = "send_heartbeat_email"


@dataclass(frozen=True)
class DailySchedule:
    job_type: str
    at_utc: time


SCHEDULES: tuple[DailySchedule, ...] = (
    # The daily heartbeat email to the founder (Doc 10, Sprint 3).
    DailySchedule(job_type=HEARTBEAT_JOB_TYPE, at_utc=time(6, 0)),
)


def enqueue_due_schedules(session: Session, *, now: datetime | None = None) -> None:
    current = now or datetime.now(UTC)
    queue = JobQueue(session)
    for schedule in SCHEDULES:
        due_at = datetime.combine(current.date(), schedule.at_utc, tzinfo=UTC)
        if current >= due_at:
            queue.enqueue(
                schedule.job_type,
                idempotency_key=f"{schedule.job_type}:{current.date().isoformat()}",
                run_at=due_at,
            )
