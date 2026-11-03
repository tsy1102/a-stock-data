from datetime import date

import stock_common
import stock_common.sc_datasource._pools as pools
import stock_common.sc_datasource._eastmoney as eastmoney
import stock_common.sc_datasource as datasource
import stock_common.sc_datasource._zhb as zhb
import stock_common.sc_datasource._industry as industry
import stock_common.sc_kpl as kpl
import levistock.stock.stock_fupanla_kph as fupan
import stock_common.sc_network as sc_network
import time


def test_push2_audit_skips_explicitly_disabled_route(monkeypatch):
    audit_stats = {"push2_call_count": 0}
    monkeypatch.setattr(sc_network, "_RL_STATS", audit_stats)

    def endpoint(allow_push2ex=True):
        return allow_push2ex

    wrapped = sc_network.requires_push2(endpoint)

    def keyword_only_endpoint(unrelated=False, *, allow_push2ex=True):
        return unrelated, allow_push2ex

    wrapped_keyword_only = sc_network.requires_push2(keyword_only_endpoint)

    assert wrapped(allow_push2ex=False) is False
    assert wrapped(False) is False
    assert audit_stats["push2_call_count"] == 0
    assert wrapped_keyword_only(False) == (False, True)
    assert audit_stats["push2_call_count"] == 1
    assert wrapped() is True
    assert audit_stats["push2_call_count"] == 2


def test_em_batch_quote_cooldown_uses_tier2_status_adapter(monkeypatch):
    observed = []

    def fake_is_banned(domain):
        observed.append(domain)
        return True

    monkeypatch.setattr(eastmoney, "_em_is_banned", fake_is_banned)

    assert datasource.is_em_batch_quotes_cooling_down() is True
    assert observed == ["push2delay.eastmoney.com"]


def test_multi_source_marks_push2ex_unqueried_when_disabled(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(stock_common, "get_cls_market_emotion", lambda: {"up_ratio_num": 47})
    monkeypatch.setattr(stock_common, "get_kpl_market_sentiment", lambda: {"ztjs": 47, "lbgd": 4})
    monkeypatch.setattr(fupan, "get_zttt", lambda: {"StockList": [["600000", "A", 3]] * 47})
    monkeypatch.setattr(sc_network, "_kph_wait_process_interval", lambda: None)
    monkeypatch.setattr(
        stock_common,
        "get_limit_up_pool",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("push2ex called")),
    )

    result = pools.get_limit_pool_multi_source.__wrapped__("2099-12-31", allow_push2ex=False)

    assert result["total"] == 47
    assert result["cross_verified"] is True
    assert result["sources"]["push2ex"] is None
    assert result["unqueried_sources"] == ["push2ex"]


def test_multi_source_keeps_missing_counts_unknown(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(stock_common, "get_cls_market_emotion", lambda: {})
    monkeypatch.setattr(stock_common, "get_kpl_market_sentiment", lambda: {})
    monkeypatch.setattr(fupan, "get_zttt", lambda: {})
    monkeypatch.setattr(sc_network, "_kph_wait_process_interval", lambda: None)

    result = pools.get_limit_pool_multi_source.__wrapped__(allow_push2ex=False)

    assert result["sources"] == {
        "cls": None,
        "kpl": None,
        "fupan": None,
        "push2ex": None,
    }
    assert result["total"] is None
    assert result["cross_verified"] is False
    assert result["max_ladder"] is None


def test_multi_source_preserves_explicit_zero_counts(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(stock_common, "get_cls_market_emotion", lambda: {"up_ratio_num": 0})
    monkeypatch.setattr(stock_common, "get_kpl_market_sentiment", lambda: {"ztjs": 0, "lbgd": 0})
    monkeypatch.setattr(fupan, "get_zttt", lambda: {"StockList": []})
    monkeypatch.setattr(sc_network, "_kph_wait_process_interval", lambda: None)

    result = pools.get_limit_pool_multi_source.__wrapped__(allow_push2ex=False)

    assert result["sources"]["cls"] == 0
    assert result["sources"]["kpl"] == 0
    assert result["sources"]["fupan"] == 0
    assert result["total"] == 0
    assert result["cross_verified"] is True
    assert result["max_ladder"] == 0


def test_limit_pool_summary_uses_same_date_kpl_aggregate_without_push2ex(monkeypatch):
    monkeypatch.setattr(pools, "ths_limit_up_pool", lambda _day: [{"code": "600000", "name": "甲"}])
    monkeypatch.setattr(industry, "_tdxhy_industry_map", lambda: {})
    monkeypatch.setattr(
        zhb,
        "get_zhb_data_date",
        lambda: "2026-10-30",
    )
    monkeypatch.setattr(
        pools,
        "get_limit_up_pool",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("push2ex called")),
    )
    monkeypatch.setattr(
        pools,
        "get_limit_broken_pool",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("push2ex called")),
    )
    monkeypatch.setattr(
        pools,
        "get_limit_down_pool",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("push2ex called")),
    )
    monkeypatch.setattr(
        pools,
        "get_limit_pool_multi_source",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("unexpected fallback")),
    )
    monkeypatch.setattr(pools, "get_last_trading_day", lambda: date(2026, 10, 30))
    monkeypatch.setattr(
        "stock_common.stock_calendar.get_last_trading_day",
        lambda *_args, **_kwargs: date(2026, 10, 30),
    )
    _target_date = pools.get_last_trading_day().strftime("%Y-%m-%d")
    monkeypatch.setattr(
        kpl,
        "get_kpl_broken_ratio",
        lambda: {"date": _target_date, "dt": 0, "broken_num": 2},
    )

    result = pools.get_limit_pool_summary.__wrapped__(allow_push2ex=False)

    assert result["limit_up_count"] == 1
    assert result["limit_up_count_available"] is True
    assert result["limit_broken_count"] == 2
    assert result["limit_broken_count_source"] == "kpl"
    assert result["limit_down_count"] == 0
    assert result["limit_down_count_available"] is True
    assert result["success_rate"] == 33.3


def test_limit_pool_summary_does_not_compute_rate_without_limit_up_count(monkeypatch):
    monkeypatch.setattr(pools, "ths_limit_up_pool", lambda _day: [])
    monkeypatch.setattr(
        pools,
        "get_limit_pool_multi_source",
        lambda *_args, **_kwargs: {"total": 0},
    )
    monkeypatch.setattr(pools, "get_last_trading_day", lambda: date(2026, 10, 30))
    monkeypatch.setattr(
        "stock_common.stock_calendar.get_last_trading_day",
        lambda *_args, **_kwargs: date(2026, 10, 30),
    )
    monkeypatch.setattr(
        kpl,
        "get_kpl_broken_ratio",
        lambda: {"date": "2026-10-30", "dt": 0, "broken_num": 0},
    )

    result = pools.get_limit_pool_summary.__wrapped__(allow_push2ex=False)

    assert result["limit_up_count"] == 0
    assert result["limit_up_count_available"] is False
    assert result["limit_broken_count"] == 0
    assert result["limit_broken_count_available"] is True
    assert result["success_rate"] is None


def test_limit_pool_summary_keeps_down_count_unknown_when_sources_fail(monkeypatch):
    monkeypatch.setattr(pools, "ths_limit_up_pool", lambda _day: [])
    monkeypatch.setattr(pools, "get_limit_up_pool", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(pools, "get_limit_broken_pool", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(pools, "get_limit_down_pool", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(
        pools, "get_limit_pool_multi_source", lambda *_args, **_kwargs: {"total": 0}
    )
    monkeypatch.setattr(pools, "get_last_trading_day", lambda: date(2026, 10, 30))
    monkeypatch.setattr(
        "stock_common.stock_calendar.get_last_trading_day",
        lambda *_args, **_kwargs: date(2026, 10, 30),
    )
    monkeypatch.setattr(datasource, "_query_dt_pool_tc", lambda _day: None)
    monkeypatch.setattr(kpl, "get_kpl_broken_ratio", lambda: {})
    monkeypatch.setattr(zhb, "get_zhb_data_date", lambda: "2026-10-29")

    result = pools.get_limit_pool_summary.__wrapped__.__wrapped__(allow_push2ex=True)

    assert result["limit_down_count"] is None
    assert result["limit_down_count_available"] is False
    assert result["limit_down_count_source"] is None


def test_limit_pool_summary_accepts_cross_verified_zero_limit_up_count(monkeypatch):
    monkeypatch.setattr(pools, "ths_limit_up_pool", lambda _day: [])
    monkeypatch.setattr(
        pools,
        "get_limit_pool_multi_source",
        lambda *_args, **_kwargs: {"total": 0, "cross_verified": True},
    )
    monkeypatch.setattr(pools, "get_last_trading_day", lambda: date(2026, 10, 30))
    monkeypatch.setattr(
        "stock_common.stock_calendar.get_last_trading_day",
        lambda *_args, **_kwargs: date(2026, 10, 30),
    )
    monkeypatch.setattr(
        kpl,
        "get_kpl_broken_ratio",
        lambda: {"date": "2026-10-30", "dt": 0, "broken_num": 0},
    )

    result = pools.get_limit_pool_summary.__wrapped__(allow_push2ex=False)

    assert result["limit_up_count"] == 0
    assert result["limit_up_count_available"] is True


def test_yesterday_pool_uses_aligned_ths_and_zhb_data_without_push2ex(monkeypatch):
    monkeypatch.setattr(zhb, "get_zhb_data_date", lambda: "2026-10-30")
    monkeypatch.setattr(
        zhb,
        "get_zhb_full_market_snapshot",
        lambda: {"600000": {"change_pct": 9.99, "price": 11.0}},
    )
    calls = []

    def fake_ths(day):
        calls.append(day)
        return [{"code": "600000", "name": "甲", "limit_count": 2}]

    monkeypatch.setattr(pools, "ths_limit_up_pool", fake_ths)
    monkeypatch.setattr(
        "stock_common.stock_calendar.previous_trading_day",
        lambda _day: date(2026, 10, 29),
    )
    monkeypatch.setattr("stock_common.stock_calendar.is_trading_day", lambda _day: True)
    monkeypatch.setattr(
        pools,
        "_quick_request",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("push2ex called")),
    )

    result = pools.get_yesterday_limit_pool.__wrapped__("2026-10-30", allow_push2ex=False)

    assert calls == ["20261029"]
    assert result[0]["date"] == "20261030"
    assert result[0]["y_limit_date"] == "20261029"
    assert result[0]["y_limit_count"] == 2
    assert result[0]["change_pct"] == 9.99
    assert result[0]["amplitude_pct"] is None


def test_yesterday_pool_rejects_non_trading_zhb_date(monkeypatch):
    monkeypatch.setattr(zhb, "get_zhb_data_date", lambda: "2026-10-31")
    monkeypatch.setattr(
        zhb,
        "get_zhb_full_market_snapshot",
        lambda: {"600000": {"change_pct": 9.99, "price": 11.0}},
    )
    monkeypatch.setattr("stock_common.stock_calendar.is_trading_day", lambda _day: False)
    monkeypatch.setattr(
        pools,
        "ths_limit_up_pool",
        lambda _day: (_ for _ in ()).throw(AssertionError("THS must not be queried")),
    )

    result = pools.get_yesterday_limit_pool.__wrapped__("2026-10-31", allow_push2ex=False)

    assert result == []
