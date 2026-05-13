"""Crate-private HTTP layer.

Wraps :class:`httpx.AsyncClient` with the same browser-mimicking headers the
Rust client uses (the upstream WAF rejects requests with a non-browser
``User-Agent`` — see :data:`DEFAULT_USER_AGENT`).

Consumers reach this through the resource builders, not directly.
"""

from typing import Any

import httpx

from .errors import ApiError, DecodeError, HttpError, NotFoundError

DEFAULT_BASE_URL = "https://api.pixiechess.xyz"

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
"""Default ``User-Agent`` sent on every request.

The upstream WAF returns a ``202`` empty-body challenge to non-browser-shaped
user agents, so the default mirrors a recent Chrome build. Override via
:meth:`pixiechess_client.PixieChessClient.builder` — but doing so on a UA the
WAF doesn't accept will start returning empty bodies. To identify your own
integration safely, suffix the default::

    PixieChessClient(user_agent=f"{DEFAULT_USER_AGENT} my-app/1.0")
"""


def _default_headers(user_agent: str) -> dict[str, str]:
    return {
        "Origin": "https://www.pixiechess.xyz",
        "Referer": "https://www.pixiechess.xyz/",
        "User-Agent": user_agent,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.8",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
    }


class HttpClient:
    """Async HTTP layer used by every resource builder.

    Not part of the public API — callers go through
    :class:`pixiechess_client.PixieChessClient`.
    """

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        user_agent: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        ua = user_agent or DEFAULT_USER_AGENT
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=_default_headers(ua),
            timeout=timeout,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "HttpClient":
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    async def get_json(self, path: str, *, params: dict[str, str] | None = None) -> Any:
        """Issue a GET and return the parsed JSON body.

        Raises :class:`NotFoundError`, :class:`ApiError`, :class:`HttpError`,
        or :class:`DecodeError` per the documented mapping.
        """
        try:
            resp = await self._client.get(path, params=params or None)
        except httpx.HTTPError as e:
            raise HttpError(e) from e
        return _handle_response(resp)


def _handle_response(resp: httpx.Response) -> Any:
    if resp.status_code == 404:
        raise NotFoundError(resp.text)
    if not resp.is_success:
        raise ApiError(resp.status_code, resp.text)
    try:
        return resp.json()
    except ValueError as e:
        raise DecodeError(e) from e
