"""Auction-related endpoints."""

from typing import Any

from .._http import HttpClient
from ..models.auctions import (
    Auction,
    AuctionDaySummary,
    AuctionPieceInfo,
    CompletedDaySummary,
    DailyVolume,
    PastAuctionsPage,
    Prices,
)


class AuctionsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get(self, address: str) -> "AuctionsGetBuilder":
        return AuctionsGetBuilder(self._http, address)

    def active(self) -> "AuctionsActiveBuilder":
        return AuctionsActiveBuilder(self._http)

    def past(self) -> "AuctionsPastBuilder":
        return AuctionsPastBuilder(self._http)

    def piece_info(self, piece_key: str) -> "AuctionPieceInfoBuilder":
        return AuctionPieceInfoBuilder(self._http, piece_key)

    def piece_daily_volume(self, piece_key: str) -> "PieceDailyVolumeBuilder":
        return PieceDailyVolumeBuilder(self._http, piece_key)

    def daily_volume(self) -> "DailyVolumeBuilder":
        return DailyVolumeBuilder(self._http)

    def today_summary(self) -> "TodaySummaryBuilder":
        return TodaySummaryBuilder(self._http)

    def last_completed_day_summary(self) -> "LastCompletedDayBuilder":
        return LastCompletedDayBuilder(self._http)

    def prices(self) -> "PricesBuilder":
        return PricesBuilder(self._http)


class AuctionsGetBuilder:
    def __init__(self, http: HttpClient, address: str) -> None:
        self._http = http
        self._address = address

    def _path(self) -> str:
        return f"/auction/{self._address}"

    async def send(self) -> Auction:
        data = await self._http.get_json(self._path())
        return Auction.model_validate(data["auction"])

    async def raw(self) -> Any:
        return await self._http.get_json(self._path())


class AuctionsActiveBuilder:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def send(self) -> list[Auction]:
        data = await self._http.get_json("/auctions/active")
        return [Auction.model_validate(a) for a in data.get("auctions", [])]

    async def raw(self) -> Any:
        return await self._http.get_json("/auctions/active")


class AuctionsPastBuilder:
    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self._page = 1
        self._page_size: int | None = None

    def page(self, n: int) -> "AuctionsPastBuilder":
        self._page = n
        return self

    def page_size(self, n: int) -> "AuctionsPastBuilder":
        self._page_size = n
        return self

    def _params(self) -> dict[str, str]:
        p: dict[str, str] = {"page": str(self._page)}
        if self._page_size is not None:
            p["pageSize"] = str(self._page_size)
        return p

    async def send(self) -> PastAuctionsPage:
        data = await self._http.get_json("/auctions/past", params=self._params())
        return PastAuctionsPage.model_validate(data)

    async def raw(self) -> Any:
        return await self._http.get_json("/auctions/past", params=self._params())


class AuctionPieceInfoBuilder:
    def __init__(self, http: HttpClient, piece_key: str) -> None:
        self._http = http
        self._piece_key = piece_key

    def _path(self) -> str:
        return f"/auctions/piece/{self._piece_key}"

    async def send(self) -> AuctionPieceInfo:
        data = await self._http.get_json(self._path())
        return AuctionPieceInfo.model_validate(data)

    async def raw(self) -> Any:
        return await self._http.get_json(self._path())


class PieceDailyVolumeBuilder:
    def __init__(self, http: HttpClient, piece_key: str) -> None:
        self._http = http
        self._piece_key = piece_key
        self._range = "30d"

    def range(self, r: str) -> "PieceDailyVolumeBuilder":
        self._range = r
        return self

    def _path(self) -> str:
        return f"/auctions/piece/{self._piece_key}/daily-volume"

    async def send(self) -> list[DailyVolume]:
        data = await self._http.get_json(self._path(), params={"range": self._range})
        return [DailyVolume.model_validate(d) for d in data.get("days", [])]

    async def raw(self) -> Any:
        return await self._http.get_json(self._path(), params={"range": self._range})


class DailyVolumeBuilder:
    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self._range = "7d"

    def range(self, r: str) -> "DailyVolumeBuilder":
        self._range = r
        return self

    async def send(self) -> list[DailyVolume]:
        data = await self._http.get_json("/auctions/daily-volume", params={"range": self._range})
        return [DailyVolume.model_validate(d) for d in data.get("days", [])]

    async def raw(self) -> Any:
        return await self._http.get_json("/auctions/daily-volume", params={"range": self._range})


class TodaySummaryBuilder:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def send(self) -> AuctionDaySummary:
        data = await self._http.get_json("/auctions/today-summary")
        return AuctionDaySummary.model_validate(data)

    async def raw(self) -> Any:
        return await self._http.get_json("/auctions/today-summary")


class LastCompletedDayBuilder:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def send(self) -> CompletedDaySummary:
        data = await self._http.get_json("/auctions/last-completed-day-summary")
        return CompletedDaySummary.model_validate(data)

    async def raw(self) -> Any:
        return await self._http.get_json("/auctions/last-completed-day-summary")


class PricesBuilder:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def send(self) -> Prices:
        data = await self._http.get_json("/prices")
        return Prices.model_validate(data)

    async def raw(self) -> Any:
        return await self._http.get_json("/prices")
