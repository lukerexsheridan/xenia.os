"""Resend adapter (Doc 08 §2): templated sends over the HTTP API.

The app's language at the boundary is the EmailSender protocol
(app.services.send_heartbeat); Resend's dialect stays in here. When no API
key is configured (local development), NullEmailSender logs and drops —
the recipient address is never logged (IDs-only rule, Doc 05).
"""

import logging

import httpx

logger = logging.getLogger(__name__)

_RESEND_ENDPOINT = "https://api.resend.com/emails"
_TIMEOUT_SECONDS = 10.0


class ResendClient:
    def __init__(self, *, api_key: str, from_address: str) -> None:
        self._api_key = api_key
        self._from_address = from_address

    def send(self, *, to: str, subject: str, text: str) -> None:
        response = httpx.post(
            _RESEND_ENDPOINT,
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={"from": self._from_address, "to": [to], "subject": subject, "text": text},
            timeout=_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        logger.info("email sent", extra={"pipeline": "resend"})


class NullEmailSender:
    """Local/no-key fallback: the send is logged (subject only) and dropped."""

    def send(self, *, to: str, subject: str, text: str) -> None:
        logger.info("email skipped (no RESEND_API_KEY): %s", subject)
