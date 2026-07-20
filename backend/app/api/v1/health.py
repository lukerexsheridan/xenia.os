"""Liveness and readiness (Doc 08 §9).

Liveness answers "is the process up"; readiness answers "can it serve" —
currently the database. Queue-depth detail lives on the internal status
endpoint, not here.
"""

import logging

from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from sqlalchemy import text

from app.core.db import get_engine

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    status: str


@router.get("/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/health/ready")
def ready(response: Response) -> HealthResponse:
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        logger.exception("readiness check failed")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthResponse(status="unavailable")
    return HealthResponse(status="ready")
