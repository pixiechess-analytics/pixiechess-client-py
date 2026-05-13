"""Tests for the public client entry point."""

import httpx
import respx

from pixiechess_client import DEFAULT_USER_AGENT, PixieChessClient

BASE = "https://api.pixiechess.xyz"


async def test_client_acts_as_async_context_manager() -> None:
    async with PixieChessClient() as c:
        assert c is not None


async def test_default_construction_does_not_raise() -> None:
    c = PixieChessClient()
    await c.aclose()


@respx.mock
async def test_default_user_agent_reaches_the_wire_through_public_client() -> None:
    # /config/public is the simplest endpoint; we don't model it yet, but
    # the HTTP layer is callable through the private handle so we can
    # round-trip a request and inspect the headers respx captured.
    route = respx.get(f"{BASE}/config/public").mock(
        return_value=httpx.Response(200, json={"openToAll": True})
    )
    async with PixieChessClient() as c:
        await c._http.get_json("/config/public")
    assert route.calls.last.request.headers["user-agent"] == DEFAULT_USER_AGENT


@respx.mock
async def test_custom_user_agent_overrides_default_through_public_client() -> None:
    route = respx.get(f"{BASE}/config/public").mock(
        return_value=httpx.Response(200, json={"openToAll": True})
    )
    async with PixieChessClient(user_agent="my-app/1.0") as c:
        await c._http.get_json("/config/public")
    assert route.calls.last.request.headers["user-agent"] == "my-app/1.0"


@respx.mock
async def test_custom_base_url_is_honored() -> None:
    other_base = "https://staging.example.com"
    route = respx.get(f"{other_base}/config/public").mock(
        return_value=httpx.Response(200, json={"openToAll": True})
    )
    async with PixieChessClient(base_url=other_base) as c:
        await c._http.get_json("/config/public")
    assert route.called
