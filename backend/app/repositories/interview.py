"""Interview transcript persistence — Ring 1, workspace-scoped."""

from datetime import datetime

from sqlalchemy import select

from app.repositories.base import WorkspaceScopedRepository
from app.repositories.orm import InterviewStateRow


class SqlInterviewRepo(WorkspaceScopedRepository):
    def get_answers(self) -> dict[str, str]:
        row = self._row()
        return dict(row.answers) if row else {}

    def save_answers(self, answers: dict[str, str]) -> None:
        row = self._row()
        if row is None:
            row = InterviewStateRow(workspace_id=self._workspace_id, answers=answers)
            self._session.add(row)
        else:
            row.answers = answers
        self._session.flush()

    def mark_completed(self, *, at: datetime) -> None:
        row = self._row()
        if row is not None:
            row.completed_at = at
            self._session.flush()

    def completed_at(self) -> datetime | None:
        row = self._row()
        return row.completed_at if row else None

    def _row(self) -> InterviewStateRow | None:
        return self._session.execute(
            select(InterviewStateRow).where(InterviewStateRow.workspace_id == self._workspace_id)
        ).scalar_one_or_none()
