"""Request-context middleware (Doc 08 §9).

Assigns a request ID to every HTTP request, binds it to the logging context so
every log line in the request carries it, and returns it as `X-Request-ID` so
customer reports can be correlated with logs. Pure ASGI — no response
buffering.
"""

from uuid import uuid4

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import bind_log_context, clear_log_context

REQUEST_ID_HEADER = b"x-request-id"


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        request_id = uuid4().hex
        clear_log_context()
        bind_log_context(request_id=request_id)

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((REQUEST_ID_HEADER, request_id.encode()))
                message = {**message, "headers": headers}
            await send(message)

        try:
            await self._app(scope, receive, send_with_request_id)
        finally:
            clear_log_context()
