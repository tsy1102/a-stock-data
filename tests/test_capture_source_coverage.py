import json
from pathlib import Path

from scripts import capture_field_probe as capture
from scripts.source_lineage_api import load_source_lineage, runtime_aliases_for_source

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "docs" / "field_verification" / "field_registry.json"


def _registry():
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def test_every_current_registry_source_has_a_capture_route_or_explicit_exclusion():
    registry = _registry()
    lineage = load_source_lineage(registry=registry)
    collectors = capture.build_collectors()
    excluded = {
        "东财-push2_full": "retired_duplicate",
        "Levistock历史未归属": "historical",
    }

    for source in registry["sources"]:
        name = source["name"]
        if name in excluded:
            assert source["status"] == excluded[name]
            continue
        aliases = runtime_aliases_for_source(name, lineage)
        assert aliases, f"{name} has no runtime identity or explicit lifecycle status"
        assert set(aliases) <= collectors.keys(), f"{name} routes to missing collectors: {aliases}"


def test_every_registry_source_field_has_a_daily_route_or_explicit_exclusion():
    registry = _registry()
    lineage = load_source_lineage(registry=registry)
    collectors = capture.build_collectors()
    excluded = {"东财-push2_full", "Levistock历史未归属"}

    for row in registry["source_fields"]:
        source = row["source"]
        if source in excluded:
            continue
        aliases = runtime_aliases_for_source(source, lineage)
        assert aliases, f"{source}::{row['code']} has no runtime identity"
        assert (
            set(aliases) <= collectors.keys()
        ), f"{source}::{row['code']} routes to missing collectors: {aliases}"


def test_verified_fields_still_have_daily_capture_routes():
    registry = _registry()
    lineage = load_source_lineage(registry=registry)
    collectors = capture.build_collectors()
    excluded = {"东财-push2_full", "Levistock历史未归属"}

    verified_sources = {
        field["source"]
        for field in registry["source_fields"]
        if field.get("status") == "verified" and field["source"] not in excluded
    }
    assert verified_sources
    for source in verified_sources:
        aliases = runtime_aliases_for_source(source, lineage)
        assert aliases
        assert set(aliases) <= collectors.keys(), source


def test_sina_extended_registry_fields_have_explicit_capture_dispositions():
    rows = [row for row in _registry()["source_fields"] if row["source"] == "新浪(扩展API)"]
    codes = {row["code"] for row in rows}
    captured = set(capture.SINA_CAPTURED_FIELD_CODES)
    paused = set(capture.SINA_PAUSED_OPTION_FIELDS)
    unresolved = set(capture.SINA_UNRESOLVED_FIELD_CODES)

    assert codes == captured | paused | unresolved
    assert not (captured & paused or captured & unresolved or paused & unresolved)


def test_baidu_registry_fields_are_explicitly_pending_probe_validation():
    rows = [row for row in _registry()["source_fields"] if row["source"] == "百度(baidu)"]
    source = next(source for source in _registry()["sources"] if source["name"] == "百度(baidu)")

    assert {row["code"] for row in rows} == set(capture.BAIDU_PENDING_FIELD_CODES)
    assert source["status"] == "pending_validation"


def test_baidu_pending_status_is_reproduced_by_registry_generator():
    from scripts.extract_registry import _SOURCE_STATUS_OVERRIDES

    assert _SOURCE_STATUS_OVERRIDES["百度(baidu)"]["status"] == "pending_validation"


def test_ftshare_limit_up_fields_have_explicit_raw_paths_and_remain_unverified():
    rows = [row for row in _registry()["source_fields"] if row["source"] == "FTShare"]
    source = next(item for item in _registry()["sources"] if item["name"] == "FTShare")
    by_code = {row["code"]: row for row in rows}
    expected_paths = {
        code: f"market.limit_up_pool_yesterday[].{code}"
        for code in (
            "first_limit_up_time",
            "limit_up_break",
            "limit_up_break_count",
            "limit_up_enter",
            "limit_up_price",
            "ready",
            "status",
            "symbol",
            "trade_date",
        )
    }

    assert set(expected_paths) <= by_code.keys()
    for code, path in expected_paths.items():
        row = by_code[code]
        assert row["path"] == path
        assert row["status"] == "unverified"
        assert not row["canonical"]
        assert not row["meaning"]
        assert row["identity_evidence"]["raw_capture"].endswith("raw_ftshare.json")
    assert sum(row["source"] == "FTShare" for row in _registry()["source_fields"]) == 15
    assert source["status"] == "historical"
    assert source["source_role"] == "retired_service_endpoint"


def test_default_baidu_lifecycle_is_pending_and_makes_no_network_request(monkeypatch):
    import stock_common

    def fail_if_requested(*_args, **_kwargs):
        raise AssertionError("default capture must not request the pending Baidu endpoint")

    monkeypatch.setattr(stock_common, "_quick_request", fail_if_requested)

    result = capture.collect_baidu([{"code": "600519"}])

    assert result["__unwired__"] == "pending_validation"
    assert "getrelatedblock" in result["reason"]


def test_explicit_baidu_probe_stops_after_first_failure(monkeypatch):
    import stock_common

    calls = []

    def fail_once(url, **kwargs):
        calls.append((url, kwargs))
        return None

    monkeypatch.setattr(stock_common, "_quick_request", fail_once)
    result = capture.collect_baidu(
        [{"code": "600519"}, {"code": "000001"}, {"code": "920001"}], probe=True
    )

    assert len(calls) == 1
    assert calls[0][1]["max_retries"] == 1
    assert result["__source_meta__"]["request_count"] == 1
    assert "__error__" in result["stocks"]["600519"]
    assert all("__skipped__" in result["stocks"][code] for code in ("000001", "920001"))


def test_baidu_parser_preserves_raw_rows_and_lifts_ma_fields():
    result = capture._parse_baidu_kline_probe(
        {
            "Result": {
                "newMarketData": {
                    "keys": ["time", "close", "ma5avgprice", "ma10avgprice", "ma20avgprice"],
                    "marketData": "2026-10-16,10,9.8,9.7,9.6",
                }
            }
        }
    )

    assert result is not None
    assert result["ma5avgprice"] == "9.8"
    assert result["ma10avgprice"] == "9.7"
    assert result["ma20avgprice"] == "9.6"
    assert result["rows"] == ["2026-10-16,10,9.8,9.7,9.6"]


def test_tdx_quote_raw_uses_shared_throttle_and_normalizes_empty_values(monkeypatch):
    from core import tdx_client

    class FakeRow:
        def to_dict(self):
            return {"code": "600519", "price": 0.0, "amount": float("nan")}

    class FakeFrame:
        empty = False

        class _Iloc:
            def __getitem__(self, _index):
                return FakeRow()

        iloc = _Iloc()

    class FakeClient:
        def __init__(self):
            self.symbols = []

        def quotes(self, symbol):
            self.symbols.append(symbol)
            return FakeFrame()

    client = FakeClient()
    throttle_calls = []
    monkeypatch.setattr(tdx_client, "_get_tdx_client", lambda: client)
    monkeypatch.setattr(tdx_client, "_tdx_throttle", lambda: throttle_calls.append(True))

    result = tdx_client.tdx_get_quote_raw("600519")

    assert client.symbols == ["600519"]
    assert throttle_calls == [True]
    assert result == {"code": "600519", "price": 0.0, "amount": None}


def test_tdx_collector_uses_source_pure_quote_and_marks_missing_components(monkeypatch):
    from core import tdx_client

    quote_calls = []
    finance_calls = []

    def quote(code):
        quote_calls.append(code)
        return {"price": 110.0, "last_close": 100.0, "amount": 25000.0, "s_vol": 7}

    def finance(code):
        finance_calls.append(code)
        return None

    monkeypatch.setattr(tdx_client, "tdx_get_quote_raw", quote)
    monkeypatch.setattr(tdx_client, "tdx_get_finance_info", finance)
    monkeypatch.setattr(
        tdx_client,
        "tdx_get_quote_full",
        lambda _code: (_ for _ in ()).throw(AssertionError("composite fallback must not be used")),
    )

    result = capture.collect_tdx([{"code": "600519"}])
    record = result["stocks"]["600519"]

    assert quote_calls == ["600519"]
    assert finance_calls == ["600519"]
    assert record["quote_raw"]["amount"] == 25000.0
    assert record["quote_full"]["price"] == 110.0
    assert record["quote_full"]["amount_wan"] == 2.5
    assert record["quote_full"]["change_pct"] == 10.0
    assert "pe_ttm" not in record["quote_full"]
    assert "finance_info" in record["__error__"]


def test_tdx_collector_marks_missing_quote_and_finance_separately(monkeypatch):
    from core import tdx_client

    monkeypatch.setattr(tdx_client, "tdx_get_quote_raw", lambda _code: None)
    monkeypatch.setattr(tdx_client, "tdx_get_finance_info", lambda _code: None)

    result = capture.collect_tdx([{"code": "600519"}])
    error = result["stocks"]["600519"]["__error__"]

    assert "quote_full" in error
    assert "finance_info" in error


def test_tdx_quote_raw_returns_none_for_an_empty_adapter_response(monkeypatch):
    from core import tdx_client

    class EmptyFrame:
        empty = True

    class FakeClient:
        def quotes(self, symbol):
            return EmptyFrame()

    monkeypatch.setattr(tdx_client, "_get_tdx_client", lambda: FakeClient())
    monkeypatch.setattr(tdx_client, "_tdx_throttle", lambda: None)

    assert tdx_client.tdx_get_quote_raw("600519") is None


def test_sina_extended_captures_structured_reports_and_flow_scalars(monkeypatch):
    import stock_common

    report_calls = []

    def report(code, report_type, num_periods=1):
        report_calls.append((code, report_type, num_periods))
        return {
            "report_type": report_type,
            "report_list": {
                "20260930": {
                    "data": [{"item_title": "营业总收入", "item_value": "123", "item_tongbi": "4"}]
                }
            },
        }

    monkeypatch.setattr(stock_common, "get_sina_financial_report_raw", report)
    monkeypatch.setattr(
        stock_common,
        "get_sina_stock_fund_flow_raw",
        lambda _code, days=1: [
            {"opendate": "2026-10-16", "trade": "10", "netamount": "20", "turnover": "1.2"}
        ],
    )

    result = capture.collect_sina_extended([{"code": "600519"}])
    record = result["stocks"]["600519"]

    assert report_calls == [("600519", "fzb", 1), ("600519", "lrb", 1), ("600519", "llb", 1)]
    assert (
        record["financial_reports"]["lrb"]["report_list"]["20260930"]["data"][0]["item_value"]
        == "123"
    )
    assert record["opendate"] == "2026-10-16"
    assert record["trade"] == "10"
    assert record["netamount"] == "20"
    assert record["turnover"] == "1.2"
    assert (
        "requires an option-contract universe"
        in result["__source_meta__"]["paused_fields"]["reason"]
    )


def test_sina_extended_stops_finance_requests_after_first_failure(monkeypatch):
    import stock_common

    report_calls = []
    flow_calls = []

    def fail_report(code, report_type, num_periods=1):
        report_calls.append((code, report_type))
        return None

    def flow(code, days=1):
        flow_calls.append(code)
        return [{"opendate": "2026-10-16", "trade": "10", "netamount": "20", "turnover": "1.2"}]

    monkeypatch.setattr(stock_common, "get_sina_financial_report_raw", fail_report)
    monkeypatch.setattr(stock_common, "get_sina_stock_fund_flow_raw", flow)

    result = capture.collect_sina_extended([{"code": "600519"}, {"code": "000001"}])

    assert report_calls == [("600519", "fzb")]
    assert flow_calls == ["600519", "000001"]
    assert "__error__" in result["stocks"]["600519"]["financial_reports"]["fzb"]
    assert "__skipped__" in result["stocks"]["000001"]["financial_reports"]["fzb"]


def test_sina_extended_marks_incomplete_flow_rows_as_errors_and_stops(monkeypatch):
    import stock_common

    monkeypatch.setattr(
        stock_common,
        "get_sina_financial_report_raw",
        lambda code, report_type, num_periods=1: {
            "report_type": report_type,
            "report_list": {},
        },
    )
    flow_calls = []

    def incomplete_flow(code, days=1):
        flow_calls.append(code)
        return [{"opendate": "2026-10-16", "trade": "1", "turnover": "2"}]

    monkeypatch.setattr(stock_common, "get_sina_stock_fund_flow_raw", incomplete_flow)
    result = capture.collect_sina_extended([{"code": "600519"}, {"code": "000001"}])

    first = result["stocks"]["600519"]
    second = result["stocks"]["000001"]
    assert flow_calls == ["600519"]
    assert first["money_flow"] == [{"opendate": "2026-10-16", "trade": "1", "turnover": "2"}]
    assert "netamount" in first["__error__"]
    assert second["money_flow"]["__skipped__"].startswith("deferred:")
