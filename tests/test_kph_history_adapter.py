from __future__ import annotations

from typing import Any

import pytest
import requests

from stock_common import sc_network
from stock_common.sc_datasource import _kph


def _row(code: str, *, industry_count: int = 3) -> list[Any]:
    row: list[Any] = [None] * 28
    row[0] = code
    row[1] = f"股票{code}"
    row[6] = "1790645140"
    row[7] = "0"
    row[8] = "100"
    row[9] = "首板"
    row[10] = "1"
    row[11] = "主题"
    row[12] = "300"
    row[13] = "400"
    row[14] = "0.5"
    row[15] = "5000"
    row[16] = "原因"
    row[23] = "200"
    row[26] = "801001"
    row[27] = str(industry_count)
    return row


class _Response:
    def __init__(self, rows: list[list[Any]], *, status_code: int = 200) -> None:
        self.rows = rows
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(
                f"HTTP {self.status_code}",
                response=self,
            )

    def json(self) -> dict[str, Any]:
        return {"errcode": "0", "list": self.rows}


class _Session:
    def __init__(self, responses: list[_Response]) -> None:
        self.responses = responses
        self.calls: list[dict[str, Any]] = []
        self.trust_env = True
        self.closed = False

    def post(self, url: str, **kwargs: Any) -> _Response:
        self.calls.append({"url": url, **kwargs})
        return self.responses[len(self.calls) - 1]

    def close(self) -> None:
        self.closed = True


def test_kph_history_fetches_all_pages_with_direct_rate_limited_requests(monkeypatch):
    first_page = [_row(f"60{index:04d}") for index in range(50)]
    last_page = [_row("600050"), _row("600051", industry_count=4)]
    session = _Session([_Response(first_page), _Response(last_page)])
    rate_limit_calls: list[None] = []

    monkeypatch.setattr(_kph.requests, "Session", lambda: session)
    monkeypatch.setattr(
        sc_network,
        "_kph_wait_process_interval",
        lambda: rate_limit_calls.append(None),
    )

    records, pagination = _kph.get_kph_limit_up_history("2026-09-29")

    assert session.trust_env is False
    assert session.closed is True
    assert [call["data"]["Index"] for call in session.calls] == ["0", "50"]
    assert all(call["data"]["st"] == "50" for call in session.calls)
    assert all(call["data"]["Day"] == "2026-09-29" for call in session.calls)
    assert len(rate_limit_calls) == 2
    assert len(records) == 52
    assert records[0]["industry_limit_up_count"] == 3
    assert records[-1]["industry_limit_up_count"] == 4
    assert pagination == {
        "page_size": 50,
        "pages_fetched": 2,
        "returned_rows": 52,
        "complete": True,
    }


def test_kph_history_rejects_a_repeated_full_page(monkeypatch):
    repeated_page = [_row(f"60{index:04d}") for index in range(50)]
    session = _Session([_Response(repeated_page), _Response(repeated_page)])
    monkeypatch.setattr(_kph.requests, "Session", lambda: session)
    monkeypatch.setattr(sc_network, "_kph_wait_process_interval", lambda: None)

    with pytest.raises(RuntimeError, match="repeated a page"):
        _kph.get_kph_limit_up_history("2026-09-29")

    assert len(session.calls) == 2
    assert session.closed is True


def test_kph_history_marks_http_throttling(monkeypatch):
    session = _Session([_Response([], status_code=429)])
    marked: list[tuple[str, int | None]] = []
    monkeypatch.setattr(_kph.requests, "Session", lambda: session)
    monkeypatch.setattr(sc_network, "_kph_wait_process_interval", lambda: None)
    monkeypatch.setattr(
        sc_network,
        "_mark_levistock_provider_block",
        lambda family, error: marked.append((family, error.response.status_code)),
    )

    with pytest.raises(requests.HTTPError):
        _kph.get_kph_limit_up_history("2026-09-29")

    assert marked == [("kph", 429)]
    assert session.closed is True
