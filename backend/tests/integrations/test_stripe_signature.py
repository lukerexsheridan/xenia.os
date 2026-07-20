import hashlib
import hmac
import time

import pytest

from app.integrations.stripe.webhooks import StripeSignatureError, verify_stripe_signature

SECRET = "whsec_unit_test"


def sign(payload: bytes, *, secret: str = SECRET, timestamp: int | None = None) -> str:
    ts = timestamp if timestamp is not None else int(time.time())
    digest = hmac.new(secret.encode(), f"{ts}.".encode() + payload, hashlib.sha256).hexdigest()
    return f"t={ts},v1={digest}"


def test_valid_signature_passes() -> None:
    payload = b'{"id": "evt_1"}'
    verify_stripe_signature(payload, sign(payload), SECRET)


def test_tampered_payload_fails() -> None:
    header = sign(b'{"id": "evt_1"}')
    with pytest.raises(StripeSignatureError, match="no matching"):
        verify_stripe_signature(b'{"id": "evt_2"}', header, SECRET)


def test_wrong_secret_fails() -> None:
    payload = b"{}"
    with pytest.raises(StripeSignatureError, match="no matching"):
        verify_stripe_signature(payload, sign(payload, secret="whsec_other"), SECRET)


def test_stale_timestamp_fails() -> None:
    payload = b"{}"
    header = sign(payload, timestamp=int(time.time()) - 3600)
    with pytest.raises(StripeSignatureError, match="tolerance"):
        verify_stripe_signature(payload, header, SECRET)


def test_malformed_header_fails() -> None:
    with pytest.raises(StripeSignatureError, match="malformed"):
        verify_stripe_signature(b"{}", "v1=deadbeef", SECRET)
