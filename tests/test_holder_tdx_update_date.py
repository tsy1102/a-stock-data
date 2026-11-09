from types import SimpleNamespace

import pandas as pd
import pytest

from core import tdx_client
from stock_common.sc_datasource import _holders


@pytest.mark.parametrize(
    ("updated_date", "expected_date"),
    [
        ("2026-10-26", "2026-10-26"),
        (20261026, "2026-10-26"),
        (20261026.0, "2026-10-26"),
    ],
)
def test_tdx_holder_fallback_accepts_supported_update_date_formats(
    monkeypatch, updated_date, expected_date
):
    client = SimpleNamespace(
        get_finance_info=lambda _market, _code: pd.DataFrame(
            [{"gudongrenshu": 120000, "updated_date": updated_date}]
        )
    )
    writes = []
    monkeypatch.setattr(tdx_client, "_get_tdx_client", lambda: client)
    monkeypatch.setattr(
        _holders,
        "_holder_update_sqlite",
        lambda code, records, now: writes.append((code, records.copy(), now)),
    )
    records = []

    assert _holders._holder_fetch_tdx_optimized("600519", records, 123.0)
    assert records == [{"date": expected_date, "holder_num": 120000}]
    assert writes == [("600519", records, 123.0)]


def test_tdx_holder_fallback_rejects_invalid_update_date(monkeypatch):
    client = SimpleNamespace(
        get_finance_info=lambda _market, _code: pd.DataFrame(
            [{"gudongrenshu": 120000, "updated_date": "2026-02-30"}]
        )
    )
    writes = []
    monkeypatch.setattr(tdx_client, "_get_tdx_client", lambda: client)
    monkeypatch.setattr(
        _holders,
        "_holder_update_sqlite",
        lambda *args: writes.append(args),
    )
    records = []

    assert not _holders._holder_fetch_tdx_optimized("600519", records, 123.0)
    assert records == []
    assert writes == []
