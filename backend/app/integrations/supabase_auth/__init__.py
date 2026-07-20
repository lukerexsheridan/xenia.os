"""Supabase Auth adapter: verifies session JWTs via JWKS and maps
sub -> User -> Workspace membership (Doc 08 SS8). Supabase never holds domain
data; the auth vendor is swappable by construction.

Skeleton status: interface only — implementation lands in Epic 1 (Sprint 2)
before the first authenticated route. Logged in DEBT.md.
"""

from app.integrations.supabase_auth.verifier import TokenVerifier

__all__ = ["TokenVerifier"]
