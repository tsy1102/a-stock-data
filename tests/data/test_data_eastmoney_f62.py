from datetime import datetime, timezone

import stock_common.sc_datasource._eastmoney as eastmoney


class _Response:
    def __init__(self, items):
        self._items = items

    def json(self):
        return {"data": {"diff": self._items}}


def test_ulist_f62_missing_values_remain_missing_and_numeric_zero_is_valid(monkeypatch):
    monkeypatch.setattr(eastmoney, "_EM_BATCH_CACHE", {})
    monkeypatch.setattr(eastmoney, "_EM_BATCH_CACHE_DATE", "")
    items = [
        {"f12": "600001", "f14": "甲", "f2": "10", "f3": "0", "f62": None},
        {"f12": "600002", "f14": "乙", "f2": "10", "f3": "0", "f62": "-"},
        {"f12": "600003", "f14": "丙", "f2": "10", "f3": "0", "f62": "--"},
        {"f12": "600004", "f14": "丁", "f2": "10", "f3": "0", "f62": "0"},
        {"f12": "600005", "f14": "戊", "f2": "10", "f3": "0", "f62": "125000"},
    ]
    monkeypatch.setattr(eastmoney, "em_get", lambda *_args, **_kwargs: _Response(items))

    result = eastmoney.get_em_batch_quotes(["600001", "600002", "600003", "600004", "600005"])

    assert result["600001"]["main_net_inflow_wan"] is None
    assert result["600002"]["main_net_inflow_wan"] is None
    assert result["600003"]["main_net_inflow_wan"] is None
    assert result["600004"]["main_net_inflow_wan"] == 0.0
    assert result["600005"]["main_net_inflow_wan"] == 12.5


def test_ulist_quote_requests_row_date_anchors_and_does_not_map_ulist_f164_to_pe(monkeypatch):
    monkeypatch.setattr(eastmoney, "_EM_BATCH_CACHE", {})
    monkeypatch.setattr(eastmoney, "_EM_BATCH_CACHE_DATE", "")
    requested = {}
    row_timestamp = int(datetime(2026, 11, 24, 1, 31, tzinfo=timezone.utc).timestamp())
    items = [
        {
            "f12": "600519",
            "f14": "贵州茅台",
            "f2": "1500",
            "f3": "1.2",
            "f62": "125000",
            "f124": row_timestamp,
            "f164": "987654321",
            "f297": 20261124,
        }
    ]

    def fake_em_get(_url, *, params, **_kwargs):
        requested.update(params)
        return _Response(items)

    monkeypatch.setattr(eastmoney, "em_get", fake_em_get)
    result = eastmoney.get_em_batch_quotes(["600519"])["600519"]

    fields = requested["fields"].split(",")
    assert "f124" in fields and "f297" in fields
    assert "f164" not in fields
    assert result["pe_ttm"] is None
    assert result["_source_as_of_date"] == "2026-11-24"
    assert result["_source_as_of_date_status"] == "verified"
    assert result["_source_as_of_date_source"] == "f124+f297"


def test_ulist_row_date_metadata_rejects_conflicts_and_incomplete_anchors():
    matching_timestamp = int(datetime(2026, 11, 24, 1, 31, tzinfo=timezone.utc).timestamp())

    assert eastmoney._ulist_row_date_metadata({"f124": matching_timestamp, "f297": 20261124}) == {
        "date": "2026-11-24",
        "status": "verified",
        "source": "f124+f297",
    }
    assert eastmoney._ulist_row_date_metadata({"f124": matching_timestamp, "f297": 20261123}) == {
        "date": "",
        "status": "conflict",
        "source": "f124+f297",
    }
    assert eastmoney._ulist_row_date_metadata({"f297": 20261124}) == {
        "date": "2026-11-24",
        "status": "partial",
        "source": "f297",
    }
    assert eastmoney._ulist_row_date_metadata({"f124": "invalid", "f297": None}) == {
        "date": "",
        "status": "invalid",
        "source": "f124+f297",
    }
