"""Wiremock-style tests for the users resource builders."""

import httpx
import respx

from pixiechess_client import PixieChessClient

BASE = "https://api.pixiechess.xyz"


def _user_payload() -> dict:
    """Full User JSON matching the live API (mirrors the corpus shape)."""
    return {
        "_id": "507f1f77bcf86cd799439011",
        "address": "0xabc",
        "username": "alice",
        "usernameDisplay": "Alice",
        "walletClientType": "metamask",
        "helmet": {"key": "knightmare", "color": "red"},
        "lastLogin": "2026-05-13T12:34:56Z",
        "winRate": 50,
        "matchCount": 10,
        "wins": 5,
        "losses": 4,
        "draws": 1,
        "casualGames": 2,
        "streak": 0,
        "colorRecord": {},
        "trophies": 0,
        "rating": 1500.0,
        "rd": 50.0,
        "isProvisional": False,
        "peakRating": 1600.0,
        "ratedGamesPlayed": 8,
        "genuineGamesPlayed": 8,
        "points": 100,
    }


def _player_info(addr: str, name: str) -> dict:
    return {
        "address": addr,
        "username": name,
        "usernameDisplay": name,
        "helmet": {"key": "knightmare", "color": "red"},
    }


def _match_entry(game_id: str) -> dict:
    return {
        "gameId": game_id,
        "createdAt": "2026-05-13T12:00:00Z",
        "white": _player_info("0xaaa", "alice"),
        "black": _player_info("0xbbb", "bob"),
        "tournamentId": "tournament_175_abc",
        "winner": "white",
        "resultForUser": "win",
        "outcome": "checkmate",
        "rated": True,
        "ratingChange": 12.5,
        "timing": {"whiteElapsedMs": 60_000, "blackElapsedMs": 58_000, "clockMs": 300_000},
    }


@respx.mock
async def test_users_get_unwraps_user_envelope() -> None:
    respx.get(f"{BASE}/user/alice").mock(
        return_value=httpx.Response(200, json={"user": _user_payload()})
    )
    async with PixieChessClient() as c:
        u = await c.users().get("alice").send()
    assert u.username == "alice"
    assert u.address == "0xabc"
    assert u.helmet is not None
    assert u.helmet.key == "knightmare"


@respx.mock
async def test_users_get_raw_keeps_envelope() -> None:
    respx.get(f"{BASE}/user/alice").mock(
        return_value=httpx.Response(200, json={"user": _user_payload()})
    )
    async with PixieChessClient() as c:
        raw = await c.users().get("alice").raw()
    assert raw["user"]["username"] == "alice"


@respx.mock
async def test_match_history_attaches_page_and_limit_params() -> None:
    route = respx.get(f"{BASE}/user/match-history/0xabc").mock(
        return_value=httpx.Response(
            200,
            json={
                "matches": [_match_entry("g1")],
                "totalPages": 4,
                "currentPage": 2,
                "totalCount": 50,
            },
        )
    )
    async with PixieChessClient() as c:
        page = await c.users().match_history("0xabc").page(2).limit(25).send()
    assert page.total_pages == 4
    assert len(page.matches) == 1
    assert page.matches[0].game_id == "g1"
    sent = route.calls.last.request.url
    assert sent.params["page"] == "2"
    assert sent.params["limit"] == "25"


@respx.mock
async def test_match_history_defaults_page_1_limit_15() -> None:
    route = respx.get(f"{BASE}/user/match-history/0xabc").mock(
        return_value=httpx.Response(
            200,
            json={"matches": [], "totalPages": 0, "currentPage": 1, "totalCount": 0},
        )
    )
    async with PixieChessClient() as c:
        await c.users().match_history("0xabc").send()
    sent = route.calls.last.request.url
    assert sent.params["page"] == "1"
    assert sent.params["limit"] == "15"


@respx.mock
async def test_match_history_iter_walks_pages_and_stops_on_empty() -> None:
    respx.get(f"{BASE}/user/match-history/0xabc", params={"page": "1", "limit": "15"}).mock(
        return_value=httpx.Response(
            200,
            json={
                "matches": [_match_entry("g1"), _match_entry("g2")],
                "totalPages": 2,
                "currentPage": 1,
                "totalCount": 4,
            },
        )
    )
    respx.get(f"{BASE}/user/match-history/0xabc", params={"page": "2", "limit": "15"}).mock(
        return_value=httpx.Response(
            200,
            json={"matches": [], "totalPages": 2, "currentPage": 2, "totalCount": 4},
        )
    )
    async with PixieChessClient() as c:
        collected = [m async for m in c.users().match_history_iter("0xabc").send()]
    assert [m.game_id for m in collected] == ["g1", "g2"]


@respx.mock
async def test_match_history_iter_stops_at_total_pages() -> None:
    respx.get(f"{BASE}/user/match-history/0xabc", params={"page": "1", "limit": "15"}).mock(
        return_value=httpx.Response(
            200,
            json={
                "matches": [_match_entry("g1")],
                "totalPages": 1,
                "currentPage": 1,
                "totalCount": 1,
            },
        )
    )
    async with PixieChessClient() as c:
        collected = [m async for m in c.users().match_history_iter("0xabc").send()]
    assert [m.game_id for m in collected] == ["g1"]
