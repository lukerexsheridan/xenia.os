"""ReceiveStripeWebhook — queue a verified Stripe event, idempotently.

Webhooks are processed through the job queue, idempotent by event ID
(Doc 08 §7): Stripe's retries and replays collapse onto one job. The
signature is verified at the API boundary before this use-case runs; the
actual billing state machine lands with Epic 11.
"""

from typing import Any

from app.repositories.jobs import JobQueue

STRIPE_WEBHOOK_JOB_TYPE = "stripe_webhook"


class ReceiveStripeWebhook:
    def __init__(self, job_queue: JobQueue) -> None:
        self._job_queue = job_queue

    def execute(self, *, event_id: str, event_type: str, event: dict[str, Any]) -> None:
        self._job_queue.enqueue(
            STRIPE_WEBHOOK_JOB_TYPE,
            idempotency_key=f"stripe:{event_id}",
            payload={"event_id": event_id, "event_type": event_type, "event": event},
        )
