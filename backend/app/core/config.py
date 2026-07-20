"""Typed application settings: 12-factor, env-driven, fail-fast (Doc 08 SS3).

A missing required key crashes at startup, not at first use.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Literal["local", "ci", "staging", "production"] = "local"
    log_level: str = "INFO"

    # Required — no default, by design.
    database_url: str

    # Supabase Auth (identity only; verified via JWKS — Doc 08 SS8).
    supabase_url: str = ""
    supabase_jwt_secret: str = ""

    # S3-compatible object storage (ADR-004).
    object_storage_endpoint: str = ""
    object_storage_access_key: str = ""
    object_storage_secret_key: str = ""
    object_storage_bucket: str = "xenia-artefacts"

    # Vendors. Empty until their integrations activate; never logged.
    openai_api_key: str = ""
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    resend_api_key: str = ""
    sentry_dsn: str = ""

    # Outbound email (Resend adapter). The heartbeat job emails the founder
    # daily (Doc 10, Sprint 3); an empty recipient skips the send with a log.
    email_from: str = "Xenia <onboarding@resend.dev>"
    heartbeat_email_to: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # required fields come from the environment
