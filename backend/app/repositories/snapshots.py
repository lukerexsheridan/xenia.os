"""SourceSnapshot metadata — the provenance contract's anchor (Doc 09 §5).

Ring 2: an observation of the public web carries no customer fingerprint.
Raw bytes live in object storage keyed by SHA-256; each row is one
observation event ("we kept what we saw, because the web won't keep it for
us"). Content is deduplicated by hash; observations never are.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.orm import SourceSnapshotRow


@dataclass(frozen=True)
class SourceSnapshot:
    id: UUID
    url: str
    content_sha256: str
    content_type: str
    http_status: int
    size_bytes: int
    fetcher_version: str
    fetched_at: datetime


def _to_snapshot(row: SourceSnapshotRow) -> SourceSnapshot:
    return SourceSnapshot(
        id=row.id,
        url=row.url,
        content_sha256=row.content_sha256,
        content_type=row.content_type,
        http_status=row.http_status,
        size_bytes=row.size_bytes,
        fetcher_version=row.fetcher_version,
        fetched_at=row.fetched_at,
    )


class SqlSourceSnapshotRepo:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(
        self,
        *,
        url: str,
        content_sha256: str,
        content_type: str,
        http_status: int,
        size_bytes: int,
        fetcher_version: str,
    ) -> SourceSnapshot:
        row = SourceSnapshotRow(
            url=url,
            content_sha256=content_sha256,
            content_type=content_type,
            http_status=http_status,
            size_bytes=size_bytes,
            fetcher_version=fetcher_version,
        )
        self._session.add(row)
        self._session.flush()
        return _to_snapshot(row)

    def get(self, snapshot_id: UUID) -> SourceSnapshot | None:
        row = self._session.get(SourceSnapshotRow, snapshot_id)
        return _to_snapshot(row) if row else None
