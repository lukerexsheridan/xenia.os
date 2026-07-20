"""Internal/ops router. The Editor console mounts here (Epic 9)."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class InternalStatusResponse(BaseModel):
    status: str


@router.get("/status")
def status() -> InternalStatusResponse:
    """Ops status stub — queue depth, sweep recency, and source health land here."""
    return InternalStatusResponse(status="ok")
