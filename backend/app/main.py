"""FastAPI application factory.

The API layer translates HTTP <-> use-cases and nothing more (Doc 08 SS3).
Route handlers longer than a screen are a code smell with a name.

Two applications, one process: the public /v1 surface (the only surface in
the public OpenAPI document — AP4) and the internal console/workbench,
mounted at /internal as its own sub-application with its own docs, every
route behind Editor authorisation (Doc 08 SS8, SS3).
"""

from http import HTTPStatus

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.internal import workbench
from app.api.internal.deps import get_editor_context
from app.api.internal.router import router as internal_status_router
from app.api.middleware import RequestContextMiddleware
from app.api.v1.router import router as v1_router
from app.core.config import Settings, get_settings
from app.core.errors import ErrorCode, XeniaError
from app.core.logging import configure_logging
from app.core.observability import init_error_reporting

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


def _register_error_handlers(application: FastAPI) -> None:
    application.add_exception_handler(XeniaError, _xenia_error_handler)  # type: ignore[arg-type]


def _create_internal_app(settings: Settings) -> FastAPI:
    """The Editor console and workbench (Doc 08 SS2): separately authorised,
    never in the public OpenAPI document. Its own docs UI is the workbench's
    deliberately ugly-but-honest surface (Doc 10, Epic 3)."""
    internal = FastAPI(
        title="Xenia Internal — Editor console & research workbench",
        version="0.1.0",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url=None,
        dependencies=[Depends(get_editor_context)],
    )
    _register_error_handlers(internal)
    internal.include_router(internal_status_router, tags=["status"])
    internal.include_router(workbench.router, prefix="/workbench", tags=["workbench"])
    return internal


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    init_error_reporting(settings)

    application = FastAPI(
        title="Xenia API",
        version="0.1.0",
        # /v1 is the only public surface (AP4); docs follow the environment.
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url=None,
    )
    application.add_middleware(RequestContextMiddleware)
    _register_error_handlers(application)
    application.include_router(v1_router, prefix="/v1")
    application.mount("/internal", _create_internal_app(settings))
    return application


app = create_app()
