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


def test_market_adapter_can_capture_raw_response_fields() -> None:
    response = {
        "errcode": "0",
        "list": {
            "SZJS": "20",
            "XDJS": "5",
            "future_field": "kept",
            "nested": {"flag": True},
        },
    }
    with patch.object(sc_kpl, "_post", return_value=response):
        result = sc_kpl.get_kpl_up_down(capture_raw=True)

    assert result["rise_num"] == 20
    assert result["__raw_response__"] == response
    assert result["raw_response:list.SZJS"] == "20"
    assert result["raw_response:list.future_field"] == "kept"
    assert result["raw_response:list.nested.flag"] is True


def test_kpl_detail_capture_preserves_raw_columns_and_pid_type() -> None:
    row = [
        "600000",
        "浦发银行",
        "raw_2",
        "raw_3",
        1790645140,
        "概念",
        10,
        11,
        12,
        13,
        14,
        15,
        "行业",
        16,
        17,
        18,
        19,
        20,
        "raw_18",
        "BK0001",
        21,
    ]
    with patch.object(sc_kpl, "_post", return_value={"errcode": "0", "info": [[row]]}):
        result = sc_kpl.get_kpl_limit_up_detail(pid_type=3, capture_raw=True)

    assert len(result) == 1
    assert result[0]["pid_type"] == 3
    assert result[0]["raw_columns"]["col_02"] == "raw_2"
    assert result[0]["raw_columns"]["col_20"] == 21
    assert result[0]["__raw_row__"] == row


def test_kpl_plate_strength_capture_preserves_source_columns() -> None:
    row = ["BK0001", "AI", 1, 2, 3, 4, 5, 6, 7, 8, 9, "skip", 10, 11, 12, 13, 14]
    with patch.object(sc_kpl, "_post", return_value={"errcode": "0", "list": [row]}):
        result = sc_kpl.get_kpl_plate_strength(capture_raw=True)

    assert result[0]["code"] == "BK0001"
    assert result[0]["pe_next"] == 14
    assert result[0]["raw_columns"]["col_12"] == 10
    assert result[0]["__raw_row__"] == row
