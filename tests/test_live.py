"""Live smoke + effectiveness tests against `api.pixiechess.xyz`.

Every test is marked ``live``; pytest skips them unless explicitly
selected::

    uv run pytest tests/test_live.py -v -m live

The smoke tests cover one call per endpoint group. The effectiveness
tests verify that every advertised query param actually changes the
response.
"""

from collections.abc import AsyncIterator

import pytest

from pixiechess_client import PixieChessClient

pytestmark = pytest.mark.live


@pytest.fixture
async def client() -> AsyncIterator[PixieChessClient]:
    c = PixieChessClient()
    yield c
    await c.aclose()


# ----- smoke: one call per endpoint group ----------------------------


async def test_live_misc_config(client: PixieChessClient) -> None:
    await client.misc().config().send()


async def test_live_misc_eth_usd_price(client: PixieChessClient) -> None:
    p = await client.misc().eth_usd_price().send()
    assert p.usd > 0


async def test_live_misc_vault_balance(client: PixieChessClient) -> None:
    b = await client.misc().vault_balance().send()
    assert isinstance(b, str) and b


async def test_live_misc_live_feed(client: PixieChessClient) -> None:
    events = await client.misc().live_feed().limit(5).send()
    assert isinstance(events, list)


async def test_live_ranks_masters(client: PixieChessClient) -> None:
    m = await client.ranks().masters().send()
    assert isinstance(m, list)


async def test_live_leaderboard_first_page(client: PixieChessClient) -> None:
    p = await client.leaderboard().get().page(1).send()
    assert p.entries


async def test_live_points_leaderboard_first_page(client: PixieChessClient) -> None:
    await client.leaderboard().points().page(1).send()


async def test_live_users_get_top(client: PixieChessClient) -> None:
    lb = await client.leaderboard().get().page(1).send()
    top = lb.entries[0]
    u = await client.users().get(top.address).send()
    assert u.address.lower() == top.address.lower()


async def test_live_users_match_history_top(client: PixieChessClient) -> None:
    lb = await client.leaderboard().get().page(1).send()
    top = lb.entries[0]
    await client.users().match_history(top.address).limit(3).send()


async def test_live_pieces_for_top(client: PixieChessClient) -> None:
    lb = await client.leaderboard().get().page(1).send()
    top = lb.entries[0]
    await client.pieces().get(top.address).send()


async def test_live_auctions_active(client: PixieChessClient) -> None:
    await client.auctions().active().send()


async def test_live_auctions_past_first_page(client: PixieChessClient) -> None:
    await client.auctions().past().page(1).page_size(5).send()


async def test_live_auctions_today_summary(client: PixieChessClient) -> None:
    await client.auctions().today_summary().send()


async def test_live_auctions_last_completed_day_summary(client: PixieChessClient) -> None:
    await client.auctions().last_completed_day_summary().send()


async def test_live_auctions_daily_volume(client: PixieChessClient) -> None:
    await client.auctions().daily_volume().range("7d").send()


async def test_live_prices(client: PixieChessClient) -> None:
    await client.auctions().prices().send()


async def test_live_tournaments_list(client: PixieChessClient) -> None:
    await client.tournaments().list().limit(5).send()


async def test_live_game_lookup_from_top_match_history(client: PixieChessClient) -> None:
    lb = await client.leaderboard().get().page(1).send()
    top = lb.entries[0]
    h = await client.users().match_history(top.address).limit(3).send()
    if not h.matches:
        return
    await client.games().get(h.matches[0].game_id).send()


# ----- effectiveness: every advertised param actually does something --


async def test_live_leaderboard_page_changes_results(client: PixieChessClient) -> None:
    p1 = await client.leaderboard().get().page(1).send()
    p2 = await client.leaderboard().get().page(2).send()
    assert p1.entries[0].rank == 1
    assert p2.entries[0].rank > p1.entries[0].rank


async def test_live_match_history_limit_actually_limits(client: PixieChessClient) -> None:
    lb = await client.leaderboard().get().page(1).send()
    h = await client.users().match_history(lb.entries[0].address).limit(3).send()
    assert len(h.matches) <= 3


async def test_live_pieces_grouped_collapses_duplicates(client: PixieChessClient) -> None:
    pts = await client.leaderboard().points().page(1).send()
    addr = pts.entries[0].address
    ungrouped = await client.pieces().get(addr).grouped(False).send()
    grouped = await client.pieces().get(addr).grouped(True).send()
    assert len(grouped.pieces) <= len(ungrouped.pieces)


async def test_live_auctions_daily_volume_range_affects_count(client: PixieChessClient) -> None:
    d7 = await client.auctions().daily_volume().range("7d").send()
    d30 = await client.auctions().daily_volume().range("30d").send()
    assert len(d30) > len(d7)


async def test_live_auctions_past_page_size_actually_paginates(client: PixieChessClient) -> None:
    small = await client.auctions().past().page(1).page_size(1).send()
    large = await client.auctions().past().page(1).page_size(10).send()
    assert len(small.day_buckets) == 1
    assert len(large.day_buckets) == 10


async def test_live_live_feed_limit_actually_limits(client: PixieChessClient) -> None:
    events = await client.misc().live_feed().limit(3).send()
    assert len(events) == 3


async def test_live_tournaments_pinned_filters(client: PixieChessClient) -> None:
    all_ = await client.tournaments().list().limit(10).pinned(False).send()
    pinned = await client.tournaments().list().limit(10).pinned(True).send()
    assert pinned.total_count <= all_.total_count


async def test_live_tournaments_active_filters(client: PixieChessClient) -> None:
    inactive = await client.tournaments().list().limit(10).active(False).send()
    active = await client.tournaments().list().limit(10).active(True).send()
    assert active.total_count < inactive.total_count
