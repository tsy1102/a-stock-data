from __future__ import annotations

import json
from datetime import date
from types import SimpleNamespace
from typing import Any

import pytest

from stock_common import sc_ftshare


def _response(
    payload: bytes | str = b"",
    *,
    status: int = 200,
    headers: dict[str, str] | None = None,
) -> SimpleNamespace:
    content = payload.encode("utf-8") if isinstance(payload, str) else payload
    return SimpleNamespace(status_code=status, content=content, headers=headers or {})


def _reset_client_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sc_ftshare, "_SID", None)
    monkeypatch.setattr(sc_ftshare, "_SESSION_READY", False)
    monkeypatch.setattr(sc_ftshare, "_LAST_INIT", 0.0)
    monkeypatch.setattr(sc_ftshare, "_LAST_POST", 0.0)
    monkeypatch.setattr(sc_ftshare, "_CONSECUTIVE_ERRORS", 0)
    monkeypatch.setattr(sc_ftshare, "_BLOCKED_REASON", None)
    monkeypatch.setattr(sc_ftshare, "_DIAGNOSTICS", [])
    monkeypatch.setattr(sc_ftshare, "_GOODWILL_BY_CODE", {})
    monkeypatch.setattr(sc_ftshare, "_GOODWILL_CACHE_EXPIRES_AT", 0.0)
    monkeypatch.delenv("FTSHARE_API_KEY", raising=False)
    monkeypatch.setattr(sc_ftshare.time, "sleep", lambda _: None)


def test_parse_accepts_json_and_multiline_sse() -> None:
    json_response = _response('{"jsonrpc":"2.0","id":"1","result":{"ok":true}}')
    sse_response = _response(
        'data: {"jsonrpc":"2.0",\ndata: "id":"2",\ndata: "result":{"ok":true}}\n\n'
    )

    assert sc_ftshare._parse(json_response) == {
        "jsonrpc": "2.0",
        "id": "1",
        "result": {"ok": True},
    }
    assert sc_ftshare._parse(sse_response) == {
        "jsonrpc": "2.0",
        "id": "2",
        "result": {"ok": True},
    }


def test_stateless_server_handshake_and_json_tool_result(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_client_state(monkeypatch)
    responses = [
        _response(
            json.dumps({"jsonrpc": "2.0", "id": "1", "result": {"protocolVersion": "2025-03-26"}})
        ),
        _response(status=202),
        _response(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "2",
                    "result": {"structuredContent": {"data": [{"value": 7}]}},
                }
            )
        ),
    ]
    requests_seen: list[dict[str, Any]] = []

    def fake_post(url: str, **kwargs: Any) -> SimpleNamespace:
        requests_seen.append(kwargs)
        return responses.pop(0)

    monkeypatch.setattr(sc_ftshare.requests, "post", fake_post)

    result = sc_ftshare._call("sample_tool")

    assert result == [{"value": 7}]
    assert len(requests_seen) == 3
    assert all("Mcp-Session-Id" not in request["headers"] for request in requests_seen)
    assert sc_ftshare._SESSION_READY is True
    assert sc_ftshare._ftshare_diagnostics_summary() == ""


def test_optional_api_key_is_sent_only_as_request_header(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_client_state(monkeypatch)
    monkeypatch.setenv("FTSHARE_API_KEY", "test-only-key")
    seen: list[dict[str, Any]] = []

    def fake_post(url: str, **kwargs: Any) -> SimpleNamespace:
        seen.append(kwargs)
        return _response('{"jsonrpc":"2.0","id":"1","result":{"ok":true}}')

    monkeypatch.setattr(sc_ftshare.requests, "post", fake_post)
    sc_ftshare._post({"jsonrpc": "2.0", "id": "1", "method": "tools/list"})

    assert seen[0]["headers"]["FTSHARE_API_KEY"] == "test-only-key"
    assert "test-only-key" not in sc_ftshare._ftshare_diagnostics_summary()


def test_current_live_tool_names_and_date_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_client_state(monkeypatch)
    calls: list[tuple[str, dict[str, Any]]] = []

    def fake_call(tool: str, args: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        calls.append((tool, args or {}))
        return []

    monkeypatch.setattr(sc_ftshare, "_call", fake_call)

    sc_ftshare.get_ft_comment_score_series("600519")
    sc_ftshare.get_ft_comment_desire("600519")
    sc_ftshare.get_ft_comment_focus("600519")
    sc_ftshare.get_ft_comment_org_participate("600519")
    sc_ftshare.get_ft_dapan_flow("20261009")
    sc_ftshare.get_ft_market_snapshot()
    sc_ftshare.get_ft_suspension_list("20261009")
    sc_ftshare.get_ft_unlock_by_date("20261009")
    sc_ftshare.get_ft_pledge_summary()
    sc_ftshare.get_ft_limit_event_timeline("920118", "20261009")

    assert calls == [
        ("ft_v1_stock_comment_score", {"symbol": "600519"}),
        ("ft_v1_stock_comment_desire", {"symbol": "600519"}),
        ("ft_v1_stock_comment_focus", {"symbol": "600519"}),
        ("ft_v1_stock_comment_org_participate", {"symbol": "600519"}),
        ("ft_v1_eastmoney_dapan_flow", {"trade_date": "20261009"}),
        ("ft_v1_daec_market_snapshot", {}),
        ("ft_v1_suspension_list", {"trade_date": "20261009"}),
        (
            "ft_v1_unlock_stock_unlock",
            {"start_date": "20261009", "end_date": "20261009"},
        ),
        ("ft_v1_pledge_pledge_summary", {}),
        (
            "ft_v2_limit_event_timeline_3s",
            {"symbol": "920118.BJ", "trade_date": "20261009"},
        ),
    ]


def test_paginated_getters_fetch_every_page(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_client_state(monkeypatch)
    calls: list[tuple[str, dict[str, Any]]] = []

    def fake_payload(
        tool: str, args: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        arguments = args or {}
        calls.append((tool, arguments))
        page = arguments["page"]
        return {
            "data": [{"tool": tool, "page": page}],
            "metadata": {"total": 2, "pagination": {"pages": 2}},
        }

    monkeypatch.setattr(sc_ftshare, "_call_payload", fake_payload)

    assert [row["page"] for row in sc_ftshare.get_ft_ggmx_changes("920118")] == [1, 2]
    assert [row["page"] for row in sc_ftshare.get_ft_limit_up_pool_yesterday("20261009")] == [1, 2]
    assert calls == [
        ("ft_v1_holder_stock_ggmx", {"stock_code": "920118", "page": 1, "page_size": 200}),
        ("ft_v1_holder_stock_ggmx", {"stock_code": "920118", "page": 2, "page_size": 200}),
        (
            "ft_v1_limit_list",
            {"limit_type": "up", "trade_date": "20261009", "page": 1, "page_size": 100},
        ),
        (
            "ft_v1_limit_list",
            {"limit_type": "up", "trade_date": "20261009", "page": 2, "page_size": 100},
        ),
    ]


def test_paginated_call_rejects_incomplete_result(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_client_state(monkeypatch)
    monkeypatch.setattr(
        sc_ftshare,
        "_call_payload",
        lambda *args, **kwargs: {
            "data": [{"value": 1}],
            "metadata": {"total": 2, "pagination": {"pages": 1}},
        },
    )

    assert sc_ftshare._call_all_pages("sample_tool", {}, page_size=100) == []
    assert "incomplete pages" in sc_ftshare._ftshare_diagnostics_summary()


def test_paginated_call_accepts_consistent_empty_result(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_client_state(monkeypatch)
    monkeypatch.setattr(
        sc_ftshare,
        "_call_payload",
        lambda *args, **kwargs: {
            "data": [],
            "metadata": {
                "total": 0,
                "returned": 0,
                "pagination": {
                    "page": 1,
                    "page_size": 200,
                    "pages": 0,
                    "has_more": False,
                },
            },
        },
    )

    assert sc_ftshare._call_all_pages("sample_tool", {}, page_size=200) == []
    assert sc_ftshare._ftshare_diagnostics_summary() == ""


@pytest.mark.parametrize(
    "payload",
    [
        {
            "data": [],
            "metadata": {"total": 1, "returned": 0, "pagination": {"pages": 0}},
        },
        {
            "data": [{"value": 1}],
            "metadata": {"total": 0, "returned": 1, "pagination": {"pages": 0}},
        },
        {
            "data": [],
            "metadata": {
                "total": 0,
                "returned": 0,
                "pagination": {"pages": 0, "has_more": True},
            },
        },
        {
            "data": [],
            "metadata": {
                "total": 0,
                "returned": 0,
                "pagination": {"pages": 0, "has_more": 0},
            },
        },
    ],
)
def test_paginated_call_rejects_inconsistent_zero_page_result(
    monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any]
) -> None:
    _reset_client_state(monkeypatch)
    monkeypatch.setattr(sc_ftshare, "_call_payload", lambda *args, **kwargs: payload)

    assert sc_ftshare._call_all_pages("sample_tool", {}, page_size=200) == []
    assert "zero-page response is inconsistent" in sc_ftshare._ftshare_diagnostics_summary()


def test_goodwill_market_pages_are_cached_and_filtered_per_stock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _reset_client_state(monkeypatch)
    calls: list[tuple[str, dict[str, Any]]] = []
    pages = {
        1: {
            "data": [
                {"security_code": "600519.SH", "goodwill_scale": "10"},
            ],
            "metadata": {"total": 2, "pagination": {"pages": 2}},
        },
        2: {
            "data": [
                {"security_code": "920118.BJ", "goodwill_scale": "20"},
            ],
            "metadata": {"total": 2, "pagination": {"pages": 2}},
        },
    }

    def fake_payload(tool: str, args: dict[str, Any] | None = None) -> dict[str, Any] | None:
        arguments = args or {}
        calls.append((tool, arguments))
        if tool == "ft_v1_goodwill_market_overview":
            return {"data": [{"report_date": "2026-06-30 00:00:00"}]}
        return pages.get(arguments.get("page"))

    monkeypatch.setattr(sc_ftshare, "_call_payload", fake_payload)

    assert sc_ftshare.get_ft_goodwill_stock_detail("600519") == [
        {"security_code": "600519.SH", "goodwill_scale": "10"}
    ]
    assert sc_ftshare.get_ft_goodwill_stock_detail("920118.BJ") == [
        {"security_code": "920118.BJ", "goodwill_scale": "20"}
    ]
    assert len(calls) == 3
    assert calls[0] == ("ft_v1_goodwill_market_overview", {})
    assert calls[1] == (
        "ft_v1_goodwill_stock_detail",
        {"date": "20260630", "page": 1, "page_size": 500},
    )
    assert calls[2] == (
        "ft_v1_goodwill_stock_detail",
        {"date": "20260630", "page": 2, "page_size": 500},
    )


@pytest.mark.parametrize("status", [403, 429])
def test_http_rate_limit_status_blocks_followup_requests(
    monkeypatch: pytest.MonkeyPatch, status: int
) -> None:
    _reset_client_state(monkeypatch)
    calls = 0

    def forbidden(url: str, **kwargs: Any) -> SimpleNamespace:
        nonlocal calls
        calls += 1
        return _response("blocked", status=status)

    monkeypatch.setattr(sc_ftshare.requests, "post", forbidden)
    body = {"jsonrpc": "2.0", "id": "1", "method": "tools/call"}

    assert sc_ftshare._post(body) is None
    assert sc_ftshare._post(body) is None
    assert calls == 1
    assert f"HTTP {status}" in sc_ftshare._ftshare_diagnostics_summary()


def test_transport_exception_is_retained_as_diagnostic(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_client_state(monkeypatch)

    def unavailable(url: str, **kwargs: Any) -> None:
        raise ConnectionError("proxy refused connection")

    monkeypatch.setattr(sc_ftshare.requests, "post", unavailable)
    body = {"jsonrpc": "2.0", "id": "1", "method": "tools/call"}

    assert sc_ftshare._post(body) is None
    summary = sc_ftshare._ftshare_diagnostics_summary()
    assert "ConnectionError" in summary
    assert "proxy refused connection" in summary


def test_expired_session_404_reinitializes_once(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_client_state(monkeypatch)
    responses = [
        _response(
            json.dumps(
                {"jsonrpc": "2.0", "id": "init1", "result": {"protocolVersion": "2025-03-26"}}
            ),
            headers={"Mcp-Session-Id": "old"},
        ),
        _response(status=202),
        _response("expired", status=404),
        _response(
            json.dumps(
                {"jsonrpc": "2.0", "id": "init2", "result": {"protocolVersion": "2025-03-26"}}
            ),
            headers={"Mcp-Session-Id": "new"},
        ),
        _response(status=202),
        _response(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": "2",
                    "result": {"structuredContent": {"data": [{"value": 3}]}},
                }
            )
        ),
    ]
    requests_seen: list[dict[str, Any]] = []

    def fake_post(url: str, **kwargs: Any) -> SimpleNamespace:
        requests_seen.append(kwargs)
        return responses.pop(0)

    monkeypatch.setattr(sc_ftshare.requests, "post", fake_post)

    assert sc_ftshare._call("sample_tool") == [{"value": 3}]
    assert len(requests_seen) == 6
    assert requests_seen[0]["headers"].get("Mcp-Session-Id") is None
    assert requests_seen[2]["headers"]["Mcp-Session-Id"] == "old"
    assert requests_seen[3]["headers"].get("Mcp-Session-Id") is None
    assert requests_seen[5]["headers"]["Mcp-Session-Id"] == "new"


def test_three_consecutive_http_errors_open_circuit(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_client_state(monkeypatch)
    calls = 0

    def unavailable(url: str, **kwargs: Any) -> SimpleNamespace:
        nonlocal calls
        calls += 1
        return _response("unavailable", status=503)

    monkeypatch.setattr(sc_ftshare.requests, "post", unavailable)
    body = {"jsonrpc": "2.0", "id": "1", "method": "tools/call"}

    for _ in range(4):
        assert sc_ftshare._post(body) is None

    assert calls == 3
    assert "circuit breaker opened" in sc_ftshare._ftshare_diagnostics_summary()


def test_json_text_content_is_decoded_and_tool_errors_are_visible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _reset_client_state(monkeypatch)
    monkeypatch.setattr(
        sc_ftshare,
        "_rpc",
        lambda *args, **kwargs: {
            "result": {"content": [{"type": "text", "text": "[{\"value\": 9}]"}]}
        },
    )

    assert sc_ftshare._call("sample_tool") == [{"value": 9}]

    monkeypatch.setattr(
        sc_ftshare,
        "_rpc",
        lambda *args, **kwargs: {
            "result": {"isError": True, "content": [{"type": "text", "text": "upstream error"}]}
        },
    )
    assert sc_ftshare._call("failing_tool") is None
    assert "upstream error" in sc_ftshare._ftshare_diagnostics_summary()


def test_capture_includes_ftshare_diagnostics(monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts import capture_field_probe

    monkeypatch.setattr(
        capture_field_probe,
        "_last_completed_trading_day",
        lambda: date(2026, 10, 9),
    )
    monkeypatch.setattr(sc_ftshare, "_clear_diagnostics", lambda: None)
    monkeypatch.setattr(
        sc_ftshare,
        "_ftshare_diagnostics_summary",
        lambda: "HTTP 429 at tools/call",
    )
    monkeypatch.setattr(sc_ftshare, "is_ftshare_enabled", lambda: True)
    for name in (
        "get_ft_dapan_flow",
        "get_ft_market_snapshot",
        "get_ft_suspension_list",
        "get_ft_limit_up_pool_yesterday",
        "get_ft_unlock_by_date",
        "get_ft_pledge_summary",
    ):
        monkeypatch.setattr(sc_ftshare, name, lambda *args, **kwargs: None)

    result = capture_field_probe.collect_ftshare([])

    assert "HTTP 429" in result["__error__"]
    assert "no populated data fields" in result["__error__"]
