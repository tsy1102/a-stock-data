import get_mak_report
import stock_common.sc_plate_rot as plate_rotation


def test_unqueried_limit_pool_source_is_not_reported_as_failed():
    source_text, status = get_mak_report._format_limit_pool_source_summary(
        {"cls": 47, "kpl": 47, "fupan": 47, "push2ex": None},
        47,
        unqueried_sources=["push2ex"],
    )

    assert "push2ex=未查询" in source_text
    assert "可用来源全数一致（3/3）" in status
    assert "失败" not in status


def test_missing_main_net_summary_explains_shared_cooldown():
    lines = get_mak_report._main_flow_summary_lines(
        {}, 3159, 0, source_status="shared_cooldown"
    )

    assert any("push2delay 共享风控冷却中" in line for line in lines)
    assert any("不代表零净流" in line for line in lines)


def test_main_net_date_filter_uses_only_verified_rows_matching_market_date():
    quotes = {
        "600001": {
            "_source_as_of_date": "2026-11-24",
            "_source_as_of_date_status": "verified",
            "main_net_inflow_wan": 12.5,
        },
        "600002": {
            "_source_as_of_date": "2026-11-23",
            "_source_as_of_date_status": "verified",
            "main_net_inflow_wan": -5.0,
        },
        "600003": {
            "_source_as_of_date": "",
            "_source_as_of_date_status": "conflict",
            "main_net_inflow_wan": 8.0,
        },
        "600004": {
            "_source_as_of_date": "2026-11-24",
            "_source_as_of_date_status": "verified",
            "main_net_inflow_wan": None,
        },
        "600005": {
            "_source_as_of_date": "2026-11-24",
            "_source_as_of_date_status": "verified",
            "main_net_inflow_wan": 0.0,
        },
    }

    flows, note, stats = get_mak_report._select_ulist_main_net_for_date(
        quotes, "2026-11-24"
    )

    assert flows == {"600001": 125000.0, "600005": 0.0}
    assert stats == {
        "date_match_rows": 3,
        "date_mismatch_rows": 1,
        "unverified_rows": 1,
        "missing_flow_rows": 1,
    }
    assert "交易日历基准 2026-11-24" in note
    assert "日期不符 1 条" in note
    assert "日期锚缺失/冲突/不完整 1 条" in note


def test_main_net_summary_shows_row_date_conflict_without_reporting_flow_total():
    lines = get_mak_report._main_flow_summary_lines(
        {},
        100,
        0,
        source_status="date_mismatch",
        source_date_note="交易日历基准 2026-11-24；未汇总其他日期。",
    )

    assert any("Ulist 行日期核验" in line for line in lines)
    assert any("行日期与交易日历基准不符" in line for line in lines)
    assert not any("扫描样本主力净额合计" in line for line in lines)


def test_plate_rotation_top_preserves_source_date(monkeypatch):
    monkeypatch.setattr(
        plate_rotation,
        "get_plate_rotation_matrix",
        lambda **_kwargs: {
            "plates": [
                {
                    "rank": 1,
                    "cells": [
                        {
                            "date": "2026-11-24",
                            "code": "803001",
                            "name": "测试板块",
                            "value": "12.3",
                            "color": "red",
                        }
                    ],
                }
            ]
        },
    )

    assert plate_rotation.get_plate_rotation_top("kaipan", 20, 5) == [
        {
            "rank": 1,
            "code": "803001",
            "name": "测试板块",
            "date": "2026-11-24",
            "value": "12.3",
            "color": "red",
        }
    ]
