import datetime as dt
import json
from types import SimpleNamespace

from scripts import field_evidence_coverage as coverage


def _lineage(*sources):
    source_records = {
        source: {
            "runtime_aliases": [alias],
            "independence_family": None,
            "independence_status": "unconfirmed",
            "anchor_eligible": False,
        }
        for source, alias in sources
    }
    aliases = {source: alias for source, alias in sources}
    return {
        "schema_version": 1,
        "sources": source_records,
        "runtime_sources": {alias: {} for _, alias in sources},
        "source_aliases": aliases,
    }


def _snapshot(source, document, *, domain="trading", origin="source_as_of", status="ok"):
    return SimpleNamespace(
        source=source,
        domain=domain,
        sample_date=dt.date(2026, 10, 14),
        capture_date=dt.date(2026, 10, 14),
        folder="20261014",
        path="raw.json",
        document=document,
        meta={"include_context": False, "sources": {source: {"scheme": document.get("scheme")}}},
        phase="closed",
        status=status,
        date_origin=origin,
        captured_at=None,
    )


def test_zhb_branches_map_exactly_and_merged_full_view_is_excluded():
    registry = {
        "source_fields": [
            {"source": "ZHB-tdxstat", "code": "[0]", "status": "unverified"},
            {"source": "ZHB-tdxstat2", "code": "[0]", "status": "unverified"},
            {"source": "ZHB-tipinfo", "code": "[0]", "status": "unverified"},
        ]
    }
    lineage = _lineage()
    lineage["runtime_sources"]["zhb"] = {}
    lineage["sources"].update(
        {
            "ZHB-tdxstat": {"runtime_aliases": ["zhb"]},
            "ZHB-tdxstat2": {"runtime_aliases": ["zhb"]},
            "ZHB-tipinfo": {"runtime_aliases": ["zhb"]},
        }
    )
    source_fields = registry["source_fields"]
    owners, source_records = coverage._identity_index(source_fields, lineage)

    identity, reason = coverage._resolve_runtime_identity(
        "zhb.stat.[0]", owners, source_records, lineage
    )
    merged_identity, merged_reason = coverage._resolve_runtime_identity(
        "zhb.full.[0]", owners, source_records, lineage
    )

    assert identity == ("ZHB-tdxstat", "[0]")
    assert reason == "mapped_by_explicit_branch"
    assert merged_identity is None
    assert merged_reason == "merged_zhb_full_view"


def test_same_runtime_code_owned_by_two_identities_is_not_counted():
    registry = {
        "source_fields": [
            {"source": "source-a", "code": "seal_amount", "status": "unverified"},
            {"source": "source-b", "code": "seal_amount", "status": "unverified"},
        ]
    }
    lineage = _lineage(("source-a", "kph"), ("source-b", "kph"))
    snapshot = _snapshot(
        "kph",
        {"scheme": "kph.history", "stocks": {"600000": {"seal_amount": 12.0}}},
    )

    result = coverage.build_field_coverage(
        [snapshot],
        registry,
        lineage,
        dt.date(2026, 10, 14),
        trading_window_dates=[dt.date(2026, 10, 14)],
    )

    assert result["summary"]["ambiguous_targets"] == 2
    assert result["summary"]["targets_observed"] == 0
    assert all(row["candidate_day_count"] == 0 for row in result["fields"])
    assert any("ambiguous_runtime_identity" in item for item in result["diagnostics"])


def test_inferred_capture_date_is_candidate_coverage_not_source_as_of_evidence():
    registry = {
        "source_fields": [
            {
                "source": "Eastmoney",
                "code": "f44",
                "canonical": "",
                "meaning": "",
                "status": "unverified",
            }
        ]
    }
    lineage = _lineage(("Eastmoney", "push2"))
    snapshot = _snapshot(
        "push2",
        {"scheme": "em.stock_get", "stocks": {"600000": {"data": {"f44": 10.5}}}},
        origin="meta_data_date",
    )

    result = coverage.build_field_coverage(
        [snapshot],
        registry,
        lineage,
        dt.date(2026, 10, 14),
        trading_window_dates=[dt.date(2026, 10, 14)],
    )
    row = result["fields"][0]

    assert row["candidate_days"] == ["T:20261014"]
    assert row["source_as_of_days"] == []
    assert row["candidate_sample_counts"] == {"T:20261014": 1}
    assert "10.5" not in json.dumps(result, ensure_ascii=False)


def test_source_as_of_date_and_closed_phase_count_as_qualified_coverage():
    registry = {
        "source_fields": [
            {
                "source": "Eastmoney",
                "code": "f44",
                "canonical": "",
                "meaning": "",
                "status": "unverified",
            }
        ]
    }
    lineage = _lineage(("Eastmoney", "push2"))
    snapshot = _snapshot(
        "push2",
        {"scheme": "em.stock_get", "stocks": {"600000": {"data": {"f44": 10.5}}}},
    )

    result = coverage.build_field_coverage(
        [snapshot],
        registry,
        lineage,
        dt.date(2026, 10, 14),
        trading_window_dates=[dt.date(2026, 10, 14)],
    )

    assert result["fields"][0]["source_as_of_days"] == ["T:20261014"]
    assert result["fields"][0]["source_as_of_sample_counts"] == {"T:20261014": 1}


def test_daily_refresh_merges_tuple_window_warnings_and_writes_local_index(tmp_path, monkeypatch):
    report_day = dt.date(2026, 10, 14)
    registry = {
        "source_fields": [
            {
                "source": "Eastmoney",
                "code": "f44",
                "canonical": "",
                "meaning": "",
                "status": "unverified",
            }
        ]
    }
    lineage = _lineage(("Eastmoney", "push2"))
    snapshot = _snapshot(
        "push2",
        {"scheme": "em.stock_get", "stocks": {"600000": {"data": {"f44": 10.5}}}},
    )
    folder_window = SimpleNamespace(
        folders=[],
        market_folders=[],
        event_folders=[],
        trading_dates=(report_day.strftime("%Y%m%d"),),
        event_start=None,
        event_end=None,
        warnings=("window warning",),
    )
    state_dir = tmp_path / "coverage"
    monkeypatch.setattr(
        coverage.cdates, "discover_capture_folders", lambda _: ([], ["discovery warning"])
    )
    monkeypatch.setattr(
        coverage.cdates, "select_folder_window", lambda *args, **kwargs: folder_window
    )
    monkeypatch.setattr(
        coverage.cdates,
        "select_snapshots",
        lambda *args, **kwargs: ([snapshot], ["snapshot warning"]),
    )
    monkeypatch.setattr(coverage.fra, "load_registry", lambda: registry)
    monkeypatch.setattr(coverage.sla, "load_source_lineage", lambda **kwargs: lineage)
    monkeypatch.setattr(coverage, "LOCAL_STATE_DIR", str(state_dir))

    summary = coverage.refresh_daily_coverage(
        str(tmp_path / "20261014"), {"data_date": "20261014"}, data_dir=str(tmp_path)
    )

    saved = json.loads((state_dir / "coverage_20261014.json").read_text(encoding="utf-8"))
    assert summary["status"] == "ok"
    assert "discovery warning" in saved["diagnostics"]
    assert "window warning" in saved["diagnostics"]
    assert "snapshot warning" in saved["diagnostics"]
