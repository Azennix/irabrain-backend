from starlette.responses import JSONResponse


MAX_REQUEST_BODY_BYTES = 20 * 1024 * 1024


class RequestBodyTooLarge(Exception):
    """Raised when a request body exceeds the configured size limit."""


class RequestSizeLimitMiddleware:
    """
    Limits HTTP request-body sizes.

    Checks Content-Length when provided and also counts streamed body
    bytes so requests without Content-Length cannot bypass the limit.
    """

    def __init__(
        self,
        app,
        max_body_size: int = MAX_REQUEST_BODY_BYTES,
    ):
        if not isinstance(max_body_size, int) or max_body_size <= 0:
            raise ValueError("max_body_size must be a positive integer.")

        self.app = app
        self.max_body_size = max_body_size

    def _too_large_response(self):
        limit_bytes = self.max_body_size

        if limit_bytes >= 1024 * 1024:
            limit_text = f"{limit_bytes / (1024 * 1024):g} MiB"
        elif limit_bytes >= 1024:
            limit_text = f"{limit_bytes / 1024:g} KiB"
        else:
            limit_text = f"{limit_bytes} bytes"

        return JSONResponse(
            status_code=413,
            content={
                "detail": (
                    f"Request body exceeds the {limit_text} limit."
                )
            },
        )

    @staticmethod
    def _bad_content_length_response():
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Invalid Content-Length header."
            },
        )

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        content_length = headers.get(b"content-length")

        if content_length is not None:
            try:
                declared_size = int(content_length)
            except (ValueError, TypeError):
                response = self._bad_content_length_response()
                await response(scope, receive, send)
                return

            if declared_size < 0:
                response = self._bad_content_length_response()
                await response(scope, receive, send)
                return

            if declared_size > self.max_body_size:
                response = self._too_large_response()
                await response(scope, receive, send)
                return

        received_bytes = 0
        response_started = False

        async def limited_receive():
            nonlocal received_bytes

            message = await receive()

            if message["type"] == "http.request":
                received_bytes += len(message.get("body", b""))

                if received_bytes > self.max_body_size:
                    raise RequestBodyTooLarge()

            return message

        async def tracked_send(message):
            nonlocal response_started

            if message["type"] == "http.response.start":
                response_started = True

            await send(message)

        try:
            await self.app(scope, limited_receive, tracked_send)

        except RequestBodyTooLarge:
            # Once response headers have been sent, we cannot replace the
            # response with a 413. Re-raise rather than attempting a second
            # response or corrupting the ASGI response stream.
            if response_started:
                raise

            response = self._too_large_response()
            await response(scope, receive, send)