from uuid import uuid4

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.repositories.jobs import JobQueue
from app.services.send_heartbeat import SendHeartbeat


class RecordingEmailSender:
    def __init__(self) -> None:
        self.sent: list[dict[str, str]] = []

    def send(self, *, to: str, subject: str, text: str) -> None:
        self.sent.append({"to": to, "subject": subject, "text": text})


def test_heartbeat_reports_queue_health(db: Engine) -> None:
    sender = RecordingEmailSender()
    with Session(db) as session:
        queue = JobQueue(session)
        queue.enqueue("pending-job", idempotency_key=f"hb:{uuid4()}")
        session.commit()
        SendHeartbeat(sender, queue).execute(to="founder@example.test")
    assert len(sender.sent) == 1
    message = sender.sent[0]
    assert message["to"] == "founder@example.test"
    assert "1 pending" in message["text"]
    assert "heartbeat" in message["subject"].lower()


def test_dead_letters_are_called_out(db: Engine) -> None:
    sender = RecordingEmailSender()
    with Session(db) as session:
        queue = JobQueue(session)
        job_id = queue.enqueue("doomed", idempotency_key=f"hb:{uuid4()}", max_attempts=1)
        assert job_id is not None
        queue.record_failure(job_id, error="boom")
        session.commit()
        SendHeartbeat(sender, queue).execute(to="founder@example.test")
    message = sender.sent[0]
    assert "1 dead-lettered" in message["text"]
    assert "dead-lettered" in message["subject"]


def test_missing_recipient_skips_the_send(db: Engine) -> None:
    sender = RecordingEmailSender()
    with Session(db) as session:
        SendHeartbeat(sender, JobQueue(session)).execute(to="")
    assert sender.sent == []
