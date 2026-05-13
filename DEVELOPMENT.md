# Development notes

Internal notes on how the package is built and how the API surface is kept in sync with the upstream `api.pixiechess.xyz`. Consumers of the published client don't need any of this; it's here for contributors and for the next person who picks up the repo cold.

## How the API surface was discovered

The upstream has no published OpenAPI / schema. The endpoint list, payload shapes, and parameter behavior all come from observation against the live API and against `pixiechess-client-rs`, which carries the same model audit + sampler tooling.

The Rust client's audit script (`tools/audit_corpus.py` in that repo) walks a JSON corpus of real responses and prints per-field stats per endpoint (presence %, null %, observed value-types) so every required / optional decision is grounded in evidence rather than assumption. The Pydantic model shapes here track those audit findings.

To re-audit against fresh data, run the Rust sampler:

```
cd ../pixiechess-client-rs
cargo run --example sample_live --release -- --out /tmp/pixiechess-api-expanded.json
python3 tools/audit_corpus.py
```

Then update the relevant `src/pixiechess_client/models/*.py` here to match.

## How no-op query params are handled

Some query parameters are accepted by the server but silently ignored — they don't change the response. Confirmed examples:

| Endpoint | Param | Verdict |
|---|---|---|
| `/leaderboard` | `pageSize` | ignored (server pins page size at 15) |
| `/tournament/list` | `sort` | ignored (identical ordering across `date`, `newest`, `oldest`) |
| `/live-feed` | `since` | ignored (returns events older than the cutoff) |
| `/live-feed` | `type` | ignored (returns all event types) |

**Policy**: confirmed silently-ignored params are *dropped from the public builder* — not deprecated, not documented as "no-op". Advertising a knob that doesn't turn is misleading. If the server later starts honoring one, the method is added back as a non-breaking minor bump.

## Regression tests

Replay regression coverage lives in the Rust client (`tests/replay.rs` over a vendored corpus). The Python client validates the same model shapes by mirroring the audit findings; a Python equivalent of the replay test can be added later if drift surfaces.

Day-to-day:

```
uv sync --dev
uv run ruff check .
uv run ruff format --check .
uv run ty check .
uv run pytest tests/
```
