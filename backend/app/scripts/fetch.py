"""The workbench fetch CLI (Doc 10, Sprint 5).

Snapshot any prospect URL through the politeness engine: the fetch is
rate-limited, robots-honouring, and leaves a replayable content-addressed
snapshot — or it is refused, honestly.

Usage: python -m app.scripts.fetch <url> [<url> ...]
"""

import sys
import time

from app.core.config import get_settings
from app.core.db import session_scope
from app.core.logging import configure_logging
from app.integrations.object_storage import S3ObjectStore
from app.integrations.sources.http_transport import HttpxTransport
from app.integrations.sources.politeness import PolitenessEngine
from app.repositories.snapshots import SqlSourceSnapshotRepo
from app.services.capture_snapshot import CaptureSnapshot, FetchRefusedError


def main(urls: list[str]) -> int:
    if not urls:
        sys.stderr.write("usage: python -m app.scripts.fetch <url> [<url> ...]\n")
        return 2
    settings = get_settings()
    configure_logging(settings.log_level)
    object_store = S3ObjectStore(
        endpoint_url=settings.object_storage_endpoint,
        access_key=settings.object_storage_access_key,
        secret_key=settings.object_storage_secret_key,
        bucket=settings.object_storage_bucket,
    )
    object_store.ensure_bucket()
    engine = PolitenessEngine(
        HttpxTransport(),
        user_agent=settings.politeness_user_agent,
        clock=time.monotonic,
        sleeper=time.sleep,
    )
    exit_code = 0
    for url in urls:
        with session_scope() as session:
            capture = CaptureSnapshot(engine, object_store, SqlSourceSnapshotRepo(session))
            try:
                snapshot = capture.execute(url)
            except FetchRefusedError as refusal:
                sys.stderr.write(f"refused  {url}  ({refusal.message})\n")
                exit_code = 1
                continue
            sys.stdout.write(
                f"snapshot {snapshot.id}  sha256={snapshot.content_sha256[:12]}…  "
                f"{snapshot.size_bytes} bytes  {url}\n"
            )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
