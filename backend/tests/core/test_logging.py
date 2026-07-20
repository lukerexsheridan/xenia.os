import json
import logging

from app.core.logging import JsonFormatter


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
