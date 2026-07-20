"""Worker entrypoint — the monolith's second process (Doc 08 SS2/SS7).

The consumer claims one job per transaction with FOR UPDATE SKIP LOCKED and
processes it inside that same transaction: success commits handler writes and
completion together; a crash aborts the transaction and the job is simply
pending again (resume by construction). Handler failures roll back the
handler's writes, then book the attempt — backoff or dead-letter — in a
fresh transaction.

The scheduler is the worker's clock: each loop enqueues any due scheduled
jobs (idempotency keys make ticking harmless).
"""

import logging
import signal
import time
from types import FrameType

from app.core.config import get_settings
from app.core.db import session_scope
from app.core.logging import configure_logging
from app.core.observability import init_error_reporting
from app.repositories.jobs import JobQueue
from app.workers.handlers import JOB_HANDLERS, JobHandler
from app.workers.schedules import enqueue_due_schedules

logger = logging.getLogger(__name__)

POLL_SECONDS = 5.0


def process_next_job(handlers: dict[str, JobHandler]) -> bool:
    """Claim and process one due job. Returns False when the queue is idle."""
    claimed_id = None
    claimed_type = ""
    try:
        with session_scope() as session:
            job = JobQueue(session).claim_next()
            if job is None:
                return False
            claimed_id, claimed_type = job.id, job.job_type
            handler = handlers.get(job.job_type)
            if handler is None:
                raise LookupError(f"no handler registered for job type {job.job_type!r}")
            handler(session, job)
            JobQueue(session).mark_succeeded(job.id)
        logger.info("job succeeded: %s", claimed_type)
        return True
    except Exception as exc:
        if claimed_id is None:
            raise  # claiming itself failed (DB down): let the loop back off
        logger.warning("job failed: %s — %s", claimed_type, exc)
        with session_scope() as session:
            JobQueue(session).record_failure(claimed_id, error=repr(exc))
        return True


def run_forever() -> None:
    stopping = False

    def request_stop(signum: int, frame: FrameType | None) -> None:
        nonlocal stopping
        stopping = True
        logger.info("worker stopping after current job")

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    logger.info("worker started")
    while not stopping:
        try:
            with session_scope() as session:
                enqueue_due_schedules(session)
            worked = process_next_job(JOB_HANDLERS)
        except Exception:
            logger.exception("worker loop error; backing off")
            worked = False
        if not worked and not stopping:
            time.sleep(POLL_SECONDS)
    logger.info("worker stopped")


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    init_error_reporting(settings)
    run_forever()


if __name__ == "__main__":
    main()
