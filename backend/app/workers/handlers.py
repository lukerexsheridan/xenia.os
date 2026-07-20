"""Job handlers: a named payload + a service call, nothing more (Doc 08 §7).

Handlers run inside the claiming transaction, so a handler's writes and the
job's completion commit together.
"""

import logging
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.integrations.resend.client import NullEmailSender, ResendClient
from app.repositories.evidence import SqlEvidenceRepo
from app.repositories.jobs import Job, JobQueue
from app.repositories.knowledge import SqlKnowledgeRepo
from app.services.derive_signals import DeriveSignals
from app.services.receive_stripe_webhook import STRIPE_WEBHOOK_JOB_TYPE
from app.services.send_heartbeat import EmailSender, SendHeartbeat
from app.workers.schedules import HEARTBEAT_JOB_TYPE, SIGNAL_DECAY_SWEEP_JOB_TYPE

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


def handle_signal_decay_sweep(session: Session, job: Job) -> None:
    """Re-derivation IS decay (Doc 09 §7): stale signals demote toward
    unknown; the sweep and the freshness economy are two halves of one
    system."""
    knowledge_repo = SqlKnowledgeRepo(session)
    derive = DeriveSignals(SqlEvidenceRepo(session), knowledge_repo)
    for business_record_id in knowledge_repo.businesses_with_signals():
        derive.execute(business_record_id)


JOB_HANDLERS: dict[str, JobHandler] = {
    HEARTBEAT_JOB_TYPE: handle_send_heartbeat_email,
    STRIPE_WEBHOOK_JOB_TYPE: handle_stripe_webhook,
    SIGNAL_DECAY_SWEEP_JOB_TYPE: handle_signal_decay_sweep,
}
