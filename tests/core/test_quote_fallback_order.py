from datetime import datetime as DateTime
from contextlib import ExitStack
from unittest.mock import patch

import pytest

import core.data_provider as dp
from core.source_priority import QUOTE_FALLBACK_EXPECTED_ORDER


@pytest.mark.parametrize(
    ("now", "workday", "expected"),
    [
        (DateTime(2026, 9, 26, 11, 0), False, True),  # holiday/weekend
        (DateTime(2026, 9, 28, 9, 29), True, True),
        (DateTime(2026, 9, 28, 9, 30), True, False),
        (DateTime(2026, 9, 28, 11, 30), True, False),
        (DateTime(2026, 9, 28, 14, 59), True, False),
        (DateTime(2026, 9, 28, 15, 0), True, False),
        (DateTime(2026, 9, 28, 18, 0), True, False),
    ],
)
def test_realtime_route_uses_zhb_only_on_non_workdays_or_before_0930(now, workday, expected):
    fixed_now = now

    class FrozenDateTime(DateTime):
        @classmethod
        def now(cls, tz=None):
            return fixed_now

    with (
        patch.object(dp, "datetime", FrozenDateTime),
        patch("stock_common.stock_calendar.is_workday", return_value=workday),
    ):
        assert dp._should_use_zhb_for_realtime() is expected


def test_canonical_quote_fallback_order_matches_runtime_calls():
    calls = []

    def empty_quote(source):
        def _get_quote(*_args, **_kwargs):
            calls.append(source)
            return {}

        return _get_quote

    class TradingDateTime(DateTime):
        @classmethod
        def now(cls, tz=None):
            return DateTime(2026, 9, 28, 10, 0)

    with ExitStack() as stack:
        stack.enter_context(patch.object(dp, "datetime", TradingDateTime))
        stack.enter_context(patch("stock_common.stock_calendar.is_workday", return_value=True))
        stack.enter_context(patch("stock_common.get_zhb_single_stock_data", return_value={}))
        stack.enter_context(patch.object(dp, "_BATCH_QUOTE_CACHE", {}))
        stack.enter_context(
            patch("core.tdx_client.tdx_get_quote_full", side_effect=empty_quote("tdx"))
        )
        stack.enter_context(
            patch("stock_common.get_tencent_quote", side_effect=empty_quote("tencent"))
        )
        stack.enter_context(
            patch(
                "stock_common.sc_datasource.get_em_quote_full_delay",
                side_effect=empty_quote("eastmoney_push2delay"),
            )
        )
        stack.enter_context(
            patch(
                "stock_common.sc_datasource.get_em_quote_full",
                side_effect=empty_quote("eastmoney_push2"),
            )
        )
        stack.enter_context(patch("stock_common.sc_fuyao.is_fuyao_enabled", return_value=False))
        stack.enter_context(patch("core.zhb_client.get_stock_name_from_zhb", return_value=None))
        stack.enter_context(
            patch("core.zhb_client.get_stock_name_from_zhb_offline_only", return_value=None)
        )
        stack.enter_context(patch("core.zhb_client.cache_stock_name_from_network"))
        dp.get_canonical_stock_data("600519", force_realtime=True)

    assert calls[: len(QUOTE_FALLBACK_EXPECTED_ORDER)] == list(QUOTE_FALLBACK_EXPECTED_ORDER)
