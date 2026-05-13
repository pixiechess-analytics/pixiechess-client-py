"""User-related endpoints.

* ``GET /user/{identifier}`` — :meth:`UsersResource.get`
* ``GET /user/match-history/{address}`` — :meth:`UsersResource.match_history`
  (and the auto-paginating :meth:`UsersResource.match_history_iter`)
"""

from collections.abc import AsyncIterator
from typing import Any

from .._http import HttpClient
from ..models.user import MatchHistoryEntry, MatchHistoryPage, User


class UsersResource:
    """Builder factory for the user endpoints."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get(self, identifier: str) -> "UsersGetBuilder":
        """``GET /user/{id-or-address}`` — unwraps the ``{"user": ...}`` envelope."""
        return UsersGetBuilder(self._http, identifier)

    def match_history(self, address: str) -> "MatchHistoryBuilder":
        """``GET /user/match-history/{address}`` — paginated."""
        return MatchHistoryBuilder(self._http, address)

    def match_history_iter(self, address: str) -> "MatchHistoryIterBuilder":
        """Async-iter every match across all pages of
        ``GET /user/match-history/{address}``.
        """
        return MatchHistoryIterBuilder(self._http, address)


class UsersGetBuilder:
    """Builder for :meth:`UsersResource.get`."""

    def __init__(self, http: HttpClient, identifier: str) -> None:
        self._http = http
        self._identifier = identifier

    def _path(self) -> str:
        return f"/user/{self._identifier}"

    async def send(self) -> User:
        """Fetch and return the typed :class:`User`."""
        data = await self._http.get_json(self._path())
        return User.model_validate(data["user"])

    async def raw(self) -> Any:
        """Fetch the raw JSON (preserves the ``{"user": ...}`` envelope)."""
        return await self._http.get_json(self._path())


class MatchHistoryBuilder:
    """Builder for :meth:`UsersResource.match_history`."""

    def __init__(self, http: HttpClient, address: str) -> None:
        self._http = http
        self._address = address
        self._page = 1
        self._limit = 15

    def page(self, n: int) -> "MatchHistoryBuilder":
        self._page = n
        return self

    def limit(self, n: int) -> "MatchHistoryBuilder":
        self._limit = n
        return self

    def _path(self) -> str:
        return f"/user/match-history/{self._address}"

    def _params(self) -> dict[str, str]:
        return {"page": str(self._page), "limit": str(self._limit)}

    async def send(self) -> MatchHistoryPage:
        data = await self._http.get_json(self._path(), params=self._params())
        return MatchHistoryPage.model_validate(data)

    async def raw(self) -> Any:
        return await self._http.get_json(self._path(), params=self._params())


class MatchHistoryIterBuilder:
    """Builder for :meth:`UsersResource.match_history_iter`.

    ``.send()`` returns an async iterator yielding every
    :class:`MatchHistoryEntry` across every page. Iteration stops on the
    first empty page or when ``page > totalPages``.
    """

    def __init__(self, http: HttpClient, address: str) -> None:
        self._http = http
        self._address = address
        self._limit = 15

    def limit(self, n: int) -> "MatchHistoryIterBuilder":
        self._limit = n
        return self

    def send(self) -> AsyncIterator[MatchHistoryEntry]:
        return self._stream()

    async def _stream(self) -> AsyncIterator[MatchHistoryEntry]:
        page = 1
        while True:
            data = await self._http.get_json(
                f"/user/match-history/{self._address}",
                params={"page": str(page), "limit": str(self._limit)},
            )
            page_model = MatchHistoryPage.model_validate(data)
            if not page_model.matches:
                return
            for m in page_model.matches:
                yield m
            if page >= page_model.total_pages:
                return
            page += 1
