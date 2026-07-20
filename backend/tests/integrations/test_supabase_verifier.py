import pytest

from app.integrations.supabase_auth import SupabaseTokenVerifier, TokenVerificationError
from tests.conftest import mint_supabase_token

SECRET = "unit-test-secret-0123456789abcdef-xyz"


def make_verifier() -> SupabaseTokenVerifier:
    return SupabaseTokenVerifier(jwt_secret=SECRET)


def test_valid_hs256_token_verifies() -> None:
    token = mint_supabase_token("sub-1", email="founder@example.test", secret=SECRET)
    identity = make_verifier().verify(token)
    assert identity.subject == "sub-1"
    assert identity.email == "founder@example.test"


def test_email_is_optional() -> None:
    token = mint_supabase_token("sub-2", secret=SECRET)
    assert make_verifier().verify(token).email is None


def test_expired_token_is_rejected() -> None:
    token = mint_supabase_token("sub-3", secret=SECRET, expires_in_seconds=-60)
    with pytest.raises(TokenVerificationError):
        make_verifier().verify(token)


def test_wrong_secret_is_rejected() -> None:
    token = mint_supabase_token("sub-4", secret="a-different-secret-0123456789abcdef")
    with pytest.raises(TokenVerificationError):
        make_verifier().verify(token)


def test_wrong_audience_is_rejected() -> None:
    token = mint_supabase_token("sub-5", secret=SECRET, audience="anon")
    with pytest.raises(TokenVerificationError):
        make_verifier().verify(token)


def test_garbage_token_is_rejected() -> None:
    with pytest.raises(TokenVerificationError):
        make_verifier().verify("not-a-jwt")


def test_hs256_rejected_when_only_jwks_configured() -> None:
    """The algorithm allow-list follows configuration, never the token header."""
    verifier = SupabaseTokenVerifier(supabase_url="https://project.supabase.co")
    token = mint_supabase_token("sub-6", secret=SECRET)
    with pytest.raises(TokenVerificationError):
        verifier.verify(token)


def test_unconfigured_verifier_refuses_to_construct() -> None:
    with pytest.raises(ValueError, match="not configured"):
        SupabaseTokenVerifier()
