"""_futures_sina.py — 新浪期货日K (V17.4.7 吸收上游 3.10.0 §13.7).

数据来源: 新浪期货日K (stock2.finance.sina.com.cn ... InnerFuturesNewService.getDailyKLine)。
覆盖全部六家交易所(含大商所), 补大商所历史日线(官网 JS 反爬 412, 无官方日行情)。

设计对齐上游(经 2026-09-22 上游权威仓库 SKILL.md 对撞校正):
  - 错误契约: 代码不存在/太老/区间内无K → ValueError; 返回格式变 → RuntimeError。
  - settle 新浪给 0 → None(无结算价)。
  - source/source_url/fetched_at 溯源(对齐本项目 _ticks/_macro 等层契约)。

注: 期货价格字段非 a-stock f-code 破解字段, 不进 field_dict 治理管线;
    取数层契约经对撞校正, 无需再走 collide 终检。
"""

from __future__ import annotations

import json
import re
from typing import Any

import pandas as pd

from stock_common.sc_network import _quick_request
from ._v39_compat import _fut_price, _to_num, _src_date, _rows, _frame, _contract

SINA_FUT_KLINE_URL = (
    "https://stock2.finance.sina.com.cn/futures/api/jsonp.php/var%20_{code}="
    "/InnerFuturesNewService.getDailyKLine"
)

# 仅导出公开 API(辅助函数来自 _v39_compat, 不污染 sc_datasource 的 import * 命名空间)
__all__ = ["futures_kline_sina", "_parse_futures_payload", "SINA_FUT_KLINE_URL"]


# ─── 纯解析函数(便于离线测试, 与网络解耦) ───
def _parse_futures_payload(code: str, text: str) -> list[dict[str, Any]]:
    """解析新浪期货日K JSONP 文本 → 行列表(按日期升序, 未做区间过滤)。

    返回行字段: date / symbol / open / high / low / close / settle / volume / open_interest。
    text 为 'null' → 抛 ValueError(代码不存在或约 2022 年前老合约); 非预期 JSONP / 非 JSON → RuntimeError。
    """
    match = re.search(rf"var _{re.escape(code)}=\((.*)\);?\s*$", text, re.S)
    if not match:
        raise RuntimeError(f"新浪期货日K {code} 的返回不是预期的 JSONP，格式可能已变")
    body = match.group(1).strip()
    if body == "null":
        raise ValueError(
            f"新浪没有期货 {code} 的日K：代码不存在，或是约 2022 年以前到期的老合约"
            "（郑商所也要写 4 位年月，如 MA2601）"
        )
    try:
        items = json.loads(body)
    except ValueError as exc:
        raise RuntimeError(f"新浪期货日K {code} 的返回不是 JSON，格式可能已变") from exc
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for r in _rows(items, f"新浪期货日K {code}"):
        day = _src_date(r["d"])
        if day in seen:
            raise RuntimeError(f"新浪期货日K {code} 同一天 {day} 出现两次，结果不可信")
        seen.add(day)
        rows.append(
            {
                "date": day,
                "symbol": code,
                "open": _fut_price(r["o"]),
                "high": _fut_price(r["h"]),
                "low": _fut_price(r["l"]),
                "close": _fut_price(r["c"]),
                "settle": _fut_price(r["s"]),  # 新浪没有结算价时给 0 → None
                "volume": _to_num(r["v"]),
                "open_interest": _to_num(r["p"]),
            }
        )
    rows.sort(key=lambda row: row["date"])
    return rows


@_contract
def futures_kline_sina(
    symbol: str, start: str | None = None, end: str | None = None
) -> pd.DataFrame:
    """国内期货日 K 线（新浪）— 单个合约或主力连续的逐日序列, 覆盖全部六家交易所(含大商所)。

    symbol: 'RB0' / 'M0'(主力连续) 或 'RB2601' / 'M2601' / 'IF2612'; 郑商所也写 4 位年月('MA2601'),
            带不带 'nf_' 前缀都行。
    start/end: 'YYYY-MM-DD', 可只给一端。主力连续换月当天会跳空, 未做复权。
    代码不存在 / 太老、区间内没有 K 线抛 ValueError; 返回格式改变抛 RuntimeError。
    """
    code = str(symbol).strip()
    code = code[3:] if code.lower().startswith("nf_") else code
    if not re.fullmatch(r"[A-Za-z]{1,2}\d{1,4}", code):
        raise ValueError(f"期货代码格式不对: {symbol}（例 RB0 / RB2601 / MA2601）")
    code = code.upper()
    lo = _src_date(start) if start else None
    hi = _src_date(end) if end else None
    if lo and hi and lo > hi:
        raise ValueError(f"start {lo} 晚于 end {hi}")
    response = _quick_request(
        SINA_FUT_KLINE_URL.format(code=code),
        params={"symbol": code},
        headers={"Referer": "https://finance.sina.com.cn/"},
        timeout=15,
    )
    if response is None:
        raise RuntimeError(f"新浪期货日K {code} 请求失败或被限流")
    rows = _parse_futures_payload(code, response.content.decode("gbk", "replace"))
    if lo or hi:
        rows = [r for r in rows if (not lo or r["date"] >= lo) and (not hi or r["date"] <= hi)]
    if not rows:
        raise ValueError(f"新浪期货 {code} 在所给区间内没有日K（合约当时未上市或已到期）")
    return _frame(
        rows,
        "sina",
        response.url,
        ["date", "symbol", "open", "high", "low", "close", "settle", "volume", "open_interest"],
    )
