"""Persistence: SQLAlchemy implementations of domain-defined protocols.

SQLAlchemy stays entirely inside this package (Doc 08 SS3). Every repository
is workspace-scoped BY CONSTRUCTOR — a repository instance without a
workspace context cannot be built. Ring-1 isolation is a type-level property
here (the belt) and Postgres RLS is the braces (Doc 08 SS8). Ring-2 stores
(BusinessRecord and friends) carry no workspace column at all.

May import: app.domain, app.core. May be imported by: app.services.
"""

from app.repositories.base import Base

__all__ = ["Base"]
