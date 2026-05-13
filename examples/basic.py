"""Runnable quickstart for the PixieChess client.

Hits the live API; prints the leaderboard top 5 plus the top player's
recent matches.

::

    uv run python examples/basic.py
    # or
    python examples/basic.py
"""

import asyncio

from pixiechess_client import PixieChessClient


async def main() -> None:
    async with PixieChessClient() as client:
        lb = await client.leaderboard().get().page(1).send()
        print(f"Leaderboard page 1 ({len(lb.entries)} entries; {lb.total_pages} total). Top 5:")
        for entry in lb.entries[:5]:
            print(
                f"  #{entry.rank:<3} {entry.username_display:<20} "
                f"{entry.rating:>7.1f}  W:{entry.wins:<4} S:{entry.streak:<3}"
            )

        if not lb.entries:
            return
        top = lb.entries[0]

        user = await client.users().get(top.address).send()
        print(
            f"\nTop player profile (typed):\n  {user.username_display}"
            f" — rating {user.rating:.1f}, {user.match_count} match(es),"
            f" trophies {user.trophies}"
        )

        raw = await client.users().get(top.address).raw()
        helmet = raw.get("user", {}).get("helmet")
        if helmet:
            print(f"  helmet (raw JSON): {helmet}")

        history = await client.users().match_history(top.address).page(1).limit(3).send()
        print(f"\nRecent matches ({len(history.matches)}):")
        for m in history.matches:
            print(
                f"  {m.created_at:%Y-%m-%d}  "
                f"{m.white.username_display} vs {m.black.username_display}  →  "
                f"{m.outcome} ({m.result_for_user})"
            )


if __name__ == "__main__":
    asyncio.run(main())
