"""Internal-console authorisation (Doc 08 §8).

Internal access requires more than a valid session: the verified subject
must be on the configured editor allowlist (`EDITOR_AUTH_SUBJECTS`). Editors
act across workspaces — the Editor gate reviews every workspace's briefs —
so Ring-1 operations name their target workspace explicitly in the path and
the dependency attaches that tenancy context to the transaction.
"""

from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, get_token_verifier
from app.core.config import get_settings
from app.core.db import set_app_context
from app.core.errors import NotAuthenticatedError, NotAuthorisedError, NotFoundError
from app.integrations.supabase_auth import TokenVerificationError, TokenVerifier
from app.repositories.identity import SqlIdentityRepo

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class EditorContext:
    auth_subject: str


def get_editor_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    verifier: Annotated[TokenVerifier, Depends(get_token_verifier)],
) -> EditorContext:
    if credentials is None:
        raise NotAuthenticatedError("missing bearer token")
    try:
        identity = verifier.verify(credentials.credentials)
    except TokenVerificationError as exc:
        raise NotAuthenticatedError("invalid or expired token") from exc
    allowed = {
        subject.strip()
        for subject in get_settings().editor_auth_subjects.split(",")
        if subject.strip()
    }
    if identity.subject not in allowed:
        raise NotAuthorisedError("internal access requires Editor authorisation")
    return EditorContext(auth_subject=identity.subject)


def get_workspace_session(
    workspace_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
) -> Session:
    """The request's transaction, bound to the path's target workspace (RLS).
    A workspace that does not exist is a 404, not a downstream surprise."""
    set_app_context(session, workspace_id=workspace_id)
    if SqlIdentityRepo(session).find_workspace(workspace_id) is None:
        raise NotFoundError("workspace not found")
    return session
