"""Aggregates every /v1 router. One include per resource module."""

from fastapi import APIRouter

from app.api.v1 import (
    billing,
    briefs,
    dna,
    drafts,
    health,
    interview,
    loop,
    me,
    stripe_webhook,
)

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(me.router, tags=["me"])
router.include_router(stripe_webhook.router, tags=["billing"])
router.include_router(loop.router, tags=["loop"])
router.include_router(briefs.router, tags=["briefs"])
router.include_router(interview.router, tags=["interview"])
router.include_router(dna.router, tags=["dna"])
router.include_router(billing.router, tags=["billing"])
router.include_router(drafts.router, tags=["drafts"])
