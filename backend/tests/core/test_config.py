import pytest
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

from app.core.config import Settings


class EnvOnlySettings(Settings):
    """Settings that ignore any local .env file, so tests are deterministic."""

    model_config = SettingsConfigDict(env_file=None, extra="ignore")


def test_settings_fail_fast_on_missing_required_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Doc 08 SS3: typed configuration fails fast on missing keys."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValidationError):
        EnvOnlySettings()  # type: ignore[call-arg]  # the missing kwarg is the test


def test_settings_read_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@h:5432/db")
    monkeypatch.setenv("ENVIRONMENT", "staging")
    settings = EnvOnlySettings()  # type: ignore[call-arg]  # database_url comes from env
    assert settings.database_url == "postgresql+psycopg://u:p@h:5432/db"
    assert settings.environment == "staging"


def test_environment_values_are_constrained(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@h:5432/db")
    monkeypatch.setenv("ENVIRONMENT", "not-a-real-environment")
    with pytest.raises(ValidationError):
        EnvOnlySettings()  # type: ignore[call-arg]
