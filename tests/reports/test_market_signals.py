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
