"""Entry point for the PixieChess client."""

from types import TracebackType

from ._http import DEFAULT_BASE_URL, DEFAULT_USER_AGENT, HttpClient
from .resources.users import UsersResource


class PixieChessClient:
    """Async client for ``api.pixiechess.xyz``.

    Use as an async context manager so the underlying :class:`httpx.AsyncClient`
    gets cleaned up::

        async with PixieChessClient() as client:
            ...

    The WAF rejects requests without browser-shaped ``User-Agent`` and
    same-site ``Origin``/``Referer``; the defaults are baked in. Pass
    ``user_agent=...`` to override — for self-identification, suffix the
    default rather than replacing it::

        PixieChessClient(user_agent=f"{DEFAULT_USER_AGENT} my-app/1.0")
    """

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        user_agent: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._http = HttpClient(base_url=base_url, user_agent=user_agent, timeout=timeout)

    async def aclose(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._http.aclose()

    def users(self) -> UsersResource:
        """User endpoints (``GET /user/{id}``, ``GET /user/match-history/{address}``)."""
        return UsersResource(self._http)

    async def __aenter__(self) -> "PixieChessClient":
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc: BaseException | None,
        _tb: TracebackType | None,
    ) -> None:
        await self.aclose()


__all__ = ["DEFAULT_USER_AGENT", "PixieChessClient"]
