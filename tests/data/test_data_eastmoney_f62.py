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
