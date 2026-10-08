import math
import json
from collections import defaultdict
from datetime import date
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from scripts import collision_dates

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
            "response_timestamp": "2026-09-29T09:25:00",
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
    report = collide.build_report_md(
        "20260929", [], len(store), 1, [], [], [], 0, set(), [], diagnostics=diagnostics
    )
    assert "source_data_date_unavailable" in report


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
