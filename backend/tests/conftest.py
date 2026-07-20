"""Test configuration.

Pure unit tests never touch the database. Integration tests (tenancy canary,
job semantics, auth flow) run against a real Postgres — RLS and SKIP LOCKED
cannot be faked honestly — via the `db` fixture, which migrates to head and
starts each test from empty tables. When Postgres is unreachable (e.g. a
laptop without the compose stack running) those tests skip loudly; CI always
provides the service database, so they always run there.

Required settings are provided here so the fail-fast config
(app/core/config.py) is satisfied deterministically. The Supabase JWT secret
lets API tests mint real HS256 tokens and exercise the real verifier.
"""

import os
from collections.abc import Iterator

os.environ.setdefault("ENVIRONMENT", "ci")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://xenia:xenia@localhost:5432/xenia")
# ≥32 bytes: HS256 keys below that trip PyJWT's insecure-key warning.
os.environ.setdefault("SUPABASE_JWT_SECRET", "xenia-test-jwt-secret-0123456789abcdef")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_xenia_test")
os.environ.setdefault("EDITOR_AUTH_SUBJECTS", "editor-test-subject")

import pytest
from sqlalchemy import Engine, create_engine, text

TEST_JWT_SECRET = os.environ["SUPABASE_JWT_SECRET"]
TEST_STRIPE_WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]
TEST_EDITOR_SUBJECT = os.environ["EDITOR_AUTH_SUBJECTS"]

# The non-superuser role the RLS canary runs under: local and CI database
# users are superusers, which bypass RLS by definition, so asserting isolation
# requires stepping down. Staging/production connect as the table owner, which
# FORCE ROW LEVEL SECURITY covers.
RLS_PROBE_ROLE = "xenia_rls_probe"

_TABLES_NEWEST_FIRST = (
    "drafts",
    "interview_states",
    "golden_set_entries",
    "decisions",
    "recommendations",
    "corrections",
    "outcomes",
    "dna_proposals",
    "signals",
    "ai_call_records",
    "canonical_content",
    "entity_binding_reviews",
    "source_health_events",
    "rubric_scores",
    "edit_log_entries",
    "research_briefs",
    "dna_change_events",
    "dnas",
    "prospects",
    "evidence",
    "source_snapshots",
    "business_records",
    "jobs",
    "audit_entries",
    "users",
    "workspaces",
    "feature_flags",
)


@pytest.fixture(scope="session")
def database_url() -> str:
    """Skip DB-backed tests when Postgres is unreachable; migrate when it is."""
    url = os.environ["DATABASE_URL"]
    probe = create_engine(url)
    try:
        with probe.connect():
            pass
    except Exception:  # pragma: no cover — environment-dependent
        pytest.skip(
            "Postgres unavailable — DB integration tests skipped here; they always run in CI"
        )
    finally:
        probe.dispose()

    from alembic import command
    from alembic.config import Config

    command.upgrade(Config("alembic.ini"), "head")
    return url


@pytest.fixture(scope="session")
def rls_probe(database_url: str) -> str:
    """Create the non-superuser probe role and grant it table access."""
    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(
            text(
                f"DO $$ BEGIN CREATE ROLE {RLS_PROBE_ROLE} NOLOGIN; "
                f"EXCEPTION WHEN duplicate_object THEN NULL; END $$"
            )
        )
        connection.execute(text(f"GRANT USAGE ON SCHEMA public TO {RLS_PROBE_ROLE}"))
        connection.execute(
            text(
                f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public "
                f"TO {RLS_PROBE_ROLE}"
            )
        )
    engine.dispose()
    return RLS_PROBE_ROLE


@pytest.fixture
def db(database_url: str) -> Iterator[Engine]:
    """The application engine, with every table emptied before the test."""
    from app.core.db import get_engine

    engine = get_engine()
    with engine.begin() as connection:
        for table in _TABLES_NEWEST_FIRST:
            connection.execute(text(f"DELETE FROM {table}"))
    yield engine


def mint_supabase_token(
    subject: str,
    *,
    email: str | None = None,
    secret: str = TEST_JWT_SECRET,
    audience: str = "authenticated",
    expires_in_seconds: int = 3600,
) -> str:
    """A real HS256 Supabase-shaped token, verified by the real verifier."""
    import time

    import jwt

    claims: dict[str, object] = {
        "sub": subject,
        "aud": audience,
        "exp": int(time.time()) + expires_in_seconds,
    }
    if email is not None:
        claims["email"] = email
    return jwt.encode(claims, secret, algorithm="HS256")
