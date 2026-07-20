"""The httpx transport behind the politeness engine's Transport protocol.

Plumbing only: no policy lives here. Redirects are followed (they are the
web's plumbing too); every request carries the honest User-Agent the engine
passes in.
"""

import httpx

from app.integrations.sources.politeness import TransportError, TransportResponse

_TIMEOUT_SECONDS = 20.0
_MAX_CONTENT_BYTES = 10 * 1024 * 1024  # a snapshot is a page, not an archive


class HttpxTransport:
    def __init__(self, *, basic_auth: tuple[str, str] | None = None) -> None:
        # e.g. the Companies House API authenticates with the key as username.
        self._basic_auth = basic_auth

    def get(self, url: str, *, user_agent: str) -> TransportResponse:
        try:
            response = httpx.get(
                url,
                headers={"User-Agent": user_agent},
                auth=self._basic_auth,
                timeout=_TIMEOUT_SECONDS,
                follow_redirects=True,
            )
        except httpx.HTTPError as exc:
            raise TransportError(str(exc)) from exc
        content = response.content[:_MAX_CONTENT_BYTES]
        return TransportResponse(
            status=response.status_code,
            content=content,
            content_type=response.headers.get("content-type", "application/octet-stream"),
        )
