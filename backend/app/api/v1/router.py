"""Aggregates every /v1 router. One include per resource module."""

from fastapi import APIRouter

from app.api.v1 import health, me, stripe_webhook

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(me.router, tags=["me"])
router.include_router(stripe_webhook.router, tags=["billing"])
