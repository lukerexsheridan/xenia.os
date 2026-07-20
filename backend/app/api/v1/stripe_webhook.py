"""Stripe webhook receiver: verified, queued, idempotent (Doc 08 §2/§7).

Machine-facing, authenticated by signature rather than by JWT, and excluded
from the public OpenAPI document — it is not part of the client contract the
frontend generates types from (AP4). It stays under /v1 because that is the
one public surface (Doc 08 §3).
"""

import json
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.config import get_settings
from app.core.errors import NotAuthenticatedError, XeniaError
from app.integrations.stripe.webhooks import StripeSignatureError, verify_stripe_signature
from app.repositories.jobs import JobQueue
from app.services.receive_stripe_webhook import ReceiveStripeWebhook

logger = logging.getLogger(__name__)

router = APIRouter()


class WebhookAck(BaseModel):
    received: bool


@router.post("/stripe/webhook", include_in_schema=False)
async def stripe_webhook(
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
) -> WebhookAck:
    secret = get_settings().stripe_webhook_secret
    if not secret:
        raise NotAuthenticatedError("Stripe webhooks are not configured")

    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    if signature is None:
        raise NotAuthenticatedError("missing Stripe-Signature header")
    try:
        verify_stripe_signature(payload, signature, secret)
    except StripeSignatureError as exc:
        logger.warning("stripe webhook rejected: %s", exc)
        raise NotAuthenticatedError("invalid Stripe signature") from exc

    event: dict[str, Any] = json.loads(payload)
    event_id, event_type = event.get("id"), event.get("type")
    if not isinstance(event_id, str) or not isinstance(event_type, str):
        raise XeniaError("event id and type are required")

    ReceiveStripeWebhook(JobQueue(session)).execute(
        event_id=event_id, event_type=event_type, event=event
    )
    return WebhookAck(received=True)
