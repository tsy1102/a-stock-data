import pytest

from core import tdx_client
from stock_common import sc_network


def test_tencent_batch_fallback_stops_before_http_when_rate_limit_fails(monkeypatch):
    monkeypatch.setattr(tdx_client, "_TENCENT_BATCH_CACHE", {})
    monkeypatch.setattr(tdx_client, "_TENCENT_BATCH_CACHE_DATE", "20990101")

    def fail_rate_limit():
        raise TimeoutError("rate-limit state unavailable")

    monkeypatch.setattr(
        sc_network,
        "_gen_wait_process_interval",
        fail_rate_limit,
    )
    requests = []
    monkeypatch.setattr(tdx_client, "_http_get", lambda *args, **kwargs: requests.append(args))

    with pytest.raises(TimeoutError, match="rate-limit state unavailable"):
        tdx_client._tencent_batch_fallback(["600000"], use_l2_cache=False)

    assert requests == []
