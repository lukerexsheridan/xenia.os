"""Founding billing (Doc 03 §9): one plan, linked out, never in-product.

The product never implements payment UI beyond linking out (Doc 08 §2):
this resource reports the workspace's synced subscription status and hands
back the dashboard-authored Payment Link (carrying the workspace as
client_reference_id) and the customer-portal login link.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_authenticated_context
from app.core.config import get_settings
from app.services.authenticate_user import AuthenticatedContext

router = APIRouter()


class BillingResponse(BaseModel):
    subscription_status: str
    payment_link_url: str | None
    portal_url: str | None


@router.get("/billing")
def get_billing(
    context: Annotated[AuthenticatedContext, Depends(get_authenticated_context)],
) -> BillingResponse:
    settings = get_settings()
    payment_link = (
        f"{settings.stripe_payment_link_url}?client_reference_id={context.workspace.id}"
        if settings.stripe_payment_link_url
        else None
    )
    return BillingResponse(
        subscription_status=context.workspace.subscription_status,
        payment_link_url=payment_link,
        portal_url=settings.stripe_portal_login_url or None,
    )
