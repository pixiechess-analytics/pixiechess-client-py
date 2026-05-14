"""User profile + match history models."""

from datetime import datetime

from pydantic import Field

from .common import CamelModel, Helmet, PlayerInfo, ResponseMeta


class ColorRecord(CamelModel):
    """Per-color win/loss/draw tally on a :class:`User`."""

    wins: int = 0
    losses: int = 0
    draws: int = 0
    total: int = 0


class User(CamelModel):
    """Full user profile returned by ``GET /user/{identifier}`` (under the
    ``{"user": ...}`` envelope, which :class:`UsersResource.get` unwraps).

    All fields are required by the live API. If the server starts omitting
    or nulling one, decode fails loudly — that's intentional.
    """

    id: str = Field(alias="_id")
    address: str

    username: str | None = None
    username_display: str | None = None
    wallet_client_type: str | None = None
    helmet: Helmet | None = None
    last_login: datetime

    win_rate: int
    match_count: int
    wins: int
    losses: int
    draws: int
    casual_games: int
    streak: int
    color_record: dict[str, ColorRecord]
    trophies: int
    rating: float
    rd: float
    is_provisional: bool
    peak_rating: float
    rated_games_played: int
    genuine_games_played: int
    points: int


class MatchTiming(CamelModel):
    """Per-side timing on a single match entry."""

    white_elapsed_ms: int
    black_elapsed_ms: int
    clock_ms: int


class MatchHistoryEntry(CamelModel):
    """One row from ``GET /user/match-history/{address}``.

    ``tournament_id`` is present on tournament matches and absent on casual
    ones. ``rated`` and ``rating_change`` only appear on rated entries.
    ``winner`` is always emitted but null on draws.
    """

    game_id: str
    created_at: datetime
    white: PlayerInfo
    black: PlayerInfo

    tournament_id: str | None = None
    winner: str | None = None
    result_for_user: str
    outcome: str
    rated: bool | None = None
    rating_change: float | None = None
    timing: MatchTiming


class MatchHistoryPage(CamelModel):
    """Paged response from ``GET /user/match-history/{address}``."""

    matches: list[MatchHistoryEntry]
    total_pages: int
    current_page: int
    total_count: int
    meta: ResponseMeta | None = Field(default=None, alias="_meta")
