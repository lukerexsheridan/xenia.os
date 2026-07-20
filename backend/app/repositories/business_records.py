"""BusinessRecords — the Ring-2 world model's spine (Doc 05 §7).

Deliberately not workspace-scoped: facts are shared. Strong keys (website
domain, register number) identify records; find-or-create keeps the world
model deduplicated from the first entry.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.business_record import BusinessRecord
from app.repositories.orm import BusinessRecordRow


def _to_domain(row: BusinessRecordRow) -> BusinessRecord:
    return BusinessRecord(
        id=row.id,
        canonical_name=row.canonical_name,
        website_domain=row.website_domain,
        register_number=row.register_number,
        created_at=row.created_at,
    )


class SqlBusinessRecordRepo:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, business_record_id: UUID) -> BusinessRecord | None:
        row = self._session.get(BusinessRecordRow, business_record_id)
        return _to_domain(row) if row else None

    def find_or_create(
        self,
        *,
        canonical_name: str,
        website_domain: str | None,
        register_number: str | None,
    ) -> BusinessRecord:
        """Match on a strong key when one is given (domain first, then
        register number — Doc 09 §5's entity-binding order); create otherwise."""
        if website_domain:
            row = self._session.execute(
                select(BusinessRecordRow).where(BusinessRecordRow.website_domain == website_domain)
            ).scalar_one_or_none()
            if row:
                return _to_domain(row)
        if register_number:
            row = self._session.execute(
                select(BusinessRecordRow).where(
                    BusinessRecordRow.register_number == register_number
                )
            ).scalar_one_or_none()
            if row:
                return _to_domain(row)
        created = BusinessRecordRow(
            canonical_name=canonical_name,
            website_domain=website_domain,
            register_number=register_number,
        )
        self._session.add(created)
        self._session.flush()
        return _to_domain(created)
