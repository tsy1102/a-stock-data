from collections import defaultdict
from datetime import date, datetime

from scripts.collision_dates import Snapshot, TRADING
from scripts.collision_snapshots import load_snapshots
from scripts.field_evidence_coverage import build_field_coverage


def _etf_snapshot() -> Snapshot:
    return Snapshot(
        source="etf",
        domain=TRADING,
        sample_date=date(2026, 11, 17),
        capture_date=date(2026, 11, 18),
        folder="20261117",
        path="raw_etf.json",
        document={
            "scheme": {"name": "etf"},
            "etf_sh": [
                {"date": "2026-11-06", "exchange": "SH", "code": "510001"},
                {"date": "2026-11-16", "exchange": "SH", "code": "510002"},
                {"date": "", "exchange": "SH", "code": "510003"},
            ],
            "etf_sz": [
                {
                    "date": "2026-11-17",
                    "exchange": "SZ",
                    "code": "159001",
                    "__source_meta__": {"date_basis": "szse_current_scale_column_header"},
                    "listing_date": "2011-12-09",
                },
                {
                    "date": "2026-11-17",
                    "exchange": "SZ",
                    "code": "159002",
                    "listing_date": "2012-01-09",
                },
            ],
        },
        meta={},
        phase="closed",
        status="ok",
        record_count=4,
        captured_at=datetime(2026, 11, 18, 15, 9),
        date_origin="record_as_of_date",
    )


def test_etf_rows_use_their_own_market_date_and_reject_ineligible_rows():
    store = defaultdict(lambda: {"vals": {}, "sample_meta": {}})
    diagnostics = []

    load_snapshots(
        [_etf_snapshot()],
        store,
        diagnostics,
        allowed_trading_dates={"20261116", "20261117"},
    )

    assert store["etf.etf_sh.date"]["vals"] == {
        ("510002", "T:20261116"): "2026-11-16",
    }
    assert store["etf.etf_sz.date"]["vals"] == {
        ("159001", "T:20261117"): "2026-11-17",
    }
    assert (
        store["etf.etf_sh.date"]["sample_meta"][("510002", "T:20261116")]["as_of_date_origin"]
        == "record.as_of_date"
    )
    assert store["etf.etf_sz.listing_date"]["vals"] == {
        ("159001", "T:20261117"): "2011-12-09",
    }
    assert ("159002", "T:20261117") not in store["etf.etf_sz.date"]["vals"]
    assert ("159002", "T:20261117") not in store["etf.etf_sz.listing_date"]["vals"]
    assert store["etf.etf_sz.date"]["sample_meta"][("159001", "T:20261117")]["phase"] == "closed"
    assert any("2 条市场记录缺少可解析的来源交易日" in item for item in diagnostics)
    assert any("1 条市场记录不在所选交易日窗口内" in item for item in diagnostics)


def test_etf_record_date_counts_as_explicit_source_date_in_field_coverage():
    result = build_field_coverage(
        [_etf_snapshot()],
        {
            "source_fields": [
                {
                    "source": "沪深交易所",
                    "code": "etf_sh.date",
                    "canonical": "",
                    "meaning": "",
                    "unit": "",
                    "status": "unverified",
                },
                {
                    "source": "沪深交易所",
                    "code": "etf_sz.date",
                    "canonical": "",
                    "meaning": "",
                    "unit": "",
                    "status": "unverified",
                },
                {
                    "source": "沪深交易所",
                    "code": "etf_sz.listing_date",
                    "canonical": "",
                    "meaning": "",
                    "unit": "",
                    "status": "unverified",
                },
            ]
        },
        {
            "sources": {
                "沪深交易所": {
                    "runtime_aliases": ["etf"],
                    "independence_family": "exchange",
                    "independence_status": "confirmed",
                    "anchor_eligible": True,
                }
            },
            "runtime_sources": {
                "etf": {
                    "independence_family": "exchange",
                    "independence_status": "confirmed",
                }
            },
        },
        date(2026, 11, 18),
        trading_window_dates=[date(2026, 11, 16), date(2026, 11, 17)],
    )

    target = next(row for row in result["fields"] if row["code"] == "etf_sh.date")
    assert target["source_as_of_days"] == ["T:20261116"]
    assert target["date_origins"] == ["record.as_of_date"]
    assert target["phases"] == ["closed"]
    sz_target = next(row for row in result["fields"] if row["code"] == "etf_sz.date")
    assert sz_target["source_as_of_days"] == ["T:20261117"]
    assert sz_target["candidate_days"] == ["T:20261117"]


def test_event_dc_top_level_collections_keep_full_field_paths():
    snapshot = Snapshot(
        source="event_dc",
        domain=TRADING,
        sample_date=date(2026, 11, 19),
        capture_date=date(2026, 11, 19),
        folder="20261119",
        path="raw_event_dc.json",
        document={
            "scheme": {"name": "em.datacenter"},
            "convertible_bonds": [{"SECURITY_CODE": "110003", "ACTUAL_ISSUE_SCALE": 27.6}],
            "ipo_calendar": [{"SECURITY_CODE": "600000", "CHANGE": "申购"}],
        },
        meta={},
        phase="closed",
        status="ok",
        record_count=2,
        captured_at=datetime(2026, 11, 19, 19, 52),
        date_origin="capture_date",
    )
    store = defaultdict(lambda: {"vals": {}, "sample_meta": {}})

    load_snapshots(
        [snapshot],
        store,
        [],
        allowed_trading_dates={"20261119"},
    )

    assert store["event_dc.convertible_bonds[].ACTUAL_ISSUE_SCALE"]["vals"] == {
        ("110003", "T:20261119"): 27.6,
    }
    assert store["event_dc.ipo_calendar[].CHANGE"]["vals"] == {
        ("600000", "T:20261119"): "申购",
    }
    assert "event_dc.ACTUAL_ISSUE_SCALE" not in store


def test_market_sources_request_metadata_is_not_flattened_as_a_field():
    snapshot = Snapshot(
        source="market_sources",
        domain=TRADING,
        sample_date=date(2026, 11, 19),
        capture_date=date(2026, 11, 20),
        folder="20261119",
        path="raw_market_sources.json",
        document={
            "__source_meta__": {
                "kph_limit_ladder": {
                    "adapter": "levistock.get_zttt",
                    "provider_family": "kph",
                    "date_domain": "trading_day",
                    "requested_trade_date": "2026-11-19",
                    "date_evidence": "request_parameter",
                }
            },
            "kph_limit_ladder": [
                {
                    "code": "002685",
                    "limit_count": 4,
                    "limit_time": 1794965100,
                }
            ],
        },
        meta={},
        phase="closed",
        status="ok",
        record_count=1,
        captured_at=datetime(2026, 11, 20, 8, 30),
        date_origin="capture_date",
    )
    store = defaultdict(lambda: {"vals": {}, "sample_meta": {}})

    load_snapshots(
        [snapshot],
        store,
        [],
        allowed_trading_dates={"20261118"},
    )

    assert store["market_sources.limit_count"]["vals"] == {
        ("002685", "T:20261118"): 4,
    }
    assert "market_sources.requested_trade_date" not in store
    assert not any("requested_trade_date" in field for field in store)
