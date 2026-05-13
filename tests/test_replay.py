"""Replay test against a vendored corpus of real responses.

Walks every example in ``tests/fixtures/pixiechess-api.json`` and asserts
that the captured response body decodes into the typed Pydantic model.
Fails loud on API shape drift.

Each top-level fixture key is ``"<METHOD> <path-template>"``. This test
owns its endpoint-key → model dispatch table.
"""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from pixiechess_client.models import (
    Auction,
    AuctionDaySummary,
    AuctionPieceInfo,
    CompletedDaySummary,
    DailyVolume,
    EthUsdPrice,
    Game,
    LeaderboardPage,
    LiveFeedEvent,
    MatchHistoryPage,
    PastAuctionsPage,
    PiecesPage,
    PointsLeaderboardPage,
    Prices,
    PublicConfig,
    RatingChange,
    TournamentDetails,
    TournamentList,
    User,
    WaitlistEntry,
)

FIXTURE = Path(__file__).parent / "fixtures" / "pixiechess-api.json"

# Each entry: (endpoint key, body → typed-decode callable). Envelope-unwrapping
# happens inside the callable so the test mirrors what each builder does on
# ``.send()``.

Parser = Callable[[Any], None]


def _parse(model: type[BaseModel]) -> Parser:
    def fn(body: Any) -> None:
        model.model_validate(body)

    return fn


def _parse_auction_envelope(body: Any) -> None:
    Auction.model_validate(body["auction"])


def _parse_auctions_list_envelope(body: Any) -> None:
    for a in body.get("auctions", []):
        Auction.model_validate(a)


def _parse_days_envelope(body: Any) -> None:
    for d in body.get("days", []):
        DailyVolume.model_validate(d)


def _parse_user_envelope(body: Any) -> None:
    User.model_validate(body["user"])


def _parse_vault_balance_envelope(body: Any) -> None:
    assert isinstance(body["balance"], str)


def _parse_ranks_masters_envelope(body: Any) -> None:
    assert isinstance(body.get("addresses", []), list)


def _parse_waitlist(body: Any) -> None:
    for e in body:
        WaitlistEntry.model_validate(e)


def _parse_live_feed(body: Any) -> None:
    for e in body:
        LiveFeedEvent.model_validate(e)


DISPATCH: dict[str, Parser] = {
    "GET /auction/{address}": _parse_auction_envelope,
    "GET /auctions/active": _parse_auctions_list_envelope,
    "GET /auctions/daily-volume": _parse_days_envelope,
    "GET /auctions/last-completed-day-summary": _parse(CompletedDaySummary),
    "GET /auctions/past": _parse(PastAuctionsPage),
    "GET /auctions/piece/{pieceKey}": _parse(AuctionPieceInfo),
    "GET /auctions/piece/{pieceKey}/daily-volume": _parse_days_envelope,
    "GET /auctions/today-summary": _parse(AuctionDaySummary),
    "GET /burned-pieces/{address}": _parse(PiecesPage),
    "GET /config/public": _parse(PublicConfig),
    "GET /eth-usd-price": _parse(EthUsdPrice),
    "GET /game/{gameId}": _parse(Game),
    "GET /game/{gameId}/rating/{address}": _parse(RatingChange),
    "GET /leaderboard": _parse(LeaderboardPage),
    "GET /live-feed": _parse_live_feed,
    "GET /pieces/{address}": _parse(PiecesPage),
    "GET /points-leaderboard": _parse(PointsLeaderboardPage),
    "GET /prices": _parse(Prices),
    "GET /ranks/masters": _parse_ranks_masters_envelope,
    "GET /tournament/details/{tournamentId}": _parse(TournamentDetails),
    "GET /tournament/list": _parse(TournamentList),
    "GET /tournament/waitlist/{tournamentId}": _parse_waitlist,
    "GET /user/match-history/{address}": _parse(MatchHistoryPage),
    "GET /user/{userId}": _parse_user_envelope,
    "GET /vault-balance": _parse_vault_balance_envelope,
}


def test_every_example_deserializes_into_typed_model() -> None:
    corpus = json.loads(FIXTURE.read_text())

    failures: list[str] = []
    unknown_keys: list[str] = []
    examples_seen = 0

    for endpoint_key, group in corpus.items():
        parser = DISPATCH.get(endpoint_key)
        if parser is None:
            unknown_keys.append(endpoint_key)
            continue
        for idx, ex in enumerate(group.get("examples", [])):
            examples_seen += 1
            status = ex["response"]["status"]
            if not (200 <= status < 300):
                continue
            body = ex["response"]["body"]
            try:
                parser(body)
            except Exception as e:  # noqa: BLE001
                failures.append(f"{endpoint_key} [example #{idx}, url={ex['request']['url']}]: {e}")

    parts: list[str] = []
    if unknown_keys:
        parts.append(
            "corpus has {} unmapped endpoint key(s):\n  - {}".format(
                len(unknown_keys), "\n  - ".join(sorted(unknown_keys))
            )
        )
    if failures:
        parts.append(
            "{} example(s) failed to deserialize:\n  - {}".format(
                len(failures), "\n  - ".join(failures)
            )
        )

    assert not parts, (
        f"replay test found drift across {examples_seen} example(s):\n\n" + "\n\n".join(parts)
    )


def test_fixture_is_well_formed() -> None:
    """Smoke: ensure the vendored fixture is parseable JSON shaped like the
    corpus produced by the upstream HAR tool.
    """
    corpus = json.loads(FIXTURE.read_text())
    assert isinstance(corpus, dict)
    assert corpus, "corpus is empty"
    for key, group in corpus.items():
        assert key.startswith("GET "), f"unexpected key {key!r}"
        assert "examples" in group, f"{key!r} has no examples list"


@pytest.fixture(autouse=True)
def _no_network() -> None:
    """Replay is offline. If the test ever starts making network calls,
    something has gone wrong in DISPATCH (a body in the corpus shouldn't
    require I/O to validate).
    """
    # No-op fixture — exists as a marker; the actual decode is pure.
