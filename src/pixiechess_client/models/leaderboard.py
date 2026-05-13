"""Leaderboard models — main rating leaderboard and the points leaderboard."""

from typing import Any

from .common import CamelModel, Helmet


class LeaderboardEntry(CamelModel):
    """One row from ``GET /leaderboard``.

    ``current_game_id`` / ``current_game_player`` only appear on rows whose
    player is mid-match (~4% of captured rows).
    """

    rank: int
    address: str
    username: str
    username_display: str
    helmet: Helmet
    rating: float
    is_provisional: bool
    games_played: int
    genuine_games_played: int
    wins: int
    streak: int
    is_online: bool
    is_in_game: bool
    current_game_id: str | None = None
    current_game_player: int | None = None


class LeaderboardStats(CamelModel):
    """Page-level stats alongside the leaderboard entries."""

    total_ranked_players: int
    games_today: int
    active_now: int


class LeaderboardPage(CamelModel):
    """One page of ``GET /leaderboard``.

    ``current_user``'s shape varies with the caller's auth state — this
    client doesn't model the auth surface, so the field is intentionally
    kept as a raw ``dict``.
    """

    entries: list[LeaderboardEntry]
    total_count: int
    page: int
    total_pages: int
    current_user: dict[str, Any] | None = None
    stats: LeaderboardStats


class PointsLeaderboardEntry(CamelModel):
    """One row from ``GET /points-leaderboard``."""

    rank: int
    address: str
    username: str
    username_display: str
    helmet: Helmet
    total_points: int
    today: int
    this_week: int
    rank_change: int
    is_online: bool
    rating: float
    genuine_games_played: int


class PointsLeaderboardCurrentUser(CamelModel):
    """Compact ``current_user`` projection on ``GET /points-leaderboard``.

    Distinct shape from :class:`PointsLeaderboardEntry` — omits address,
    username, helmet, etc.
    """

    rank: int
    rank_change: int
    total_points: int
    today: int
    this_week: int


class PointsLeaderboardPage(CamelModel):
    """One page of ``GET /points-leaderboard``.

    ``current_user`` is only emitted on authenticated requests; absent
    otherwise.
    """

    entries: list[PointsLeaderboardEntry]
    total_count: int
    page: int
    total_pages: int
    current_user: PointsLeaderboardCurrentUser | None = None
