"""Declarative base, naming conventions, and the workspace-scoped base class.

A stable naming convention from the first migration keeps Alembic autogenerate
deterministic (the migration-drift lint depends on it).
"""

from uuid import UUID

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Session

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class WorkspaceScopedRepository:
    """Tenancy at the type level: the belt of belt-and-braces (Doc 08 §8).

    A repository over Ring-1 data cannot be built without a workspace context,
    and every query it issues filters on that workspace. The braces — Postgres
    RLS keyed to the transaction-local setting `app.workspace_id` — catch what
    slips past this class (raw SQL, future tools, bugs).
    """

    def __init__(self, session: Session, workspace_id: UUID) -> None:
        self._session = session
        self._workspace_id = workspace_id
