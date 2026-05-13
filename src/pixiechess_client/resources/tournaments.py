"""Tournament endpoints.

``sort`` was verified silently ignored on the live API and isn't exposed.
"""

from typing import Any

from .._http import HttpClient
from ..models.tournaments import TournamentDetails, TournamentList, WaitlistEntry


class TournamentsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self) -> "TournamentsListBuilder":
        return TournamentsListBuilder(self._http)

    def details(self, tournament_id: str) -> "TournamentDetailsBuilder":
        return TournamentDetailsBuilder(self._http, tournament_id)

    def waitlist(self, tournament_id: str) -> "TournamentWaitlistBuilder":
        return TournamentWaitlistBuilder(self._http, tournament_id)


class TournamentsListBuilder:
    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self._limit = 10
        self._offset = 0
        self._pinned = False
        self._date_filter: str | None = None
        self._tz_offset: int | None = None
        self._active: bool | None = None

    def limit(self, n: int) -> "TournamentsListBuilder":
        self._limit = n
        return self

    def offset(self, n: int) -> "TournamentsListBuilder":
        self._offset = n
        return self

    def pinned(self, v: bool) -> "TournamentsListBuilder":
        self._pinned = v
        return self

    def date_filter(self, s: str) -> "TournamentsListBuilder":
        self._date_filter = s
        return self

    def tz_offset(self, n: int) -> "TournamentsListBuilder":
        self._tz_offset = n
        return self

    def active(self, v: bool) -> "TournamentsListBuilder":
        self._active = v
        return self

    def _params(self) -> dict[str, str]:
        p: dict[str, str] = {
            "limit": str(self._limit),
            "offset": str(self._offset),
            "pinned": str(self._pinned).lower(),
        }
        if self._date_filter is not None:
            p["dateFilter"] = self._date_filter
        if self._tz_offset is not None:
            p["tzOffset"] = str(self._tz_offset)
        if self._active is not None:
            p["active"] = str(self._active).lower()
        return p

    async def send(self) -> TournamentList:
        data = await self._http.get_json("/tournament/list", params=self._params())
        return TournamentList.model_validate(data)

    async def raw(self) -> Any:
        return await self._http.get_json("/tournament/list", params=self._params())


class TournamentDetailsBuilder:
    def __init__(self, http: HttpClient, tournament_id: str) -> None:
        self._http = http
        self._tournament_id = tournament_id

    def _path(self) -> str:
        return f"/tournament/details/{self._tournament_id}"

    async def send(self) -> TournamentDetails:
        data = await self._http.get_json(self._path())
        return TournamentDetails.model_validate(data)

    async def raw(self) -> Any:
        return await self._http.get_json(self._path())


class TournamentWaitlistBuilder:
    def __init__(self, http: HttpClient, tournament_id: str) -> None:
        self._http = http
        self._tournament_id = tournament_id

    def _path(self) -> str:
        return f"/tournament/waitlist/{self._tournament_id}"

    async def send(self) -> list[WaitlistEntry]:
        data = await self._http.get_json(self._path())
        return [WaitlistEntry.model_validate(e) for e in data]

    async def raw(self) -> Any:
        return await self._http.get_json(self._path())
