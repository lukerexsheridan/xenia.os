"""Stripe webhook signature verification (Doc 08 §2).

Implements Stripe's `Stripe-Signature` scheme (HMAC-SHA256 over
"{timestamp}.{payload}") with the standard library — the full SDK is not
worth its dependency budget for one HMAC (AP8). Event processing itself is
queued and lands with billing in Epic 11; this module only answers "did
Stripe send this, recently?".
"""

import hashlib
import hmac
import time

DEFAULT_TOLERANCE_SECONDS = 300


class StripeSignatureError(Exception):
    """The webhook signature is missing, malformed, stale, or wrong."""


def verify_stripe_signature(
    payload: bytes,
    signature_header: str,
    secret: str,
    *,
    tolerance_seconds: int = DEFAULT_TOLERANCE_SECONDS,
    now: float | None = None,
) -> None:
    """Raise StripeSignatureError unless the payload is authentically Stripe's."""
    timestamp, candidates = _parse_header(signature_header)
    if abs((now if now is not None else time.time()) - timestamp) > tolerance_seconds:
        raise StripeSignatureError("timestamp outside tolerance")
    expected = hmac.new(
        secret.encode(), f"{timestamp}.".encode() + payload, hashlib.sha256
    ).hexdigest()
    if not any(hmac.compare_digest(expected, candidate) for candidate in candidates):
        raise StripeSignatureError("no matching v1 signature")


def _parse_header(header: str) -> tuple[int, list[str]]:
    timestamp: int | None = None
    candidates: list[str] = []
    for part in header.split(","):
        key, _, value = part.strip().partition("=")
        if key == "t" and value.isdigit():
            timestamp = int(value)
        elif key == "v1" and value:
            candidates.append(value)
    if timestamp is None or not candidates:
        raise StripeSignatureError("malformed Stripe-Signature header")
    return timestamp, candidates
