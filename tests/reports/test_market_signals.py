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
