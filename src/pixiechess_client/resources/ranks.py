"""Ranks endpoint group (``GET /ranks/masters``)."""

from typing import Any

from .._http import HttpClient


class RanksResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def masters(self) -> "MastersBuilder":
        return MastersBuilder(self._http)


class MastersBuilder:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def send(self) -> list[str]:
        data = await self._http.get_json("/ranks/masters")
        return list(data.get("addresses", []))

    async def raw(self) -> Any:
        return await self._http.get_json("/ranks/masters")
