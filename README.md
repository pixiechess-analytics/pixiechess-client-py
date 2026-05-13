# pixiechess-client (Python)

Unofficial async Python client for the [PixieChess](https://www.pixiechess.xyz) API.

> Not affiliated with PixieChess. Consumes the public `api.pixiechess.xyz` surface.

## Status

Scaffold. The package installs cleanly; no endpoints implemented yet. Mirrors the layout of [`pixiechess-client-rs`](https://github.com/pixiechess-analytics/pixiechess-client-rs) — same 8 resource groups, same uniform `.send()` / `.raw()` builder shape, same model field map (verified against the live API rather than the stale old Python client).

## Planned shape

```python
import asyncio
from pixiechess_client import PixieChessClient

async def main() -> None:
    async with PixieChessClient() as client:
        # Typed
        lb = await client.leaderboard().get().page(1).send()
        for entry in lb.entries[:5]:
            print(entry.rank, entry.username_display, entry.rating)

        # Raw (bypasses Pydantic)
        raw = await client.leaderboard().get().page(1).raw()

        # Streamed
        async for entry in client.leaderboard().iter().send():
            ...

asyncio.run(main())
```

## Stack

- Python 3.13+
- Async via `asyncio`
- HTTP via `httpx`
- Models via `pydantic` v2 with `to_camel` alias generators (so model fields are `snake_case` in Python while the wire is `camelCase`)

## License

MIT. See [`LICENSE`](LICENSE).
