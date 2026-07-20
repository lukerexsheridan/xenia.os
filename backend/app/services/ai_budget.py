"""The AI cost governor (Doc 10, Epic 12; Doc 08 §8).

A hard monthly token ceiling over the ai_call_records ledger. When the
ceiling is reached, composition surfaces an honest wait (429), never a
silent degradation or a quiet overspend — the budget is a founder-ratified
number [calibrates against real ledgers], and zero disables the governor
while the ceiling is being learned.
"""

from datetime import UTC, datetime

from app.core.config import get_settings
from app.core.errors import BudgetExhaustedError
from app.repositories.knowledge import SqlKnowledgeRepo


def enforce_ai_budget(knowledge_repo: SqlKnowledgeRepo, *, now: datetime | None = None) -> None:
    ceiling = get_settings().ai_monthly_token_budget
    if ceiling <= 0:
        return
    current = now or datetime.now(UTC)
    month_start = current.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    spent = knowledge_repo.tokens_since(month_start)
    if spent >= ceiling:
        raise BudgetExhaustedError(
            "this month's AI budget is spent — composition resumes when the "
            "month turns or the ceiling is raised deliberately"
        )
