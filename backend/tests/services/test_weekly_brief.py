"""The weekly brief: composition golden, the silence rule, the send
(Doc 10, Sprint 20)."""

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.domain.prospect import Prospect, ProspectStatus
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.dna import SqlDnaRepo
from app.repositories.identity import SqlIdentityRepo
from app.repositories.prospects import SqlProspectRepo
from app.repositories.recommendations import SqlRecommendationRepo
from app.repositories.teaching import SqlTeachingRepo
from app.services.compose_weekly_brief import SendWeeklyBrief, WeeklyBriefData, compose

GOLDEN = Path(__file__).parent.parent / "golden"


def full_week() -> WeeklyBriefData:
    return WeeklyBriefData(
        workspace_name="Brightpath Agency",
        week_key="2026-W30",
        found=(("Brightpath Ltd", "likely"), ("Steadyco", "possible")),
        ruled_out=("ruled out Franchico — franchise model, your disqualifier",),
        learned=(
            "Declines keep citing 'wrong industry' — narrowing the industries I surface "
            "— because a pattern in your declines",
        ),
        needs_you=("Alpha Ltd",),
    )


def test_doc03_c8_the_weekly_brief_matches_its_golden_file() -> None:
    """The email is a deliverable artefact; its exact text is deliberate.
    Regenerate via tests/golden/regenerate.py, never casually."""
    golden_path = GOLDEN / "weekly_brief_v1.txt"
    assert golden_path.exists(), "regenerate the weekly-brief golden deliberately"
    body = compose(full_week())
    assert body is not None
    assert body + "\n" == golden_path.read_text()


def test_doc03_p3_silence_is_the_honest_send() -> None:
    """Nothing found, nothing learned, nothing pending -> no email exists."""
    silent = WeeklyBriefData(
        workspace_name="Quiet Agency",
        week_key="2026-W30",
        found=(),
        ruled_out=(),
        learned=(),
        needs_you=(),
    )
    assert compose(silent) is None


def test_an_empty_queue_with_learning_still_reports_honestly() -> None:
    data = WeeklyBriefData(
        workspace_name="A",
        week_key="2026-W30",
        found=(),
        ruled_out=(),
        learned=("something learned — because you corrected me",),
        needs_you=(),
    )
    body = compose(data)
    assert body is not None
    assert "I don't pad the queue" in body


class RecordingSender:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str, str]] = []

    def send(self, *, to: str, subject: str, text: str) -> None:
        self.sent.append((to, subject, text))


def test_the_send_respects_silence_and_addresses_the_owner(db: Engine) -> None:
    with Session(db) as session:
        workspace, _ = SqlIdentityRepo(session).provision_workspace(
            name="Weekly Agency",
            auth_subject=f"weekly-{uuid4()}",
            email="founder@weekly.example",
        )
        sender = RecordingSender()
        service = SendWeeklyBrief(
            SqlIdentityRepo(session),
            SqlRecommendationRepo(session, workspace.id),
            SqlProspectRepo(session, workspace.id),
            SqlBusinessRecordRepo(session),
            SqlDnaRepo(session, workspace.id),
            SqlTeachingRepo(session, workspace.id),
            sender,
        )
        # A brand-new workspace has nothing worth saying: silence.
        assert service.execute(workspace_id=workspace.id) == "skipped_silent"
        assert sender.sent == []

        # With something pending, the owner hears about it.
        record = SqlBusinessRecordRepo(session).find_or_create(
            canonical_name="Alpha Ltd", website_domain="alpha.example", register_number=None
        )
        prospect = SqlProspectRepo(session, workspace.id).add(
            Prospect(
                id=uuid4(),
                workspace_id=workspace.id,
                business_record_id=record.id,
                binding_confidence=0.9,
                status=ProspectStatus.PURSUED,
                surfaced_at=datetime.now(UTC),
            )
        )
        assert service.execute(workspace_id=workspace.id) == "sent"
        session.commit()
    to, _subject, text = sender.sent[0]
    assert to == "founder@weekly.example"
    assert "Alpha Ltd" in text and "Needs you" in text
    assert prospect.id is not None
