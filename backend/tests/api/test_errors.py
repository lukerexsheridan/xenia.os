"""The error taxonomy's HTTP mapping: codes are stable contract (Doc 08 §3)."""

import pytest
from fastapi.testclient import TestClient

from app.core import errors
from app.main import create_app

CASES = [
    (errors.NotFoundError, 404, "not_found"),
    (errors.NotAuthenticatedError, 401, "not_authenticated"),
    (errors.NotAuthorisedError, 403, "not_authorised"),
    (errors.XeniaError, 422, "validation_failed"),
    (errors.ConflictError, 409, "conflict"),
    (errors.DelegationRequiredError, 403, "delegation_required"),
    (errors.BudgetExhaustedError, 429, "budget_exhausted"),
]


@pytest.mark.parametrize(("exception_type", "status_code", "code"), CASES)
def test_xenia_errors_map_to_stable_http_responses(
    exception_type: type[errors.XeniaError], status_code: int, code: str
) -> None:
    app = create_app()

    @app.get("/_test/raise")
    def raise_it() -> None:
        raise exception_type("something happened")

    response = TestClient(app).get("/_test/raise")
    assert response.status_code == status_code
    assert response.json() == {"code": code, "message": "something happened"}


def test_401_carries_the_www_authenticate_header() -> None:
    app = create_app()

    @app.get("/_test/unauthenticated")
    def raise_it() -> None:
        raise errors.NotAuthenticatedError("no token")

    response = TestClient(app).get("/_test/unauthenticated")
    assert response.headers["WWW-Authenticate"] == "Bearer"
