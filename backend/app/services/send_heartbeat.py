"""SendHeartbeat — the daily ops report to the founder (Doc 10, Sprint 3).

Proves the whole background chain end-to-end: scheduler → queue → worker →
integration. The email carries the queue's health, so a dead-lettered job is
in front of a human within a day even before dashboards exist.

EmailSender is the service-defined port for outbound mail; the Resend adapter
(and its no-key null fallback) implement it. It lives here rather than in the
domain because ops email is infrastructure, not business ontology — the
domain-defined interfaces of AP2 govern domain concepts.
"""

import logging
from datetime import UTC, datetime
from typing import Protocol

from app.repositories.jobs import JobQueue

logger = logging.getLogger(__name__)


class EmailSender(Protocol):
    def send(self, *, to: str, subject: str, text: str) -> None: ...


class SendHeartbeat:
    def __init__(self, email_sender: EmailSender, job_queue: JobQueue) -> None:
        self._email_sender = email_sender
        self._job_queue = job_queue

    def execute(self, *, to: str) -> None:
        if not to:
            logger.info("heartbeat email skipped: HEARTBEAT_EMAIL_TO is not set")
            return
        counts = self._job_queue.counts_by_status()
        today = datetime.now(UTC).date().isoformat()
        dead = counts.get("dead", 0)
        lines = [
            f"Xenia worker heartbeat — {today}.",
            "",
            f"Queue: {counts.get('pending', 0)} pending, "
            f"{counts.get('succeeded', 0)} succeeded, {dead} dead-lettered.",
        ]
        if dead:
            lines.append("Dead-lettered jobs need a look — details are in the worker logs.")
        self._email_sender.send(
            to=to,
            subject=f"Xenia heartbeat — {today}" + (f" ({dead} dead-lettered)" if dead else ""),
            text="\n".join(lines),
        )
