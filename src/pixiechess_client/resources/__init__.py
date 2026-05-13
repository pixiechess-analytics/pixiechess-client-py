"""Resource builders — one accessor per logical PixieChess endpoint group.

Mirrors `pixiechess-client-rs/src/resources/`.
"""

from .users import UsersResource

__all__ = ["UsersResource"]
