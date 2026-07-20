"""Supabase Auth adapter: verifies session JWTs (JWKS or HS256 secret) and
exposes only VerifiedIdentity to the rest of the app (Doc 08 SS8). Supabase
never holds domain data; the auth vendor is swappable by construction — the
API layer depends on the TokenVerifier protocol, not on this implementation.
"""

from app.integrations.supabase_auth.verifier import (
    SupabaseTokenVerifier,
    TokenVerificationError,
    TokenVerifier,
    VerifiedIdentity,
)

__all__ = [
    "SupabaseTokenVerifier",
    "TokenVerificationError",
    "TokenVerifier",
    "VerifiedIdentity",
]
