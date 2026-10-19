from types import SimpleNamespace

import pytest

from stock_common.sc_datasource import _eastmoney, _financials


def test_sina_financial_raw_adapter_keeps_report_periods_and_uses_one_attempt(monkeypatch):
    calls = []
    response = SimpleNamespace(
        json=lambda: {
            "result": {
                "data": {
                    "report_list": {
                        "20260930": {
                            "data": [
                                {
                                    "item_title": "营业总收入",
                                    "item_value": "123",
                                    "item_tongbi": "4",
                                }
                            ]
                        }
                    }
                }
            }
        }
    )

    def request(url, **kwargs):
        calls.append((url, kwargs))
        return response

    monkeypatch.setattr(_financials, "_quick_request", request)

    result = _financials.get_sina_financial_report_raw("600519", "lrb", num_periods=1)

    assert result == {
        "report_type": "lrb",
        "report_list": {
            "20260930": {
                "data": [{"item_title": "营业总收入", "item_value": "123", "item_tongbi": "4"}]
            }
        },
    }
    assert calls[0][1]["params"]["paperCode"] == "sh600519"
    assert calls[0][1]["params"]["source"] == "lrb"
    assert calls[0][1]["max_retries"] == 1


def test_sina_financial_raw_adapter_rejects_unknown_statement_type():
    with pytest.raises(ValueError, match="report_type"):
        _financials.get_sina_financial_report_raw("600519", "cashflow")


def test_sina_fund_flow_adapter_uses_stock_endpoint_and_market_code(monkeypatch):
    calls = []
    rows = [{"opendate": "2026-10-16", "trade": "10", "netamount": "20", "turnover": "1.2"}]

    def request(url, **kwargs):
        calls.append((url, kwargs))
        return SimpleNamespace(json=lambda: rows)

    monkeypatch.setattr(_eastmoney, "_quick_request", request)

    result = _eastmoney.get_sina_stock_fund_flow_raw("920001", days=1)

    assert result == rows
    url, kwargs = calls[0]
    assert "MoneyFlow.ssl_qsfx_zjlrqs" in url
    assert "ssl_bkzj_bk" not in url
    assert kwargs["params"]["daima"] == "bj920001"
    assert kwargs["params"]["sort"] == "opendate"
    assert kwargs["max_retries"] == 1


def test_fund_flow_backup_preserves_list_contract_and_returns_empty_on_failure(monkeypatch):
    rows = [{"opendate": "2026-10-16", "netamount": "20"}]
    monkeypatch.setattr(_eastmoney, "get_sina_stock_fund_flow_raw", lambda *_args, **_kwargs: rows)
    assert _eastmoney.fund_flow_backup("600519", days=1) == rows

    monkeypatch.setattr(_eastmoney, "get_sina_stock_fund_flow_raw", lambda *_args, **_kwargs: None)
    assert _eastmoney.fund_flow_backup("600519", days=1) == []


def test_invalid_sina_fund_flow_arguments_do_not_request(monkeypatch):
    monkeypatch.setattr(
        _eastmoney,
        "_quick_request",
        lambda *_args, **_kwargs: pytest.fail("invalid arguments must not make a request"),
    )

    assert _eastmoney.get_sina_stock_fund_flow_raw("60051", days=1) is None
    assert _eastmoney.get_sina_stock_fund_flow_raw("600519", days=0) is None
