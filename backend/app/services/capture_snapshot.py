"""CaptureSnapshot — fetch politely, keep what we saw (Doc 09 §5).

Every fetch flows through the politeness engine (N2's single enforcement
point) and, on success, leaves a replayable snapshot: content-addressed bytes
in object storage plus a provenance row. A refusal (robots, circuit breaker,
unwelcome response) surfaces as an honest error — logged, never evaded.
"""

import hashlib
from typing import Protocol

from app.core.errors import XeniaError
from app.integrations.object_storage import ObjectStore
from app.integrations.sources.politeness import FetchedContent, FetchOutcome
from app.repositories.snapshots import SourceSnapshot, SqlSourceSnapshotRepo

FETCHER_VERSION = "workbench-fetch/1"


def snapshot_object_key(content_sha256: str) -> str:
    return f"snapshots/{content_sha256}"


class PoliteFetcher(Protocol):
    """The service's port onto acquisition: satisfied by the politeness
    engine — the only fetcher this system possesses (N2)."""

    def fetch(self, url: str) -> FetchOutcome: ...


class FetchRefusedError(XeniaError):
    """The politeness engine declined the fetch. Honest, final, not retried."""


class CaptureSnapshot:
    def __init__(
        self,
        engine: PoliteFetcher,
        object_store: ObjectStore,
        snapshot_repo: SqlSourceSnapshotRepo,
    ) -> None:
        self._engine = engine
        self._object_store = object_store
        self._snapshot_repo = snapshot_repo

    def execute(self, url: str) -> SourceSnapshot:
        outcome = self._engine.fetch(url)
        if not isinstance(outcome, FetchedContent):
            raise FetchRefusedError(f"fetch refused ({outcome.reason.value}): {outcome.detail}")
        digest = hashlib.sha256(outcome.content).hexdigest()
        self._object_store.put_if_absent(
            snapshot_object_key(digest), outcome.content, content_type=outcome.content_type
        )
        return self._snapshot_repo.add(
            url=url,
            content_sha256=digest,
            content_type=outcome.content_type,
            http_status=outcome.status,
            size_bytes=len(outcome.content),
            fetcher_version=FETCHER_VERSION,
        )

    def content_for(self, snapshot: SourceSnapshot) -> bytes:
        """Replay a snapshot's bytes from the content-addressed store."""
        return self._object_store.get(snapshot_object_key(snapshot.content_sha256))
