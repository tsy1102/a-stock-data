from __future__ import annotations

from unittest.mock import patch

from core import stock_cache
from stock_common import sc_kpl


def test_market_sentiment_cache_uses_integer_ttl() -> None:
    cache_writes = []
    response = {
        "errcode": "0",
        "info": [{"ztjs": "74", "df_num": "4", "strong": "63", "lbgd": "4"}],
        "tip": "ok",
    }

    with patch.object(stock_cache, "_DISABLE_CACHE", False):
        with patch.object(stock_cache, "get_cache", return_value=None):
            with patch.object(
                stock_cache,
                "set_cache",
                side_effect=lambda *args, **kwargs: cache_writes.append((args, kwargs)),
            ):
                with patch.object(sc_kpl, "_post", return_value=response):
                    result = sc_kpl.get_kpl_market_sentiment()

    assert result == {"ztjs": 74, "df_num": 4, "strong": 63, "lbgd": 4, "day": "", "tip": "ok"}
    assert len(cache_writes) == 1
    args, kwargs = cache_writes[0]
    assert args[:2] == ("kpl_sentiment", "get_kpl_market_sentiment")
    assert args[3] == stock_cache.TTL["kpl_sentiment"]
    assert isinstance(args[3], int)
    assert kwargs["trading_day"] is True
