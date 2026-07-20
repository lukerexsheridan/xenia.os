"""The authenticated multi-tenant skeleton, end to end (Doc 10, Epic 1 exit).

Real HS256 tokens through the real verifier, real provisioning against
Postgres, and the audit trail the exit criteria demand.
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from app.main import create_app
from app.repositories.identity import SqlIdentityRepo
from tests.conftest import mint_supabase_token


def client() -> TestClient:
    return TestClient(create_app())


def bearer(subject: str, email: str | None = None) -> dict[str, str]:
    return {"Authorization": f"Bearer {mint_supabase_token(subject, email=email)}"}


def test_me_requires_a_token(db: Engine) -> None:
    response = client().get("/v1/me")
    assert response.status_code == 401
    assert response.json()["code"] == "not_authenticated"
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_me_rejects_a_garbage_token(db: Engine) -> None:
    response = client().get("/v1/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert response.status_code == 401
    assert response.json()["code"] == "not_authenticated"


def test_first_login_provisions_workspace_and_audits_it(db: Engine) -> None:
    subject = f"auth-{uuid4()}"
    response = client().get("/v1/me", headers=bearer(subject, email="jo@brightpath.example"))
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["role"] == "owner"
    assert body["user"]["email"] == "jo@brightpath.example"
    assert body["workspace"]["name"] == "jo"

    with db.connect() as connection:
        actions = (
            connection.execute(
                text("SELECT action FROM audit_entries WHERE workspace_id = :id ORDER BY action"),
                {"id": body["workspace"]["id"]},
            )
            .scalars()
            .all()
        )
    assert actions == ["user.provisioned", "workspace.provisioned"]


def test_second_login_resolves_to_the_same_workspace(db: Engine) -> None:
    subject = f"auth-{uuid4()}"
    app_client = client()
    first = app_client.get("/v1/me", headers=bearer(subject)).json()
    second = app_client.get("/v1/me", headers=bearer(subject)).json()
    assert first["user"]["id"] == second["user"]["id"]
    assert first["workspace"]["id"] == second["workspace"]["id"]

    with db.connect() as connection:
        audit_count = connection.execute(
            text("SELECT count(*) FROM audit_entries WHERE workspace_id = :id"),
            {"id": first["workspace"]["id"]},
        ).scalar_one()
    assert audit_count == 2  # provisioning only — routine logins are not audit spam


def test_two_identities_get_two_isolated_workspaces(db: Engine) -> None:
    app_client = client()
    workspace_a = app_client.get("/v1/me", headers=bearer(f"a-{uuid4()}")).json()["workspace"]
    workspace_b = app_client.get("/v1/me", headers=bearer(f"b-{uuid4()}")).json()["workspace"]
    assert workspace_a["id"] != workspace_b["id"]


def test_responses_carry_a_request_id(db: Engine) -> None:
    response = client().get("/v1/health")
    assert "x-request-id" in response.headers


def test_racing_first_logins_map_to_a_retryable_conflict(
    db: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If provisioning races between lookup and insert, the unique constraint
    breaks the tie and the loser gets a 409, not a 500."""
    subject = f"race-{uuid4()}"
    app_client = client()
    assert app_client.get("/v1/me", headers=bearer(subject)).status_code == 200

    # Simulate the race window: the lookup misses although the user now exists.
    monkeypatch.setattr(SqlIdentityRepo, "find_user_by_subject", lambda self, s: None)
    response = app_client.get("/v1/me", headers=bearer(subject))
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"
