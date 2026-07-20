"""The politeness engine — N2's single enforcement point (Doc 09 §5).

One shared subsystem every fetch flows through: per-domain rate limits,
robots.txt honour, an honest User-Agent, bounded retries with backoff, and
per-domain circuit breakers. A blocked domain circuit-breaks and logs —
never evades. The compliant-means-only posture (Doc 05 §6) is enforced here,
in one place, rather than trusted to every adapter.

Robots semantics follow RFC 9309: an absent robots.txt (4xx) permits
fetching; an unreachable or erroring robots.txt (5xx, transport failure) is
treated as a full disallow — when we cannot read the rules, we assume we are
not welcome.

Everything time-shaped (clock, sleeper, transport) is injected, so the whole
engine is deterministic under test. State (rate clocks, breakers, robots
cache) is per-engine-instance: one engine per process (the workbench CLI, a
worker) — the V1 scale this serves (Doc 08 §10).
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from http import HTTPStatus
from typing import Protocol
from urllib import robotparser
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)

MIN_SECONDS_BETWEEN_REQUESTS_PER_DOMAIN = 5.0
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 3
CIRCUIT_BREAKER_COOLDOWN_SECONDS = 900.0
MAX_TRANSIENT_RETRIES = 2
RETRY_BACKOFF_SECONDS = 2.0
ROBOTS_CACHE_SECONDS = 3600.0

# Status codes that mean "we are not welcome" and count towards the breaker.
_UNWELCOME_STATUSES = frozenset({401, 403, 407, 429})


class TransportError(Exception):
    """The transport could not complete the request (network-level failure)."""


@dataclass(frozen=True)
class TransportResponse:
    status: int
    content: bytes
    content_type: str


class Transport(Protocol):
    """Performs one HTTP GET. Implementations set no policy — policy is the
    engine's job, transport is plumbing."""

    def get(self, url: str, *, user_agent: str) -> TransportResponse: ...


class RefusalReason(StrEnum):
    ROBOTS_DISALLOWED = "robots_disallowed"
    ROBOTS_UNAVAILABLE = "robots_unavailable"
    CIRCUIT_OPEN = "circuit_open"
    UNWELCOME_RESPONSE = "unwelcome_response"
    UNREACHABLE = "unreachable"


@dataclass(frozen=True)
class FetchedContent:
    url: str
    status: int
    content: bytes
    content_type: str


@dataclass(frozen=True)
class FetchRefusal:
    url: str
    reason: RefusalReason
    detail: str


FetchOutcome = FetchedContent | FetchRefusal


@dataclass
class _DomainState:
    last_request_at: float | None = None
    consecutive_failures: int = 0
    circuit_open_until: float | None = None
    robots: robotparser.RobotFileParser | None = None
    robots_unavailable: bool = False
    robots_fetched_at: float | None = None


class PolitenessEngine:
    def __init__(
        self,
        transport: Transport,
        *,
        user_agent: str,
        clock: Callable[[], float],
        sleeper: Callable[[float], None],
        min_interval_seconds: float = MIN_SECONDS_BETWEEN_REQUESTS_PER_DOMAIN,
        breaker_threshold: int = CIRCUIT_BREAKER_FAILURE_THRESHOLD,
        breaker_cooldown_seconds: float = CIRCUIT_BREAKER_COOLDOWN_SECONDS,
    ) -> None:
        self._transport = transport
        self._user_agent = user_agent
        self._clock = clock
        self._sleeper = sleeper
        self._min_interval = min_interval_seconds
        self._breaker_threshold = breaker_threshold
        self._breaker_cooldown = breaker_cooldown_seconds
        self._domains: dict[str, _DomainState] = {}

    def fetch(self, url: str) -> FetchOutcome:
        domain = _domain_of(url)
        state = self._domains.setdefault(domain, _DomainState())

        if (refusal := self._check_circuit(url, state)) is not None:
            return refusal
        if (refusal := self._check_robots(url, domain, state)) is not None:
            return refusal

        return self._fetch_with_retries(url, domain, state)

    # ── circuit breaker ──────────────────────────────────────────────────

    def _check_circuit(self, url: str, state: _DomainState) -> FetchRefusal | None:
        if state.circuit_open_until is None:
            return None
        if self._clock() >= state.circuit_open_until:
            # Cooldown elapsed: half-open — the next fetch is the probe.
            state.circuit_open_until = None
            state.consecutive_failures = 0
            return None
        return FetchRefusal(
            url=url,
            reason=RefusalReason.CIRCUIT_OPEN,
            detail="domain circuit-broken after repeated failures; cooling down",
        )

    def _record_failure(self, domain: str, state: _DomainState) -> None:
        state.consecutive_failures += 1
        if state.consecutive_failures >= self._breaker_threshold:
            state.circuit_open_until = self._clock() + self._breaker_cooldown
            # An ops signal, never an evasion trigger (N2).
            logger.warning("circuit opened for domain after repeated failures: %s", domain)

    # ── robots honour ────────────────────────────────────────────────────

    def _check_robots(self, url: str, domain: str, state: _DomainState) -> FetchRefusal | None:
        now = self._clock()
        stale = (
            state.robots_fetched_at is None or now - state.robots_fetched_at > ROBOTS_CACHE_SECONDS
        )
        if stale:
            self._refresh_robots(url, domain, state)
        if state.robots_unavailable:
            return FetchRefusal(
                url=url,
                reason=RefusalReason.ROBOTS_UNAVAILABLE,
                detail="robots.txt unreachable — assuming disallow (RFC 9309)",
            )
        if state.robots is not None and not state.robots.can_fetch(self._user_agent, url):
            logger.info("robots.txt disallows fetch: %s", domain)
            return FetchRefusal(
                url=url,
                reason=RefusalReason.ROBOTS_DISALLOWED,
                detail="disallowed by robots.txt; honoured, never evaded (N2)",
            )
        return None

    def _refresh_robots(self, url: str, domain: str, state: _DomainState) -> None:
        parts = urlsplit(url)
        robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
        state.robots_fetched_at = self._clock()
        try:
            response = self._transport.get(robots_url, user_agent=self._user_agent)
        except TransportError:
            state.robots, state.robots_unavailable = None, True
            return
        if response.status >= HTTPStatus.INTERNAL_SERVER_ERROR:
            state.robots, state.robots_unavailable = None, True
        elif response.status >= HTTPStatus.BAD_REQUEST:
            state.robots, state.robots_unavailable = None, False  # absent → allow
        else:
            parser = robotparser.RobotFileParser()
            parser.parse(response.content.decode("utf-8", errors="replace").splitlines())
            state.robots, state.robots_unavailable = parser, False

    # ── rate-limited, retried fetch ──────────────────────────────────────

    def _fetch_with_retries(self, url: str, domain: str, state: _DomainState) -> FetchOutcome:
        last_detail = ""
        for attempt in range(1 + MAX_TRANSIENT_RETRIES):
            if attempt:
                self._sleeper(RETRY_BACKOFF_SECONDS * attempt)
            self._respect_rate_limit(state)
            try:
                response = self._transport.get(url, user_agent=self._user_agent)
            except TransportError as exc:
                last_detail = str(exc)
                continue
            if response.status in _UNWELCOME_STATUSES:
                self._record_failure(domain, state)
                return FetchRefusal(
                    url=url,
                    reason=RefusalReason.UNWELCOME_RESPONSE,
                    detail=f"HTTP {response.status} — backing off, never evading (N2)",
                )
            if response.status >= HTTPStatus.INTERNAL_SERVER_ERROR:
                last_detail = f"HTTP {response.status}"
                continue
            state.consecutive_failures = 0
            return FetchedContent(
                url=url,
                status=response.status,
                content=response.content,
                content_type=response.content_type,
            )
        self._record_failure(domain, state)
        return FetchRefusal(
            url=url, reason=RefusalReason.UNREACHABLE, detail=last_detail or "no response"
        )

    def _respect_rate_limit(self, state: _DomainState) -> None:
        now = self._clock()
        if state.last_request_at is not None:
            wait = self._min_interval - (now - state.last_request_at)
            if wait > 0:
                self._sleeper(wait)
        state.last_request_at = self._clock()


def _domain_of(url: str) -> str:
    return urlsplit(url).netloc.lower()
