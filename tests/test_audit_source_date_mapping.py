import json
from datetime import date

import pytest

from scripts import audit_source_date_mapping as audit


def _write_meta(folder, *, capture_date, data_date, source_dates):
    folder.mkdir()
    meta = {
        "capture_date": capture_date,
        "data_date": data_date,
        "market_phase": "closed",
        "sources": {
            source: {"status": "ok", "as_of_date": source_date}
            for source, source_date in source_dates.items()
        },
    }
    (folder / "meta.json").write_text(json.dumps(meta), encoding="utf-8")


def test_audit_reads_only_retained_metadata_and_reports_source_offsets(tmp_path):
    _write_meta(
        tmp_path / "20261014",
        capture_date="20261014",
        data_date="20261014",
        source_dates={"source_a": "20261014"},
    )
    _write_meta(
        tmp_path / "20261016",
        capture_date="20261018",
        data_date="20261016",
        source_dates={"source_a": "20261016", "source_b": "20261014"},
    )
    _write_meta(
        tmp_path / "20261019",
        capture_date="20261019",
        data_date="20261019",
        source_dates={"source_a": "20261019", "source_b": "20261016"},
    )
    _write_meta(
        tmp_path / "20261020",
        capture_date="20261020",
        data_date="20261020",
        source_dates={"source_a": "20261020", "source_b": None},
    )

    observations, diagnostics = audit.collect_observations(tmp_path)
    summary = audit.summarize_observations(observations)

    assert len(observations) == 4
    assert {row["folder"] for row in observations} == {
        "20261016",
        "20261019",
        "20261020",
    }
    assert any("早于保留起点" in item for item in diagnostics)
    source_a = next(item for item in summary["sources"] if item["source"] == "source_a")
    source_b = next(item for item in summary["sources"] if item["source"] == "source_b")
    assert source_a["observed_pattern"] == "repeated_offset_observed_not_contract"
    assert source_b["observed_pattern"] == "insufficient_observations"
    assert source_b["source_minus_data_calendar_days"] == {-3: 1}


def test_audit_never_accepts_a_start_before_retention_boundary(tmp_path):
    with pytest.raises(ValueError, match="不能早于样本保留边界"):
        audit.collect_observations(tmp_path, date(2026, 10, 14))


def test_summary_calls_offsets_observed_not_a_source_contract():
    summary = audit.summarize_observations(
        [
            {
                "source": "stable",
                "source_minus_data_calendar_days": 0,
                "source_minus_capture_calendar_days": 0,
            },
            {
                "source": "stable",
                "source_minus_data_calendar_days": 0,
                "source_minus_capture_calendar_days": 0,
            },
            {
                "source": "stable",
                "source_minus_data_calendar_days": 0,
                "source_minus_capture_calendar_days": 0,
            },
        ]
    )

    assert summary["sources"][0]["observed_pattern"] == "repeated_offset_observed_not_contract"
