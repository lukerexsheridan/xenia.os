"""FastAPI application factory.

The API layer translates HTTP <-> use-cases and nothing more (Doc 08 SS3).
Route handlers longer than a screen are a code smell with a name.
"""

from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.internal.router import router as internal_router
from app.api.middleware import RequestContextMiddleware
from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.errors import ErrorCode, XeniaError
from app.core.logging import configure_logging

# The error taxonomy's HTTP face: codes are stable contract (Doc 08 SS3);
# the frontend maps them to the Doc 06 failure voice.
_HTTP_STATUS_BY_CODE: dict[ErrorCode, int] = {
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.NOT_AUTHENTICATED: 401,
    ErrorCode.NOT_AUTHORISED: 403,
    ErrorCode.VALIDATION_FAILED: 422,
    ErrorCode.CONFLICT: 409,
    ErrorCode.DELEGATION_REQUIRED: 403,
    ErrorCode.BUDGET_EXHAUSTED: 429,
}


def _xenia_error_handler(request: Request, exc: XeniaError) -> JSONResponse:
    status_code = _HTTP_STATUS_BY_CODE[exc.code]
    headers = {"WWW-Authenticate": "Bearer"} if status_code == HTTPStatus.UNAUTHORIZED else None
    return JSONResponse(
        status_code=status_code,
        content={"code": exc.code.value, "message": exc.message},
        headers=headers,
    )


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    application = FastAPI(
        title="Xenia API",
        version="0.1.0",
        # /v1 is the only public surface (AP4); docs follow the environment.
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url=None,
    )
    application.add_middleware(RequestContextMiddleware)
    application.add_exception_handler(XeniaError, _xenia_error_handler)  # type: ignore[arg-type]
    application.include_router(v1_router, prefix="/v1")
    # Internal/ops endpoints: separately authorised, never in the public
    # OpenAPI document (Doc 08 SS3).
    application.include_router(internal_router, prefix="/internal", include_in_schema=False)
    return application


app = create_app()
