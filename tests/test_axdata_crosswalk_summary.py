import hashlib
import json
from pathlib import Path

import pytest

from scripts import axdata_daily_validation as validation
from scripts.axdata_crosswalk_summary import read_summary, summarize_crosswalk


def test_summary_preserves_current_crosswalk_counts_and_source_fingerprint() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "docs" / "axdata_interface_crosswalk.json"
    raw = source.read_bytes()
    crosswalk = json.loads(raw.decode("utf-8"))

    source_sha256 = hashlib.sha256(raw).hexdigest()
    summary = summarize_crosswalk(crosswalk, source_sha256)

    assert summary["interface_count"] == 257
    assert summary["field_occurrence_count"] == 3343
    assert summary["field_occurrences_below_e3"] == 3343
    assert sum(summary["interface_relation_status_counts"].values()) == 257
    assert summary["source_sha256"] == source_sha256


@pytest.mark.parametrize(
    "crosswalk",
    [
        {},
        {"generated_date": "2026-10-21", "interfaces": [None]},
        {
            "generated_date": "2026-10-21",
            "interfaces": [{"static_reconciliation": [], "fields": []}],
        },
        {
            "generated_date": "2026-10-21",
            "interfaces": [{"static_reconciliation": {}, "fields": [None]}],
        },
    ],
)
def test_summarize_crosswalk_rejects_incomplete_or_invalid_rows(crosswalk: dict) -> None:
    with pytest.raises(ValueError):
        summarize_crosswalk(crosswalk, "a" * 64)


def test_read_summary_rejects_wrong_schema_and_invalid_counts(tmp_path: Path) -> None:
    path = tmp_path / "summary.json"
    path.write_text(json.dumps({"schema_version": 0}), encoding="utf-8")
    assert read_summary(path) is None

    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "generated_date": "2026-10-21",
                "source_sha256": "a" * 64,
                "interface_count": True,
                "field_occurrence_count": 2,
                "field_occurrences_below_e3": 2,
                "interface_relation_status_counts": {"unknown": 1},
            }
        ),
        encoding="utf-8",
    )
    assert read_summary(path) is None


def test_daily_queue_summary_reads_compact_projection_only(tmp_path: Path, monkeypatch) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    source_bytes = b"canonical crosswalk"
    (docs / "axdata_interface_crosswalk.json").write_bytes(source_bytes)
    summary = {
        "schema_version": 1,
        "generated_date": "2026-10-21",
        "source_file": "axdata_interface_crosswalk.json",
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "interface_count": 257,
        "field_occurrence_count": 3343,
        "field_occurrences_below_e3": 3343,
        "interface_relation_status_counts": {"candidate": 257},
    }
    (docs / "axdata_interface_crosswalk_summary.json").write_text(
        json.dumps(summary), encoding="utf-8"
    )
    monkeypatch.setattr(validation, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(validation, "_STATIC_QUEUE_CACHE", None)

    result = validation._static_queue_summary()

    assert result["interface_count"] == 257
    assert result["field_occurrence_count"] == 3343
    assert result["field_occurrences_below_e3"] == 3343
    assert result["interface_relation_status_counts"] == {"candidate": 257}

    (docs / "axdata_interface_crosswalk.json").write_bytes(b"updated canonical crosswalk")
    monkeypatch.setattr(validation, "_STATIC_QUEUE_CACHE", None)
    stale = validation._static_queue_summary()
    assert stale == {"status": "unavailable", "reason": "AxData crosswalk summary is stale"}
