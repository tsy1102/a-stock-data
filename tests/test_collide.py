import math
import json
from io import StringIO
from collections import defaultdict
from datetime import date
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from scripts import collision_dates, collision_rules

_collide_path = Path(__file__).resolve().parents[1] / "scripts" / "collide.py"
_collide_spec = spec_from_file_location("collide_marker_test_module", _collide_path)
assert _collide_spec is not None and _collide_spec.loader is not None
collide = module_from_spec(_collide_spec)
_collide_spec.loader.exec_module(collide)


def test_flatten_ignores_error_and_skip_markers_as_fields():
    out = []

    collide._flatten(
        {"quote_snapshot": {"last_price": 1.23, "__skipped__": "unsupported"}},
        "eltdx",
        "eltdx",
        "bj920001",
        "2026-09-28",
        out,
    )
    collide._flatten(
        {"quote_snapshot": {"last_price": 1.23, "__error__": "timeout"}},
        "test",
        "test",
        "600000",
        "2026-09-28",
        out,
    )
    collide._flatten(
        {"__skipped__": "unsupported", "last_price": 1.23},
        "eltdx",
        "eltdx",
        "bj920001",
        "2026-09-28",
        out,
    )

    assert out == [
        ("eltdx.quote_snapshot.last_price", 1.23),
        ("test.quote_snapshot.last_price", 1.23),
    ]


def test_flatten_preserves_booleans_but_keeps_structured_values_opt_in():
    out = []
    collide._flatten(
        {
            "ready": False,
            "break_times": ["09:32:45", "09:33:15"],
            "empty_values": [],
            "details": {"flag": True, "values": [1, 2]},
            "__identity__": {"symbol": "000001"},
        },
        "ftshare",
        "ftshare",
        "000001",
        "T:20260827",
        out,
    )

    assert out == [
        ("ftshare.ready", "false"),
        ("ftshare.details.flag", "true"),
    ]

    structured = []
    collide._flatten(
        {
            "break_times": ["09:32:45", "09:33:15"],
            "empty_values": [],
            "details": {"flag": True, "values": [1, 2]},
            "__identity__": {"symbol": "000001"},
        },
        "ftshare",
        "ftshare",
        "000001",
        "T:20260827",
        structured,
        include_structured_values=True,
    )

    assert structured == [
        ("ftshare.break_times", '["09:32:45","09:33:15"]'),
        ("ftshare.empty_values", "[]"),
        ("ftshare.details.flag", "true"),
        ("ftshare.details.values", "[1,2]"),
    ]


def test_kpl_and_kph_raw_files_flatten_as_separate_sources():
    snapshots = [
        {
            "trade_date": "2026-09-29",
            "scheme": "kph.limit_up_history",
            "stocks": {"920779": {"limit_time": 1790645140, "seal_money": 200.0}},
            "identity_observations": [
                "920779: reported_exchange=SSE; reported_instrument_id=920779.SH"
            ],
        },
        {
            "trade_date": "2026-09-29",
            "scheme": "kpl.limit_up_detail",
            "stocks": {"600000": {"zt_time": 1790645140, "max_seal": 34.0}},
        },
    ]
    flattened = []
    for source, document in zip(("kph", "kpl"), snapshots):
        for container in collide._record_containers(document, source=source):
            for code, record in container.items():
                collide._flatten(
                    record,
                    source,
                    document["scheme"],
                    code,
                    document["trade_date"],
                    flattened,
                )

    assert ("kph.limit_time", 1790645140) in flattened
    assert ("kph.seal_money", 200.0) in flattened
    assert ("kpl.zt_time", 1790645140) in flattened
    assert ("kpl.max_seal", 34.0) in flattened
    assert not any("identity_observations" in field for field, _value in flattened)


def test_verified_kph_kpl_dictionary_paths_are_independent_anchors():
    from scripts import collide

    context = collide.load_registry_context()
    assert context["safe_to_run"] is True
    assert {
        ("kph", code)
        for code in (
            "limit_time",
            "seal_amount",
            "seal_money",
            "net_inflow",
            "turnover",
            "turnover_rate",
        )
    } <= context["anchors"]
    assert {
        ("kpl", code)
        for code in (
            "zt_time",
            "max_seal",
            "seal_amount",
            "main_inflow",
            "amount",
            "turnover_real",
        )
    } <= context["anchors"]


def test_flatten_skips_only_ineligible_source_subtree_and_hides_metadata():
    out = []
    collide._flatten(
        {
            "snapshot": {"last_price": 10.0},
            "auction_final": {
                "auction_price": 10.2,
                "__source_meta__": {
                    "collision_eligible": False,
                    "exclusion_reason": "source_data_date_unavailable",
                },
            },
            "auction_live": {
                "auction_price": 10.1,
                "__source_meta__": {"collision_eligible": True},
            },
        },
        "fuyao",
        "fuyao",
        "600000",
        "T:20260929",
        out,
    )

    assert out == [
        ("fuyao.snapshot.last_price", 10.0),
        ("fuyao.auction_live.auction_price", 10.1),
    ]


def test_fuyao_ineligible_auction_is_diagnosed_without_dropping_other_fields(tmp_path):
    folder = tmp_path / "20260929"
    folder.mkdir()
    (folder / "meta.json").write_text(
        '{"data_date":"20260929","capture_date":"20260929"}', encoding="utf-8"
    )
    document = {
        "auction_snapshot_meta": {
            "collision_eligible": False,
            "exclusion_reason": "source_data_date_unavailable",
            "data_status": "ready",
            "source_data_date": None,
            "source_data_date_basis": "not_exposed_by_auction_snapshot_contract",
            "response_timestamp": "2026-09-29T09:25:00",
            "response_timestamp_date": "2026-09-29",
            "item_count": 1,
        },
        "stocks": {
            "600000": {
                "snapshot": {"last_price": 10.0},
                "auction_final": {
                    "auction_price": 10.2,
                    "__source_meta__": {
                        "collision_eligible": False,
                        "exclusion_reason": "source_data_date_unavailable",
                    },
                },
            }
        },
    }
    (folder / "raw_fuyao.json").write_text(json.dumps(document), encoding="utf-8")
    folders, _ = collision_dates.discover_capture_folders(
        str(tmp_path), lambda day: day.weekday() < 5
    )
    snapshots, _ = collision_dates.select_snapshots(folders)
    store = defaultdict(lambda: {"vals": {}, "sample_meta": {}, "src": None})
    diagnostics = []

    collide.load_snapshots(snapshots, store, diagnostics)

    assert "fuyao.snapshot.last_price" in store
    assert "fuyao.auction_final.auction_price" not in store
    assert any("stocks.*.auction_final" in item for item in diagnostics)
    assert any("source_data_date_unavailable" in item for item in diagnostics)
    assert any("response_timestamp" in item for item in diagnostics)
    assert any("response_timestamp_date='2026-09-29'" in item for item in diagnostics)
    assert any("not_exposed_by_auction_snapshot_contract" in item for item in diagnostics)
    report = collide.build_report_md(
        "20260929", [], len(store), 1, [], [], [], 0, set(), [], diagnostics=diagnostics
    )
    assert "source_data_date_unavailable" in report


def test_report_separates_registered_mapping_revalidations_from_new_candidates():
    actionable = {
        "left": "zhb.full.new_metric",
        "right": "tencent[99]",
        "level": "L1",
        "overall_hit": 0.95,
        "n_days": 3,
        "n_pairs": 60,
        "n_informative_pairs": 54,
        "ratio": None,
        "hub_flag": False,
        "in_registry": False,
        "same_code": False,
    }
    mapped = {
        **actionable,
        "left": "zhb.full.known_metric",
        "right": "tencent[41]",
        "in_registry": True,
    }

    report = collide.build_report_md(
        "20261018",
        ["20261016", "20261017", "20261018"],
        2,
        60,
        [actionable["left"]],
        [actionable, mapped],
        [],
        1,
        set(),
        [],
    )

    assert "可审定新候选=1" in report
    assert "首次发现新候选对=1" in report
    assert "已登记关系复验=1" in report
    assert "`zhb.full.new_metric`" in report
    assert "## 三、已登记映射的本窗口复验（1）" in report
    assert report.index("zhb.full.known_metric") > report.index("## 三、已登记映射的本窗口复验")


def test_context_records_are_excluded_by_default_and_available_on_request(tmp_path):
    folder = tmp_path / "20260929"
    folder.mkdir()
    source_documents = {
        "market_sources": {
            "scheme": "market_sources",
            "kpl_sentiment": [{"code": "600000", "sentiment_metric": 0.5}],
            "dragon_tiger_today": [{"SECURITY_CODE": "600000", "context_amount": 11.0}],
        },
        "exchange": {
            "scheme": "exchange",
            "records": [{"zqdm": "600000", "context_amount": 12.0}],
        },
        "em_hot": {
            "scheme": "em_hot",
            "hot_rank": [{"ticker": "600000", "heat_score": 13.0}],
        },
        "fuyao": {
            "scheme": "fuyao",
            "stocks": {"600000": {"snapshot": {"last_price": 10.0}}},
            "market": {
                "dragon_tiger": [{"ticker": "600000", "context_amount": 14.0}],
                "hot_list_hour": [{"ticker": "600000", "heat_score": 15.0}],
                "h1_indicators_ready": True,
            },
        },
    }
    for source, document in source_documents.items():
        (folder / f"raw_{source}.json").write_text(json.dumps(document), encoding="utf-8")
    (folder / "meta.json").write_text(
        json.dumps(
            {
                "capture_date": "20260929",
                "data_date": "20260929",
                "sources": {
                    source: {
                        "ok": True,
                        "status": "context_only" if source in {"exchange", "em_hot"} else "ok",
                        "scheme": source,
                    }
                    for source in source_documents
                },
            }
        ),
        encoding="utf-8",
    )
    folders, _ = collision_dates.discover_capture_folders(
        str(tmp_path), lambda day: day.weekday() < 5
    )
    snapshots, _ = collision_dates.select_snapshots(folders)

    default_store = defaultdict(lambda: {"vals": {}, "sample_meta": {}, "src": None})
    default_diagnostics = []
    collide.load_snapshots(snapshots, default_store, default_diagnostics)

    assert "fuyao.snapshot.last_price" in default_store
    assert any(key.endswith("sentiment_metric") for key in default_store)
    assert not any("context_amount" in key or "heat_score" in key for key in default_store)
    assert any("exchange" in item and "默认策略排除" in item for item in default_diagnostics)
    assert any("em_hot" in item and "默认策略排除" in item for item in default_diagnostics)
    assert any("dragon_tiger_today" in item for item in default_diagnostics)

    context_store = defaultdict(lambda: {"vals": {}, "sample_meta": {}, "src": None})
    collide.load_snapshots(snapshots, context_store, [], include_context=True)

    assert any("context_amount" in key for key in context_store)
    assert any("heat_score" in key for key in context_store)


def test_ftshare_limit_up_context_uses_record_trade_date_and_stock_symbol(tmp_path):
    folder = tmp_path / "20260828"
    folder.mkdir()
    document = {
        "scheme": "ftshare",
        "stocks": {},
        "market": {
            "limit_up_pool_yesterday": [
                {
                    "symbol": "000017.XSHE",
                    "trade_date": "20260827",
                    "limit_up_break": ["09:32:45"],
                    "limit_up_enter": [],
                    "ready": True,
                },
                {
                    "symbol": "000018.XSHE",
                    "trade_date": "20260826",
                    "limit_up_break": ["09:33:15"],
                    "limit_up_enter": [],
                    "ready": False,
                },
            ]
        },
    }
    (folder / "raw_ftshare.json").write_text(json.dumps(document), encoding="utf-8")
    (folder / "meta.json").write_text(
        json.dumps(
            {
                "capture_date": "20260828",
                "data_date": "20260828",
                "sources": {"ftshare": {"ok": True, "status": "ok", "scheme": "ftshare"}},
            }
        ),
        encoding="utf-8",
    )
    folders, _ = collision_dates.discover_capture_folders(
        str(tmp_path), lambda day: day.weekday() < 5
    )
    snapshots, _ = collision_dates.select_snapshots(folders)

    default_store = defaultdict(lambda: {"vals": {}, "sample_meta": {}, "src": None})
    collide.load_snapshots(snapshots, default_store, [])
    assert not any(key.startswith("ftshare.") for key in default_store)

    context_store = defaultdict(lambda: {"vals": {}, "sample_meta": {}, "src": None})
    diagnostics = []
    collide.load_snapshots(
        snapshots,
        context_store,
        diagnostics,
        include_context=True,
        allowed_trading_dates={"20260827"},
    )

    field = context_store["ftshare.limit_up_break"]
    key = ("000017", "T:20260827")
    assert field["vals"][key] == '["09:32:45"]'
    assert context_store["ftshare.limit_up_enter"]["vals"][key] == "[]"
    assert context_store["ftshare.ready"]["vals"][key] == "true"
    assert field["sample_meta"][key]["as_of_date"] == "20260827"
    assert field["sample_meta"][key]["as_of_date_origin"] == "record.trade_date"
    assert not any(("000018", "T:20260826") in row["vals"] for row in context_store.values())
    assert any("市场记录不在所选交易日窗口内" in item for item in diagnostics)


def _field(values, source):
    return {
        "vals": values,
        "src": source,
        "is_constant": False,
        "sample_meta": {key: {"phase": phase} for key, phase in values.pop("_phases", {}).items()},
    }


def _daily_fields(days, codes=20, ratio=1.0, intraday_days=()):
    left = {}
    right = {}
    phases = {}
    for day_index, day in enumerate(days):
        for code_index in range(codes):
            key = (f"{code_index:06d}", f"T:{day}")
            value = code_index + 1 + day_index * codes
            left[key] = value
            right[key] = value * ratio
            phases[key] = "intraday" if day in intraday_days else "closed"
    left["_phases"] = phases.copy()
    right["_phases"] = phases.copy()
    return _field(left, "tdx"), _field(right, "sina")


def test_l1_requires_minimum_samples_on_each_independent_day():
    left, right = _daily_fields(["20260924", "20260928", "20260929"], codes=18)

    result = collide.collide_pair(left, right)

    assert result["level"] == "L1"
    assert result["n_days"] == 3
    assert set(result["daily_sample_counts"].values()) == {18}
    assert set(result["daily_informative_sample_counts"].values()) == {18}


def test_l1_zero_and_missing_coincidences_do_not_meet_informative_floor():
    left, right = _daily_fields(["20260924", "20260928", "20260929"], codes=20)
    for key in left["vals"]:
        code_index = int(key[0])
        if code_index < 16:
            left["vals"][key] = 0
            right["vals"][key] = 0
        elif code_index == 16:
            left["vals"][key] = None
            right["vals"][key] = None

    result = collide.collide_pair(left, right)

    assert result is not None
    assert result["level"] == "L4"
    assert set(result["daily_sample_counts"].values()) == {20}
    assert set(result["daily_informative_sample_counts"].values()) == {3}


def test_l1_uses_informative_hit_rate_after_daily_sample_floor():
    left, right = _daily_fields(["20260924", "20260928", "20260929"], codes=20)
    for key in left["vals"]:
        if int(key[0]) < 15:
            left["vals"][key] = 0
            right["vals"][key] = 0

    result = collide.collide_pair(left, right)

    assert result["level"] == "L1"
    assert set(result["daily_sample_counts"].values()) == {20}
    assert set(result["daily_informative_sample_counts"].values()) == {5}
    assert result["n_pairs"] == 60
    assert result["n_informative_pairs"] == 15


def test_below_daily_sample_floor_cannot_reach_l1():
    left, right = _daily_fields(["20260924", "20260928", "20260929"], codes=17)

    result = collide.collide_pair(left, right)

    assert result is not None
    assert result["level"] == "L4"
    assert result["n_days"] == 3


def test_intraday_samples_do_not_count_toward_l1_days():
    left, right = _daily_fields(
        ["20260924", "20260928", "20260929"],
        codes=20,
        intraday_days={"20260929"},
    )

    result = collide.collide_pair(left, right)

    assert result is not None
    assert result["level"] == "L4"
    assert result["excluded_intraday_pairs"] == 20


def test_unknown_phase_samples_do_not_count_toward_l1():
    left, right = _daily_fields(["20260924", "20260928", "20260929"])
    for info in (left, right):
        info["sample_meta"] = {key: {"phase": "unknown"} for key in info["vals"]}

    result = collide.collide_pair(left, right)

    assert result is not None
    assert result["level"] == "L4"
    assert result["excluded_unknown_phase_pairs"] == 60


def test_trading_and_calendar_dates_cannot_align_as_same_sample():
    left = _field({(str(i), "T:20260929"): i + 1 for i in range(20)}, "tdx")
    right = _field({(str(i), "C:20260929"): i + 1 for i in range(20)}, "reports")

    assert collide.collide_pair(left, right) is None


def test_ratio_family_requires_three_full_days_and_is_l1u():
    left, right = _daily_fields(["20260924", "20260928", "20260929"], codes=20, ratio=100.0)

    result = collide.collide_pair(left, right)

    assert result["level"] == "L1-U"
    assert result["ratio"] == 100
    assert result["n_days"] == 3


def test_known_mirror_sources_do_not_count_as_independent_evidence():
    assert collide.evidence_source_family("push2.f43") == "eastmoney"
    assert collide.evidence_source_family("push2_full.f43") == "eastmoney"
    assert collide.evidence_source_family("em_fund_flow.f137") == "eastmoney"
    assert not collide.are_independent_sources("push2.f43", "push2_full.f43")
    assert not collide.are_independent_sources("push2.f137", "em_fund_flow.f137")
    assert collide.are_independent_sources("push2.f43", "tencent[4]")
    assert collide.evidence_source_family("tencent[4]") != "push2"


def test_unknown_source_lineage_is_not_independent_evidence():
    assert collide.evidence_source_family("unregistered_source.some_field") is None
    assert not collide.are_independent_sources("unregistered_source.some_field", "tencent[4]")


def test_registry_verified_identity_keeps_full_nested_code_path():
    context = collide.load_registry_context()
    verified = context["verified"]
    anchors = context["anchors"]

    assert ("tdx", "quote_full.amount_wan") in verified
    assert ("tdx", "quote_full.amount_wan") in anchors
    assert collide.is_verified("tdx.quote_full.amount_wan", verified)
    assert not collide.is_verified("tdx.amount_wan", verified)
    assert ("zhb", "stat.board_count") in verified
    assert collide.is_verified("zhb.stat.board_count", verified)
    assert not collide.is_verified("zhb.board_count", verified)


def test_code_of_preserves_full_nested_identity():
    assert collide.code_of("tdx.quote_full.amount_wan") == "quote_full.amount_wan"
    assert collide.code_of("zhb.stat.board_count") == "stat.board_count"
    assert collide.code_of("tencent[4]") == "[4]"
    assert collide.code_of("zhb.full.change_5d") == "change_5d"
    assert collide.code_of("zhb.stat.change_5d") == "stat.change_5d"
    assert collide.code_of("zhb.stat2.low_52w") == "stat2.low_52w"


def test_zhb_merged_field_paths_match_existing_registry_mappings():
    context = collide.load_registry_context()

    left = (collide.alias_src("zhb.full.change_5d"), collide.code_of("zhb.full.change_5d"))
    right = (collide.alias_src("ulist239.f109"), collide.code_of("ulist239.f109"))

    assert left == ("zhb", "change_5d")
    assert (left + right) in context["known_mappings"]


def test_duplicate_runtime_alias_code_is_not_used_as_a_verified_anchor(monkeypatch, tmp_path):
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "source_fields": [
                    {
                        "source": "ZHB-a",
                        "code": "shared",
                        "status": "verified",
                        "meaning": "shared field",
                    },
                    {
                        "source": "ZHB-b",
                        "code": "shared",
                        "status": "unverified",
                        "meaning": "shared field",
                    },
                ],
                "mappings": [],
            }
        ),
        encoding="utf-8",
    )
    lineage = {
        "sources": {
            "ZHB-a": {
                "runtime_aliases": ["zhb"],
                "anchor_eligible": True,
                "independence_status": "confirmed",
                "independence_family": "tdx",
            },
            "ZHB-b": {
                "runtime_aliases": ["zhb"],
                "anchor_eligible": True,
                "independence_status": "confirmed",
                "independence_family": "tdx",
            },
        },
        "runtime_sources": {
            "zhb": {"independence_status": "confirmed", "independence_family": "tdx"}
        },
        "source_aliases": {},
    }
    monkeypatch.setattr(collide, "REG_PATH", str(registry_path))
    monkeypatch.setattr(collide.SLA, "load_source_lineage", lambda registry=None: lineage)

    context = collide.load_registry_context()

    assert context["safe_to_run"] is True
    assert ("zhb", "shared") not in context["verified"]
    assert ("zhb", "shared") not in context["anchors"]
    assert context["ambiguous_verified"] == 1


def test_verified_fields_with_unresolved_semantics_are_not_known_or_anchors(monkeypatch, tmp_path):
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "source_fields": [
                    {
                        "source": "ZHB-test",
                        "code": "clear",
                        "status": "verified",
                        "meaning": "清晰含义",
                    },
                    {"source": "ZHB-test", "code": "missing", "status": "verified"},
                    {
                        "source": "ZHB-test",
                        "code": "placeholder",
                        "status": "verified",
                        "meaning": "待破解",
                    },
                    {
                        "source": "ZHB-test",
                        "code": "meaning_conflict",
                        "status": "verified",
                        "meaning": "含义甲",
                        "attribute_conflicts": {"meaning": ["含义甲", "含义乙"]},
                    },
                    {
                        "source": "ZHB-test",
                        "code": "unit_conflict",
                        "status": "verified",
                        "meaning": "明确含义",
                        "attribute_conflicts": {"unit": ["元", "万元"]},
                    },
                    {
                        "source": "ZHB-test",
                        "code": "alignment_ambiguity",
                        "status": "verified",
                        "meaning": "",
                        "attribute_ambiguities": {"meaning": ["字段甲/字段乙"]},
                    },
                    {
                        "source": "ZHB-test",
                        "code": "canonical_alias_only",
                        "status": "verified",
                        "meaning": "明确含义",
                        "attribute_conflicts": {"canonical": ["alias_a", "alias_b"]},
                    },
                ],
                "mappings": [],
            }
        ),
        encoding="utf-8",
    )
    lineage = {
        "sources": {
            "ZHB-test": {
                "runtime_aliases": ["zhb"],
                "anchor_eligible": True,
                "independence_status": "confirmed",
                "independence_family": "tdx",
            }
        },
        "runtime_sources": {
            "zhb": {"independence_status": "confirmed", "independence_family": "tdx"}
        },
        "source_aliases": {},
    }
    monkeypatch.setattr(collide, "REG_PATH", str(registry_path))
    monkeypatch.setattr(collide.SLA, "load_source_lineage", lambda registry=None: lineage)

    context = collide.load_registry_context()

    assert context["safe_to_run"] is True
    assert ("zhb", "clear") in context["verified"]
    assert ("zhb", "clear") in context["anchors"]
    assert ("zhb", "canonical_alias_only") in context["verified"]
    assert ("zhb", "canonical_alias_only") in context["anchors"]
    for code in (
        "missing",
        "placeholder",
        "meaning_conflict",
        "unit_conflict",
        "alignment_ambiguity",
    ):
        assert ("zhb", code) not in context["verified"]
        assert ("zhb", code) not in context["anchors"]
    assert context["unresolved_verified_metadata"] == 5


def test_default_field_selection_uses_only_verified_independent_anchors():
    store = {
        field_id: {
            "is_identifier": False,
            "is_constant": False,
            "type": "num",
        }
        for field_id in (
            "tdx.quote_full.amount_wan",
            "tdx.amount_wan",
            "sina.amount_wan",
            "tdx.disproved_field",
        )
    }
    verified = {("tdx", "quote_full.amount_wan")}
    anchors = {("tdx", "quote_full.amount_wan")}
    disproved = {("tdx", "disproved_field")}

    left, right = collide.select_collision_fields(
        store, verified, disproved, anchors, exploratory=False
    )

    assert left == ["tdx.amount_wan", "sina.amount_wan"]
    assert right == ["tdx.quote_full.amount_wan"]


def test_exploratory_selection_includes_unknowns_but_does_not_promote_matches():
    store = {
        field_id: {"is_identifier": False, "is_constant": False, "type": "num"}
        for field_id in ("tdx.unknown", "sina.unknown", "tdx.disproved")
    }

    left, right = collide.select_collision_fields(
        store,
        verified=set(),
        disproved={("tdx", "disproved")},
        anchors=set(),
        exploratory=True,
    )
    result = {"level": "L1-U"}

    assert left == ["tdx.unknown", "sina.unknown"]
    assert right == ["tdx.unknown", "sina.unknown"]
    assert collide.mark_exploratory_candidate(result, right_is_anchor=False)
    assert result == {"level": "L4", "exploratory": True}


def test_verified_anchor_candidate_is_not_downgraded():
    result = {"level": "L1"}

    assert not collide.mark_exploratory_candidate(result, right_is_anchor=True)
    assert result == {"level": "L1"}


def test_missing_registry_disables_collision_context(monkeypatch, tmp_path):
    monkeypatch.setattr(collide, "REG_PATH", str(tmp_path / "missing_registry.json"))

    context = collide.load_registry_context()

    assert context["safe_to_run"] is False
    assert context["verified"] == set()
    assert context["anchors"] == set()
    assert context["diagnostics"]


def test_collision_gate_rejects_same_source_mirror_fields():
    left, right = _daily_fields(["20260924", "20260928", "20260929"])
    left["src"] = "push2"
    right["src"] = "push2_full"

    assert collide.collide_pair(left, right) is None


def test_missing_source_provenance_cannot_create_l1():
    left, right = _daily_fields(["20260924", "20260928", "20260929"])
    right["src"] = ""

    result = collide.collide_pair(left, right)

    assert result is not None
    assert result["level"] == "L4"


def test_method_candidates_keep_metrics_dates_and_source_provenance():
    left_values = {}
    right_values = {}
    for index in range(20):
        key = (f"{index:06d}", "T:20260929")
        left_values[key] = index + 1
        right_values[key] = 2 * (index + 1) + 3
    left = _field(left_values, "tdx")
    right = _field(right_values, "sina")

    candidate = collide.method_candidates_for_pair(
        "tdx.close_price", "sina.close_price", left, right
    )

    assert candidate is not None
    methods = {method["method"] for method in candidate["methods"]}
    assert {"robust_correlation", "affine_formula", "semantic_label"} <= methods
    assert candidate["sample_dates"] == ["T:20260929"]
    assert candidate["evidence_sources"] == ["sina", "tdx"]


def test_range_disjoint_unit_conversion_pairs_remain_eligible_for_analysis(monkeypatch):
    left, right = _daily_fields(["20260924", "20260928", "20260929"], ratio=10_000)
    right["src"] = "tencent"
    monkeypatch.setattr(collide, "are_independent_sources", lambda _left, _right: True)
    store = {"tdx.finance_info.zhongguben": left, "tencent[73]": right}
    collide.classify(store)

    eligible, reason = collide._pair_analysis_eligibility(left, right)
    candidate = collide.method_candidates_for_pair(
        "tdx.finance_info.zhongguben", "tencent[73]", left, right
    )
    result = collide.collide_pair(left, right)

    assert left["vmax"] < right["vmin"]
    assert eligible is True
    assert reason == "range_disjoint"
    assert candidate is not None
    assert result is not None
    assert result["level"] == "L1-U"
    assert result["ratio"] == 10_000


def test_known_mapping_control_evaluates_range_disjoint_unit_conversions(monkeypatch):
    left, right = _daily_fields(["20260924", "20260928", "20260929"], ratio=10_000)
    right["src"] = "tencent"
    monkeypatch.setattr(collide, "are_independent_sources", lambda _left, _right: True)
    store = {"tdx.zongguben": left, "tencent[73]": right}
    collide.classify(store)
    mappings = {("tdx", "zongguben", "tencent", "[73]")}

    positive = collide._known_mapping_candidate_controls(store, mappings)["positive_control"]

    assert positive["eligible_numeric_pairs"] == 1
    assert positive["range_disjoint_pairs"] == 1
    assert positive["with_method_signal"] == 1


def test_candidate_frontier_preserves_a_best_candidate_per_target():
    def candidate(left, right, sample_count):
        return {
            "left": left,
            "right": right,
            "methods": [{"method": "robust_correlation", "pearson": 0.99}],
            "sample_count": sample_count,
            "sample_dates": ["T:20261019"],
            "evidence_sources": ["source-a", "source-b"],
            "sample_codes": ["600000"],
        }

    first = candidate("unknown.a", "anchor.a1", 50)
    omitted_for_a = candidate("unknown.a", "anchor.a2", 40)
    omitted_for_b = candidate("unknown.b", "anchor.b1", 35)
    by_left = {
        "unknown.a": [first, omitted_for_a],
        "unknown.b": [omitted_for_b],
    }

    frontier = collide.select_method_candidate_frontier(by_left, [first])

    assert {(row["left"], row["right"]) for row in frontier} == {
        ("unknown.a", "anchor.a2"),
        ("unknown.b", "anchor.b1"),
    }


def test_candidate_summary_preserves_method_specific_evidence():
    method = {
        "method": "per_stock_time_series",
        "median_abs_pearson": 0.91,
        "sign_consistency": 1.0,
        "stocks": 8,
        "sample_dates": ["T:20261009", "T:20261012", "T:20261013"],
        "stock_correlations": [{"code": f"600{index:03d}", "pearson": 0.9} for index in range(8)],
    }
    candidate = {
        "left": "unknown.field",
        "right": "anchor.field",
        "methods": [method],
        "sample_count": 24,
        "sample_dates": method["sample_dates"],
        "evidence_sources": ["anchor"],
    }

    summary = collide._method_candidate_summary(candidate)

    assert summary["methods"][0]["sample_dates"] == method["sample_dates"]
    assert summary["methods"][0]["median_abs_pearson"] == 0.91
    assert len(summary["methods"][0]["stock_correlations"]) == 5


def test_formula_candidates_require_out_of_stock_validation():
    random = __import__("random").Random(20261020)
    left_values = {}
    price_values = {}
    shares_values = {}
    days = ("20261009", "20261012", "20261013", "20261014")
    for stock_index in range(20):
        code = f"600{stock_index:03d}"
        shares = random.uniform(10, 1000)
        for day in days:
            key = (code, f"T:{day}")
            price = random.uniform(5, 200)
            price_values[key] = price
            shares_values[key] = shares
            left_values[key] = price * shares * 1000 + 2

    def numeric_field(values, source):
        return {
            "vals": values,
            "src": source,
            "type": "num",
            "sample_meta": {key: {"phase": "closed"} for key in values},
        }

    store = {
        "unknown.target": numeric_field(left_values, "unknown"),
        "tencent.price": numeric_field(price_values, "tencent"),
        "fuyao.shares": numeric_field(shares_values, "fuyao"),
    }
    formulas, stats = collide.formula_candidates_for_target(
        "unknown.target",
        store,
        [{"right": "tencent.price"}, {"right": "fuyao.shares"}],
    )

    assert stats["tested"] > 0
    assert formulas
    assert formulas[0]["operator"] == "product"
    assert formulas[0]["validation_r2"] >= 0.985
    assert formulas[0]["adjudication_status"] == "candidate_only"


def test_discriminating_sample_prefers_stock_with_out_of_sample_disagreement():
    left_values = {}
    first_values = {}
    second_values = {}
    days = ("20261009", "20261012", "20261013")
    for stock_index in range(20):
        code = f"600{stock_index:03d}"
        for day_index, day in enumerate(days):
            key = (code, f"T:{day}")
            value = 100 + stock_index * 50 + day_index * 3
            left_values[key] = value
            first_values[key] = value
            second_values[key] = value + (500 if stock_index == 0 else 0)

    def numeric_field(values, source):
        return {
            "vals": values,
            "src": source,
            "type": "num",
            "sample_meta": {key: {"phase": "closed"} for key in values},
        }

    store = {
        "unknown.target": numeric_field(left_values, "unknown"),
        "anchor.first": numeric_field(first_values, "anchor-a"),
        "anchor.second": numeric_field(second_values, "anchor-b"),
    }

    suggestion = collide.discriminating_sample_for_target(
        "unknown.target",
        store,
        [{"right": "anchor.first"}, {"right": "anchor.second"}],
    )

    assert suggestion["status"] == "prioritize_recheck"
    assert suggestion["stock_code"] == "600000"
    assert suggestion["normalized_prediction_spread"] > 0.02


def test_local_field_coverage_index_maps_status_and_date_evidence(tmp_path, monkeypatch):
    old_folder = tmp_path / "docs" / "field_verification" / "20261012"
    old_folder.mkdir(parents=True)
    (old_folder / "meta.json").write_text(
        json.dumps(
            {
                "data_date": "2026-10-12",
                "sources": {"foo": {"status": "blocked"}},
            }
        ),
        encoding="utf-8",
    )
    folder = tmp_path / "docs" / "field_verification" / "20261019"
    folder.mkdir(parents=True)
    coverage_dir = tmp_path / ".tmp" / "field_evidence_coverage"
    coverage_dir.mkdir(parents=True)
    meta = {
        "data_date": "2026-10-19",
        "sources": {"foo": {"status": "partial"}},
        "field_evidence_coverage": {"report_date": "2026-10-19", "status": "ok"},
    }
    coverage = {
        "fields": [
            {
                "source": "Foo",
                "code": "bar",
                "registry_status": "unverified",
                "identity_status": "mapped",
                "runtime_aliases": ["foo"],
                "independence_family": "family-b",
                "independence_status": "confirmed",
                "anchor_eligible": True,
                "source_as_of_days": ["T:20261019"],
                "candidate_days": ["T:20261019"],
                "source_as_of_sample_counts": {"T:20261019": 20},
                "source_statuses": ["ok"],
            }
        ]
    }
    (folder / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    (coverage_dir / "coverage_20261019.json").write_text(json.dumps(coverage), encoding="utf-8")
    monkeypatch.setattr(collide, "ROOT", str(tmp_path))

    index = collide.load_field_coverage_index(
        [
            str(old_folder),
            collision_dates.CaptureFolder(
                name=folder.name,
                path=str(folder),
                folder_date=date(2026, 10, 19),
                capture_date=date(2026, 10, 19),
                market_date=date(2026, 10, 19),
                meta=meta,
                market_date_origin="meta.data_date",
            ),
        ],
        ["2026-10-19"],
        date(2026, 10, 13),
        date(2026, 10, 19),
    )
    target = collide._coverage_records_for_target("foo.bar", index)

    assert index["summary"]["detail_status"] == "available"
    assert index["source_statuses"]["foo"]["non_ok_dates"] == ["20261019"]
    assert target["source_count"] == 1
    assert "independent_anchor_families" not in target
    assert target["source_as_of_days"] == ["T:20261019"]


def test_candidate_triage_uses_actual_independent_anchor_comparisons():
    triage = collide.build_candidate_triage(
        ["unknown.target"],
        {},
        {"unknown.target": {"independent_pairs": 2}},
        {},
        {"records": {}, "summary": {"coverage_detail_files": 1}},
        {},
        {},
        {"unknown.target": {"family-a": 2, "family-b": 1}},
    )

    target = triage["targets"][0]
    assert target["coverage"]["independent_anchor_families"] == ["family-a", "family-b"]
    assert target["coverage"]["independent_anchor_pairs"] == 3
    assert triage["summary"]["targets_with_independent_anchor_coverage"] == 1


def test_candidate_triage_markdown_renders_evidence_and_control_summaries():
    triage = {
        "summary": {
            "target_count": 1,
            "targets_with_method_candidates": 1,
            "targets_without_method_candidates": 0,
            "targets_with_multiple_candidates": 1,
            "candidate_pairs_generated": 4,
            "global_details_retained": 2,
            "global_detail_limit": 500,
            "field_frontier_details_retained": 1,
            "candidate_pairs_without_full_detail": 0,
            "method_candidate_inventory_count": 3,
            "candidate_pairs_outside_primary_and_frontier": 1,
            "field_coverage": {"detail_status": "available", "coverage_identity_count": 1},
            "formula_combinations_tested": 5,
            "capture_source_statuses": {
                "source-a": {"non_ok_dates": ["20261019"], "status_counts": {"partial": 1}}
            },
        },
        "targets": [
            {
                "left": "unknown.field",
                "status": "multiple_method_candidates_need_discrimination",
                "candidate_count": 2,
                "pair_counts": {"independent_pairs": 3},
                "top_candidates": [
                    {
                        "right": "anchor.field",
                        "methods": [{"method": "robust_correlation", "pearson": 0.99}],
                    }
                ],
                "formula_candidates": [],
                "next_sample": {
                    "status": "prioritize_recheck",
                    "stock_code": "600000",
                    "normalized_prediction_spread": 0.2,
                },
                "coverage": {
                    "status": "available",
                    "independent_anchor_families": ["family-a"],
                    "independent_anchor_pairs": 3,
                    "source_as_of_days": ["T:20261019"],
                },
            }
        ],
    }
    frontier = [
        {
            "left": "unknown.field",
            "right": "anchor.field",
            "methods": [{"method": "affine_formula"}],
            "sample_count": 42,
            "sample_dates": ["T:20261019"],
            "evidence_sources": ["family-a", "family-b"],
        }
    ]
    formulas = [
        {
            "left": "unknown.field",
            "formula": "unknown.field ≈ x × (a × b) + y",
            "validation_r2": 0.99,
            "normalized_rmse": 0.01,
            "validation_samples": 10,
            "validation_stocks": 4,
        }
    ]
    controls = {
        "positive_control": {
            "eligible_numeric_pairs": 2,
            "with_method_signal": 1,
            "insufficient_numeric_samples": 0,
        },
        "negative_control": {"numeric_refuted_pairs": 1, "with_method_signal": 1},
    }

    rendered = collide.append_candidate_triage_report(
        "# collision report", triage, frontier, formulas, controls
    )

    assert "候选覆盖、公式与下一步采样" in rendered
    assert "补足全局截断的字段候选" in rendered
    assert "双输入公式候选" in rendered
    assert "source-a" in rendered
    assert "600000" in rendered
    assert "已证伪负向对照" in rendered
    assert "完整明细 3 条" in rendered


def test_report_completeness_reconciles_full_candidate_inventory_and_markdown_caps():
    inventory = [{"left": "unknown.field", "right": f"anchor.{index}"} for index in range(501)]
    targets = [
        {"left": f"unknown.{index}", "candidate_count": 501 if index == 0 else 0}
        for index in range(51)
    ]
    report = {
        "L1": [],
        "L1-C": [],
        "source_coverage": [],
        "actionable_L1": [],
        "mapped_pair_revalidations": [],
        "L4": [{} for _ in range(61)],
        "guardrail_hits": [{}],
        "method_candidates": inventory[:500],
        "method_candidate_count": 501,
        "method_candidate_inventory": inventory,
        "method_candidate_frontier": [],
        "candidate_triage": {"summary": {"target_count": 51}, "targets": targets},
        "formula_candidates": [{} for _ in range(51)],
        "diagnostics": ["warning"] * 101,
        "source_identity_reconciliation": {"status": "ok", "endpoints": {"ep": {}}},
    }

    completeness = collide.build_report_completeness(report)
    markdown = collide.append_report_completeness_report("# Report", completeness)

    assert completeness["status"] == "complete"
    assert completeness["method_candidate_inventory"]["generated_count"] == 501
    assert completeness["method_candidate_inventory"]["saved_count"] == 501
    assert completeness["method_candidate_inventory"]["missing_detail_count"] == 0
    assert completeness["method_candidate_inventory"]["target_candidate_count_sum"] == 501
    assert completeness["sections"]["method_candidates"]["json_record_count"] == 500
    assert completeness["sections"]["guardrail_hits"]["json_record_count"] == 1
    assert completeness["sections"]["source_identity_reconciliation"]["detail_scope"].startswith(
        "完整 JSON 顶层内容"
    )
    omissions = {
        row["section"]: row["omitted_from_markdown"] for row in completeness["markdown_omissions"]
    }
    assert omissions["L4"] == 1
    assert omissions["method_candidates"] == 400
    assert omissions["method_candidate_inventory"] == 501
    assert omissions["candidate_triage.targets"] == 1
    assert omissions["formula_candidates"] == 1
    assert omissions["diagnostics"] == 1
    assert "全量方法候选位于同名 JSON" in markdown
    assert "Markdown 未逐行展示" in markdown


def test_report_completeness_blocks_a_missing_method_candidate_detail():
    report = {
        "L1": [],
        "L1-C": [],
        "source_coverage": [],
        "actionable_L1": [],
        "mapped_pair_revalidations": [],
        "L4": [],
        "guardrail_hits": [],
        "method_candidates": [],
        "method_candidate_count": 2,
        "method_candidate_inventory": [{"left": "unknown.a", "right": "anchor.a"}],
        "method_candidate_frontier": [],
        "candidate_triage": {"summary": {"target_count": 0}, "targets": []},
        "formula_candidates": [],
        "diagnostics": [],
    }

    completeness = collide.build_report_completeness(report)
    markdown = collide.append_report_completeness_report("# Report", completeness)

    assert completeness["status"] == "incomplete"
    assert completeness["method_candidate_inventory"]["missing_detail_count"] == 1
    assert "审阅阻断" in markdown


def test_report_completeness_blocks_duplicate_candidate_pairs():
    candidate = {"left": "unknown.a", "right": "anchor.a"}
    report = {
        "L1": [],
        "L1-C": [],
        "source_coverage": [],
        "actionable_L1": [],
        "mapped_pair_revalidations": [],
        "L4": [],
        "guardrail_hits": [],
        "method_candidates": [candidate, candidate],
        "method_candidate_count": 2,
        "method_candidate_inventory": [candidate, candidate],
        "method_candidate_frontier": [],
        "candidate_triage": {
            "summary": {"target_count": 1},
            "targets": [{"left": "unknown.a", "candidate_count": 2}],
        },
        "formula_candidates": [],
        "diagnostics": [],
    }

    completeness = collide.build_report_completeness(report)

    assert completeness["status"] == "incomplete"
    assert completeness["method_candidate_inventory"]["duplicate_pair_count"] == 1


def test_source_coverage_reports_contract_evidence_and_actual_pair_participation():
    tdx_key = ("600000", "T:20261019")
    fuyao_key = ("600000", "T:20261019")
    store = {
        "tdx.f1": {
            "vals": {tdx_key: 10.0},
            "sample_meta": {tdx_key: {"domain": "trading", "as_of_date": "20261019"}},
        },
        "fuyao.snapshot.close": {
            "vals": {fuyao_key: 10.0},
            "sample_meta": {fuyao_key: {"domain": "trading", "as_of_date": "20261019"}},
        },
    }
    coverage = collide.build_source_coverage_report(
        store=store,
        verified={("fuyao", "snapshot.close"), ("ftshare_rest", "close")},
        anchors={("fuyao", "snapshot.close")},
        contract_anchors={("ftshare_rest", "close")},
        official_contract_verified={("fuyao", "snapshot.close"), ("ftshare_rest", "close")},
        official_contract_anchors={("fuyao", "snapshot.close"), ("ftshare_rest", "close")},
        left_ids=["tdx.f1"],
        right_ids=["fuyao.snapshot.close", "ftshare_rest.close"],
        pair_evaluations_by_source={
            "tdx": {"as_target": 2},
            "fuyao": {"as_right_field": 1},
            "ftshare_rest": {"as_right_field": 1, "l1c_anchor": 1},
        },
        l1_relations=[{"left": "tdx.f1", "right": "fuyao.snapshot.close"}],
        l1_contract_relations=[{"left": "tdx.f2", "right": "ftshare_rest.close"}],
        l4_relations=[{"left": "tdx.f3", "right": "fuyao.snapshot.close"}],
        method_candidate_inventory=[{"left": "tdx.f4", "right": "fuyao.snapshot.close"}],
    )
    by_source = {row["source"]: row for row in coverage}
    fuyao = by_source["fuyao"]
    ftshare = by_source["ftshare_rest"]

    assert fuyao["official_contract_verified_field_count"] == 1
    assert fuyao["independent_anchor_field_count"] == 1
    assert fuyao["contract_only_anchor_field_count"] == 0
    assert fuyao["observed_window_field_value_count"] == 1
    assert fuyao["observed_window_trading_day_count"] == 1
    assert fuyao["L1_relation_count"] == 1
    assert fuyao["L4_relation_count"] == 1
    assert ftshare["official_contract_anchor_field_count"] == 1
    assert ftshare["contract_only_anchor_field_count"] == 1
    assert ftshare["L1_C_anchor_comparisons"] == 1
    assert ftshare["L1_C_relation_count"] == 1

    rendered = collide.append_source_coverage_report("# Report", coverage)
    assert "来源字段覆盖与碰撞参与" in rendered
    assert "窗口字段 / 字段值样本 / 交易日" in rendered
    assert "fuyao" in rendered and "ftshare_rest" in rendered


def test_per_stock_time_series_is_an_explicit_candidate_method():
    left_values = {}
    right_values = {}
    for code_index in range(4):
        for day_index, day in enumerate(("20260924", "20260928", "20260929")):
            key = (f"{code_index:06d}", f"T:{day}")
            value = day_index + code_index + 1
            left_values[key] = value
            right_values[key] = value * 3 + 2
    left = _field(left_values, "tdx")
    right = _field(right_values, "sina")

    candidate = collide.method_candidates_for_pair("tdx.f1", "sina.f2", left, right)

    assert candidate is not None
    assert "per_stock_time_series" in {method["method"] for method in candidate["methods"]}


def test_linear_leave_one_out_matches_direct_recalculation():
    x_values = [1.0, 2.0, 3.0, 4.0, 100.0]
    y_values = [1.0, 2.0, 3.0, 4.0, -100.0]
    direct = [
        collide._pearson(
            x_values[:index] + x_values[index + 1 :], y_values[:index] + y_values[index + 1 :]
        )
        for index in range(len(x_values))
    ]
    direct = [value for value in direct if value is not None]

    result = collide._correlation_metrics(x_values, y_values)

    assert result is not None
    assert result["leave_one_out_sign_stable"] is False
    assert math.isclose(result["leave_one_out_min"], min(direct), rel_tol=1e-12)
    assert math.isclose(result["leave_one_out_max"], max(direct), rel_tol=1e-12)


def test_event_snapshots_keep_natural_dates_and_source_scoped_identity(tmp_path):
    folder = tmp_path / "20260929"
    folder.mkdir()
    (folder / "meta.json").write_text(
        '{"data_date":"20260929","capture_date":"20260930"}', encoding="utf-8"
    )
    documents = {
        "news_wscn_cctv": {"cctv_xwlb": [{"id": "1", "date": "2026-09-29", "title": "same"}]},
        "cls": {"news": [{"id": "1", "pub_time": "2026-09-29", "title": "same"}]},
    }
    for source, document in documents.items():
        (folder / f"raw_{source}.json").write_text(json.dumps(document), encoding="utf-8")

    folders, _ = collision_dates.discover_capture_folders(
        str(tmp_path), lambda day: day.weekday() < 5
    )
    snapshots, _ = collision_dates.select_snapshots(folders)
    store = defaultdict(lambda: {"vals": {}, "sample_meta": {}, "src": None})
    diagnostics = []
    collide.load_snapshots(
        snapshots,
        store,
        diagnostics,
        event_start=date(2026, 9, 29),
        event_end=date(2026, 9, 29),
    )

    news_values = store["news_wscn_cctv.title"]["vals"]
    cls_values = store["cls.title"]["vals"]
    assert len(news_values) == len(cls_values) == 1
    assert next(iter(news_values))[1] == "C:20260929"
    assert set(news_values) == set(cls_values)
    news_meta = next(iter(store["news_wscn_cctv.title"]["sample_meta"].values()))
    assert news_meta["as_of_date"] == "20260929"
    assert news_meta["capture_date"] == "20260930"

    cls_snapshot = next(snapshot for snapshot in snapshots if snapshot.source == "cls")
    cls_snapshot.document["news"][0]["title"] = "a different event"
    unmatched_store = defaultdict(lambda: {"vals": {}, "sample_meta": {}, "src": None})
    collide.load_snapshots(
        snapshots,
        unmatched_store,
        [],
        event_start=date(2026, 9, 29),
        event_end=date(2026, 9, 29),
    )
    assert (
        unmatched_store["news_wscn_cctv.title"]["vals"]
        .keys()
        .isdisjoint(unmatched_store["cls.title"]["vals"])
    )


def test_official_contract_anchor_rule_is_in_runtime_banner_and_generated_docs():
    generated_path = collision_rules.emit_markdown()
    rendered = Path(generated_path).read_text(encoding="utf-8")
    output = StringIO()

    collision_rules.print_active_rules(output)

    assert "## 三、官方契约语义锚候选 L1-C" in rendered
    assert "不计独立来源覆盖" in rendered
    assert "官方契约语义锚分支（参与碰撞，不代表来源独立）" in output.getvalue()
    assert "Fuyao" in output.getvalue()
    assert "不自动定案" in output.getvalue()


def test_ftshare_rest_source_status_separates_active_contract_and_retired_mcp():
    base_report = "## L1 候选\n\n保持原候选内容。"
    result = {"status": "active_with_historical_legacy", "active_runtime_source": "ftshare_rest"}

    report = collide.append_source_identity_report(base_report, result)

    assert report.startswith(base_report)
    assert "来源身份状态（不参与字段语义定案）" in report
    assert "已进入日常采集" in report
    assert "旧私有托管 MCP 采集器已退役" in report
