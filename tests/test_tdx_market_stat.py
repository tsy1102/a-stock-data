import pandas as pd

import core.tdx_client as tdx_client


def test_market_stat_normalizes_tdx_total_market_cap_to_yuan(monkeypatch):
    source = pd.DataFrame(
        [
            {
                "up_count": 4667,
                "down_count": 779,
                "neutral_count": 126,
                "suspended_count": 6,
                "total_count": 5578,
                "total_amount": 0,
                "total_volume": 0,
                "total_market_cap": 10_320_000_000_000,
                "limit_up_count": 121,
                "limit_down_count": 10,
            }
        ]
    )

    class FakeClient:
        def market_stat(self):
            return source

    monkeypatch.setattr(tdx_client, "_get_tdx_client", lambda: FakeClient())
    monkeypatch.setattr(tdx_client, "_MARKET_STAT_CACHE", {})
    monkeypatch.setattr(tdx_client, "_MARKET_STAT_TS", 0.0)

    result = tdx_client.tdx_get_market_stat()

    assert result is not None
    assert result["total_market_cap"] == 103_200_000_000_000
    assert result["up_count"] == 4667
