"""_ticks.py — 腾讯逐笔成交 (V17.4.7 吸收上游 3.10.0 §1.4, 替代失效的 mootdx transaction).

数据来源: 腾讯行情页「成交明细」接口 (stock.gtimg.cn/data/index.php), 一页 70 笔, 逐页翻到空页为止。

设计对齐上游(经 2026-09-22 上游权威仓库 SKILL.md 对撞校正):
  - 错误契约: 参数错/确实无数据(北交所·指数·代码不存在·当日无成交) → ValueError;
              源格式变/完整性核对失败 → RuntimeError。
  - 收盘后完整性核对: 连续竞价段(≤15:00:59)逐笔成交额合计 与 腾讯行情快照当日成交额 差 > 0.1% 抛 RuntimeError。
  - 盘后定价段腾讯偶尔缺页缓存缺号 → frame.attrs["missing_seq"]，完整性核验结果 → frame.attrs["complete"]。
  - source/source_url/fetched_at 溯源(对齐本项目 _macro 等层契约)。

注: 字段语义(transact_seq/price/side 等)非 a-stock f-code 破解字段, 不进 field_dict 治理管线;
    取数层契约经对撞校正, 无需再走 collide 终检。
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from stock_common.symbol_norm import normalize_symbol
from stock_common.sc_network import _quick_request
from ._v39_compat import _req_num, _src_date, _frame, _contract

TENCENT_TICK_URL = "https://stock.gtimg.cn/data/index.php"
TENCENT_QT_URL = "https://qt.gtimg.cn/q="
_TICK_MAX_PAGES = 300  # 一页 70 笔; 2026-09-22 实测最活跃的票全天约 4800 笔 / 69 页
_TICK_HTTP_ATTEMPTS = 4
_TICK_RETRY_BACKOFF_SECONDS = 0.6
_TICK_SESSION_END = (
    "15:00:59"  # 连续竞价 + 收盘集合竞价到此为止(科创板收盘那笔在 15:00:02), 之后是盘后定价
)

# 仅导出公开 API(辅助函数来自 _v39_compat, 不污染 sc_datasource 的 import * 命名空间)
__all__ = [
    "tencent_ticks",
    "_parse_qt_snapshot",
    "_parse_tick_page",
    "TENCENT_TICK_URL",
    "TENCENT_QT_URL",
]


# ─── 纯解析函数(便于离线测试, 与网络解耦) ───
def _parse_qt_snapshot_details(symbol: str, text: str) -> tuple[str, str, float, Optional[float]]:
    """解析快照为交易日、时刻、总成交额和可选的盘后成交额（元）。"""
    if "v_pv_none_match" in text:
        raise ValueError(f"腾讯没有 {symbol} 这个代码")
    match = re.search(rf'v_{symbol}="([^"]*)"', text)
    if not match:
        raise RuntimeError(f"腾讯行情快照 {symbol} 的返回里没有 v_{symbol} 变量，格式可能已变")
    fields = match.group(1).split("~")
    if len(fields) < 36 or not re.fullmatch(r"[0-9]{14}", fields[30]):
        raise RuntimeError(
            f"腾讯行情快照 {symbol} 字段数 {len(fields)} 或时间字段不对，格式可能已变"
        )
    parts = fields[35].split(
        "/"
    )  # 「最新价/成交量/成交额(元)」; 科创板的成交量是股、其余是手, 只用成交额
    if len(parts) != 3:
        raise RuntimeError(f"腾讯行情快照 {symbol} 的价/量/额字段是 {fields[35]!r}，格式可能已变")
    aftermarket_amount: Optional[float] = None
    if len(fields) > 58:
        raw_aftermarket_amount = fields[58].strip()
        if raw_aftermarket_amount not in ("", "-", "--"):
            # 腾讯快照第 58 项单位为万元；逐笔 amount 的单位为元。
            aftermarket_amount = _req_num(raw_aftermarket_amount, "盘后成交额") * 10_000
    return (
        _src_date(fields[30][:8]),
        fields[30][8:],
        _req_num(parts[2], "成交额"),
        aftermarket_amount,
    )


def _parse_qt_snapshot(symbol: str, text: str) -> tuple[str, str, float]:
    """解析快照为 (交易日, 时刻, 当日成交额元)；代码不存在抛 ValueError。"""
    day, clock, amount, _ = _parse_qt_snapshot_details(symbol, text)
    return day, clock, amount


def _parse_tick_page(symbol: str, page: int, text: str) -> Optional[List[Dict[str, Any]]]:
    """解析腾讯逐笔单页文本 → 记录列表; 翻过最后一页腾讯返回空内容 → None。"""
    if not text:
        return None
    match = re.fullmatch(rf'v_detail_data_{symbol}=\[(\d+),"([^"]*)"\];?', text)
    if not match or int(match.group(1)) != page:
        raise RuntimeError(f"腾讯逐笔 {symbol} 第 {page} 页不是预期格式: {text[:80]!r}")
    if not match.group(2):
        return None
    records: List[Dict[str, Any]] = []
    try:
        for item in match.group(2).split("|"):
            seq, clock, price, change, volume, amount, side = item.split("/")
            if not re.fullmatch(r"\d\d:\d\d:\d\d", clock) or side not in ("B", "S", "M"):
                raise ValueError(item)
            records.append(
                {
                    "seq": int(seq),
                    "time": clock,
                    "price": _req_num(price, "price"),
                    "change": _req_num(change, "change"),
                    "volume": _req_num(volume, "volume"),
                    "amount": _req_num(amount, "amount"),
                    "side": side,
                }
            )
    except ValueError as exc:  # 字段数不对 / 序号不是整数 / 方向认不出: 源格式变了, 不是参数错
        raise RuntimeError(f"腾讯逐笔 {symbol} 第 {page} 页记录格式改变: {exc}") from exc
    return records


# ─── 网络封装 ───
def _tencent_request(
    url: str,
    *,
    purpose: str,
    params: Optional[Dict[str, Any]] = None,
) -> requests.Response:
    """Tencent request using the shared limited session and bounded transient retries."""
    last_error: Dict[str, Any] = {}
    for attempt in range(_TICK_HTTP_ATTEMPTS):
        error: Dict[str, Any] = {}
        response = _quick_request(
            url,
            params=params,
            timeout=(5, 15),
            max_retries=1,
            error_out=error,
            stream=True,
        )
        if response is not None:
            return response

        last_error = error
        try:
            status_code = int(error.get("status_code") or 0)
        except (TypeError, ValueError):
            status_code = 0
        kind = error.get("kind")
        retryable = kind in {"timeout", "connection_error", "http_429"} or 500 <= status_code < 600
        if not retryable or attempt + 1 >= _TICK_HTTP_ATTEMPTS:
            break
        time.sleep(_TICK_RETRY_BACKOFF_SECONDS * (2**attempt))

    detail = last_error.get("status_code") or last_error.get("kind") or "unknown error"
    raise RuntimeError(f"腾讯{purpose}请求失败（{detail}），已按重试策略停止")


def _read_tencent_response(response: requests.Response, *, purpose: str) -> str:
    """Read and close a streamed response; body-read failures are deliberately not retried."""
    try:
        return response.content.decode("gbk", "replace").strip()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"腾讯{purpose}响应体读取失败；该阶段不自动重试") from exc
    finally:
        close = getattr(response, "close", None)
        if callable(close):
            close()


def _tencent_qt_snapshot(symbol: str) -> tuple[str, str, float, Optional[float]]:
    """腾讯行情快照 → 交易日、时刻、当日成交额元、可选盘后成交额元。"""
    response = _tencent_request(TENCENT_QT_URL + symbol, purpose=f"行情快照 {symbol}")
    text = _read_tencent_response(response, purpose=f"行情快照 {symbol}")
    return _parse_qt_snapshot_details(symbol, text)


def _tencent_tick_page(symbol: str, page: int) -> Optional[List[Dict[str, Any]]]:
    """第 page 页逐笔(0 起) → 记录列表; 翻过最后一页腾讯返回空内容 → None。"""
    response = _tencent_request(
        TENCENT_TICK_URL,
        purpose=f"逐笔 {symbol} 第 {page} 页",
        params={"appn": "detail", "action": "data", "c": symbol, "p": page},
    )
    text = _read_tencent_response(response, purpose=f"逐笔 {symbol} 第 {page} 页")
    return _parse_tick_page(symbol, page, text)


@_contract
def tencent_ticks(code: str) -> pd.DataFrame:
    """腾讯逐笔成交(分笔) — 最近一个交易日的全部成交明细, 沪深个股与 ETF。

    一行一笔: date / code / time / seq(腾讯序号) / price / change(较上一笔) / volume(手) /
    amount(元) / side(B 主动买 · S 主动卖 · M 中性)。约 3 秒一笔的分笔, 不是 Level-2 逐笔。
    北交所、指数、代码不存在、当日没有成交抛 ValueError。收盘后调用会用行情快照的当日成交额
    核对连续竞价段, 对不上抛 RuntimeError；盘后缺号记录在 `missing_seq`，`complete` 为 True/False/None。
    `complete` 只有取数前快照时刻不早于 15:31 且快照包含盘后金额时才可核验；盘中或缺少金额字段时为 None。
    """
    sym = normalize_symbol(code)
    prefix = sym.market.lower()
    ticker = sym.code
    if prefix == "bj":
        raise ValueError("腾讯逐笔不支持北交所（返回空）；北交所日线见 tdx_daily_package")
    if (prefix, ticker[:3]) in (("sh", "000"), ("sz", "399")):
        raise ValueError(f"{prefix}{ticker} 是指数，没有逐笔成交")
    symbol = sym.tencent()
    day, clock, amount_before, aftermarket_amount = _tencent_qt_snapshot(symbol)
    if amount_before == 0:
        raise ValueError(f"{symbol} 在 {day} 没有成交（停牌、尚未开盘或集合竞价未撮合）")
    rows: List[Dict[str, Any]] = []
    missing: List[int] = []
    for page in range(_TICK_MAX_PAGES):
        records = _tencent_tick_page(symbol, page)
        if records is None:
            break
        for r in records:
            expected = rows[-1]["seq"] + 1 if rows else 0
            if r["seq"] < expected or (rows and r["time"] < rows[-1]["time"]):
                raise RuntimeError(
                    f"腾讯逐笔 {symbol} 序号或时间倒退（第 {page} 页 {r['seq']} {r['time']}），结果不可信"
                )
            if r["seq"] > expected:
                if r["time"] <= _TICK_SESSION_END:
                    raise RuntimeError(
                        f"腾讯逐笔 {symbol} 缺序号 {expected}–{r['seq'] - 1}（{r['time']} 之前，第 {page} 页），"
                        "腾讯该页缓存不完整，稍后重试"
                    )
                missing.extend(range(expected, r["seq"]))
            rows.append(r)
        time.sleep(0.1)
    else:
        raise RuntimeError(f"腾讯逐笔 {symbol} 翻到第 {_TICK_MAX_PAGES} 页仍未结束，格式可能已变")
    if not rows:
        if clock < "092500":
            raise ValueError(f"{symbol} 集合竞价尚未撮合（{clock}），还没有逐笔")
        raise RuntimeError(
            f"{symbol} 在 {day} 成交 {amount_before:.0f} 元，腾讯逐笔却为空："
            "开盘前腾讯可能已清空上一交易日的明细，否则是接口变了"
        )
    day_after, _, amount_after, _ = _tencent_qt_snapshot(symbol)
    if day_after != day:
        raise RuntimeError(f"取数期间交易日从 {day} 变成 {day_after}，请重试")
    session = sum(r["amount"] for r in rows if r["time"] <= _TICK_SESSION_END)
    # 两次快照成交额相同说明取数期间没有新成交(收盘后 / 午休 / 停牌), 此时连续竞价段逐笔合计应与当日成交额相符
    if (
        amount_after == amount_before
        and abs(session - amount_before) > amount_before * 0.001 + 1000
    ):
        raise RuntimeError(
            f"腾讯逐笔 {symbol} 连续竞价段成交额 {session:.0f} 元，与行情快照 {amount_before:.0f} 元对不上，"
            "逐笔可能不全"
        )
    aftermarket_rows = [r for r in rows if r["time"] > _TICK_SESSION_END]
    aftermarket_sum = sum(r["amount"] for r in aftermarket_rows)
    if missing:
        complete: Optional[bool] = False
    elif clock < "153100" or aftermarket_amount is None:
        complete = None
    else:
        complete = abs(aftermarket_sum - aftermarket_amount) <= len(aftermarket_rows) + 1
    frame = _frame(
        rows,
        "tencent",
        f"{TENCENT_TICK_URL}?appn=detail&action=data&c={symbol}",
        ["time", "seq", "price", "change", "volume", "amount", "side"],
    )
    frame.insert(0, "date", day)
    frame.insert(1, "code", symbol)
    frame.attrs["missing_seq"] = missing
    frame.attrs["complete"] = complete
    return frame
