from datetime import datetime

import stock_common.sc_datasource as datasource
import stock_common.sc_market_signals as market_signals


def test_szse_etf_section_uses_date_returned_by_source(monkeypatch):
    monkeypatch.setattr(market_signals, "_backtrack_trading_days", lambda _n: [])

    def fake_etf_shares(_day, exchange):
        assert exchange == "SZ"
        return [
            {
                "date": "2026-10-30",
                "code": "159919",
                "name": "沪深300ETF",
                "shares_10k": 1000.0,
            }
        ]

    monkeypatch.setattr(datasource, "etf_shares", fake_etf_shares)

    lines = market_signals.render_etf_shares_section("2026-11-01")

    assert any("截至 2026-10-30" in line for line in lines)
    assert not any("截至 2026-11-01" in line for line in lines)


def test_market_signal_render_failure_does_not_hide_later_sources(monkeypatch, caplog):
    source_names = (
        "render_ipo_calendar_section",
        "render_etf_shares_section",
        "render_sina_research_section",
        "render_cctv_news_section",
        "render_sse_e_interaction_section",
        "render_st_list_section",
    )

    def fail(_today_str):
        raise ValueError("invalid upstream row")

    monkeypatch.setattr(market_signals, source_names[0], fail)
    for name in source_names[1:]:
        monkeypatch.setattr(
            market_signals,
            name,
            lambda today_str, source=name: [f"rendered:{source}:{today_str}"],
        )

    lines = market_signals.render_market_signals_section("2026-11-03")

    assert any("近期新股申购日历渲染失败" in line for line in lines)
    assert all(any(name in line for line in lines) for name in source_names[1:])
    assert "market signal renderer failed" in caplog.text


def test_ipo_calendar_closes_same_day_after_application_cutoff_and_estimates_raise(monkeypatch):
    row = {
        "APPLY_DATE": "2026-11-04",
        "SECURITY_CODE": "920309",
        "SECURITY_NAME_ABBR": "菊乐股份",
        "ISSUE_PRICE": 31.92,
        "TOTAL_ISSUE_NUM": 1175.774,
        "TRADE_MARKET": "北京证券交易所",
    }
    monkeypatch.setattr(datasource, "ipo_calendar_recent", lambda _limit: [row])

    future_lines = market_signals.render_ipo_calendar_section(
        "2026-11-03", now=datetime(2026, 11, 3, 20, 49)
    )
    assert any("31.92 | 3.75 | 北京证券交易所 | 待申购" in line for line in future_lines)

    before_cutoff = market_signals.render_ipo_calendar_section(
        "2026-11-04", now=datetime(2026, 11, 4, 14, 59)
    )
    assert any("北京证券交易所 | 当日申购未截止" in line for line in before_cutoff)

    after_cutoff = market_signals.render_ipo_calendar_section(
        "2026-11-04", now=datetime(2026, 11, 4, 20, 49)
    )
    assert any("当前时点起 21 日内有 **0** 只待申购新股" in line for line in after_cutoff)
    assert any("菊乐股份（当日申购已截止）" in line for line in after_cutoff)
    assert not any("920309" in line and "待申购" in line for line in after_cutoff)


def test_market_appendices_disclose_display_caps(monkeypatch):
    research = [
        {"date": "2026-11-04", "title": f"研报{i}", "org": "机构", "type": "公司"}
        for i in range(20)
    ]
    interactions = [
        {
            "code": "600000",
            "name": "浦发银行",
            "question": f"问题{i}",
            "question_time": "2026-11-04",
        }
        for i in range(15)
    ]
    monkeypatch.setattr(datasource, "sina_research_reports", lambda **_kwargs: research)
    monkeypatch.setattr(datasource, "sse_e_interaction", lambda **_kwargs: interactions)

    sina_lines = market_signals.render_sina_research_section()
    interaction_lines = market_signals.render_sse_e_interaction_section()

    assert any("返回 20 条，展示前 15 条" in line for line in sina_lines)
    assert sum(line.lstrip().startswith("•") for line in sina_lines) == 15
    assert any("返回 15 条，展示前 12 条" in line for line in interaction_lines)
    assert sum(line.lstrip().startswith("•") for line in interaction_lines) == 12


def test_st_list_discloses_display_cap(monkeypatch):
    rows = [
        {
            "code": f"600{i:03d}",
            "market": "sh",
            "name": f"ST样本{i}",
            "st_type": "ST",
            "price": 1.0,
            "pct_change": 0.0,
        }
        for i in range(35)
    ]
    monkeypatch.setattr(datasource, "st_stock_list", lambda: rows)

    lines = market_signals.render_st_list_section()

    assert any("共 35 只，本节展示前 30 只" in line for line in lines)
    assert sum(line.lstrip().startswith("|") for line in lines) == 32
