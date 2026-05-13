"""Game models — single-game state plus the per-player rating delta."""

from datetime import datetime
from typing import Any

from pydantic import Field

from .common import CamelModel, ResponseMeta


class GameEnding(CamelModel):
    """Inner block on a finished game describing how it ended."""

    piece_key: str | None = None


class GameResult(CamelModel):
    """Result block on a finished game."""

    code: str
    winner: int
    piece_key: str | None = None
    winner_id: str
    ending: GameEnding | None = None


class Game(CamelModel):
    """Single-game state, returned by ``GET /game/{gameId}``.

    ``board`` and ``players`` are kept as open ``dict`` / ``list[dict]``:
    ``board`` is a full chess game-state document (move history, FEN,
    draw offers, piece-mapping, …) and ``players`` carries per-side
    runtime state whose schema varies between in-progress and finished
    games.
    """

    id: str = Field(alias="_id")
    game_id: str
    board: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    players: list[dict[str, Any]] | None = None
    player_ids: dict[str, str] = {}
    player_statuses: dict[str, bool] = {}
    tournament_id: str | None = None
    status: str | None = None
    result: GameResult | None = None
    rated: bool = False
    spectator_limit: int | None = None
    game_duration_ms: int | None = None
    piece_selection_timeout_ms: int | None = None
    piece_selection_start_time: int | None = None
    finished_at: int | None = None
    """Unix-milliseconds timestamp; the server emits this as a raw integer,
    not an RFC-3339 string like ``created_at`` / ``updated_at``."""
    rematch_declined: bool | None = None
    """Only set when the server flips it; absent on most rows."""
    backfilled_early_resign: bool | None = None
    """Set on games where the resign was reconciled offline by a backfill
    job. ~13% of finished games in the captured sample."""
    meta: ResponseMeta | None = None


class RatingChange(CamelModel):
    """Response from ``GET /game/{gameId}/rating/{address}`` — the rating
    delta for a single player on a single game.
    """

    rated: bool
    rating_before: float | None = None
    rating_after: float | None = None
    change: float | None = None
    meta: ResponseMeta | None = None
