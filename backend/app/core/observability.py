"""Error reporting (ADR-005): Sentry, release-tagged, PII-scrubbed.

Initialised from both entrypoints (API and worker) when a DSN is configured;
a no-op otherwise. `send_default_pii` stays False and structured logs remain
IDs-only (Doc 05) — nothing here may carry names or prospect content.
"""

from app.core.config import Settings


def init_error_reporting(settings: Settings) -> None:
    if not settings.sentry_dsn:
        return
    import sentry_sdk  # noqa: PLC0415 — imported only when a DSN is configured

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        send_default_pii=False,
    )
