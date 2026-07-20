"""Auth and session dependencies — the API layer's composition point (AP7).

Resolves identity and workspace context, wires concrete repositories into
use-cases, and attaches the tenancy context (RLS session settings + logging
correlation) to the request's one transaction.
"""

from collections.abc import Iterator
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import session_scope, set_app_context
from app.core.errors import ConflictError, NotAuthenticatedError
from app.core.logging import bind_log_context, current_request_id
from app.integrations.supabase_auth import (
    SupabaseTokenVerifier,
    TokenVerificationError,
    TokenVerifier,
)
from app.repositories.audit import SqlAuditEntryRepo
from app.repositories.identity import SqlIdentityRepo
from app.services.authenticate_user import AuthenticatedContext, AuthenticateUser

_bearer = HTTPBearer(auto_error=False)


def get_db_session() -> Iterator[Session]:
    """One transaction per request (Doc 08 §3)."""
    with session_scope() as session:
        yield session


@lru_cache
def get_token_verifier() -> TokenVerifier:
    settings = get_settings()
    if not settings.supabase_url and not settings.supabase_jwt_secret:
        raise NotAuthenticatedError("authentication is not configured")
    return SupabaseTokenVerifier(
        supabase_url=settings.supabase_url, jwt_secret=settings.supabase_jwt_secret
    )


def get_authenticated_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    session: Annotated[Session, Depends(get_db_session)],
    verifier: Annotated[TokenVerifier, Depends(get_token_verifier)],
) -> AuthenticatedContext:
    if credentials is None:
        raise NotAuthenticatedError("missing bearer token")
    try:
        identity = verifier.verify(credentials.credentials)
    except TokenVerificationError as exc:
        # The specific failure stays server-side; the response is generic.
        raise NotAuthenticatedError("invalid or expired token") from exc

    set_app_context(session, auth_subject=identity.subject)

    def audit_repo_for(workspace_id: UUID) -> SqlAuditEntryRepo:
        return SqlAuditEntryRepo(session, workspace_id)

    try:
        context = AuthenticateUser(SqlIdentityRepo(session), audit_repo_for).execute(
            auth_subject=identity.subject, email=identity.email, request_id=current_request_id()
        )
    except IntegrityError as exc:
        # Two first logins for the same subject raced between lookup and
        # provisioning; the users.auth_subject unique constraint broke the tie.
        # The retry resolves to the workspace the winner provisioned.
        raise ConflictError("sign-in raced with another session — please retry") from exc
    set_app_context(session, workspace_id=context.workspace.id)
    bind_log_context(workspace_id=str(context.workspace.id), user_id=str(context.user.id))
    return context
