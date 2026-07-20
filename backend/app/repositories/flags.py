"""DB-backed feature flags (Doc 08 §9): typed, boring, global by design.

Used for staged rollout of pipeline versions and format experiments, never for
permanent configuration. Every flag records a removal date at creation
(Doc 10 §6); an absent flag is simply off.
"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.repositories.orm import FeatureFlagRow


class SqlFeatureFlagRepo:
    def __init__(self, session: Session) -> None:
        self._session = session

    def is_enabled(self, key: str) -> bool:
        row = self._session.execute(
            select(FeatureFlagRow.enabled).where(FeatureFlagRow.key == key)
        ).scalar_one_or_none()
        return bool(row)

    def declare(self, *, key: str, description: str, removal_date: date, enabled: bool) -> None:
        """Create the flag if it does not exist; existing state is never clobbered."""
        existing = self._session.get(FeatureFlagRow, key)
        if existing is None:
            self._session.add(
                FeatureFlagRow(
                    key=key, enabled=enabled, description=description, removal_date=removal_date
                )
            )
            self._session.flush()
