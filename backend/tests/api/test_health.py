from fastapi.testclient import TestClient
from sqlalchemy import Engine

from app.main import create_app


def test_health_returns_ok() -> None:
    client = TestClient(create_app())
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_reports_ready_when_database_is_up(db: Engine) -> None:
    response = TestClient(create_app()).get("/v1/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_internal_status_reports_queue_depth(db: Engine) -> None:
    from tests.conftest import TEST_EDITOR_SUBJECT, mint_supabase_token

    response = TestClient(create_app()).get(
        "/internal/status",
        headers={"Authorization": f"Bearer {mint_supabase_token(TEST_EDITOR_SUBJECT)}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["jobs"] == {}


def test_internal_routes_are_excluded_from_public_openapi() -> None:
    """Doc 08 SS3: internal routers are never exposed in the public OpenAPI document."""
    schema = create_app().openapi()
    internal_paths = [path for path in schema["paths"] if path.startswith("/internal")]
    assert internal_paths == []


def test_public_api_is_versioned_under_v1() -> None:
    """AP4: one versioned public surface."""
    schema = create_app().openapi()
    assert all(path.startswith("/v1") for path in schema["paths"])
