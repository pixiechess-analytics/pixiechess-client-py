"""Auction-related models.

Mirrors `pixiechess-client-rs/src/models/auctions.rs`.
"""

from datetime import date, datetime

from pydantic import Field, field_validator

from .common import CamelModel, ResponseMeta, date_dict_validator


class AuctionMetadata(CamelModel):
    """Piece-key + sub-key identifiers attached to an auction."""

    piece_key: str
    sub_key: str


class Auction(CamelModel):
    """Active or scheduled auction. ``GET /auction/{address}`` returns the
    ``auction`` field of the ``{auction: ...}`` envelope.
    """

    id: str = Field(alias="_id")
    address: str
    created_at: datetime
    updated_at: datetime
    end_time: int
    start_time: int
    metadata: AuctionMetadata
    type_: str = Field(alias="type")
    last_mint_price_in_wei: str | None = None


class PastAuction(CamelModel):
    """Finished auction returned under ``/auctions/past``."""

    id: str = Field(alias="_id")
    address: str
    created_at: datetime
    end_time: int
    start_time: int
    metadata: AuctionMetadata
    type_: str = Field(alias="type")
    updated_at: datetime | None = None
    last_mint_price_in_wei: str | None = None

    end_date: date | None = None
    """Decoded from the server's ``"MM/DD"`` string; year defaults to the
    current calendar year (mirrors the Rust validator)."""
    final_price: str | None = None

    @field_validator("end_date", mode="before")
    @classmethod
    def _md_date(cls, v: object) -> date | None:
        if v is None or isinstance(v, date):
            return v if isinstance(v, date) else None
        if isinstance(v, str):
            month_s, _, day_s = v.partition("/")
            month, day = int(month_s), int(day_s)
            year = datetime.now().year
            return date(year, month, day)
        raise ValueError(f"expected 'MM/DD' string, got {v!r}")


class AuctionPieceInfo(CamelModel):
    """``GET /auctions/piece/{piece_key}`` summary."""

    piece_key: str
    has_auction_history: bool
    total_units_sold: int
    most_recent_past_auction: PastAuction | None = None
    meta: ResponseMeta | None = Field(default=None, alias="_meta")


class VrgdaPrice(CamelModel):
    """One row from the VRGDA price block returned by ``/prices``."""

    address: str
    price: str
    total_sold: int
    max_mints: int
    price_trend: str | None = None


class InstantMintPrice(CamelModel):
    """Instant-mint price block on ``/prices`` (optional)."""

    address: str
    price: str
    total_sold: int
    max_mints: int
    price_trend: str | None = None


class AuctionDaySummary(CamelModel):
    """``GET /auctions/today-summary``."""

    pieces_sold: int
    total_sales_eth: float


class CompletedDaySummary(CamelModel):
    """``GET /auctions/last-completed-day-summary``."""

    date: date
    total_eth: float
    pieces_sold: int
    eth_change_percent: float

    _v_date = date_dict_validator("date")


class DailyVolume(CamelModel):
    """One day-row from ``/auctions/daily-volume`` or
    ``/auctions/piece/{piece_key}/daily-volume``.
    """

    date: date
    pieces_sold: int
    total_eth: float

    _v_date = date_dict_validator("date")


class Prices(CamelModel):
    """``GET /prices`` — current pricing snapshot."""

    vrgda: list[VrgdaPrice]
    instant_mint: InstantMintPrice | None = None
    poll_interval_ms: int


class SalesStats(CamelModel):
    """Aggregate stats attached to a :class:`PastDayBucket`."""

    pieces_sold: int
    total_eth_volume: float
    lowest_price: float
    highest_price: float


class PastAuctionEntry(CamelModel):
    """One past-auction row inside a day bucket."""

    id: str = Field(alias="_id")
    address: str
    end_time: int
    start_time: int
    metadata: AuctionMetadata
    type_: str = Field(alias="type")
    date_obj: datetime
    sales_stats: SalesStats


class PastDayBucket(CamelModel):
    """One day-bucket inside :class:`PastAuctionsPage`. The server
    sometimes sends the date under ``_id`` instead of ``date``; both are
    accepted via the alias-from-validator.
    """

    date: date
    auctions: list[PastAuctionEntry]

    @field_validator("date", mode="before")
    @classmethod
    def _from_id_or_date(cls, v: object) -> date | dict:
        # `_id` is preferred when present; serde-style alias.
        if isinstance(v, dict):
            return v
        if isinstance(v, date):
            return v
        raise ValueError(f"expected {{year, month, day}}, got {v!r}")

    _v_date = date_dict_validator("date")


class PastAuctionsPage(CamelModel):
    """``GET /auctions/past`` paged response."""

    page: int
    page_size: int
    total_day_groups: int
    total_pages: int
    total_count: int
    day_buckets: list[PastDayBucket]
