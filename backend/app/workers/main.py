"""Worker entrypoint — the monolith's second process (Doc 08 SS2).

Skeleton status: a heartbeat loop. The jobs-table consumer, scheduler, and
retry/dead-letter semantics land in Epic 1/Sprint 3 (see DEBT.md).
"""

import logging
import time

from app.core.config import get_settings
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)

HEARTBEAT_SECONDS = 60


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("worker started", extra={"pipeline": "worker-skeleton"})
    while True:
        logger.info("worker heartbeat")
        time.sleep(HEARTBEAT_SECONDS)


if __name__ == "__main__":
    main()
