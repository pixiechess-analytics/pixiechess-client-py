"""Game-related endpoints."""

from typing import Any

from .._http import HttpClient
from ..models.game import Game, RatingChange


class GamesResource:
    """Builder factory for the game endpoints."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get(self, game_id: str) -> "GamesGetBuilder":
        """``GET /game/{gameId}``."""
        return GamesGetBuilder(self._http, game_id)

    def rating_change(self, game_id: str, address: str) -> "GameRatingChangeBuilder":
        """``GET /game/{gameId}/rating/{address}``."""
        return GameRatingChangeBuilder(self._http, game_id, address)


class GamesGetBuilder:
    def __init__(self, http: HttpClient, game_id: str) -> None:
        self._http = http
        self._game_id = game_id

    def _path(self) -> str:
        return f"/game/{self._game_id}"

    async def send(self) -> Game:
        data = await self._http.get_json(self._path())
        return Game.model_validate(data)

    async def raw(self) -> Any:
        return await self._http.get_json(self._path())


class GameRatingChangeBuilder:
    def __init__(self, http: HttpClient, game_id: str, address: str) -> None:
        self._http = http
        self._game_id = game_id
        self._address = address

    def _path(self) -> str:
        return f"/game/{self._game_id}/rating/{self._address}"

    async def send(self) -> RatingChange:
        data = await self._http.get_json(self._path())
        return RatingChange.model_validate(data)

    async def raw(self) -> Any:
        return await self._http.get_json(self._path())
