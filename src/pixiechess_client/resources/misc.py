"""Miscellaneous endpoints: config, vault balance, ETH/USD, live feed.

``since`` and ``type`` query params on ``/live-feed`` were verified
silently ignored on the live API and aren't exposed.
"""

from typing import Any

from .._http import HttpClient
from ..models.misc import EthUsdPrice, LiveFeedEvent, PublicConfig


class MiscResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def config(self) -> "ConfigBuilder":
        return ConfigBuilder(self._http)

    def eth_usd_price(self) -> "EthUsdPriceBuilder":
        return EthUsdPriceBuilder(self._http)

    def vault_balance(self) -> "VaultBalanceBuilder":
        return VaultBalanceBuilder(self._http)

    def live_feed(self) -> "LiveFeedBuilder":
        return LiveFeedBuilder(self._http)


class ConfigBuilder:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def send(self) -> PublicConfig:
        data = await self._http.get_json("/config/public")
        return PublicConfig.model_validate(data)

    async def raw(self) -> Any:
        return await self._http.get_json("/config/public")


class EthUsdPriceBuilder:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def send(self) -> EthUsdPrice:
        data = await self._http.get_json("/eth-usd-price")
        return EthUsdPrice.model_validate(data)

    async def raw(self) -> Any:
        return await self._http.get_json("/eth-usd-price")


class VaultBalanceBuilder:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def send(self) -> str:
        data = await self._http.get_json("/vault-balance")
        return data["balance"]

    async def raw(self) -> Any:
        return await self._http.get_json("/vault-balance")


class LiveFeedBuilder:
    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self._limit: int | None = None

    def limit(self, n: int) -> "LiveFeedBuilder":
        self._limit = n
        return self

    def _params(self) -> dict[str, str]:
        return {"limit": str(self._limit)} if self._limit is not None else {}

    async def send(self) -> list[LiveFeedEvent]:
        data = await self._http.get_json("/live-feed", params=self._params())
        return [LiveFeedEvent.model_validate(e) for e in data]

    async def raw(self) -> Any:
        return await self._http.get_json("/live-feed", params=self._params())
