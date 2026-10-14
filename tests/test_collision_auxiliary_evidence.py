import json
from datetime import date
from types import SimpleNamespace

from scripts import collision_auxiliary_evidence as evidence


def _folder(root, name, *, market_date, capture_date, meta=None):
    path = root / name
    path.mkdir()
    return SimpleNamespace(
        name=name,
        path=str(path),
        market_date=date.fromisoformat(market_date) if market_date else None,
        capture_date=date.fromisoformat(capture_date),
        meta=meta or {},
    )


def test_daily_aggregate_evidence_deduplicates_dates_and_drops_raw_values(tmp_path):
    first = _folder(
        tmp_path,
        "20261012",
        market_date="2026-10-12",
        capture_date="2026-10-12",
        meta={
            "data_date": "20261012",
            "source_identity_reconciliation": {
                "status": "ok",
                "endpoints": {
                    "ggmx": {"status": "collecting_evidence"},
                    "dyccl": {"status": "operationally_redundant"},
                },
            },
        },
    )
    second = _folder(
        tmp_path,
        "20261013",
        market_date="2026-10-12",
        capture_date="2026-10-13",
        meta={
            "data_date": "20261012",
            "axdata_validation": {
                "status": "already_recorded",
                "data_date": "20261012",
                "queue": {"interface_count": 257},
                "passive_evidence": {},
                "probe": {"status": "already_recorded", "request_count": 0},
            },
        },
    )
    (first.path and (tmp_path / "20261012" / "axdata_validation.json")).write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "status": "sampled",
                "data_date": "2026-10-12",
                "market_phase": "closed",
                "evaluated_at": "2026-10-12T16:00:00+08:00",
                "queue": {
                    "status": "ok",
                    "interface_count": 257,
                    "field_occurrence_count": 3343,
                    "field_occurrences_below_e3": 931,
                    "active_probe_allowlist": ["tencent_realtime_snapshot"],
                    "other_candidates": "static review only",
                },
                "passive_evidence": {
                    "axdata_shortline_vs_eltdx": {
                        "status": "compared",
                        "target_trade_date": "20261012",
                        "paired_stocks": 20,
                        "paired_codes": ["600519"],
                        "field_comparisons": {
                            "return_on_equity": {"equal": 18, "different": 2, "both_null": 0}
                        },
                    },
                    "kph_limit_up_history_vs_kpl_detail": {
                        "status": "compared",
                        "target_trade_date": "20261012",
                        "paired_stocks": 15,
                        "field_comparisons": {
                            "seal_amount": {"equal": 10, "different": 5, "missing": 0}
                        },
                    },
                },
                "probe": {
                    "status": "sampled",
                    "interface_id": "tencent_realtime_snapshot",
                    "request_count": 1,
                    "source_identity": {
                        "status": "partially_redundant",
                        "matched_data_dates": 3,
                        "matched_symbols": 3,
                        "unresolved_fields": ["pe_dynamic"],
                        "next_recheck_in_data_dates": 20,
                    },
                    "comparison": {
                        "field_comparisons": {
                            "last_price": {"status": "equal", "axdata_value": 10.5}
                        }
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = evidence.build_daily_aggregate_evidence(
        [first, second], ["20261012"]
    )

    assert result["axdata"]["data_date_count"] == 1
    assert result["axdata"]["duplicate_capture_records_deduplicated"] == 1
    assert result["axdata"]["probe_request_count"] == 1
    assert result["axdata"]["identity_status_counts"] == {"partially_redundant": 1}
    assert result["axdata"]["daily_records"][0]["probe"]["equal_fields"] == 1
    assert (
        result["axdata"]["daily_records"][0]["probe"]["source_identity"]["status"]
        == "partially_redundant"
    )
    assert result["axdata"]["queue"]["interface_count"] == 257
    assert result["axdata"]["passive_field_comparison_totals"][
        "axdata_shortline_vs_eltdx:return_on_equity"
    ] == {"equal": 18, "different": 2, "both_null": 0, "missing": 0}
    assert result["ftshare"]["data_date_count"] == 1
    assert result["ftshare"]["daily_records"][0]["endpoint_status_counts"] == {
        "collecting_evidence": 1,
        "operationally_redundant": 1,
    }
    serialized = json.dumps(result, ensure_ascii=False)
    assert "600519" not in serialized
    assert "10.5" not in serialized
    assert "axdata_value" not in serialized


def test_auxiliary_report_keeps_aggregate_checks_out_of_anchor_lane():
    report = evidence.append_daily_aggregate_report(
        "## L1 候选",
        {
            "axdata": {
                "data_date_count": 1,
                "duplicate_capture_records_deduplicated": 0,
                "queue": {"interface_count": 257, "field_occurrence_count": 3343},
                "daily_records": [
                    {
                        "data_date": "2026-10-14",
                        "status": "probe_skipped",
                        "probe": {
                            "status": "endpoint_redundant_until_scheduled_recheck",
                            "request_count": 0,
                            "source_identity": {
                                "status": "partially_redundant",
                                "unresolved_fields": ["pe_dynamic"],
                                "next_recheck_in_data_dates": 18,
                            },
                        },
                        "passive_evidence": {},
                    }
                ],
                "passive_field_comparison_totals": {},
            },
            "ftshare": {"data_date_count": 0, "daily_records": []},
        },
    )

    assert "## L1 候选" in report
    assert "AxData / FTShare 每日轮验（不作为独立字段锚）" in report
    assert "257 个接口" in report
    assert "来源身份状态" in report
    assert "partially_redundant（18 个数据日后复验）；待核 1 字段" in report
