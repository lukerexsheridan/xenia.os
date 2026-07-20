"""Database engine and session factory.

Session lifecycle only — models and queries live in app.repositories (Doc 08 SS3).
Transactions are drawn at the use-case boundary by services.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from uuid import UUID

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

# Transaction-local settings the Ring-1 RLS policies key on (Doc 08 §8).
# Set via set_config(..., is_local => true), so they die with the transaction —
# a pooled connection can never leak one request's tenancy into the next.
WORKSPACE_ID_SETTING = "app.workspace_id"
AUTH_SUBJECT_SETTING = "app.auth_subject"


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_settings().database_url, pool_pre_ping=True)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


@contextmanager
def session_scope() -> Iterator[Session]:
    """One transaction per use-case (Doc 08 §3)."""
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def set_app_context(
    session: Session,
    *,
    workspace_id: UUID | None = None,
    auth_subject: str | None = None,
) -> None:
    """Attach the tenancy context to the current transaction (the RLS braces).

    The belt is repository-level scoping; these settings are what the Postgres
    row-level-security policies read, so even a raw-SQL mistake hits the same
    wall (Doc 08 §8).
    """
    values: list[tuple[str, str]] = []
    if workspace_id is not None:
        values.append((WORKSPACE_ID_SETTING, str(workspace_id)))
    if auth_subject is not None:
        values.append((AUTH_SUBJECT_SETTING, auth_subject))
    for name, value in values:
        session.execute(
            text("SELECT set_config(:name, :value, true)"),
            {"name": name, "value": value},
        )
