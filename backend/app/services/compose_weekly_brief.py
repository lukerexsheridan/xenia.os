"""The Weekly Brief — the employee reporting in (Doc 03 C8; Doc 10 Sprint 20).

Found-this-week, what-I-learned, what-needs-you: calm, skimmable, plain
text. The P3 discipline is structural: when there is nothing worth saying,
`compose` returns None and no email exists to send — an email that respects
silence teaches trust. Composition is pure and deterministic (golden-file
tested); gathering and sending live in the service around it.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.domain.recommendation import RecommendationPolarity
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.dna import SqlDnaRepo
from app.repositories.identity import SqlIdentityRepo
from app.repositories.prospects import SqlProspectRepo
from app.repositories.recommendations import SqlRecommendationRepo
from app.repositories.teaching import SqlTeachingRepo
from app.services.send_heartbeat import EmailSender

# How far back "what I learned" looks. One delivery cycle.
_LEARNING_WINDOW = timedelta(days=7)


@dataclass(frozen=True)
class WeeklyBriefData:
    workspace_name: str
    week_key: str
    found: tuple[tuple[str, str], ...]  # (business name, confidence word)
    ruled_out: tuple[str, ...]  # exclusion reasons, verbatim
    learned: tuple[str, ...]  # changelog narrations
    needs_you: tuple[str, ...]  # pursued businesses awaiting an outcome


def compose(data: WeeklyBriefData) -> str | None:
    """The email body, or None when silence is the honest send (P3)."""
    if not data.found and not data.learned and not data.needs_you:
        return None
    lines: list[str] = [
        f"Your week, from Xenia — {data.week_key}.",
        "",
    ]
    if data.found:
        lines.append("Found this week:")
        for name, confidence in data.found:
            lines.append(f"  - {name} ({confidence})")
    else:
        lines.append("Nothing new met the bar this week — I don't pad the queue; I keep looking.")
    if data.ruled_out:
        lines.append("")
        lines.append("Ruled out, so you don't spend attention on them:")
        for reason in data.ruled_out:
            lines.append(f"  - {reason}")
    if data.learned:
        lines.append("")
        lines.append("What I learned from you this week:")
        for lesson in data.learned:
            lines.append(f"  - {lesson}")
    if data.needs_you:
        lines.append("")
        lines.append("Needs you — how did these land?")
        for name in data.needs_you:
            lines.append(f"  - {name} (tap an outcome in the app when you know)")
    lines.append("")
    lines.append("Open this week's queue in the app — one decision per card.")
    return "\n".join(lines)


_NARRATABLE_CAUSES = {
    "correction": "you corrected me",
    "behaviour_pattern": "a pattern in your declines",
    "outcome_pattern": "a win corroborated it",
    "endorsement": "you endorsed a change",
}


class SendWeeklyBrief:
    def __init__(
        self,
        identity_repo: SqlIdentityRepo,
        recommendation_repo: SqlRecommendationRepo,
        prospect_repo: SqlProspectRepo,
        business_record_repo: SqlBusinessRecordRepo,
        dna_repo: SqlDnaRepo,
        teaching_repo: SqlTeachingRepo,
        email_sender: EmailSender,
    ) -> None:
        self._identity_repo = identity_repo
        self._recommendation_repo = recommendation_repo
        self._prospect_repo = prospect_repo
        self._business_record_repo = business_record_repo
        self._dna_repo = dna_repo
        self._teaching_repo = teaching_repo
        self._email_sender = email_sender

    def execute(self, *, workspace_id: UUID, now: datetime | None = None) -> str:
        current = now or datetime.now(UTC)
        recipient = self._identity_repo.workspace_owner_email(workspace_id)
        if not recipient:
            return "skipped_no_recipient"
        data = self._gather(workspace_id, current)
        body = compose(data)
        if body is None:
            return "skipped_silent"  # respecting silence (P3)
        self._email_sender.send(
            to=recipient,
            subject=f"Xenia — your week ({data.week_key})",
            text=body,
        )
        return "sent"

    def _gather(self, workspace_id: UUID, now: datetime) -> WeeklyBriefData:
        workspace = self._identity_repo.get_workspace(workspace_id)
        week_key = self._recommendation_repo.latest_week_key() or "no week yet"
        found: list[tuple[str, str]] = []
        ruled_out: list[str] = []
        if self._recommendation_repo.latest_week_key():
            for item in self._recommendation_repo.list_week(week_key):
                if item.polarity is RecommendationPolarity.RECOMMENDED:
                    found.append((self._name_of(item.prospect_id), item.score.band.value))
                elif item.exclusion_reason:
                    ruled_out.append(item.exclusion_reason)

        learned: list[str] = []
        dna = self._dna_repo.get()
        if dna is not None:
            for event in self._dna_repo.changelog(dna.id):
                if event.occurred_at < now - _LEARNING_WINDOW:
                    continue
                narration = _NARRATABLE_CAUSES.get(event.cause.value)
                statement = (
                    event.after.statement
                    if event.after
                    else event.before.statement
                    if event.before
                    else None
                )
                if narration and statement:
                    learned.append(f"{statement} — because {narration}")

        needs_you = [
            self._name_of(prospect.id)
            for prospect in self._prospect_repo.list()
            if prospect.status.name == "PURSUED"
            and not self._teaching_repo.outcomes_for_prospect(prospect.id)
        ]
        return WeeklyBriefData(
            workspace_name=workspace.name,
            week_key=week_key,
            found=tuple(found),
            ruled_out=tuple(ruled_out),
            learned=tuple(learned),
            needs_you=tuple(needs_you),
        )

    def _name_of(self, prospect_id: UUID) -> str:
        prospect = self._prospect_repo.get(prospect_id)
        record = self._business_record_repo.get(prospect.business_record_id) if prospect else None
        return record.canonical_name if record else "a business"
