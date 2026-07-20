"""Webhook receiver: verified, queued, idempotent — replay-safe (Sprint 3)."""

import hashlib
import hmac
import json
import time
from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from app.main import create_app
from tests.conftest import TEST_STRIPE_WEBHOOK_SECRET


def signed_post(
    client: TestClient, event: dict[str, Any], *, secret: str = TEST_STRIPE_WEBHOOK_SECRET
) -> Any:
    payload = json.dumps(event).encode()
    timestamp = int(time.time())
    digest = hmac.new(
        secret.encode(), f"{timestamp}.".encode() + payload, hashlib.sha256
    ).hexdigest()
    return client.post(
        "/v1/stripe/webhook",
        content=payload,
        headers={"Stripe-Signature": f"t={timestamp},v1={digest}"},
    )


def job_keys(db: Engine) -> list[str]:
    with db.connect() as connection:
        return list(
            connection.execute(
                text("SELECT idempotency_key FROM jobs WHERE job_type = 'stripe_webhook'")
            ).scalars()
        )


def test_valid_event_is_queued(db: Engine) -> None:
    event_id = f"evt_{uuid4().hex[:12]}"
    response = signed_post(TestClient(create_app()), {"id": event_id, "type": "invoice.paid"})
    assert response.status_code == 200
    assert response.json() == {"received": True}
    assert job_keys(db) == [f"stripe:{event_id}"]


def test_replayed_event_queues_exactly_one_job(db: Engine) -> None:
    client = TestClient(create_app())
    event = {"id": f"evt_{uuid4().hex[:12]}", "type": "invoice.paid"}
    assert signed_post(client, event).status_code == 200
    assert signed_post(client, event).status_code == 200
    assert len(job_keys(db)) == 1


def test_bad_signature_is_rejected_and_not_queued(db: Engine) -> None:
    event = {"id": f"evt_{uuid4().hex[:12]}", "type": "invoice.paid"}
    response = signed_post(TestClient(create_app()), event, secret="whsec_wrong")
    assert response.status_code == 401
    assert job_keys(db) == []


def test_missing_signature_header_is_rejected(db: Engine) -> None:
    response = TestClient(create_app()).post("/v1/stripe/webhook", content=b"{}")
    assert response.status_code == 401


def test_event_without_id_is_rejected(db: Engine) -> None:
    response = signed_post(TestClient(create_app()), {"type": "invoice.paid"})
    assert response.status_code == 422
    assert job_keys(db) == []


def test_webhook_is_not_in_the_public_openapi_document() -> None:
    schema = create_app().openapi()
    assert "/v1/stripe/webhook" not in schema["paths"]
