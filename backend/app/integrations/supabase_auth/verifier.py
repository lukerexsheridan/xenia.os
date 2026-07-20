"""Supabase JWT verification (Doc 08 §8): identity only, nothing else trusted.

Two key mechanisms, both standard Supabase issuance modes:
- asymmetric (RS256/ES256) via the project JWKS endpoint — cached and rotated
  by PyJWKClient;
- symmetric (HS256) via the project JWT secret — the legacy default, and what
  local development and tests use.

The accepted algorithm is taken from the token header but checked against a
fixed allow-list derived from configuration — a token can never talk its way
into an algorithm the deployment did not enable.
"""

from dataclasses import dataclass
from typing import Any, Protocol

import jwt

SUPABASE_AUDIENCE = "authenticated"
_JWKS_PATH = "/auth/v1/.well-known/jwks.json"
_JWKS_CACHE_SECONDS = 300
_ASYMMETRIC_ALGORITHMS = ("RS256", "ES256")


class TokenVerificationError(Exception):
    """The token could not be verified. Detail stays server-side (logs only)."""


@dataclass(frozen=True)
class VerifiedIdentity:
    """The claims the backend trusts after verification: identity only."""

    subject: str
    email: str | None


class TokenVerifier(Protocol):
    def verify(self, token: str) -> VerifiedIdentity: ...


class SupabaseTokenVerifier:
    """Verifies Supabase-issued JWTs against the project JWKS (cached, rotated)."""

    def __init__(self, *, supabase_url: str = "", jwt_secret: str = "") -> None:
        if not supabase_url and not jwt_secret:
            raise ValueError(
                "Supabase auth is not configured: set SUPABASE_URL (JWKS) "
                "and/or SUPABASE_JWT_SECRET (HS256)."
            )
        self._jwt_secret = jwt_secret
        self._issuer = f"{supabase_url.rstrip('/')}/auth/v1" if supabase_url else None
        self._jwks_client = (
            jwt.PyJWKClient(
                f"{supabase_url.rstrip('/')}{_JWKS_PATH}",
                cache_keys=True,
                lifespan=_JWKS_CACHE_SECONDS,
            )
            if supabase_url
            else None
        )

    def verify(self, token: str) -> VerifiedIdentity:
        try:
            algorithm = jwt.get_unverified_header(token).get("alg", "")
            claims: dict[str, Any] = jwt.decode(
                token,
                self._key_for(token, algorithm),
                algorithms=[algorithm],
                audience=SUPABASE_AUDIENCE,
                issuer=self._issuer,
                options={
                    "require": ["sub", "exp", "aud"],
                    "verify_iss": self._issuer is not None,
                },
            )
        except jwt.PyJWTError as exc:
            raise TokenVerificationError(str(exc)) from exc
        return VerifiedIdentity(subject=claims["sub"], email=claims.get("email"))

    def _key_for(self, token: str, algorithm: str) -> Any:
        if algorithm == "HS256":
            if not self._jwt_secret:
                raise TokenVerificationError("HS256 token but no JWT secret configured")
            return self._jwt_secret
        if algorithm in _ASYMMETRIC_ALGORITHMS:
            if self._jwks_client is None:
                raise TokenVerificationError(f"{algorithm} token but no JWKS URL configured")
            try:
                return self._jwks_client.get_signing_key_from_jwt(token).key
            except jwt.PyJWTError as exc:  # pragma: no cover — network path
                raise TokenVerificationError(str(exc)) from exc
        raise TokenVerificationError(f"unsupported algorithm: {algorithm!r}")
