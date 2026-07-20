"""The AI cost governor (Doc 10, Epic 12): the ceiling is an honest wait."""

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import BudgetExhaustedError
from app.repositories.knowledge import SqlKnowledgeRepo
from app.services.ai_budget import enforce_ai_budget


def spend(session: Session, tokens: int) -> None:
    SqlKnowledgeRepo(session).record_ai_call(
        pipeline="compose_brief/1",
        prompt_version="compose_brief/1",
        model="test",
        input_tokens=tokens,
        output_tokens=0,
    )


def test_a_zero_ceiling_disables_the_governor(db: Engine) -> None:
    with Session(db) as session:
        spend(session, 10_000_000)
        enforce_ai_budget(SqlKnowledgeRepo(session))  # no ceiling, no error


def test_the_ceiling_surfaces_an_honest_wait(db: Engine, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_MONTHLY_TOKEN_BUDGET", "1000")
    get_settings.cache_clear()
    try:
        with Session(db) as session:
            repo = SqlKnowledgeRepo(session)
            spend(session, 999)
            enforce_ai_budget(repo)  # under the ceiling: composition proceeds
            spend(session, 1)
            with pytest.raises(BudgetExhaustedError, match="resumes when the month turns"):
                enforce_ai_budget(repo)
    finally:
        get_settings.cache_clear()
