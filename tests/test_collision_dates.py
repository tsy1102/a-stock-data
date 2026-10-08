import json
from datetime import date, datetime, timezone
from pathlib import Path

from scripts import collision_dates


def _write_capture(root: Path, folder: str, meta: dict, source: str, document: dict):
    target = root / folder
    target.mkdir(parents=True, exist_ok=True)
    (target / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    (target / f"raw_{source}.json").write_text(json.dumps(document), encoding="utf-8")


def _weekday(day: date) -> bool:
    return day.weekday() < 5 and day not in {
        date(2026, 9, 25),
        date(2026, 9, 26),
        date(2026, 9, 27),
    }


def test_parse_date_accepts_compact_iso_and_timestamp():
    assert collision_dates.parse_date("20260929") == date(2026, 9, 29)
    assert collision_dates.parse_date("2026-09-29T10:30:00") == date(2026, 9, 29)
    utc_epoch_ms = int(datetime(2026, 9, 29, 16, 30, tzinfo=timezone.utc).timestamp() * 1000)
    assert collision_dates.parse_date(utc_epoch_ms) == date(2026, 9, 30)
    assert collision_dates.parse_date("2026-09-29T16:30:00Z") == date(2026, 9, 30)
    assert collision_dates.parse_date(datetime(2026, 9, 29, 16, 30, tzinfo=timezone.utc)) == date(
        2026, 9, 30
    )
    assert collision_dates.parse_date("bad-date") is None


def test_record_count_ignores_empty_metadata_but_counts_nested_event_rows():
    assert collision_dates._record_count({"stocks": {}, "scheme": {"name": "empty"}}) == 0
    assert collision_dates._record_count({"cctv_xwlb": [{"date": "2026-09-29"}]}) == 1


def test_record_count_ignores_fuyao_auction_provenance_metadata():
    document = {
        "auction_snapshot_meta": {
            "collision_eligible": False,
            "response_timestamp": "2026-09-29T09:25:00",
            "item_count": 1,
        },
        "stocks": {
            "600000": {
                "auction_final": {
                    "auction_price": 10.2,
                    "__source_meta__": {
                        "collision_eligible": False,
                        "source_data_date": None,
                    },
                }
            }
        },
    }

    assert collision_dates._record_count(document) == 1
    assert collision_dates._record_count({"stocks": document["stocks"]}) == 1


def test_legacy_weekend_folder_maps_to_prior_session_without_rename(tmp_path):
    target = tmp_path / "20260920"
    target.mkdir()
    folders, warnings = collision_dates.discover_capture_folders(str(tmp_path), _weekday)

    assert folders[0].market_date == date(2026, 9, 18)
    assert folders[0].capture_date == date(2026, 9, 20)
    assert folders[0].market_date_origin == "folder_inferred"
    assert any("目录未改名" in warning for warning in warnings)
    assert target.is_dir()


def test_explicit_nontrading_data_date_is_rejected_without_inference(tmp_path):
    _write_capture(
        tmp_path,
        "20260929",
        {"data_date": "20260927", "run_date": "20260929"},
        "push2",
        {"stocks": {}},
    )
    folders, warnings = collision_dates.discover_capture_folders(str(tmp_path), _weekday)

    assert folders[0].market_date is None
    assert any("显式 data_date" in warning for warning in warnings)


def test_window_counts_distinct_sessions_and_separate_natural_capture_days(tmp_path):
    for folder in ("20260924", "20260925", "20260926", "20260928", "20260929"):
        (tmp_path / folder).mkdir()
    folders, _ = collision_dates.discover_capture_folders(str(tmp_path), _weekday)
    window = collision_dates.select_folder_window(folders, 2, date(2026, 9, 29), all_history=False)

    assert window.trading_dates == ("20260928", "20260929")
    assert window.event_start == date(2026, 9, 28)
    assert window.event_end == date(2026, 9, 29)
    assert {folder.name for folder in window.folders} == {"20260928", "20260929"}


def test_event_window_can_use_later_capture_for_prior_natural_event(tmp_path):
    _write_capture(
        tmp_path,
        "20260929",
        {"data_date": "20260929", "capture_date": "20260930"},
        "news_wscn_cctv",
        {"cctv_xwlb": [{"date": "2026-09-29", "title": "news"}]},
    )
    folders, _ = collision_dates.discover_capture_folders(str(tmp_path), _weekday)
    window = collision_dates.select_folder_window(folders, 2, date(2026, 9, 29), all_history=False)

    assert "20260929" in window.event_folders
    assert "20260929" in window.market_folders


def test_window_excludes_bad_market_date_but_keeps_calendar_capture(tmp_path):
    for folder in ("20260813", "20260814", "20260817", "20260818", "20260819"):
        (tmp_path / folder).mkdir()
    folders, _ = collision_dates.discover_capture_folders(str(tmp_path), _weekday)
    window = collision_dates.select_folder_window(
        folders,
        6,
        date(2026, 8, 19),
        excluded_trading_dates={"20260814"},
    )

    assert "20260814" not in window.trading_dates
    assert "20260814" not in window.market_folders
    assert "20260814" in window.event_folders


def test_all_history_does_not_include_future_market_dates(tmp_path):
    (tmp_path / "20260928").mkdir()
    _write_capture(
        tmp_path,
        "20260930",
        {"data_date": "20260930", "capture_date": "20260930"},
        "push2",
        {"stocks": {"600000": {"data": {"f1": 1}}}},
    )
    folders, _ = collision_dates.discover_capture_folders(str(tmp_path), _weekday)
    window = collision_dates.select_folder_window(folders, 7, date(2026, 9, 29), all_history=True)

    assert window.trading_dates == ("20260928",)
    assert "20260930" not in window.market_folders
    assert any("晚于报告日" in warning for warning in window.warnings)


def test_snapshot_selector_prefers_closed_complete_duplicate(tmp_path):
    document_small = {"stocks": {"600000": {"data": {"f1": 1}}}}
    document_complete = {
        "stocks": {
            "600000": {"data": {"f1": 1}},
            "000001": {"data": {"f1": 2}},
        }
    }
    _write_capture(
        tmp_path,
        "20260928",
        {
            "data_date": "20260928",
            "capture_date": "20260928",
            "start": "2026-09-28 10:00:00",
            "market_phase": "intraday",
            "sources": {"push2": {"status": "ok"}},
        },
        "push2",
        document_small,
    )
    _write_capture(
        tmp_path,
        "20260929",
        {
            "data_date": "20260928",
            "capture_date": "20260929",
            "start": "2026-09-29 16:00:00",
            "market_phase": "closed",
            "sources": {"push2": {"status": "ok"}},
        },
        "push2",
        document_complete,
    )
    folders, _ = collision_dates.discover_capture_folders(str(tmp_path), _weekday)
    snapshots, warnings = collision_dates.select_snapshots(folders, checker=_weekday)

    assert len(snapshots) == 1
    assert snapshots[0].folder == "20260929"
    assert snapshots[0].sample_date == date(2026, 9, 28)
    assert any("重复快照 push2/20260928" in warning for warning in warnings)


def test_legacy_same_day_morning_capture_is_marked_intraday(tmp_path):
    _write_capture(
        tmp_path,
        "20260928",
        {"data_date": "20260928", "start": "2026-09-28 10:49:53"},
        "push2",
        {"stocks": {"600000": {"data": {"f1": 1}}}},
    )
    folders, _ = collision_dates.discover_capture_folders(str(tmp_path), _weekday)
    snapshots, warnings = collision_dates.select_snapshots(folders, checker=_weekday)

    assert snapshots[0].phase == "intraday"
    assert any("盘中快照" in warning for warning in warnings)


def test_unknown_market_phase_warns_and_is_not_inferred_closed(tmp_path):
    _write_capture(
        tmp_path,
        "20260928",
        {"data_date": "20260928", "capture_date": "20260928"},
        "push2",
        {"stocks": {"600000": {"data": {"f1": 1}}}},
    )
    folders, _ = collision_dates.discover_capture_folders(str(tmp_path), _weekday)
    snapshots, warnings = collision_dates.select_snapshots(folders, checker=_weekday)

    assert snapshots[0].phase == "unknown"
    assert any("时段未知" in warning for warning in warnings)


def test_capture_time_overrides_conflicting_closed_phase_metadata(tmp_path):
    _write_capture(
        tmp_path,
        "20260928",
        {
            "data_date": "20260928",
            "capture_date": "20260928",
            "start": "2026-09-28 10:00:00",
            "market_phase": "closed",
        },
        "push2",
        {"stocks": {"600000": {"data": {"f1": 1}}}},
    )
    folders, _ = collision_dates.discover_capture_folders(str(tmp_path), _weekday)
    snapshots, warnings = collision_dates.select_snapshots(folders, checker=_weekday)

    assert snapshots[0].phase == "intraday"
    assert any("market_phase=closed 与采集时间矛盾" in warning for warning in warnings)


def test_source_as_of_date_after_capture_date_is_skipped(tmp_path):
    _write_capture(
        tmp_path,
        "20260928",
        {"data_date": "20260928", "capture_date": "20260928"},
        "push2",
        {"as_of_date": "20260929", "stocks": {"600000": {"data": {"f1": 1}}}},
    )
    folders, _ = collision_dates.discover_capture_folders(str(tmp_path), _weekday)
    snapshots, warnings = collision_dates.select_snapshots(folders, checker=_weekday)

    assert snapshots == []
    assert any("晚于采集日" in warning for warning in warnings)


def test_event_record_keeps_natural_date_domain_on_weekend():
    event_day = collision_dates.event_record_date(
        "news_wscn_cctv", {"date": "2026-09-27", "title": "example"}
    )
    assert event_day == date(2026, 9, 27)
    assert collision_dates.sample_date_key(collision_dates.CALENDAR, event_day) == "C:20260927"
    assert collision_dates.sample_date_key(collision_dates.TRADING, event_day) == "T:20260927"
