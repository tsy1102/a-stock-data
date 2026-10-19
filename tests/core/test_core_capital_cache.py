"""test_core_capital_cache.py — share_capital 缓存单位防御 + schema 版本（V16.4.0）。

覆盖：
  - 旧单位缓存（total_shares 股单位 >1e7）读取自愈 → 万股
  - schema 版本不匹配 → 缓存失效重建
  - schema 版本匹配 → 正常读取
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pytest


@pytest.fixture()
def cap_module(tmp_path, monkeypatch):
    """把 share_capital 缓存文件指向临时目录，重置内存缓存。"""
    import stock_common.sc_capital_cache as cc

    fake = tmp_path / "share_capital.json"
    monkeypatch.setattr(cc, "_CAPITAL_CACHE_FILE", str(fake))
    monkeypatch.setattr(cc, "_capital_memory_cache", None)
    monkeypatch.setattr(cc, "_capital_cache_meta", {"updated_at": ""})
    return cc, fake


def _write_cache(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _days_ago(days: int) -> str:
    return (date.today() - timedelta(days=days)).strftime("%Y-%m-%d")


def test_old_unit_cache_self_heal(cap_module):
    """旧单位缓存（股）读取时自动归一为万股。"""
    cc, fake = cap_module
    _write_cache(
        fake,
        {
            "meta": {"schema_version": 2, "updated_at": _days_ago(1)},
            "data": {
                "000001": {
                    "total_shares": 19405918750.0,
                    "float_shares": 19405601250.0,
                    "updated_at": _days_ago(1),
                }
            },
        },
    )
    r = cc.get_share_capital("000001")
    assert r["total_shares"] == pytest.approx(1940591.875)  # 股 → 万股
    assert r["float_shares"] == pytest.approx(1940560.125)


def test_schema_mismatch_rebuild(cap_module, monkeypatch):
    """schema 版本不符 → 缓存失效，走 _fetch 重建。"""
    cc, fake = cap_module
    _write_cache(
        fake,
        {
            "meta": {"schema_version": 1, "updated_at": "2026-08-03"},  # 旧版本
            "data": {
                "000001": {
                    "total_shares": 19405918750.0,
                    "float_shares": 19405601250.0,
                    "updated_at": "2026-08-03",
                }
            },
        },
    )
    captured = {}

    def _fake_fetch(code):
        captured["fetched"] = code
        return {"total_shares": 100.0, "float_shares": 50.0, "updated_at": "2026-08-11"}

    monkeypatch.setattr(cc, "_fetch_share_capital", _fake_fetch)
    r = cc.get_share_capital("000001")
    assert captured.get("fetched") == "000001"  # 版本不符 → 重新拉取
    assert r["total_shares"] == 100.0


def test_schema_match_normal(cap_module, monkeypatch):
    """schema 版本匹配 → 直接读缓存（不触发 _fetch）。"""
    cc, fake = cap_module
    _write_cache(
        fake,
        {
            "meta": {"schema_version": 2, "updated_at": _days_ago(1)},
            "data": {
                "000001": {
                    "total_shares": 1940591.875,
                    "float_shares": 1940560.125,
                    "updated_at": _days_ago(1),
                }
            },
        },
    )
    captured = {}

    def _fake_fetch(code):
        captured["fetched"] = code
        return {"total_shares": 0.0, "float_shares": 0.0, "updated_at": ""}

    monkeypatch.setattr(cc, "_fetch_share_capital", _fake_fetch)
    r = cc.get_share_capital("000001")
    assert "fetched" not in captured
    assert r["total_shares"] == pytest.approx(1940591.875)


def test_save_writes_schema_version(cap_module):
    """_save 写入 schema_version=2。"""
    cc, fake = cap_module
    cc._capital_memory_cache = {
        "000001": {"total_shares": 100.0, "float_shares": 50.0, "updated_at": "2026-08-11"}
    }
    cc._save_capital_cache()
    saved = json.loads(fake.read_text(encoding="utf-8"))
    assert saved["meta"]["schema_version"] == cc._CAPITAL_SCHEMA_VERSION == 2
    assert saved["data"]["000001"]["total_shares"] == 100.0


def test_stale_json_entry_is_refreshed(cap_module, monkeypatch):
    cc, fake = cap_module
    stale_date = _days_ago(cc._CAPITAL_TTL_DAYS)
    _write_cache(
        fake,
        {
            "meta": {"schema_version": cc._CAPITAL_SCHEMA_VERSION},
            "data": {
                "000001": {
                    "total_shares": 100.0,
                    "float_shares": 50.0,
                    "updated_at": stale_date,
                }
            },
        },
    )
    monkeypatch.setattr(
        cc,
        "_fetch_share_capital",
        lambda code: {
            "total_shares": 200.0,
            "float_shares": 100.0,
            "updated_at": date.today().strftime("%Y-%m-%d"),
        },
    )

    result = cc.get_share_capital("000001")

    assert result["total_shares"] == 200.0
    assert cc._capital_memory_cache["000001"]["updated_at"] == date.today().strftime("%Y-%m-%d")


def test_capital_validator_rejects_stale_and_non_finite_values(cap_module):
    cc, _ = cap_module
    stale = {
        "total_shares": 100.0,
        "float_shares": 50.0,
        "updated_at": _days_ago(cc._CAPITAL_TTL_DAYS),
    }
    non_finite = {
        "total_shares": float("inf"),
        "float_shares": 50.0,
        "updated_at": _days_ago(1),
    }

    assert not cc._valid_capital_result(stale)
    assert not cc._valid_capital_result(non_finite)


def test_malformed_share_count_is_treated_as_cache_miss(cap_module, monkeypatch):
    cc, fake = cap_module
    _write_cache(
        fake,
        {
            "meta": {"schema_version": cc._CAPITAL_SCHEMA_VERSION},
            "data": {
                "000001": {
                    "total_shares": "not-a-number",
                    "float_shares": 0,
                    "updated_at": _days_ago(1),
                }
            },
        },
    )
    monkeypatch.setattr(
        cc,
        "_fetch_share_capital",
        lambda code: {
            "total_shares": 200.0,
            "float_shares": 100.0,
            "updated_at": date.today().strftime("%Y-%m-%d"),
        },
    )

    result = cc.get_share_capital("000001")

    assert result["total_shares"] == 200.0


def test_zero_share_fetch_is_not_persisted(cap_module, tmp_path, monkeypatch):
    cc, _ = cap_module
    import core.stock_cache as cache
    import core.tdx_client as tdx_client
    import stock_common.sc_datasource as datasource

    monkeypatch.setattr(cache, "_CACHE_DB", str(tmp_path / "stock_cache.db"))
    monkeypatch.setattr(cache, "_db", None)
    monkeypatch.setattr(cache, "_DISABLE_CACHE", False)
    tdx_calls = []
    eastmoney_calls = []

    def fake_tdx(code):
        tdx_calls.append(code)
        return {"zongguben": 0, "liutongguben": 0}

    def fake_eastmoney(code):
        eastmoney_calls.append(code)
        return {"total_shares": 0, "float_shares": 0}

    monkeypatch.setattr(tdx_client, "tdx_get_finance_info", fake_tdx)
    monkeypatch.setattr(datasource, "eastmoney_stock_info_push2", fake_eastmoney)

    first = cc._fetch_share_capital("000001")
    second = cc._fetch_share_capital("000001")

    assert first["total_shares"] == second["total_shares"] == 0
    assert tdx_calls == ["000001", "000001"]
    assert eastmoney_calls == ["000001", "000001"]
    assert cache.get_cache("share_capital", "_fetch_share_capital", "000001") is None
