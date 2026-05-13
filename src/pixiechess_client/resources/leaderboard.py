"""Leaderboard endpoints — ``GET /leaderboard`` and ``GET /points-leaderboard``.

The rating-leaderboard page size is server-pinned at 15 and not configurable.
"""

from collections.abc import AsyncIterator
from typing import Any

from .._http import HttpClient
from ..models.leaderboard import (
    LeaderboardEntry,
    LeaderboardPage,
    PointsLeaderboardEntry,
    PointsLeaderboardPage,
)


class LeaderboardResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get(self) -> "LeaderboardGetBuilder":
        """``GET /leaderboard`` — server pins page size at 15."""
        return LeaderboardGetBuilder(self._http)

    def iter(self) -> "LeaderboardIterBuilder":
        return LeaderboardIterBuilder(self._http)

    def points(self) -> "PointsGetBuilder":
        """``GET /points-leaderboard``."""
        return PointsGetBuilder(self._http)

    def points_iter(self) -> "PointsIterBuilder":
        return PointsIterBuilder(self._http)


class LeaderboardGetBuilder:
    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self._page = 1

    def page(self, n: int) -> "LeaderboardGetBuilder":
        self._page = n
        return self

    def _params(self) -> dict[str, str]:
        return {"page": str(self._page)}

    async def send(self) -> LeaderboardPage:
        data = await self._http.get_json("/leaderboard", params=self._params())
        return LeaderboardPage.model_validate(data)

    async def raw(self) -> Any:
        return await self._http.get_json("/leaderboard", params=self._params())


class LeaderboardIterBuilder:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def send(self) -> AsyncIterator[LeaderboardEntry]:
        return self._stream()

    async def _stream(self) -> AsyncIterator[LeaderboardEntry]:
        page = 1
        while True:
            data = await self._http.get_json("/leaderboard", params={"page": str(page)})
            page_model = LeaderboardPage.model_validate(data)
            if not page_model.entries:
                return
            for e in page_model.entries:
                yield e
            if page >= page_model.total_pages:
                return
            page += 1


class PointsGetBuilder:
    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self._page = 1

    def page(self, n: int) -> "PointsGetBuilder":
        self._page = n
        return self

    async def send(self) -> PointsLeaderboardPage:
        data = await self._http.get_json("/points-leaderboard", params={"page": str(self._page)})
        return PointsLeaderboardPage.model_validate(data)

    async def raw(self) -> Any:
        return await self._http.get_json("/points-leaderboard", params={"page": str(self._page)})


class PointsIterBuilder:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def send(self) -> AsyncIterator[PointsLeaderboardEntry]:
        return self._stream()

    async def _stream(self) -> AsyncIterator[PointsLeaderboardEntry]:
        page = 1
        while True:
            data = await self._http.get_json("/points-leaderboard", params={"page": str(page)})
            page_model = PointsLeaderboardPage.model_validate(data)
            if not page_model.entries:
                return
            for e in page_model.entries:
                yield e
            if page >= page_model.total_pages:
                return
            page += 1
