"""Tournament-related models.

Mirrors `pixiechess-client-rs/src/models/tournaments.rs`. Field-level
required/optional shape matches the Rust client's two-round audit.
"""

from datetime import datetime
from typing import Any

from pydantic import Field

from .common import CamelModel, Helmet


class TournamentImages(CamelModel):
    """Image URLs attached to a tournament listing."""

    trophy: str | None = None
    title_card: str | None = None
    title_card_centered: str | None = None
    artwork: str | None = None
    artwork_cropped: str | None = None
    artwork_mobile: str | None = None


class TournamentColors(CamelModel):
    """Theming colors attached to a tournament listing."""

    primary: str
    secondary: str
    gradient: str
    gradient_button: bool = False


class TournamentUserInfo(CamelModel):
    """One registered (or pending-registration) player's snapshot on a
    tournament.

    ``username`` is ~98% present (a small fraction of accounts emit
    `_id` + helmet without it). Burn-related fields (``burn_initiated_at``,
    ``pending_burn_tx_hash{,es}``, ``drop_reason``, ``dropped_at_start``)
    appear only on entries actively going through a burn-and-confirm flow.
    """

    user_id: str
    username_display: str
    helmet: Helmet
    expires: int
    chosen_pieces: list[str] = []
    free_piece_keys: list[str] = []
    pending_burn_asset_ids: list[Any] = []

    username: str | None = None
    confirmed_entry_tx_hash: str | None = None
    signup_at: int | None = None
    burn_initiated_at: int | None = None
    pending_burn_tx_hash: str | None = None
    pending_burn_tx_hashes: list[str] = []
    drop_reason: str | None = None
    dropped_at_start: bool | None = None


class BurnRuleset(CamelModel):
    """Burn ruleset for a tournament."""

    min: int
    max: int
    exclusive_pieces: list[str] = []
    exclusive_piece_types: list[str] = []
    banned_pieces: list[str] = []
    banned_piece_types: list[str] = []


class SubstitutionRule(CamelModel):
    """Substitution rule for a gameplay ruleset."""

    min: int
    max: int


class GameplayRuleset(CamelModel):
    """Gameplay ruleset attached to a tournament."""

    substitution: SubstitutionRule | None = None


class TournamentRuleset(CamelModel):
    """Full ruleset for a tournament."""

    burn: BurnRuleset | None = None
    gameplay: GameplayRuleset | None = None


class NotificationStatus(CamelModel):
    """UI notification state for a tournament."""

    registration_soon: bool = False
    registration_open: bool = False
    starting_soon_for: list[str] = []
    starting_now: bool = False


class PayoutSplit(CamelModel):
    """One placement entry in a tournament's payout split."""

    placement: int
    percentage: float


class MatchupSource(CamelModel):
    """Pointer to a parent matchup in the tournament bracket."""

    round: int
    position: int
    id: str | None = Field(default=None, alias="_id")


class SourceMatches(CamelModel):
    """Bracket parents for a matchup. The whole block is ``null`` on
    first-round entries; individual ``top``/``bottom`` can also be null
    when a parent slot has no source (e.g. a bye).
    """

    top: MatchupSource | None = None
    bottom: MatchupSource | None = None
    id: str | None = Field(default=None, alias="_id")


class MatchupEntry(CamelModel):
    """One bracket cell in :attr:`Tournament.matchups_by_round`."""

    id: str = Field(alias="_id")
    user_ids: list[str]
    game_id: str | None = None
    winner_id: str
    round: int
    match_position: int
    source_matches: SourceMatches | None = None
    rematch_count: int
    draw: bool | None = None


class Tournament(CamelModel):
    """A single tournament. Used by both ``GET /tournament/list`` (row
    projection) and ``GET /tournament/details/{id}.data`` (full record).
    Intersection fields are required; per-endpoint extras are optional.
    """

    id: str | None = Field(default=None, alias="_id")
    tournament_id: str
    registration_opens: int
    start_time: int
    name: str
    description: str
    images: TournamentImages
    colors: TournamentColors
    slots: int
    pinned: bool
    prize_amount: float
    prize_currency: str
    status: str
    created_at: datetime

    # Details-only fields
    preset: str | None = None
    test: bool = False
    test_pieces: list[str] = []
    enable_free_pieces: bool = False
    free_piece_keys: list[str] = []
    game_duration_ms: int | None = None
    piece_selection_timeout_ms: int | None = None
    rematch_duration_ms: int | None = None
    additional_rematch_duration_ms: int | None = None
    schedule_id: str | None = None
    schedule_position: int | None = None
    user_infos: list[TournamentUserInfo] = []
    matchups_by_round: list[list[MatchupEntry]] = []
    ruleset: TournamentRuleset | None = None
    notification_status: NotificationStatus | None = None
    payout_mode: str | None = None
    payout_splits: list[PayoutSplit] = []
    payout_skipped_players: list[str] = []
    updated_at: datetime | None = None
    has_play_in_round: bool = False
    winner_id: str | None = None
    payout_status: str | None = None
    payout_total_eth: float | None = None
    payout_started_at: int | None = None
    payout_completed_at: int | None = None
    is_free_tournament: bool = False
    hidden: bool = False

    # List-only fields
    user_infos_count: int | None = None
    confirmed_entries_count: int | None = None


class GameTimingPlayer(CamelModel):
    """One player's per-game timing."""

    user_id: str
    turn_start_time: int | None = None
    elapsed: int
    status: str | None = None


class GameTiming(CamelModel):
    """Per-game timing attached to :class:`TournamentDetails`."""

    id: str = Field(alias="_id")
    game_id: str
    duration_ms: int
    players: list[GameTimingPlayer]
    move_deadline: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TournamentDetails(CamelModel):
    """``GET /tournament/details/{tournament_id}`` payload."""

    data: Tournament
    game_timings: dict[str, GameTiming] = {}
    game_player_ids: dict[str, dict[str, str]] = {}
    game_statuses: dict[str, str] = {}


class TournamentList(CamelModel):
    """``GET /tournament/list`` paged response."""

    total_count: int
    tournaments: list[Tournament]


class WaitlistEntry(CamelModel):
    """One row from ``GET /tournament/waitlist/{tournament_id}``."""

    id: str = Field(alias="_id")
    tournament_id: str
    address: str
    has_been_attempted: bool = False
    created_at: datetime
    updated_at: datetime | None = None
