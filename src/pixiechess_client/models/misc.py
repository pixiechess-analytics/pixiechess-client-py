"""Miscellaneous models: public config, live-feed events, ETH/USD price."""

from datetime import datetime
from typing import Any

from pydantic import Field

from .common import CamelModel


class EthUsdPrice(CamelModel):
    """Current ETH/USD spot price returned by ``GET /eth-usd-price``."""

    usd: float


class PublicConfig(CamelModel):
    """Public configuration flags from ``GET /config/public``."""

    open_to_all: bool


class LiveFeedEvent(CamelModel):
    """One event from ``GET /live-feed``.

    The ``data`` payload is opaque (``dict[str, Any]``) since shape varies
    by event ``type``.
    """

    id: str = Field(alias="_id")
    type_: str = Field(alias="type")
    data: dict[str, Any]
    created_at: datetime
