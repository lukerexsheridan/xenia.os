"""Snapshot capture: every fetch leaves a replayable snapshot (Sprint 5 DoD)."""

import hashlib
from dataclasses import dataclass, field

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.integrations.sources.politeness import (
    FetchedContent,
    FetchRefusal,
    RefusalReason,
)
from app.repositories.snapshots import SqlSourceSnapshotRepo
from app.services.capture_snapshot import (
    FETCHER_VERSION,
    CaptureSnapshot,
    FetchRefusedError,
    snapshot_object_key,
)


class InMemoryObjectStore:
    def __init__(self) -> None:
        self.blobs: dict[str, bytes] = {}
        self.put_calls = 0

    def put_if_absent(self, key: str, data: bytes, *, content_type: str) -> None:
        self.put_calls += 1
        self.blobs.setdefault(key, data)

    def get(self, key: str) -> bytes:
        return self.blobs[key]

    def exists(self, key: str) -> bool:
        return key in self.blobs


@dataclass
class ScriptedEngine:
    outcomes: list[FetchedContent | FetchRefusal]
    fetched: list[str] = field(default_factory=list)

    def fetch(self, url: str) -> FetchedContent | FetchRefusal:
        self.fetched.append(url)
        return self.outcomes.pop(0)


CONTENT = b"<html>Brightpath sells DTC skincare</html>"
URL = "https://brightpath.example/about"


def fetched(content: bytes = CONTENT) -> FetchedContent:
    return FetchedContent(url=URL, status=200, content=content, content_type="text/html")


def test_doc09_s5_every_fetch_leaves_a_replayable_snapshot(db: Engine) -> None:
    store = InMemoryObjectStore()
    with Session(db) as session:
        capture = CaptureSnapshot(
            ScriptedEngine([fetched()]), store, SqlSourceSnapshotRepo(session)
        )
        snapshot = capture.execute(URL)
        session.commit()

    digest = hashlib.sha256(CONTENT).hexdigest()
    assert snapshot.content_sha256 == digest
    assert store.get(snapshot_object_key(digest)) == CONTENT  # round-trip
    assert snapshot.url == URL
    assert snapshot.http_status == 200
    assert snapshot.size_bytes == len(CONTENT)
    assert snapshot.fetcher_version == FETCHER_VERSION
    assert snapshot.fetched_at is not None  # provenance: observed, at a time


def test_identical_content_is_stored_once_but_observed_twice(db: Engine) -> None:
    store = InMemoryObjectStore()
    with Session(db) as session:
        repo = SqlSourceSnapshotRepo(session)
        first = CaptureSnapshot(ScriptedEngine([fetched()]), store, repo).execute(URL)
        second = CaptureSnapshot(ScriptedEngine([fetched()]), store, repo).execute(URL)
        session.commit()
    assert first.id != second.id  # two observation events
    assert first.content_sha256 == second.content_sha256
    assert len(store.blobs) == 1  # one blob, content-addressed


def test_a_refusal_surfaces_honestly_and_stores_nothing(db: Engine) -> None:
    store = InMemoryObjectStore()
    refusal = FetchRefusal(
        url=URL, reason=RefusalReason.ROBOTS_DISALLOWED, detail="disallowed by robots.txt"
    )
    with Session(db) as session:
        capture = CaptureSnapshot(ScriptedEngine([refusal]), store, SqlSourceSnapshotRepo(session))
        with pytest.raises(FetchRefusedError, match="robots_disallowed"):
            capture.execute(URL)
    assert store.blobs == {}
