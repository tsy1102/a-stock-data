from __future__ import annotations

from typing import Any

import pytest

from stock_common.sc_datasource import _etf


class _Response:
    def __init__(self, payload: Any) -> None:
        self._payload = payload

    def json(self) -> Any:
        return self._payload


def _payload(*, scale_header: str) -> list[dict[str, Any]]:
    return [
        {
            "metadata": {
                "name": "基金列表",
                "subname": "2026-11-20",
                "pagecount": 1,
                "recordcount": 1,
                "cols": {"dqgm": scale_header},
            },
            "data": [
                {
                    "sys_key": "<u>159915</u>",
                    "jjjcurl": "<u>创业板ETF易方达</u>",
                    "dqgm": "<a>1,234.56</a>",
                    "tzlb": "股票基金",
                    "glrmc": "易方达基金管理有限公司",
                    "ssrq": "2011-12-09",
                }
            ],
        }
    ]


def test_szse_etf_date_uses_current_scale_column_date(monkeypatch):
    requested = []
    header = (
        "当前规模<br>（万份）<span class='tip'>T日晚间更新的T日规模仅供参考，"
        "以T+1日早间更新的T日规模为准</span><br>（2026-11-19）"
    )

    def fake_request(url, **kwargs):
        requested.append((url, kwargs))
        return _Response(_payload(scale_header=header))

    monkeypatch.setattr(_etf, "_quick_request", fake_request)

    rows = _etf._etf_shares_szse_host("https://www.szse.cn", "2026-11-20")

    assert rows == [
        {
            "date": "2026-11-19",
            "exchange": "SZ",
            "code": "159915",
            "name": "创业板ETF易方达",
            "fund_category": "股票基金",
            "shares_10k": 1234.56,
            "manager": "易方达基金管理有限公司",
            "listing_date": "2011-12-09",
        }
    ]
    assert len(requested) == 1
    assert requested[0][1]["timeout"] == 15


@pytest.mark.parametrize(
    "header",
    [
        "当前规模（万份）",
        "当前规模（万份）（2026-11-19）（2026-11-20）",
        "当前规模（万份）（2026-02-30）",
    ],
)
def test_szse_etf_date_fails_closed_without_one_valid_scale_date(monkeypatch, header):
    monkeypatch.setattr(
        _etf,
        "_quick_request",
        lambda *_args, **_kwargs: _Response(_payload(scale_header=header)),
    )

    with pytest.raises(RuntimeError, match="当前规模列"):
        _etf._etf_shares_szse_host("https://www.szse.cn", "2026-11-20")
