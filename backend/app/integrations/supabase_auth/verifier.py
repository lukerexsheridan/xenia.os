"""JWT verification interface. Implementation: Epic 1 (see DEBT.md)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class VerifiedIdentity:
    """The claims the backend trusts after verification: identity only."""

    subject: str
    email: str | None


class TokenVerifier:
    """Verifies Supabase-issued JWTs against the project JWKS (cached, rotated)."""

    def verify(self, token: str) -> VerifiedIdentity:
        raise NotImplementedError(
            "Supabase JWT verification is implemented in Epic 1 (Sprint 2) — "
            "no authenticated endpoint may merge without it. See DEBT.md."
        )
