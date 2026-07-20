"""RunInterview — the conversation that founds the DNA (Doc 10, Sprint 18).

Resumable by construction (the next question is the first unanswered one);
the final answer transcribes the whole conversation into the founding DNA in
the same transaction, every element customer-voiced and changelogged from
birth. Endorsement stays a separate, deliberate moment (Doc 03 §3) — the
interview produces the model, the customer signs it.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from app.core.errors import ConflictError
from app.domain.audit import AuditAction
from app.domain.dna import Dna
from app.domain.interview import (
    INTERVIEW_SCRIPT,
    InterviewQuestion,
    elements_from_answers,
    next_question,
    record_answer,
)
from app.repositories.audit import SqlAuditEntryRepo
from app.repositories.dna import SqlDnaRepo
from app.repositories.interview import SqlInterviewRepo


@dataclass(frozen=True)
class InterviewState:
    question: InterviewQuestion | None  # None -> complete
    answered: int
    total: int
    completed: bool
    dna_created: bool


class RunInterview:
    def __init__(
        self,
        interview_repo: SqlInterviewRepo,
        dna_repo: SqlDnaRepo,
        audit_repo: SqlAuditEntryRepo,
    ) -> None:
        self._interview_repo = interview_repo
        self._dna_repo = dna_repo
        self._audit_repo = audit_repo

    def state(self) -> InterviewState:
        answers = self._interview_repo.get_answers()
        question = next_question(answers)
        return InterviewState(
            question=question,
            answered=len(answers),
            total=len(INTERVIEW_SCRIPT),
            completed=question is None,
            dna_created=self._dna_repo.get() is not None,
        )

    def answer(
        self,
        *,
        workspace_id: UUID,
        key: str,
        text: str,
        actor_user_id: UUID,
        request_id: str | None = None,
    ) -> InterviewState:
        if self._dna_repo.get() is not None:
            raise ConflictError("this workspace's DNA already exists — teach it, don't restart")
        answers = record_answer(self._interview_repo.get_answers(), key=key, text=text)
        self._interview_repo.save_answers(answers)
        if next_question(answers) is None:
            self._found_dna(workspace_id, answers, actor_user_id, request_id)
        return self.state()

    def _found_dna(
        self,
        workspace_id: UUID,
        answers: dict[str, str],
        actor_user_id: UUID,
        request_id: str | None,
    ) -> None:
        now = datetime.now(UTC)
        dna, events = Dna.create(
            workspace_id=workspace_id,
            elements=elements_from_answers(answers, now=now),
            now=now,
        )
        self._dna_repo.save(dna, events)
        self._interview_repo.mark_completed(at=now)
        self._audit_repo.append(
            action=AuditAction.DNA_CREATED,
            target_type="dna",
            target_id=str(dna.id),
            actor_user_id=actor_user_id,
            request_id=request_id,
        )
