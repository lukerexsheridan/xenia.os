"""Job handlers: a named payload + a service call, nothing more (Doc 08 §7).

Handlers run inside the claiming transaction, so a handler's writes and the
job's completion commit together.
"""

import logging
import time
from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.ai.pipelines.extract_page_evidence import ExtractPageEvidence
from app.ai.providers.openai_responses import OpenAIResponsesProvider
from app.core.config import get_settings
from app.domain.audit import AuditAction
from app.domain.prospect import ProspectStatus
from app.integrations.object_storage import S3ObjectStore
from app.integrations.resend.client import NullEmailSender, ResendClient
from app.integrations.sources.http_transport import HttpxTransport
from app.integrations.sources.politeness import PolitenessEngine
from app.repositories.acquisition import (
    SqlCanonicalContentRepo,
    SqlEntityBindingReviewRepo,
    SqlSourceHealthRepo,
)
from app.repositories.audit import SqlAuditEntryRepo
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.dna import SqlDnaRepo
from app.repositories.evidence import SqlEvidenceRepo
from app.repositories.identity import SqlIdentityRepo
from app.repositories.jobs import Job, JobQueue
from app.repositories.knowledge import SqlKnowledgeRepo
from app.repositories.prospects import SqlProspectRepo
from app.repositories.recommendations import SqlRecommendationRepo
from app.repositories.snapshots import SqlSourceSnapshotRepo
from app.repositories.teaching import SqlTeachingRepo
from app.services.acquire_footprint import AcquireFootprint
from app.services.assemble_queue import AssembleQueue
from app.services.capture_snapshot import CaptureSnapshot
from app.services.compose_weekly_brief import SendWeeklyBrief
from app.services.derive_signals import DeriveSignals
from app.services.extract_evidence import ExtractEvidence
from app.services.receive_stripe_webhook import STRIPE_WEBHOOK_JOB_TYPE
from app.services.research_run import RunResearch
from app.services.resolve_entity import ResolveEntity
from app.services.send_heartbeat import EmailSender, SendHeartbeat
from app.workers.schedules import (
    HEARTBEAT_JOB_TYPE,
    QUEUE_ASSEMBLY_JOB_TYPE,
    SIGNAL_DECAY_SWEEP_JOB_TYPE,
    WEEKLY_BRIEF_SWEEP_JOB_TYPE,
)

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
    """Billing state sync (Doc 10, Sprint 20): checkout binds the customer
    to the workspace via client_reference_id; subscription events keep the
    status honest. Unknown event types are received and ignored — additive,
    never brittle. IDs only in logs (Doc 05)."""
    identity = SqlIdentityRepo(session)
    event_type = str(job.payload.get("event_type", ""))
    data_object = job.payload.get("event", {}).get("data", {}).get("object", {})
    if event_type == "checkout.session.completed":
        reference = data_object.get("client_reference_id")
        customer = data_object.get("customer")
        if reference and customer:
            identity.set_billing(
                UUID(str(reference)), stripe_customer_id=str(customer), status="active"
            )
    elif event_type in ("customer.subscription.updated", "customer.subscription.deleted"):
        customer = data_object.get("customer")
        if customer:
            workspace_id = identity.workspace_id_for_stripe_customer(str(customer))
            if workspace_id is not None:
                status = (
                    "canceled"
                    if event_type.endswith("deleted")
                    else str(data_object.get("status", "active"))
                )
                identity.set_billing(workspace_id, stripe_customer_id=None, status=status)
    logger.info(
        "stripe webhook processed: %s (%s)",
        job.payload.get("event_id"),
        event_type,
    )


def handle_signal_decay_sweep(session: Session, job: Job) -> None:
    """Re-derivation IS decay (Doc 09 §7): stale signals demote toward
    unknown; the sweep and the freshness economy are two halves of one
    system."""
    knowledge_repo = SqlKnowledgeRepo(session)
    derive = DeriveSignals(SqlEvidenceRepo(session), knowledge_repo)
    for business_record_id in knowledge_repo.businesses_with_signals():
        derive.execute(business_record_id)


def handle_assemble_queues(session: Session, job: Job) -> None:
    """Monday's queues for every workspace (Doc 03 §5): deterministic
    scoring against each tenant's DNA, through workspace-scoped repos."""
    for workspace_id in SqlIdentityRepo(session).list_workspace_ids():
        result = AssembleQueue(
            SqlDnaRepo(session, workspace_id),
            SqlProspectRepo(session, workspace_id),
            SqlBusinessRecordRepo(session),
            SqlKnowledgeRepo(session),
            SqlRecommendationRepo(session, workspace_id),
            SqlAuditEntryRepo(session, workspace_id),
        ).execute(workspace_id=workspace_id)
        logger.info(
            "queue assembled: workspace=%s week=%s recommended=%d excluded=%d",
            workspace_id,
            result.week_key,
            result.recommended,
            result.excluded,
        )


WEEKLY_BRIEF_SEND_JOB_TYPE = "weekly_brief_send"


def handle_weekly_brief_sweep(session: Session, job: Job) -> None:
    """Daily tick: enqueue this week's send for every workspace whose local
    clock says Monday. The idempotency key makes once-per-week structural."""
    now = datetime.now(UTC)
    queue = JobQueue(session)
    identity = SqlIdentityRepo(session)
    for workspace_id in identity.list_workspace_ids():
        workspace = identity.get_workspace(workspace_id)
        try:
            local_now = now.astimezone(ZoneInfo(workspace.delivery_timezone))
        except KeyError:
            local_now = now  # an unknown timezone falls back to UTC, honestly
        if local_now.weekday() != 0:
            continue
        year, week, _ = local_now.isocalendar()
        queue.enqueue(
            WEEKLY_BRIEF_SEND_JOB_TYPE,
            idempotency_key=f"weekly_brief:{workspace_id}:{year}-W{week:02d}",
            payload={"workspace_id": str(workspace_id)},
            workspace_id=workspace_id,
        )


def handle_weekly_brief_send(session: Session, job: Job) -> None:
    workspace_id = UUID(str(job.payload["workspace_id"]))
    outcome = SendWeeklyBrief(
        SqlIdentityRepo(session),
        SqlRecommendationRepo(session, workspace_id),
        SqlProspectRepo(session, workspace_id),
        SqlBusinessRecordRepo(session),
        SqlDnaRepo(session, workspace_id),
        SqlTeachingRepo(session, workspace_id),
        _email_sender(),
    ).execute(workspace_id=workspace_id)
    logger.info("weekly brief for %s: %s", workspace_id, outcome)


OUTCOME_PROMPT_JOB_TYPE = "outcome_prompt"


def handle_outcome_prompt(session: Session, job: Job) -> None:
    """The scheduled nudge for ground truth (Doc 03 §7: Xenia prompts,
    never assumes). If the prospect is still pursued and no outcome has
    arrived, the prompt is recorded as an auditable act; the surface that
    renders it (the weekly brief) belongs to the delivery epics."""
    workspace_id = UUID(str(job.payload["workspace_id"]))
    prospect_id = UUID(str(job.payload["prospect_id"]))
    prospect = SqlProspectRepo(session, workspace_id).get(prospect_id)
    if prospect is None or prospect.status is not ProspectStatus.PURSUED:
        return
    if SqlTeachingRepo(session, workspace_id).outcomes_for_prospect(prospect_id):
        return
    SqlAuditEntryRepo(session, workspace_id).append(
        action=AuditAction.OUTCOME_PROMPTED,
        target_type="prospect",
        target_id=str(prospect_id),
        actor_user_id=None,
        request_id=None,
    )


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
    QUEUE_ASSEMBLY_JOB_TYPE: handle_assemble_queues,
    WEEKLY_BRIEF_SWEEP_JOB_TYPE: handle_weekly_brief_sweep,
    WEEKLY_BRIEF_SEND_JOB_TYPE: handle_weekly_brief_send,
    OUTCOME_PROMPT_JOB_TYPE: handle_outcome_prompt,
    RESEARCH_RUN_JOB_TYPE: handle_research_run,
}
