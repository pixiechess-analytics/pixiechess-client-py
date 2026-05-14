"""Unofficial async Python client for the PixieChess API.

The public surface lands incrementally — see the project README for the
status of each endpoint and the planned shape of the public API.
"""

from ._http import DEFAULT_USER_AGENT
from .client import PixieChessClient
from .errors import (
    ApiError,
    DecodeError,
    HttpError,
    NotFoundError,
    PixieChessError,
)

__version__ = "0.1.3"

__all__ = [
    "DEFAULT_USER_AGENT",
    "ApiError",
    "DecodeError",
    "HttpError",
    "NotFoundError",
    "PixieChessClient",
    "PixieChessError",
    "__version__",
]
