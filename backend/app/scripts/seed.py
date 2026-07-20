"""Seed synthetic workspaces for local and staging environments (ADR-006).

Two generated agencies, real-shaped and deterministic: the Sprint 2 deploy
criterion ("two seeded workspaces on staging, provably isolated") made
runnable. Refuses to run in production — customer data only there.

Usage: python -m app.scripts.seed
"""

import sys
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import session_scope, set_app_context
from app.repositories.audit import SqlAuditEntryRepo
from app.repositories.identity import SqlIdentityRepo
from app.services.authenticate_user import AuthenticateUser

SYNTHETIC_WORKSPACES = (
    ("Brightpath Digital", "seed-brightpath", "founder@brightpath.example"),
    ("Northline Studio", "seed-northline", "founder@northline.example"),
)


def seed() -> None:
    settings = get_settings()
    if settings.environment == "production":
        sys.exit("refusing to seed production — synthetic data never lives there (ADR-006)")

    for name, auth_subject, email in SYNTHETIC_WORKSPACES:
        with session_scope() as session:
            set_app_context(session, auth_subject=auth_subject)

            def audit_repo_for(workspace_id: UUID, session: Session = session) -> SqlAuditEntryRepo:
                return SqlAuditEntryRepo(session, workspace_id)

            context = AuthenticateUser(SqlIdentityRepo(session), audit_repo_for).execute(
                auth_subject=auth_subject, email=email, workspace_name=name
            )
            workspace = context.workspace
            sys.stdout.write(f"workspace ready: {workspace.name} ({workspace.id})\n")


if __name__ == "__main__":
    seed()
