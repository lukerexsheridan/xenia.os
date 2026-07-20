"""The politeness engine's unit suite (Doc 10, Sprint 5 DoD).

A blocked domain circuit-breaks and logs — never evades; robots are
honoured; the rate limiter and breaker are exercised with injected clocks so
every case is deterministic.
"""

from dataclasses import dataclass, field

import pytest

from app.integrations.sources.politeness import (
    CIRCUIT_BREAKER_COOLDOWN_SECONDS,
    CIRCUIT_BREAKER_FAILURE_THRESHOLD,
    MIN_SECONDS_BETWEEN_REQUESTS_PER_DOMAIN,
    FetchedContent,
    FetchRefusal,
    PolitenessEngine,
    RefusalReason,
    TransportError,
    TransportResponse,
)

UA = "XeniaResearch/test (+https://xenia.example)"


@dataclass
class FakeClock:
    now: float = 1000.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@dataclass
class FakeTransport:
    """Scripted responses per URL; records every request it received."""

    responses: dict[str, TransportResponse | Exception]
    requests: list[tuple[str, str]] = field(default_factory=list)
    default: TransportResponse | Exception = field(
        default_factory=lambda: TransportResponse(200, b"<html>ok</html>", "text/html")
    )

    def get(self, url: str, *, user_agent: str) -> TransportResponse:
        self.requests.append((url, user_agent))
        outcome = self.responses.get(url, self.default)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def make_engine(
    transport: FakeTransport, clock: FakeClock | None = None
) -> tuple[PolitenessEngine, FakeClock, list[float]]:
    clock = clock or FakeClock()
    sleeps: list[float] = []

    def sleeper(seconds: float) -> None:
        sleeps.append(seconds)
        clock.advance(seconds)

    engine = PolitenessEngine(transport, user_agent=UA, clock=clock, sleeper=sleeper)
    return engine, clock, sleeps


def allow_all_robots() -> TransportResponse:
    return TransportResponse(200, b"User-agent: *\nAllow: /\n", "text/plain")


def test_doc09_s5_every_fetch_carries_the_honest_user_agent() -> None:
    transport = FakeTransport({"https://example.co.uk/robots.txt": allow_all_robots()})
    engine, _, _ = make_engine(transport)
    outcome = engine.fetch("https://example.co.uk/about")
    assert isinstance(outcome, FetchedContent)
    assert all(user_agent == UA for _, user_agent in transport.requests)


def test_doc09_s5_robots_disallow_is_honoured_never_evaded() -> None:
    transport = FakeTransport(
        {
            "https://example.co.uk/robots.txt": TransportResponse(
                200, b"User-agent: *\nDisallow: /private/\n", "text/plain"
            )
        }
    )
    engine, _, _ = make_engine(transport)
    outcome = engine.fetch("https://example.co.uk/private/page")
    assert isinstance(outcome, FetchRefusal)
    assert outcome.reason is RefusalReason.ROBOTS_DISALLOWED
    # The disallowed page itself was never requested — honoured, not probed.
    assert all(url.endswith("/robots.txt") for url, _ in transport.requests)


def test_rfc9309_absent_robots_permits_fetching() -> None:
    transport = FakeTransport(
        {"https://example.co.uk/robots.txt": TransportResponse(404, b"", "text/plain")}
    )
    engine, _, _ = make_engine(transport)
    assert isinstance(engine.fetch("https://example.co.uk/about"), FetchedContent)


def test_rfc9309_unreachable_robots_means_disallow() -> None:
    transport = FakeTransport(
        {"https://example.co.uk/robots.txt": TransportError("connect timeout")}
    )
    engine, _, _ = make_engine(transport)
    outcome = engine.fetch("https://example.co.uk/about")
    assert isinstance(outcome, FetchRefusal)
    assert outcome.reason is RefusalReason.ROBOTS_UNAVAILABLE


def test_doc09_s5_per_domain_rate_limit_spaces_requests() -> None:
    transport = FakeTransport({"https://example.co.uk/robots.txt": allow_all_robots()})
    engine, _, sleeps = make_engine(transport)
    engine.fetch("https://example.co.uk/one")
    engine.fetch("https://example.co.uk/two")
    assert any(0 < wait <= MIN_SECONDS_BETWEEN_REQUESTS_PER_DOMAIN for wait in sleeps), (
        "the second same-domain request must wait out the interval"
    )


def test_doc09_s5_unwelcome_response_backs_off_never_evades() -> None:
    transport = FakeTransport(
        {
            "https://example.co.uk/robots.txt": allow_all_robots(),
            "https://example.co.uk/page": TransportResponse(403, b"", "text/html"),
        }
    )
    engine, _, _ = make_engine(transport)
    outcome = engine.fetch("https://example.co.uk/page")
    assert isinstance(outcome, FetchRefusal)
    assert outcome.reason is RefusalReason.UNWELCOME_RESPONSE
    assert "never evading" in outcome.detail


def test_doc09_s5_repeated_failures_open_the_circuit_and_cooldown_closes_it() -> None:
    transport = FakeTransport(
        {
            "https://example.co.uk/robots.txt": allow_all_robots(),
            "https://example.co.uk/page": TransportResponse(429, b"", "text/html"),
        }
    )
    engine, clock, _ = make_engine(transport)
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        engine.fetch("https://example.co.uk/page")

    requests_before = len(transport.requests)
    refused = engine.fetch("https://example.co.uk/page")
    assert isinstance(refused, FetchRefusal)
    assert refused.reason is RefusalReason.CIRCUIT_OPEN
    assert len(transport.requests) == requests_before  # refused fast, no traffic

    clock.advance(CIRCUIT_BREAKER_COOLDOWN_SECONDS + 1)
    transport.responses["https://example.co.uk/page"] = TransportResponse(
        200, b"welcome back", "text/html"
    )
    assert isinstance(engine.fetch("https://example.co.uk/page"), FetchedContent)


def test_transient_server_errors_are_retried_then_reported() -> None:
    transport = FakeTransport(
        {
            "https://example.co.uk/robots.txt": allow_all_robots(),
            "https://example.co.uk/page": TransportResponse(503, b"", "text/html"),
        }
    )
    engine, _, _ = make_engine(transport)
    outcome = engine.fetch("https://example.co.uk/page")
    assert isinstance(outcome, FetchRefusal)
    assert outcome.reason is RefusalReason.UNREACHABLE
    page_requests = [url for url, _ in transport.requests if url.endswith("/page")]
    assert len(page_requests) > 1  # retried before giving up


def test_domains_are_rate_limited_independently() -> None:
    transport = FakeTransport(
        {
            "https://a.example/robots.txt": allow_all_robots(),
            "https://b.example/robots.txt": allow_all_robots(),
        }
    )
    engine, _, sleeps = make_engine(transport)
    engine.fetch("https://a.example/x")
    engine.fetch("https://b.example/y")
    assert sleeps == []  # different domains: no wait imposed


@pytest.mark.parametrize("status", [500, 502, 503])
def test_erroring_robots_means_disallow(status: int) -> None:
    transport = FakeTransport(
        {"https://example.co.uk/robots.txt": TransportResponse(status, b"", "text/plain")}
    )
    engine, _, _ = make_engine(transport)
    outcome = engine.fetch("https://example.co.uk/about")
    assert isinstance(outcome, FetchRefusal)
    assert outcome.reason is RefusalReason.ROBOTS_UNAVAILABLE
