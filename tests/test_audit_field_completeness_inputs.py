import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scripts import audit_field_completeness as audit


def test_missing_raw_files_are_reported_as_empty_sets(monkeypatch, tmp_path):
    monkeypatch.setattr(audit, "CAP", str(tmp_path))

    raw = audit.raw_field_sets()

    assert raw["东财-push2(stock/get)"] == set()
    assert raw["东财-ulist239(np/get)"] == set()
    assert raw["ZHB-tdxstat"] == set()
    assert raw["ZHB-tdxstat2"] == set()
    assert raw["ZHB-tipinfo"] == set()


def test_push2_audit_uses_current_capture_and_unions_successful_samples(monkeypatch, tmp_path):
    current = {
        "stocks": {
            "000001": {"__error__": "timeout"},
            "000002": {"data": {"f43": 10.0, "f44": 11.0}},
        }
    }
    legacy = {"stocks": {"000003": {"data": {"f45": 1000}}}}
    (tmp_path / "raw_push2.json").write_text(json.dumps(current), encoding="utf-8")
    (tmp_path / "raw_push2_full.json").write_text(json.dumps(legacy), encoding="utf-8")
    monkeypatch.setattr(audit, "CAP", str(tmp_path))

    raw = audit.raw_field_sets()

    assert raw["东财-push2(stock/get)"] == {"f43", "f44", "f45"}


def test_tdx_audit_includes_raw_quote_adapter_fields(monkeypatch, tmp_path):
    payload = {
        "stocks": {
            "600519": {
                "quote_raw": {"code": "600519", "price": 100.0, "inside_dish": 5},
                "quote_full": {"price": 100.0, "amount_wan": 12.5},
                "finance_info": {"lirunzonghe": 8.0},
            }
        }
    }
    (tmp_path / "raw_tdx.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(audit, "CAP", str(tmp_path))

    raw = audit.raw_field_sets()["TDX(双命名源)"]

    assert "quote_raw.price" in raw
    assert "quote_raw.inside_dish" in raw
    assert "quote_full.amount_wan" in raw
    assert "finance_info.lirunzonghe" in raw


def test_ftshare_audit_includes_market_endpoint_fields(monkeypatch, tmp_path):
    payload = {
        "stocks": {"000001": {"comment_score": [{"score": 1.0}]}},
        "market": {
            "dapan_flow": [{"trade_date": "20261016", "main_net": 12.5}],
            "limit_up_pool_yesterday": [
                {
                    "symbol": "000001.XSHE",
                    "trade_date": "20261016",
                    "limit_up_break": ["10:15:00"],
                    "limit_up_break_count": 1,
                    "ready": True,
                }
            ],
            "pledge_summary": {"pledge_total_ratio": "0"},
            "probe_trading_day": "20261016",
        },
    }
    (tmp_path / "raw_ftshare.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(audit, "CAP", str(tmp_path))

    raw = audit.raw_field_sets()["FTShare"]

    assert {
        "comment_score",
        "symbol",
        "trade_date",
        "limit_up_break",
        "limit_up_break_count",
        "ready",
        "main_net",
        "pledge_total_ratio",
    } <= raw
    assert "probe_trading_day" not in raw


def test_levistock_candidate_audit_reads_only_observed_cls_payload(monkeypatch, tmp_path):
    payload = {
        "schema_version": "1.0",
        "data_date": "2026-10-16",
        "probe": {
            "status": "observed",
            "candidate_id": "cls_sector_rotation",
            "provider_family": "cls",
            "request_count": 1,
        },
        "payload": [
            {
                "trade_date": "2026-10-16",
                "plates": [{"plate_code": "BK001", "plate_name": "示例板块", "change": 1.25}],
            }
        ],
    }
    (tmp_path / "levistock_candidate_raw.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(audit, "CAP", str(tmp_path))

    raw = audit.raw_field_sets()

    candidate_label = "Levistock候选(cls_sector_rotation; 来源族=cls,非独立锚)"
    assert raw[candidate_label] == {"trade_date", "plate_code", "plate_name", "change"}
    assert "provider_family" not in raw[candidate_label]
    assert "request_count" not in raw[candidate_label]


@pytest.mark.parametrize(
    "probe",
    [
        {"status": "pending", "candidate_id": "cls_sector_rotation", "provider_family": "cls"},
        {"status": "observed", "candidate_id": "other", "provider_family": "eastmoney"},
    ],
)
def test_levistock_candidate_audit_requires_observed_status_and_keeps_family_separate(
    monkeypatch, tmp_path, probe
):
    (tmp_path / "levistock_candidate_raw.json").write_text(
        json.dumps({"probe": probe, "payload": [{"unverified_field": 1}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(audit, "CAP", str(tmp_path))

    raw = audit.raw_field_sets()

    candidate_sources = [source for source in raw if source.startswith("Levistock候选(")]
    if probe["status"] == "observed":
        assert candidate_sources == ["Levistock候选(other; 来源族=eastmoney,非独立锚)"]
        assert raw[candidate_sources[0]] == {"unverified_field"}
    else:
        assert not candidate_sources


def test_kpl_and_kph_audit_reads_split_runtime_raw_paths(monkeypatch, tmp_path):
    market = {
        "scheme": "market.mixed",
        "kpl_sentiment": {"ztjs": 10, "tip": "sample"},
        "kpl_up_down": {"rise_num": 100, "fall_num": 20},
        "kpl_broken_ratio": {"broken_num": 3, "broken_ratio": 0.2},
        "kph_limit_ladder": [{"code": "600000", "limit_count": 2, "limit_time": 930000}],
    }
    kpl_detail = {
        "scheme": "kpl.limit_up_detail",
        "stocks": {
            "600000": {
                "amount": 1000,
                "main_inflow": 250,
                "zt_time": 1728000000,
                "__identity__": {"code": "600000", "trade_date": "20261016"},
            }
        },
    }
    kph_history = {
        "scheme": "kph.limit_up_history",
        "stocks": {
            "600000": {
                "limit_time": 930000,
                "seal_money": 500,
                "__identity__": {"symbol": "600000", "trade_date": "20261016"},
            }
        },
    }
    (tmp_path / "raw_market_sources.json").write_text(json.dumps(market), encoding="utf-8")
    (tmp_path / "raw_kpl.json").write_text(json.dumps(kpl_detail), encoding="utf-8")
    (tmp_path / "raw_kph.json").write_text(json.dumps(kph_history), encoding="utf-8")
    monkeypatch.setattr(audit, "CAP", str(tmp_path))

    raw = audit.raw_field_sets()

    assert {"ztjs", "tip", "rise_num", "fall_num", "broken_num", "broken_ratio"} <= raw[
        "开盘啦(kpl)"
    ]
    assert {"limit_count", "limit_time"} <= raw["开盘红(Levistock适配)"]
    assert {"amount", "main_inflow", "zt_time"} <= raw["开盘啦(kpl_limit_up_detail)"]
    assert {"limit_time", "seal_money"} <= raw["开盘红"]
    assert not {"__identity__", "scheme", "code", "trade_date"} & raw["开盘啦(kpl_limit_up_detail)"]


def test_first_stock_returns_empty_mapping_when_capture_has_no_success(monkeypatch, tmp_path):
    monkeypatch.setattr(audit, "CAP", str(tmp_path))
    document = {"stocks": {"000001": {"__skipped__": "unsupported"}}}

    assert audit.first_stock(document) == {}


def test_partial_stock_records_contribute_fields_but_placeholder_errors_do_not():
    document = {
        "stocks": {
            "000001": {
                "__error__": "one endpoint failed",
                "quote": {"close": 10},
                "__identity__": {"symbol": "000001", "exchange": "SSE"},
            },
            "000002": {"__skipped__": "deferred"},
            "000003": {"__error__": "request failed"},
        }
    }

    records = audit._stock_records(document)

    assert records == [
        {
            "__error__": "one endpoint failed",
            "quote": {"close": 10},
            "__identity__": {"symbol": "000001", "exchange": "SSE"},
        }
    ]
    assert audit.all_stock_leaves(document) == {"close"}


def test_sina_raw_audit_unions_all_stocks_and_all_report_rows(monkeypatch, tmp_path):
    payload = {
        "stocks": {
            "000001": {
                "financial_reports": {
                    "fzb": {
                        "report_type": "fzb",
                        "report_list": {
                            "20260930": {
                                "data": [
                                    {"item_title": "营业收入", "item_value": "1"},
                                    {"item_tongbi": "2"},
                                ]
                            }
                        },
                    }
                },
                "money_flow": [{"opendate": "2026-10-16", "netamount": "10"}],
            },
            "000002": {
                "__error__": "one statement failed",
                "money_flow": [{"trade": "1", "turnover": "2"}],
            },
        }
    }
    (tmp_path / "raw_sina_extended.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(audit, "CAP", str(tmp_path))

    raw = audit.raw_field_sets()["新浪(扩展API)"]

    assert {
        "item_value",
        "item_tongbi",
        "report_type",
        "opendate",
        "netamount",
        "trade",
        "turnover",
    } <= raw
    assert not {"__error__", "__skipped__", "financial_reports", "money_flow", "item_title"} & raw


def test_compare_field_sets_reports_both_unregistered_and_unobserved_fields():
    result = audit.compare_field_sets(
        {"f1", "f3"},
        {"f1", "f2"},
    )

    assert result == {
        "matched": {"f1"},
        "unregistered_raw": {"f3"},
        "registered_not_observed": {"f2"},
    }


def test_malformed_capture_is_not_silently_treated_as_missing(monkeypatch, tmp_path):
    (tmp_path / "raw_push2.json").write_text("{bad json", encoding="utf-8")
    monkeypatch.setattr(audit, "CAP", str(tmp_path))

    with pytest.raises(json.JSONDecodeError):
        audit.raw_field_sets()
