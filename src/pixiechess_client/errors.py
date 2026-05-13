"""Error hierarchy for the PixieChess client.

Mirrors `pixiechess-client-rs`'s `Error` enum:

- :class:`NotFoundError` — HTTP 404 from the upstream.
- :class:`ApiError` — Any other non-2xx HTTP status; carries ``status`` + ``message``.
- :class:`DecodeError` — Body was 2xx but didn't deserialize into the expected model.
- :class:`HttpError` — Transport-level failure (TLS, network, timeout).
"""


class PixieChessError(Exception):
    """Base class for every error this client raises."""


class NotFoundError(PixieChessError):
    """The upstream returned ``404 Not Found``."""

    def __init__(self, body: str = "") -> None:
        super().__init__(body)
        self.body = body


class ApiError(PixieChessError):
    """The upstream returned a non-2xx response other than 404."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.message = message


class DecodeError(PixieChessError):
    """The response body was 2xx but couldn't be parsed."""

    def __init__(self, source: Exception) -> None:
        super().__init__(str(source))
        self.source = source


class HttpError(PixieChessError):
    """Transport-level failure — connection refused, TLS error, timeout, etc."""

    def __init__(self, source: Exception) -> None:
        super().__init__(str(source))
        self.source = source
