"""Aggregates every /v1 router. One include per resource module."""

from fastapi import APIRouter

from app.api.v1 import health

router = APIRouter()
router.include_router(health.router, tags=["health"])
