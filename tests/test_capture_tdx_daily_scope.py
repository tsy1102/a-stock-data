from core import tdx_client
from scripts import capture_field_probe
from scripts.capture_tcp_collectors import collect_tdx_f10


def test_daily_tdx_f10_capture_excludes_all_history_dividend_records(monkeypatch):
    monkeypatch.setattr(tdx_client, "tdx_get_financial_analysis", lambda code: {"code": code})
    monkeypatch.setattr(tdx_client, "tdx_get_share_capital", lambda code: {"code": code})
    monkeypatch.setattr(
        tdx_client,
        "tdx_get_dividend_history",
        lambda code: (_ for _ in ()).throw(
            AssertionError("daily capture must not request all-history data")
        ),
    )

    result = collect_tdx_f10([{"code": "920306"}])

    assert result == {
        "stocks": {
            "920306": {
                "financial_analysis": {"code": "920306"},
                "share_capital": {"code": "920306"},
            }
        }
    }
    assert "tdx_f10" in capture_field_probe.build_collectors()
