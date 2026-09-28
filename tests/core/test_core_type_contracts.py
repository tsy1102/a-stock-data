from pathlib import Path
from typing import Any

import pytest

from core import zhb_sync
from core.zhb_client import ZhbData
import stock_common.sc_capital_cache as capital_cache
import stock_common.sc_fuyao as fuyao


class _NonObjectResponse:
    status_code = 200

    def json(self) -> list[Any]:
        return []


def test_fuyao_raw_rejects_non_object_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(fuyao, "get_fuyao_key", lambda: "test-key")
    monkeypatch.setattr(
        fuyao,
        "_quick_request",
        lambda *args, **kwargs: _NonObjectResponse(),
    )

    assert fuyao._fuyao_raw("/test") is None


def test_market_cap_accepts_numeric_strings_from_legacy_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        capital_cache,
        "get_share_capital",
        lambda code: {"total_shares": "10000", "float_shares": "20000"},
    )

    assert capital_cache.calc_mcap_yi("600000", 2.0) == 2.0
    assert capital_cache.calc_float_mcap_yi("600000", 2.0) == 4.0


def test_zhb_industry_code_getter_returns_text() -> None:
    zhb = ZhbData()
    zhb._stock_stats2 = {"600000": {"industry_code": 880301}}

    assert zhb.get_industry_code("600000") == "880301"


def test_sync_state_non_object_json_uses_defaults(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state_file = tmp_path / "sync_state.json"
    state_file.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(zhb_sync, "_SYNC_STATE_FILE", str(state_file))
    monkeypatch.setattr(zhb_sync, "_log_sync", lambda message: None)

    assert zhb_sync._load_sync_state() == {
        "last_sync_time": 0,
        "last_sync_date": "",
        "last_sync_success": False,
        "consecutive_failures": 0,
        "total_syncs": 0,
        "total_failures": 0,
    }


def test_parse_cron_returns_five_integer_fields() -> None:
    assert zhb_sync._parse_cron("30 10 * * 1-5") == (
        [30],
        [10],
        list(range(1, 32)),
        list(range(1, 13)),
        [1, 2, 3, 4, 5],
    )
