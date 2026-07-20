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

    # Founding billing (Doc 03 §9: one plan; the product links out, never
    # implements payment UI). A Stripe Payment Link and the customer-portal
    # login link, both created in the dashboard.
    stripe_payment_link_url: str = ""
    stripe_portal_login_url: str = ""

    # The monthly AI token ceiling (Doc 08 §8's cost governor). 0 disables
    # the governor while the real ceiling is being learned from ledgers.
    ai_monthly_token_budget: int = 0

    # Outbound email (Resend adapter). The heartbeat job emails the founder
    # daily (Doc 10, Sprint 3); an empty recipient skips the send with a log.
    email_from: str = "Xenia <onboarding@resend.dev>"
    heartbeat_email_to: str = ""

    # The honest User-Agent every fetch carries (Doc 09 §5's politeness
    # engine; N2). Overridden per environment with a real contact URL.
    politeness_user_agent: str = "XeniaResearch/0.1 (+https://xenia.example/about-our-research)"

    # Browser origins allowed to call the API (the SPA on Vercel; the Vite
    # dev server locally). Comma-separated; credentials are bearer headers,
    # never cookies, so no origin wildcard is ever needed.
    cors_allow_origins: str = "http://localhost:5173"

    # Auth subjects permitted on the internal workbench/console (Doc 08 §8:
    # internal access is separately authorised). Comma-separated Supabase subs.
    editor_auth_subjects: str = ""

    # Source credentials (Epic 4 adapters). Empty = family declared
    # couldn't-see rather than guessed at (Doc 09 §2's honest degradation).
    companies_house_api_key: str = ""
    ad_library_access_token: str = ""

    # The V1 provider model behind app/ai (AP6). [calibrates] per pipeline.
    openai_model: str = "gpt-5"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # required fields come from the environment
