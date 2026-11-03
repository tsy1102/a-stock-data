from core import tdx_client
from stock_common import sc_network


def test_tencent_http_get_stops_before_network_when_source_limiter_fails(monkeypatch):
    def fail_rate_limit(*_args, **_kwargs):
        raise TimeoutError("source limiter unavailable")

    monkeypatch.setattr(sc_network, "_provider_interval_wait", fail_rate_limit)
    requests = []
    monkeypatch.setattr(
        sc_network._HTTP_SESSION,
        "get",
        lambda *args, **kwargs: requests.append((args, kwargs)),
    )

    result = tdx_client._http_get("https://qt.gtimg.cn/q=sh600000")

    assert result is None
    assert requests == []


def test_tdx_tcp_throttle_reserves_cross_process_slot(monkeypatch):
    intervals = []
    monkeypatch.setattr(tdx_client, "_last_request_time", 0.0)
    monkeypatch.setattr(tdx_client, "_TDX_MIN_INTERVAL", 0.1)
    monkeypatch.setattr(
        sc_network,
        "_tdx_wait_process_interval",
        lambda interval: intervals.append(interval) or 0.0,
    )

    with tdx_client._TDX_CALL_LOCK:
        tdx_client._tdx_throttle()

    assert intervals == [0.1]
