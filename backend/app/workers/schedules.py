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
SIGNAL_DECAY_SWEEP_JOB_TYPE = "signal_decay_sweep"
QUEUE_ASSEMBLY_JOB_TYPE = "assemble_queues"
WEEKLY_BRIEF_SWEEP_JOB_TYPE = "weekly_brief_sweep"


@dataclass(frozen=True)
class DailySchedule:
    job_type: str
    at_utc: time
    # None -> every day; 0-6 -> only that ISO weekday (0 = Monday).
    weekday: int | None = None


SCHEDULES: tuple[DailySchedule, ...] = (
    # The daily heartbeat email to the founder (Doc 10, Sprint 3).
    DailySchedule(job_type=HEARTBEAT_JOB_TYPE, at_utc=time(6, 0)),
    # The freshness economy's clock (Doc 09 §7): stale signals demote daily.
    DailySchedule(job_type=SIGNAL_DECAY_SWEEP_JOB_TYPE, at_utc=time(5, 0)),
    # Monday's queues, assembled before anyone's Monday starts (Doc 03 §5).
    # Runs after the decay sweep so ranking sees post-decay confidences.
    DailySchedule(job_type=QUEUE_ASSEMBLY_JOB_TYPE, at_utc=time(5, 45), weekday=0),
    # The weekly brief sweep runs daily; each workspace sends only when it is
    # Monday morning in *their* timezone (Doc 03 C8), once per week by
    # idempotency key.
    DailySchedule(job_type=WEEKLY_BRIEF_SWEEP_JOB_TYPE, at_utc=time(6, 0)),
)


def enqueue_due_schedules(session: Session, *, now: datetime | None = None) -> None:
    current = now or datetime.now(UTC)
    queue = JobQueue(session)
    for schedule in SCHEDULES:
        if schedule.weekday is not None and current.weekday() != schedule.weekday:
            continue
        due_at = datetime.combine(current.date(), schedule.at_utc, tzinfo=UTC)
        if current >= due_at:
            queue.enqueue(
                schedule.job_type,
                idempotency_key=f"{schedule.job_type}:{current.date().isoformat()}",
                run_at=due_at,
            )
