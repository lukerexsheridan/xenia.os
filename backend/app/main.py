"""FastAPI application factory.

The API layer translates HTTP <-> use-cases and nothing more (Doc 08 SS3).
Route handlers longer than a screen are a code smell with a name.
"""

from fastapi import FastAPI

from app.api.internal.router import router as internal_router
from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging


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
    application.include_router(v1_router, prefix="/v1")
    # Internal/ops endpoints: separately authorised, never in the public
    # OpenAPI document (Doc 08 SS3).
    application.include_router(internal_router, prefix="/internal", include_in_schema=False)
    return application


app = create_app()
