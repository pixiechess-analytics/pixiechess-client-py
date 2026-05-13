"""Entry point for the PixieChess client."""

from types import TracebackType

from ._http import DEFAULT_BASE_URL, DEFAULT_USER_AGENT, HttpClient
from .resources.auctions import AuctionsResource
from .resources.games import GamesResource
from .resources.leaderboard import LeaderboardResource
from .resources.misc import MiscResource
from .resources.pieces import PiecesResource
from .resources.ranks import RanksResource
from .resources.tournaments import TournamentsResource
from .resources.users import UsersResource


class PixieChessClient:
    """Async client for ``api.pixiechess.xyz``.

    Use as an async context manager so the underlying :class:`httpx.AsyncClient`
    gets cleaned up::

        async with PixieChessClient() as client:
            ...

    The WAF rejects requests without browser-shaped ``User-Agent`` and
    same-site ``Origin``/``Referer``; the defaults are baked in. Pass
    ``user_agent=...`` to override — for self-identification, suffix the
    default rather than replacing it::

        PixieChessClient(user_agent=f"{DEFAULT_USER_AGENT} my-app/1.0")
    """

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        user_agent: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._http = HttpClient(base_url=base_url, user_agent=user_agent, timeout=timeout)

    async def aclose(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._http.aclose()

    def users(self) -> UsersResource:
        """User endpoints (``GET /user/{id}``, ``GET /user/match-history/{address}``)."""
        return UsersResource(self._http)

    def games(self) -> GamesResource:
        """Game endpoints (``GET /game/{gameId}``, rating-change)."""
        return GamesResource(self._http)

    def leaderboard(self) -> LeaderboardResource:
        """Leaderboard endpoints (rating + points; paged + streamed)."""
        return LeaderboardResource(self._http)

    def pieces(self) -> PiecesResource:
        """Piece endpoints (live + burned pieces for a wallet)."""
        return PiecesResource(self._http)

    def auctions(self) -> AuctionsResource:
        """Auction endpoints."""
        return AuctionsResource(self._http)

    def tournaments(self) -> TournamentsResource:
        """Tournament endpoints (list, details, waitlist)."""
        return TournamentsResource(self._http)

    def misc(self) -> MiscResource:
        """Misc endpoints (config, ETH/USD, vault balance, live feed)."""
        return MiscResource(self._http)

    def ranks(self) -> RanksResource:
        """Ranks endpoints (``GET /ranks/masters``)."""
        return RanksResource(self._http)

    async def __aenter__(self) -> "PixieChessClient":
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc: BaseException | None,
        _tb: TracebackType | None,
    ) -> None:
        await self.aclose()


__all__ = ["DEFAULT_USER_AGENT", "PixieChessClient"]
