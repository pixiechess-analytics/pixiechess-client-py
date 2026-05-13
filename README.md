# pixiechess-client (Python)

Unofficial async Python client for the [PixieChess](https://www.pixiechess.xyz) API.

> Not affiliated with PixieChess. Consumes the public `api.pixiechess.xyz` surface.

## Endpoints

| Resource | Endpoints |
|---|---|
| `users` | `GET /user/{id-or-address}`, `GET /user/match-history/{address}` (+ async stream) |
| `games` | `GET /game/{gameId}`, `GET /game/{gameId}/rating/{address}` |
| `leaderboard` | `GET /leaderboard`, `GET /points-leaderboard` (both + async streams) |
| `pieces` | `GET /pieces/{address}`, `GET /burned-pieces/{address}` (+ async streams) |
| `auctions` | `GET /auction/{address}`, `GET /auctions/{active,past,daily-volume,today-summary,last-completed-day-summary}`, `GET /auctions/piece/{key}[/daily-volume]`, `GET /prices` |
| `tournaments` | `GET /tournament/{list,details/{id},waitlist/{id}}` |
| `misc` | `GET /config/public`, `GET /eth-usd-price`, `GET /vault-balance`, `GET /live-feed` |
| `ranks` | `GET /ranks/masters` |

Auth and websocket realtime are out of scope.

## Install

```bash
pip install pixiechess-client
```

Requires Python 3.13+.

## Quickstart

```python
import asyncio
from pixiechess_client import PixieChessClient

async def main() -> None:
    async with PixieChessClient() as client:
        lb = await client.leaderboard().get().page(1).send()
        for entry in lb.entries[:5]:
            print(f"#{entry.rank:<3} {entry.username_display:<20} {entry.rating:>7.1f}")

asyncio.run(main())
```

## Typed vs raw

Every endpoint goes through a builder that exposes two terminal methods. Pick the one that fits the caller:

```python
# Typed: returns a Pydantic model.
history = await client.users().match_history("0xabc").page(2).limit(25).send()

# Raw: returns dict (skips Pydantic).
raw = await client.users().match_history("0xabc").page(2).limit(25).raw()
```

One-shot endpoints follow the same shape:

```python
masters = await client.ranks().masters().send()
raw_masters = await client.ranks().masters().raw()
```

Some paged endpoints additionally expose an `iter()` / `iter_*()` builder returning an async iterator over every page:

```python
async for entry in client.leaderboard().iter().send():
    ...
```

## Custom User-Agent

The upstream WAF returns a `202` empty-body challenge to non-browser-shaped user agents, so the default `User-Agent` mirrors a recent Chrome build (`pixiechess_client.DEFAULT_USER_AGENT`). To identify your own integration without losing WAF compatibility, suffix the default rather than replacing it:

```python
from pixiechess_client import DEFAULT_USER_AGENT, PixieChessClient

client = PixieChessClient(user_agent=f"{DEFAULT_USER_AGENT} my-app/1.0")
```

The `user_agent` kwarg has replace semantics, so a fully-custom UA is fine too — just be aware the WAF may reject it.

## Stack

- Python 3.13+
- Async via `asyncio`
- HTTP via `httpx`
- Models via `pydantic` v2 (`snake_case` Python field names, `camelCase` on the wire)

## License

MIT. See [`LICENSE`](LICENSE).

---

See [`DEVELOPMENT.md`](DEVELOPMENT.md) for notes on how the API surface is kept in sync with the upstream and how no-op query params are filtered out.
