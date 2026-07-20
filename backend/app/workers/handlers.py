"""Job handlers: a named payload + a service call, nothing more (Doc 08 §7).

Handlers run inside the claiming transaction, so a handler's writes and the
job's completion commit together.
"""

import logging
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.integrations.resend.client import NullEmailSender, ResendClient
from app.repositories.jobs import Job, JobQueue
from app.services.receive_stripe_webhook import STRIPE_WEBHOOK_JOB_TYPE
from app.services.send_heartbeat import EmailSender, SendHeartbeat
from app.workers.schedules import HEARTBEAT_JOB_TYPE

logger = logging.getLogger(__name__)

JobHandler = Callable[[Session, Job], None]


def _email_sender() -> EmailSender:
    settings = get_settings()
    if settings.resend_api_key:
        return ResendClient(api_key=settings.resend_api_key, from_address=settings.email_from)
    return NullEmailSender()


def handle_send_heartbeat_email(session: Session, job: Job) -> None:
    SendHeartbeat(_email_sender(), JobQueue(session)).execute(to=get_settings().heartbeat_email_to)


def handle_stripe_webhook(session: Session, job: Job) -> None:
    # Billing state sync lands in Epic 11; until then receipt is recorded so
    # replayed history is processable later. IDs only in logs (Doc 05).
    logger.info(
        "stripe webhook received: %s (%s)",
        job.payload.get("event_id"),
        job.payload.get("event_type"),
    )


JOB_HANDLERS: dict[str, JobHandler] = {
    HEARTBEAT_JOB_TYPE: handle_send_heartbeat_email,
    STRIPE_WEBHOOK_JOB_TYPE: handle_stripe_webhook,
}
