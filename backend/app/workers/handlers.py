"""Job handlers: a named payload + a service call, nothing more (Doc 08 §7).

Handlers run inside the claiming transaction, so a handler's writes and the
job's completion commit together.
"""

import logging
import time
from collections.abc import Callable
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.pipelines.extract_page_evidence import ExtractPageEvidence
from app.ai.providers.openai_responses import OpenAIResponsesProvider
from app.core.config import get_settings
from app.integrations.object_storage import S3ObjectStore
from app.integrations.resend.client import NullEmailSender, ResendClient
from app.integrations.sources.http_transport import HttpxTransport
from app.integrations.sources.politeness import PolitenessEngine
from app.repositories.acquisition import (
    SqlCanonicalContentRepo,
    SqlEntityBindingReviewRepo,
    SqlSourceHealthRepo,
)
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.evidence import SqlEvidenceRepo
from app.repositories.jobs import Job, JobQueue
from app.repositories.knowledge import SqlKnowledgeRepo
from app.repositories.snapshots import SqlSourceSnapshotRepo
from app.services.acquire_footprint import AcquireFootprint
from app.services.capture_snapshot import CaptureSnapshot
from app.services.derive_signals import DeriveSignals
from app.services.extract_evidence import ExtractEvidence
from app.services.receive_stripe_webhook import STRIPE_WEBHOOK_JOB_TYPE
from app.services.research_run import RunResearch
from app.services.resolve_entity import ResolveEntity
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


RESEARCH_RUN_JOB_TYPE = "research_run"


def handle_research_run(session: Session, job: Job) -> None:
    """One queued command: research this business (Doc 10, Epic 6). Every
    stage is idempotent, so a retried job resumes past completed work — the
    checkpointing property, not a procedure."""
    settings = get_settings()
    store = S3ObjectStore(
        endpoint_url=settings.object_storage_endpoint,
        access_key=settings.object_storage_access_key,
        secret_key=settings.object_storage_secret_key,
        bucket=settings.object_storage_bucket,
    )
    store.ensure_bucket()
    capture = CaptureSnapshot(
        PolitenessEngine(
            HttpxTransport(),
            user_agent=settings.politeness_user_agent,
            clock=time.monotonic,
            sleeper=time.sleep,
        ),
        store,
        SqlSourceSnapshotRepo(session),
    )
    pipeline = (
        ExtractPageEvidence(
            OpenAIResponsesProvider(api_key=settings.openai_api_key, model=settings.openai_model)
        )
        if settings.openai_api_key
        else None
    )
    run = RunResearch(
        AcquireFootprint(
            capture,
            SqlBusinessRecordRepo(session),
            SqlCanonicalContentRepo(session),
            SqlSourceHealthRepo(session),
            ResolveEntity(SqlBusinessRecordRepo(session), SqlEntityBindingReviewRepo(session)),
            ad_library_access_token=settings.ad_library_access_token,
        ),
        ExtractEvidence(
            SqlKnowledgeRepo(session),
            SqlEvidenceRepo(session),
            SqlBusinessRecordRepo(session),
            SqlSourceHealthRepo(session),
            pipeline,
        ),
        DeriveSignals(SqlEvidenceRepo(session), SqlKnowledgeRepo(session)),
        SqlKnowledgeRepo(session),
    )
    report = run.execute(UUID(str(job.payload["business_record_id"])))
    logger.info(
        "research run complete: %s (%s, %s fetches)",
        report.business_record_id,
        report.recipe.trigger.value,
        report.ledger.get("fetches", 0),
    )


JOB_HANDLERS: dict[str, JobHandler] = {
    HEARTBEAT_JOB_TYPE: handle_send_heartbeat_email,
    STRIPE_WEBHOOK_JOB_TYPE: handle_stripe_webhook,
    SIGNAL_DECAY_SWEEP_JOB_TYPE: handle_signal_decay_sweep,
    RESEARCH_RUN_JOB_TYPE: handle_research_run,
}
