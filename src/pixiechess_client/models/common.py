"""Shared models used across multiple resource bodies."""

from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base model with ``camelCase`` wire aliasing and ``snake_case`` field names.

    Subclasses inherit the model_config so they decode `camelCase` JSON into
    `snake_case` fields and accept either name at construction time.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
    )


class Helmet(CamelModel):
    """A piece "helmet" — a small visual badge attached to a player."""

    key: str
    color: str


class PlayerInfo(CamelModel):
    """Compact player identity returned inline on match-history rows.

    Only ``address`` is guaranteed. The wire response can omit every
    other field for "ghost" wallets — addresses that played games but
    never registered a username/helmet. The /user/{addr} endpoint also
    404s for these.
    """

    address: str
    username: str | None = None
    username_display: str | None = None
    helmet: Helmet | None = None


class SuggestSignup(CamelModel):
    """Marker the server attaches when it wants the caller to prompt sign-up."""

    reason: str


class ResponseMeta(CamelModel):
    """Optional ``_meta`` envelope — carries the signup hint and any future
    server-side additions.
    """

    suggest_signup: SuggestSignup | None = None


class DateDict(BaseModel):
    """Helper for the ``{year, month, day}`` nested-date shape the server emits
    on a handful of summary endpoints (``DailyVolume.date``,
    ``CompletedDaySummary.date``, etc.). Decoded into :class:`datetime.date`
    at the field level via :func:`parse_date_dict`.
    """

    year: int
    month: int
    day: int

    def to_date(self) -> date:
        return date(self.year, self.month, self.day)


def parse_date_dict(value: object) -> date:
    """Validator: accept ``{year, month, day}`` and return a :class:`date`."""
    if isinstance(value, date):
        return value
    if isinstance(value, dict):
        return DateDict.model_validate(value).to_date()
    raise ValueError(f"expected {{year, month, day}}, got {value!r}")


def date_dict_validator(field: str):
    """Decorator factory: attach a validator that turns ``{year, month, day}``
    payloads into :class:`date` for the named field. Use on subclasses::

        class DailyVolume(CamelModel):
            date: dt.date
            _v_date = date_dict_validator("date")
    """
    return field_validator(field, mode="before")(parse_date_dict)


__all__ = [
    "CamelModel",
    "DateDict",
    "Helmet",
    "PlayerInfo",
    "ResponseMeta",
    "SuggestSignup",
    "date_dict_validator",
    "parse_date_dict",
]
