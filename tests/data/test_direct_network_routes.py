from __future__ import annotations

from types import SimpleNamespace

import pytest

from core import tdx_client
from stock_common import sc_kpl, sc_network, sc_plate_rot
from stock_common.sc_datasource import _holders, _official_backup, _pools


class _FakeHTTPResponse:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return self.body


def test_shared_requests_session_ignores_all_proxy_environment(monkeypatch):
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
        monkeypatch.setenv(name, "http://proxy.invalid:8000")
    monkeypatch.delenv("NO_PROXY", raising=False)

    merged = sc_network._HTTP_SESSION.merge_environment_settings(
        "https://example.invalid/",
        {"http": None, "https": None},
        stream=False,
        verify=None,
        cert=None,
    )

    assert sc_network._HTTP_SESSION.trust_env is False
    assert merged["proxies"].get("http") is None
    assert merged["proxies"].get("https") is None
    assert merged["proxies"].get("all") is None


def test_tdx_http_fallback_uses_direct_shared_session(monkeypatch):
    calls = []
    response = SimpleNamespace(status_code=200, text="v_sh600000=\"600000~浦发\";")
    monkeypatch.setattr(sc_network, "_provider_interval_wait", lambda *_args: 0.0)
    monkeypatch.setattr(tdx_client, "_DOMAIN_LAST_TIME", {})
    monkeypatch.setattr(
        sc_network._HTTP_SESSION,
        "get",
        lambda *args, **kwargs: calls.append((args, kwargs)) or response,
    )

    result = tdx_client._http_get("https://qt.gtimg.cn/q=sh600000")

    assert result is response
    assert len(calls) == 1
    assert "proxies" not in calls[0][1]
    assert sc_network._HTTP_SESSION.trust_env is False


def test_cninfo_irm_uses_direct_shared_session_and_source_slots(monkeypatch):
    calls = []
    waits = []
    payloads = [
        {"data": [{"stockCode": "000001", "secid": "org-1"}]},
        {"rows": [{"stockCode": "000001", "mainContent": "Q", "attachedContent": "A"}]},
    ]
    monkeypatch.setattr(sc_network, "_source_rate_limit_wait", waits.append)

    def fake_post(*args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(json=lambda: payloads.pop(0))

    monkeypatch.setattr(sc_network._HTTP_SESSION, "post", fake_post)

    result = _holders.cninfo_irm("000001")

    assert result == [
        {
            "code": "000001",
            "company": None,
            "question": "Q",
            "answer": "A",
            "answerer": None,
            "ask_time": "",
        }
    ]
    assert [item[0][0] for item in calls] == [
        "https://irm.cninfo.com.cn/newircs/index/queryKeyboardInfo",
        "https://irm.cninfo.com.cn/newircs/company/question",
    ]
    assert all("proxies" not in kwargs for _, kwargs in calls)
    assert waits == [
        "https://irm.cninfo.com.cn/newircs/index/queryKeyboardInfo",
        "https://irm.cninfo.com.cn/newircs/company/question",
    ]
    assert sc_network._HTTP_SESSION.trust_env is False


def test_kpl_uses_explicit_direct_urllib_opener(monkeypatch):
    calls = []
    monkeypatch.setattr(sc_network, "_source_rate_limit_wait", lambda _url: None)
    monkeypatch.setattr(sc_kpl, "_throttle", lambda: None)
    monkeypatch.setattr(
        sc_kpl,
        "_DIRECT_OPENER",
        SimpleNamespace(
            open=lambda request, timeout: calls.append((request, timeout))
            or _FakeHTTPResponse(b'{"errcode":"0","data":[]}')
        ),
    )

    result = sc_kpl._post("hq", {"a": "test"})

    assert result == {"errcode": "0", "data": []}
    assert sc_kpl._DIRECT_PROXY_HANDLER.proxies == {}
    assert len(calls) == 1
    assert calls[0][1] == 15


def test_plate_rotation_uses_explicit_direct_urllib_opener(monkeypatch):
    calls = []
    waits = []
    monkeypatch.setattr(sc_network, "_source_rate_limit_wait", lambda url: waits.append(url))
    monkeypatch.setattr(sc_plate_rot, "_throttle", lambda: None)
    monkeypatch.setattr(
        sc_plate_rot,
        "_DIRECT_OPENER",
        SimpleNamespace(
            open=lambda request, timeout: calls.append((request, timeout))
            or _FakeHTTPResponse(b'{"html":""}')
        ),
    )

    result = sc_plate_rot._post("/api/test", {"from": "ths"})

    assert result == {"html": ""}
    assert sc_plate_rot._DIRECT_PROXY_HANDLER.proxies == {}
    assert waits == [sc_plate_rot._BASE]
    assert len(calls) == 1


def test_official_get_uses_direct_shared_requests_session(monkeypatch):
    calls = []
    response = SimpleNamespace(raise_for_status=lambda: None)
    monkeypatch.setattr(_official_backup, "_source_rate_limit_wait", lambda _url: None)
    monkeypatch.setattr(
        sc_network._HTTP_SESSION,
        "get",
        lambda *args, **kwargs: calls.append((args, kwargs)) or response,
    )

    result = _official_backup._official_get("https://query.sse.com.cn/example")

    assert result is response
    assert len(calls) == 1
    assert sc_network._HTTP_SESSION.trust_env is False
    assert "proxies" not in calls[0][1]


def test_pool_kpl_post_uses_direct_shared_requests_session(monkeypatch):
    calls = []
    response = SimpleNamespace(status_code=200, text='{"errcode":"0","data":{"n":1}}')
    monkeypatch.setattr(_pools, "_source_rate_limit_wait", lambda _url: None)
    monkeypatch.setattr(
        sc_network._HTTP_SESSION,
        "post",
        lambda *args, **kwargs: calls.append((args, kwargs)) or response,
    )

    result = _pools._kpl_post("https://apphq.longhuvip.com/w1/api/index.php", "test", "HomeDingPan")

    assert result == {"n": 1}
    assert len(calls) == 1
    assert "proxies" not in calls[0][1]
    assert sc_network._HTTP_SESSION.trust_env is False


def test_bse_quote_session_disables_environment_proxy_before_request(monkeypatch):
    class Session:
        def __init__(self):
            self.headers = {}
            self.trust_env = True
            self.trust_env_at_request = None

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def get(self, *_args, **_kwargs):
            self.trust_env_at_request = self.trust_env
            raise RuntimeError("stop after routing check")

    session = Session()
    monkeypatch.setattr(_official_backup.requests, "Session", lambda: session)
    monkeypatch.setattr(_official_backup, "_source_rate_limit_wait", lambda _url: None)

    with pytest.raises(RuntimeError, match="routing check"):
        _official_backup.bse_quote_backup("2026-11-03")

    assert session.trust_env_at_request is False
