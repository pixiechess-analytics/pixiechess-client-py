"""Piece (NFT) models — owned pieces, burned-piece records, and shared
metadata/attribute shapes.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .common import CamelModel, ResponseMeta


class PieceAttribute(BaseModel):
    """One attribute on a piece. ``value`` is open-shape (str / int / float)
    so it's kept as ``Any``.

    Unlike most models in this crate, ``trait_type`` is ``snake_case`` on
    the wire too (NFT metadata convention), so this model deliberately
    keeps ``snake_case`` field names without ``to_camel`` aliasing.
    """

    model_config = ConfigDict(extra="ignore")

    trait_type: str
    value: Any


class PieceMetadata(CamelModel):
    """NFT-style metadata block on a piece."""

    name: str | None = None
    image: str | None = None
    animation_url: str | None = None
    description: str | None = None
    attributes: list[PieceAttribute] = []


class BurnedTournament(CamelModel):
    """Tournament context attached to a burned piece.

    ``name`` and ``color`` are always present; ``tournament_id`` is absent
    on burns not tied to a tournament redemption (~32% of burned rows).
    """

    tournament_id: str | None = None
    name: str
    color: str


class BurnedInfo(CamelModel):
    """Burn record attached to a piece. ``time`` is the Unix-ish timestamp;
    ``tournament`` is always present on burned-piece rows.
    """

    time: int
    tournament: BurnedTournament


class Piece(CamelModel):
    """A single piece (NFT). Shared shape for ``/pieces/{address}`` and
    ``/burned-pieces/{address}``; the per-endpoint extras stay optional.
    """

    id: str = Field(alias="_id")
    collection_address: str
    token_id: int
    owner: str
    metadata: PieceMetadata | None = None
    last_transfer_block_number: int
    created_at: datetime
    updated_at: datetime

    count: int | None = None
    """Live pieces with ``grouped=true`` carry the number of duplicate
    tokens collapsed into this row. Absent on burned pieces."""
    burned: BurnedInfo | None = None
    """Set on burned-pieces rows; absent on live pieces."""
    original_asset_id: str | None = None
    """Set on burned-pieces rows; absent on live pieces."""


class PiecesPage(CamelModel):
    """One page of ``GET /pieces/{address}`` or ``GET /burned-pieces/{address}``."""

    pieces: list[Piece]
    total_pages: int
    current_page: int
    total_count: int
    meta: ResponseMeta | None = Field(default=None, alias="_meta")
