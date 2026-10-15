import pandas as pd
import pytest

from core import tdx_client


class _FakeIndexClient:
    def __init__(self, bars):
        self.bars = bars

    def index_bars(self, **_kwargs):
        return self.bars


class _FakeResponse:
    def __init__(self, price, open_price, change_pct):
        fields = [""] * 33
        fields[3] = str(price)
        fields[5] = str(open_price)
        fields[32] = str(change_pct)
        self.text = f'v_sh000001="{"~".join(fields)}"'
        self.encoding = None


def _install_tdx_mocks(monkeypatch, bars):
    monkeypatch.setattr(tdx_client, "_get_tdx_client", lambda: _FakeIndexClient(bars))
    monkeypatch.setattr(tdx_client, "_tdx_throttle", lambda: None)


def test_tdx_index_quote_rejects_stock_like_values_and_uses_tencent(monkeypatch):
    _install_tdx_mocks(
        monkeypatch,
        pd.DataFrame(
            [
                {"close": 11.45, "open": 11.57},
                {"close": 11.50, "open": 11.57},
            ]
        ),
    )
    monkeypatch.setattr(
        tdx_client,
        "_quick_request",
        lambda *_args, **_kwargs: _FakeResponse(3767.23, 3790.63, -0.62),
    )

    result = tdx_client.tdx_get_index_quote("sh000001")

    assert result == {"price": 3767.23, "open": 3790.63, "change_pct": -0.62}


def test_tdx_index_quote_falls_back_when_previous_close_is_invalid(monkeypatch):
    _install_tdx_mocks(
        monkeypatch,
        pd.DataFrame(
            [
                {"close": 0, "open": 3790.63},
                {"close": 3767.23, "open": 3790.63},
            ]
        ),
    )
    monkeypatch.setattr(
        tdx_client,
        "_quick_request",
        lambda *_args, **_kwargs: _FakeResponse(3767.23, 3790.63, -0.62),
    )

    assert tdx_client.tdx_get_index_quote("sh000001") == {
        "price": 3767.23,
        "open": 3790.63,
        "change_pct": -0.62,
    }


def test_tdx_index_quote_rejects_invalid_values_from_both_sources(monkeypatch):
    _install_tdx_mocks(
        monkeypatch,
        pd.DataFrame(
            [
                {"close": 11.45, "open": 11.57},
                {"close": 11.50, "open": 11.57},
            ]
        ),
    )
    monkeypatch.setattr(
        tdx_client,
        "_quick_request",
        lambda *_args, **_kwargs: _FakeResponse(11.50, 11.57, 0.0),
    )

    assert tdx_client.tdx_get_index_quote("sh000001") == {}


def test_tdx_index_quote_accepts_valid_tdx_values_without_fallback(monkeypatch):
    _install_tdx_mocks(
        monkeypatch,
        pd.DataFrame(
            [
                {"close": 3760.00, "open": 3790.63},
                {"close": 3767.23, "open": 3790.63},
            ]
        ),
    )
    monkeypatch.setattr(
        tdx_client,
        "_quick_request",
        lambda *_args, **_kwargs: pytest.fail("valid TDX quote should not use fallback"),
    )

    result = tdx_client.tdx_get_index_quote("sh000001")

    assert result == {"price": 3767.23, "open": 3790.63, "change_pct": 0.19}
