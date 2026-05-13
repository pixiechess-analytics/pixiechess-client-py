"""Resource builders — one accessor per logical PixieChess endpoint group.

Mirrors `pixiechess-client-rs/src/resources/`.
"""

from .auctions import AuctionsResource
from .games import GamesResource
from .leaderboard import LeaderboardResource
from .misc import MiscResource
from .pieces import PiecesResource
from .ranks import RanksResource
from .tournaments import TournamentsResource
from .users import UsersResource

__all__ = [
    "AuctionsResource",
    "GamesResource",
    "LeaderboardResource",
    "MiscResource",
    "PiecesResource",
    "RanksResource",
    "TournamentsResource",
    "UsersResource",
]
