"""Tests for the private HTTP layer."""

import httpx
import pytest
import respx

from pixiechess_client._http import DEFAULT_USER_AGENT, HttpClient
from pixiechess_client.errors import ApiError, DecodeError, NotFoundError

BASE = "https://api.pixiechess.xyz"


@respx.mock
async def test_get_json_returns_parsed_body() -> None:
    respx.get(f"{BASE}/users/42").mock(
        return_value=httpx.Response(200, json={"id": 42, "name": "alice"})
    )
    async with HttpClient() as c:
        v = await c.get_json("/users/42")
    assert v == {"id": 42, "name": "alice"}


@respx.mock
async def test_get_json_attaches_query_params() -> None:
    route = respx.get(f"{BASE}/leaderboard").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    async with HttpClient() as c:
        v = await c.get_json("/leaderboard", params={"page": "2", "pageSize": "25"})
    assert v == {"ok": True}
    assert route.called
    # respx records the actual request URL.
    sent_url = route.calls.last.request.url
    assert sent_url.params["page"] == "2"
    assert sent_url.params["pageSize"] == "25"


@respx.mock
async def test_404_maps_to_not_found_error() -> None:
    respx.get(f"{BASE}/missing").mock(return_value=httpx.Response(404, text="not here"))
    async with HttpClient() as c:
        with pytest.raises(NotFoundError) as info:
            await c.get_json("/missing")
    assert "not here" in info.value.body


@respx.mock
async def test_500_maps_to_api_error() -> None:
    respx.get(f"{BASE}/broken").mock(return_value=httpx.Response(500, text="boom"))
    async with HttpClient() as c:
        with pytest.raises(ApiError) as info:
            await c.get_json("/broken")
    assert info.value.status == 500
    assert "boom" in info.value.message


@respx.mock
async def test_non_json_2xx_maps_to_decode_error() -> None:
    respx.get(f"{BASE}/garbage").mock(return_value=httpx.Response(200, text="not json {{{"))
    async with HttpClient() as c:
        with pytest.raises(DecodeError):
            await c.get_json("/garbage")


@respx.mock
async def test_default_user_agent_reaches_the_wire() -> None:
    route = respx.get(f"{BASE}/ua").mock(return_value=httpx.Response(200, json={}))
    async with HttpClient() as c:
        await c.get_json("/ua")
    assert route.calls.last.request.headers["user-agent"] == DEFAULT_USER_AGENT


@respx.mock
async def test_custom_user_agent_overrides_default() -> None:
    route = respx.get(f"{BASE}/ua").mock(return_value=httpx.Response(200, json={}))
    async with HttpClient(user_agent="my-app/1.0") as c:
        await c.get_json("/ua")
    assert route.calls.last.request.headers["user-agent"] == "my-app/1.0"


@respx.mock
async def test_origin_and_referer_baked_in() -> None:
    route = respx.get(f"{BASE}/ping").mock(return_value=httpx.Response(200, json={}))
    async with HttpClient() as c:
        await c.get_json("/ping")
    headers = route.calls.last.request.headers
    assert headers["origin"] == "https://www.pixiechess.xyz"
    assert headers["referer"] == "https://www.pixiechess.xyz/"
