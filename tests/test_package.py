"""Sanity tests so CI's pytest step has something to run before resources land."""

import pixiechess_client


def test_version_constant_is_present() -> None:
    assert isinstance(pixiechess_client.__version__, str)
    assert pixiechess_client.__version__.count(".") == 2
