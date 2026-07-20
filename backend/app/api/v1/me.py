"""The authenticated identity resource: who am I, in which workspace."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_authenticated_context
from app.domain.user import WorkspaceRole
from app.services.authenticate_user import AuthenticatedContext

router = APIRouter()


class MeUser(BaseModel):
    id: UUID
    email: str | None
    role: WorkspaceRole


class MeWorkspace(BaseModel):
    id: UUID
    name: str


class MeResponse(BaseModel):
    user: MeUser
    workspace: MeWorkspace


@router.get("/me")
def me(
    context: Annotated[AuthenticatedContext, Depends(get_authenticated_context)],
) -> MeResponse:
    return MeResponse(
        user=MeUser(id=context.user.id, email=context.user.email, role=context.user.role),
        workspace=MeWorkspace(id=context.workspace.id, name=context.workspace.name),
    )
