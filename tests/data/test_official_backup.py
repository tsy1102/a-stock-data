from __future__ import annotations

from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from types import SimpleNamespace
import time
import warnings

import pandas as pd
import pytest

from stock_common.sc_datasource import _official_backup


def _szse_workbook() -> bytes:
    rows = [
        {
            "证券代码": code,
            "证券简称": name,
            "融资余额(元)": "1000",
            "融资买入额(元)": "100",
            "融券余额(元)": "200",
            "融券余量(股/份)": "20",
            "融券卖出量(股/份)": "2",
        }
        for code, name in (("000001", "平安"), ("000002", "万科"), ("000003", "国华"))
    ]
    buffer = BytesIO()
    pd.DataFrame(rows).to_excel(buffer, index=False)
    return buffer.getvalue()


def test_margin_snapshot_is_shared_across_concurrent_codes_and_dates(monkeypatch):
    monkeypatch.setattr(_official_backup, "_OFFICIAL_MARGIN_CACHE", OrderedDict())
    calls = []
    workbook = _szse_workbook()

    def fake_get(url, params=None, referer=None):
        calls.append((url, dict(params or {}), referer))
        time.sleep(0.02)
        return SimpleNamespace(content=workbook, url=url)

    monkeypatch.setattr(_official_backup, "_official_get", fake_get)
    codes = ("000001", "000002", "000003", "000001")
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(
            executor.map(
                lambda code: _official_backup.margin_trading_backup("2026-11-02", "sz", code),
                codes,
            )
        )

    assert len(calls) == 1
    assert [frame.iloc[0]["code"] for frame in results] == list(codes)
    results[0].loc[0, "name"] = "mutated"
    unchanged = _official_backup.margin_trading_backup("20261102", "SZ", "000001")
    assert unchanged.iloc[0]["name"] == "平安"
    assert len(calls) == 1

    _official_backup.margin_trading_backup("2026-11-03", "SZ", "000001")
    assert len(calls) == 2
    assert calls[0][1]["txtDate"] == "2026-11-02"
    assert calls[1][1]["txtDate"] == "2026-11-03"


def test_margin_snapshot_cache_is_scoped_by_exchange(monkeypatch):
    monkeypatch.setattr(_official_backup, "_OFFICIAL_MARGIN_CACHE", OrderedDict())
    calls = []
    workbook = _szse_workbook()

    def fake_get(url, params=None, referer=None):
        calls.append(url)
        if "queryMargin.do" in url:
            return SimpleNamespace(
                url=url,
                json=lambda: {
                    "pageHelp": {
                        "total": 1,
                        "data": [
                            {
                                "opDate": "20261102",
                                "stockCode": "600000",
                                "securityAbbr": "浦发",
                                "rzye": "1000",
                                "rzmre": "100",
                                "rqylje": "200",
                                "rqyl": "20",
                                "rqmcl": "2",
                            }
                        ],
                    }
                },
            )
        return SimpleNamespace(content=workbook, url=url)

    monkeypatch.setattr(_official_backup, "_official_get", fake_get)
    sz = _official_backup.margin_trading_backup("2026-11-02", "SZ", "000001")
    sh = _official_backup.margin_trading_backup("2026-11-02", "SH", "600000")

    assert sz.iloc[0]["code"] == "000001"
    assert sh.iloc[0]["code"] == "600000"
    assert len(calls) == 2


def test_official_excel_suppresses_only_known_openpyxl_style_warning(monkeypatch):
    expected = pd.DataFrame({"证券代码": ["000001"]})

    def fake_read_excel(*args, **kwargs):
        warnings.warn_explicit(
            "Workbook contains no default style, apply openpyxl's default",
            UserWarning,
            filename="stylesheet.py",
            lineno=237,
            module="openpyxl.styles.stylesheet",
        )
        warnings.warn_explicit(
            "unrelated workbook warning",
            UserWarning,
            filename="other.py",
            lineno=1,
            module="other.reader",
        )
        return expected.copy()

    monkeypatch.setattr(_official_backup.pd, "read_excel", fake_read_excel)
    response = SimpleNamespace(content=b"workbook")

    with pytest.warns(UserWarning, match="unrelated workbook warning") as caught:
        actual = _official_backup._official_excel(response)

    assert len(caught) == 1
    pd.testing.assert_frame_equal(actual, expected)
