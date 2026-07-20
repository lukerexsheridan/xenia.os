"""Test configuration.

Unit tests never touch a real database; migration checks run separately in CI
against the service Postgres. Required settings are provided here so the
fail-fast config (app/core/config.py) is satisfied deterministically.
"""

import os

os.environ.setdefault("ENVIRONMENT", "ci")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://xenia:xenia@localhost:5432/xenia")
