"""Piece endpoints — owned pieces (``/pieces/{address}``) and burned pieces
(``/burned-pieces/{address}``).
"""

from collections.abc import AsyncIterator
from typing import Any

from .._http import HttpClient
from ..models.pieces import Piece, PiecesPage


class PiecesResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get(self, address: str) -> "PiecesGetBuilder":
        """``GET /pieces/{address}``."""
        return PiecesGetBuilder(self._http, address, burned=False)

    def burned(self, address: str) -> "PiecesGetBuilder":
        """``GET /burned-pieces/{address}``."""
        return PiecesGetBuilder(self._http, address, burned=True)

    def iter(self, address: str) -> "PiecesIterBuilder":
        return PiecesIterBuilder(self._http, address, burned=False)

    def burned_iter(self, address: str) -> "PiecesIterBuilder":
        return PiecesIterBuilder(self._http, address, burned=True)


class PiecesGetBuilder:
    def __init__(self, http: HttpClient, address: str, *, burned: bool) -> None:
        self._http = http
        self._address = address
        self._burned = burned
        self._page = 1
        self._limit: int | None = None
        self._grouped = False

    def page(self, n: int) -> "PiecesGetBuilder":
        self._page = n
        return self

    def limit(self, n: int) -> "PiecesGetBuilder":
        self._limit = n
        return self

    def grouped(self, v: bool) -> "PiecesGetBuilder":
        self._grouped = v
        return self

    def _path(self) -> str:
        base = "burned-pieces" if self._burned else "pieces"
        return f"/{base}/{self._address}"

    def _params(self) -> dict[str, str]:
        p: dict[str, str] = {"page": str(self._page), "grouped": str(self._grouped).lower()}
        if self._limit is not None:
            p["limit"] = str(self._limit)
        return p

    async def send(self) -> PiecesPage:
        data = await self._http.get_json(self._path(), params=self._params())
        return PiecesPage.model_validate(data)

    async def raw(self) -> Any:
        return await self._http.get_json(self._path(), params=self._params())


class PiecesIterBuilder:
    def __init__(self, http: HttpClient, address: str, *, burned: bool) -> None:
        self._http = http
        self._address = address
        self._burned = burned
        self._limit: int | None = None
        self._grouped = False

    def limit(self, n: int) -> "PiecesIterBuilder":
        self._limit = n
        return self

    def grouped(self, v: bool) -> "PiecesIterBuilder":
        self._grouped = v
        return self

    def send(self) -> AsyncIterator[Piece]:
        return self._stream()

    async def _stream(self) -> AsyncIterator[Piece]:
        base = "burned-pieces" if self._burned else "pieces"
        path = f"/{base}/{self._address}"
        page = 1
        while True:
            params: dict[str, str] = {
                "page": str(page),
                "grouped": str(self._grouped).lower(),
            }
            if self._limit is not None:
                params["limit"] = str(self._limit)
            data = await self._http.get_json(path, params=params)
            page_model = PiecesPage.model_validate(data)
            if not page_model.pieces:
                return
            for p in page_model.pieces:
                yield p
            if page >= page_model.total_pages:
                return
            page += 1
