from fastapi.testclient import TestClient

from app.main import create_app


def test_health_returns_ok() -> None:
    client = TestClient(create_app())
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_internal_routes_are_excluded_from_public_openapi() -> None:
    """Doc 08 SS3: internal routers are never exposed in the public OpenAPI document."""
    schema = create_app().openapi()
    internal_paths = [path for path in schema["paths"] if path.startswith("/internal")]
    assert internal_paths == []


def test_public_api_is_versioned_under_v1() -> None:
    """AP4: one versioned public surface."""
    schema = create_app().openapi()
    assert all(path.startswith("/v1") for path in schema["paths"])
