from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from stock_common import sc_ftshare


class FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200):
        self.payload = payload
        self.status_code = status_code
        self.headers: dict[str, str] = {}
        self.closed = False

    def json(self) -> dict:
        return self.payload

    def close(self) -> None:
        self.closed = True


def _quote_item(symbol: str = "600000.SH", day: str = "2026-10-20") -> dict:
    quote_time = datetime.fromisoformat(f"{day}T15:00:00+08:00")
    return {
        "symbol": symbol,
        "name": "浦发银行",
        "close": "10.50",
        "change_rate": 0.01,
        "ts_millis": int(quote_time.timestamp() * 1000),
    }


def _payload(items: list[dict], *, page: int = 1, total_pages: int = 1) -> dict:
    return {
        "code": 0,
        "message": "ok",
        "data": {
            "page": page,
            "page_size": 40,
            "total_pages": total_pages,
            "total_items": len(items),
            "items": items,
        },
    }


def test_filter_uses_documented_json_array_syntax():
    assert sc_ftshare._build_filter(["600000.XSHG", "000001.XSHE"]) == (
        'symkey IN ["600000.XSHG","000001.XSHE"]'
    )


def test_capture_normalizes_symbol_matches_effective_date_and_redacts_key(monkeypatch):
    monkeypatch.setattr(sc_ftshare, "FTSHARE_MIN_REQUEST_INTERVAL_SECONDS", 0)
    response = FakeResponse(_payload([_quote_item()]))
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return response

    monkeypatch.setattr(sc_ftshare.requests, "get", fake_get)
    secret = "test-ftshare-secret"
    result = sc_ftshare.get_a_share_quote_snapshot(
        ["600000"], data_date="2026-10-20", environ={"FTSHARE_API_KEY": secret}
    )

    assert result["scheme"] == "ftshare.rest.a_share_quote"
    assert result["as_of_date"] == "2026-10-20"
    assert set(result["stocks"]) == {"600000"}
    assert result["stocks"]["600000"]["symbol"] == "600000.SH"
    assert result["source_meta"]["collision_eligible"] is True
    assert result["source_meta"]["upstream_lineage_status"] == "unverified"
    assert response.closed is True
    assert len(calls) == 1
    url, kwargs = calls[0]
    assert url.endswith(sc_ftshare.FTSHARE_QUOTE_PATH)
    assert kwargs["headers"]["FTSHARE_API_KEY"] == secret
    assert kwargs["params"]["filter"] == 'symkey IN ["600000.XSHG"]'
    assert kwargs["allow_redirects"] is False
    assert secret not in json.dumps(result, ensure_ascii=False)


@pytest.mark.parametrize("status_code", [403, 429])
def test_rate_limit_stops_without_retry_or_response_body(monkeypatch, status_code):
    monkeypatch.setattr(sc_ftshare, "FTSHARE_MIN_REQUEST_INTERVAL_SECONDS", 0)
    response = FakeResponse({"error": "sensitive body must not leak"}, status_code=status_code)
    calls = []
    monkeypatch.setattr(
        sc_ftshare.requests, "get", lambda *args, **kwargs: calls.append(1) or response
    )

    with pytest.raises(sc_ftshare.FTShareRateLimitError) as exc:
        sc_ftshare.get_a_share_quote_snapshot(
            ["600000"], data_date="2026-10-20", environ={"FTSHARE_API_KEY": "secret"}
        )

    assert len(calls) == 1
    assert response.closed is True
    assert "secret" not in str(exc.value)
    assert "sensitive body" not in str(exc.value)
    assert "no retry" in str(exc.value)


def test_quote_date_mismatch_is_rejected_without_historical_substitution(monkeypatch):
    monkeypatch.setattr(sc_ftshare, "FTSHARE_MIN_REQUEST_INTERVAL_SECONDS", 0)
    response = FakeResponse(_payload([_quote_item(day="2026-10-19")]))
    monkeypatch.setattr(sc_ftshare.requests, "get", lambda *args, **kwargs: response)

    with pytest.raises(
        sc_ftshare.FTShareRequestError, match="does not match requested effective date"
    ):
        sc_ftshare.get_a_share_quote_snapshot(
            ["600000"], data_date="2026-10-20", environ={"FTSHARE_API_KEY": "secret"}
        )
    assert response.closed is True


@pytest.mark.parametrize("invalid_timestamp", [None, True, 1.5, []])
def test_invalid_quote_timestamp_is_skipped_without_type_error(monkeypatch, invalid_timestamp):
    monkeypatch.setattr(sc_ftshare, "FTSHARE_MIN_REQUEST_INTERVAL_SECONDS", 0)
    item = _quote_item()
    item["ts_millis"] = invalid_timestamp
    response = FakeResponse(_payload([item]))
    monkeypatch.setattr(sc_ftshare.requests, "get", lambda *args, **kwargs: response)

    with pytest.raises(
        sc_ftshare.FTShareRequestError, match="does not match requested effective date"
    ):
        sc_ftshare.get_a_share_quote_snapshot(
            ["600000"], data_date="2026-10-20", environ={"FTSHARE_API_KEY": "secret"}
        )
    assert response.closed is True


def test_capture_requires_key_without_exposing_credential_contents(tmp_path: Path):
    key_file = tmp_path / "ftshare-key.txt"
    with pytest.raises(sc_ftshare.FTShareRequestError, match="key is unavailable"):
        sc_ftshare._load_api_key(key_file, environ={})


def test_lineage_and_registry_expose_documented_contract_anchors_only():
    from scripts.collide import load_registry_context

    context = load_registry_context()
    contract_codes = {
        code for source, code in context["contract_anchors"] if source == "ftshare_rest"
    }
    assert len(contract_codes) == 31
    assert "close" in contract_codes
    assert "symbol_id" not in contract_codes
    assert ("ftshare_rest", "close") in context["verified"]
    assert not any(source == "ftshare_rest" for source, _ in context["anchors"])
    assert ("ftshare_rest", "close") in context["official_contract_verified"]
    assert ("ftshare_rest", "close") in context["official_contract_anchors"]


def test_fuyao_contract_evidence_is_reported_without_becoming_l1c():
    from scripts.collide import load_registry_context

    context = load_registry_context()

    assert ("fuyao", "accounts_receivable") in context["official_contract_verified"]
    assert ("fuyao", "accounts_receivable") in context["official_contract_anchors"]
    assert ("fuyao", "accounts_receivable") in context["anchors"]
    assert ("fuyao", "accounts_receivable") not in context["contract_anchors"]
    assert ("fuyao", "pe_ttm") not in context["official_contract_verified"]
