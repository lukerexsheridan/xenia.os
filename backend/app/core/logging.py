"""Structured JSON logging (Doc 08 SS9).

IDs only — no names, no prospect content, no PII in logs (Doc 05).
Correlation fields (request_id, workspace_id) attach via `extra=`; trace IDs
become additive when the tracing backend lands (ADR-005).
"""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

_CORRELATION_FIELDS = ("request_id", "workspace_id", "user_id", "pipeline", "prompt_version")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in _CORRELATION_FIELDS:
            value = record.__dict__.get(field)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())
