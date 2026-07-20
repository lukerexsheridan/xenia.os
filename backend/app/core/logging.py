"""Structured JSON logging (Doc 08 SS9).

IDs only — no names, no prospect content, no PII in logs (Doc 05).
Correlation fields (request_id, workspace_id, user_id) bind per-request via
contextvars (`bind_log_context`) so every log line in a request carries them;
`extra=` overrides remain available per call. Trace IDs become additive when
the tracing backend lands (ADR-005).
"""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

_CORRELATION_FIELDS = ("request_id", "workspace_id", "user_id", "pipeline", "prompt_version")

_log_context: ContextVar[dict[str, str] | None] = ContextVar("log_context", default=None)


def bind_log_context(**fields: str) -> None:
    """Merge correlation fields into the current context (request-scoped)."""
    _log_context.set({**(_log_context.get() or {}), **fields})


def clear_log_context() -> None:
    _log_context.set(None)


def current_request_id() -> str | None:
    """The request ID bound by the request middleware, if any."""
    return (_log_context.get() or {}).get("request_id")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        payload.update(_log_context.get() or {})
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
