import json
import logging

from app.core.logging import (
    JsonFormatter,
    bind_log_context,
    clear_log_context,
    current_request_id,
)


def make_record(**extra: str) -> logging.LogRecord:
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    for key, value in extra.items():
        record.__dict__[key] = value
    return record


def test_logs_are_structured_json() -> None:
    payload = json.loads(JsonFormatter().format(make_record()))
    assert payload["message"] == "hello"
    assert payload["level"] == "INFO"
    assert "timestamp" in payload


def test_correlation_fields_attach_when_present() -> None:
    """Doc 08 SS9: request/workspace IDs on every log line — IDs only, no PII."""
    payload = json.loads(
        JsonFormatter().format(make_record(request_id="req-1", workspace_id="ws-1"))
    )
    assert payload["request_id"] == "req-1"
    assert payload["workspace_id"] == "ws-1"


def test_bound_context_appears_on_every_line() -> None:
    """Doc 08 SS9: request/workspace correlation without per-call ceremony."""
    clear_log_context()
    try:
        bind_log_context(request_id="req-9", workspace_id="ws-9")
        payload = json.loads(JsonFormatter().format(make_record()))
        assert payload["request_id"] == "req-9"
        assert payload["workspace_id"] == "ws-9"
        assert current_request_id() == "req-9"
    finally:
        clear_log_context()


def test_explicit_extra_overrides_bound_context() -> None:
    clear_log_context()
    try:
        bind_log_context(request_id="bound")
        payload = json.loads(JsonFormatter().format(make_record(request_id="explicit")))
        assert payload["request_id"] == "explicit"
    finally:
        clear_log_context()
