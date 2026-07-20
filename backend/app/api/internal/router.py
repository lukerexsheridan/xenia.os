"""Internal/ops router. The Editor console mounts here (Epic 9)."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.db import session_scope
from app.repositories.jobs import JobQueue

router = APIRouter()


class InternalStatusResponse(BaseModel):
    status: str
    jobs: dict[str, int]


@router.get("/status")
def status() -> InternalStatusResponse:
    """Ops status: queue depth by job status. Sweep recency and source health
    land here with their epics (Doc 08 §9)."""
    with session_scope() as session:
        return InternalStatusResponse(status="ok", jobs=JobQueue(session).counts_by_status())
