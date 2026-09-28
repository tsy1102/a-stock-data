from __future__ import annotations
from datetime import datetime, timedelta
import code
import json
import math
import re
import time
from stock_common.sc_network import _debug_log
from stock_common.sc_utils import em_exchange_prefix

# stock_common/sc_datasource/_official_backup.py
# V17.2.11: 官方交易所备胎源（参考 a-stock-data V3.8.0 官方备胎扩展，2026-09-05 实测）
# 沪深交易所官方两融 + 北交所官方行情，用作东财封禁时的降级备份源。
# 上游为单文件 SKILL.md；此处按项目 exec 子模块规范移植为命名空间片段。
# 仅依赖 requests / pandas（与项目一致），不走东财限流（独立官方域名）。
#
# 数值语义严格对齐上游：单位、字段名、分页/交易日校验均原样移植，便于数值级对撞。

from datetime import timezone
from typing import Any, Optional

from io import BytesIO

import requests
import pandas as pd

# ── Layer 12 官方源辅助函数（移植自上游 SKILL.md，保持数值语义一致）──


def _official_code(value: object) -> str:
    value = str(value).strip()
    if not re.fullmatch(r"[0-9]{6}", value):
        raise ValueError("代码必须是 6 位纯数字；指数 provider 与证券交易所不是同一概念")
    return value


def _official_date(value: object) -> str:
    value = str(value).strip()
    fmt = "%Y%m%d" if re.fullmatch(r"[0-9]{8}", value) else "%Y-%m-%d"
    return datetime.strptime(value, fmt).date().isoformat()


def _official_number(value: Any, required: bool = False) -> Optional[float]:
    if pd.isna(value) or str(value).strip() in ("", "-", "--"):
        if required:
            raise RuntimeError("官方源缺少必需数值")
        return None
    number = float(str(value).replace(",", ""))
    if not math.isfinite(number):
        raise RuntimeError("官方源返回非有限数值")
    return number


def _official_get(
    url: str, params: Optional[dict[str, Any]] = None, referer: Optional[str] = None
) -> requests.Response:
    response = requests.get(
        url,
        params=params,
        headers={"User-Agent": "Mozilla/5.0", "Referer": referer or url},
        timeout=(10, 40),
    )
    response.raise_for_status()
    return response


def _official_excel(response: requests.Response) -> pd.DataFrame:
    try:
        frame = pd.read_excel(BytesIO(response.content), dtype=str)
    except (ValueError, OSError) as exc:
        raise RuntimeError("官方源未返回可解析的 Excel；可能未发布或响应结构改变") from exc
    # 两种中证文件的表头空格略有差异，按完整列名去空白后匹配。
    frame.columns = [re.sub(r"\s+", "", str(c)) for c in frame.columns]
    return frame


def _official_columns(frame: pd.DataFrame, names: list[str]) -> None:
    missing = set(names) - set(frame.columns)
    if missing:
        raise RuntimeError("官方数据列缺失: " + ", ".join(sorted(missing)))


def _official_frame(
    rows: list[dict[str, Any]], keys: list[str], source: str, url: str
) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    if frame.empty or frame.duplicated(keys).any():
        raise RuntimeError("官方数据为空或主键重复，不能当成完整快照")
    frame["source"] = source
    frame["source_url"] = url
    frame["fetched_at"] = datetime.now(timezone.utc).isoformat()
    return frame.sort_values(keys).reset_index(drop=True)


def _official_total(value: Any) -> int:
    if not re.fullmatch(r"[0-9]+", str(value)):
        raise RuntimeError("官方分页总数必须为非负整数")
    return int(value)


def _official_margin_code(value: Any, exchange: str) -> str:
    code = _official_code(value)
    prefixes = ("5", "6", "900") if exchange == "SH" else ("0", "1", "2", "3")
    if not code.startswith(prefixes):
        raise ValueError("两融证券代码与请求的交易所不符")
    return code


def margin_trading_backup(
    trade_date: str, exchange: str, code: Optional[str] = None
) -> pd.DataFrame:
    """一次只取一个交易所。未发布抛错；完整源中筛不到 code 才返回空表。"""
    trade_date = _official_date(trade_date)
    exchange = str(exchange).upper()
    if exchange not in ("SH", "SZ"):
        raise ValueError("exchange 必须为 SH 或 SZ；本函数不覆盖北交所两融")
    if code is not None:
        code = _official_margin_code(code, exchange)
    if exchange == "SH":
        url = "https://query.sse.com.cn/marketdata/tradedata/queryMargin.do"
        response = _official_get(
            url,
            {
                "isPagination": "true",
                "tabType": "mxtype",
                "detailsDate": trade_date.replace("-", ""),
                "pageHelp.pageSize": 5000,
                "pageHelp.pageNo": 1,
                "pageHelp.beginPage": 1,
                "pageHelp.cacheSize": 1,
                "pageHelp.endPage": 1,
            },
            "https://www.sse.com.cn/",
        )
        page = response.json().get("pageHelp") or {}
        data = page.get("data")
        if (
            not isinstance(data, list)
            or not data
            or len(data) != _official_total(page.get("total"))
        ):
            raise RuntimeError("上交所该日数据未发布或分页不完整")
        fields = {
            "rzye": "margin_balance",
            "rzmre": "margin_buy",
            "rqylje": "short_balance",
            "rqyl": "short_volume",
            "rqmcl": "short_sell_volume",
        }
        rows = []
        for rec in data:
            if _official_date(rec.get("opDate")) != trade_date:
                raise RuntimeError("上交所两融数据日期不符")
            if not set(fields).issubset(rec):
                raise RuntimeError("上交所两融字段发生变化")
            rows.append(
                {
                    "date": trade_date,
                    "code": _official_margin_code(rec["stockCode"], exchange),
                    "name": rec.get("securityAbbr"),
                    "exchange": exchange,
                    **{
                        dest: _official_number(rec[src], required=(src != "rqylje"))
                        for src, dest in fields.items()
                    },
                }
            )
    else:
        url = "https://www.szse.cn/api/report/ShowReport"
        response = _official_get(
            url,
            {"SHOWTYPE": "xlsx", "CATALOGID": "1837_xxpl", "TABKEY": "tab2", "txtDate": trade_date},
            "https://www.szse.cn/",
        )
        data = _official_excel(response)
        fields = {
            "融资余额(元)": "margin_balance",
            "融资买入额(元)": "margin_buy",
            "融券余额(元)": "short_balance",
            "融券余量(股/份)": "short_volume",
            "融券卖出量(股/份)": "short_sell_volume",
        }
        _official_columns(data, ["证券代码", "证券简称", *fields])
        rows = [
            {
                "date": trade_date,
                "code": _official_margin_code(str(rec["证券代码"]).zfill(6), exchange),
                "name": rec["证券简称"],
                "exchange": exchange,
                **{dest: _official_number(rec[src], required=True) for src, dest in fields.items()},
            }
            for rec in data.to_dict("records")
        ]
    frame = _official_frame(
        rows, ["date", "code"], "sse" if exchange == "SH" else "szse", response.url
    )
    return frame if code is None else frame.loc[frame.code == code].reset_index(drop=True)


def bse_quote_backup(trade_date: str, code: Optional[str] = None) -> pd.DataFrame:
    """北交所当前全板/单票快照；拒绝用当前数据回填其他交易日。"""
    trade_date = _official_date(trade_date)
    if code is not None:
        code = _official_code(code)
        if not code.startswith(("4", "8", "92")):
            raise ValueError("请输入北交所代码（4/8/92 开头）")
    page_url = "https://www.bse.cn/nq/quotation.html"
    url = "https://www.bse.cn/nqhqController/nqhq_en.do"
    raw_rows = []
    total = None
    with requests.Session() as session:
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0",
                "Referer": page_url,
                "Accept": "application/json, text/javascript, */*; q=0.01",
            }
        )
        # 官网有时设置匿名 Cookie 后 302 回自己；不跟随重定向，避免循环。
        session.get(page_url, timeout=(10, 40), allow_redirects=False).raise_for_status()
        for page_number in range(100):
            form = {
                "page": page_number,
                "type_en": '["B"]',
                "sortfield": "hqzqdm",
                "sorttype": "asc",
                "xxfcbj_en": "[2]",
                "zqdm": code or "",
            }
            response = session.post(url, data=form, timeout=(10, 40), allow_redirects=False)
            if 300 <= response.status_code < 400:
                session.get(page_url, timeout=(10, 40), allow_redirects=False).raise_for_status()
                response = session.post(url, data=form, timeout=(10, 40), allow_redirects=False)
            response.raise_for_status()
            if response.status_code != 200:
                raise RuntimeError("北交所匿名会话尚未建立")
            payload = response.text.strip()
            match = re.fullmatch(r"[A-Za-z_$][\w$]*\((.*)\);?", payload, re.S)
            data = json.loads(match.group(1) if match else payload)
            if (
                not isinstance(data, list)
                or len(data) != 1
                or not isinstance(data[0].get("content"), list)
            ):
                raise RuntimeError("北交所行情响应结构异常")
            current_total = _official_total(data[0].get("totalElements"))
            if total is not None and total != current_total:
                raise RuntimeError("分页期间北交所记录总数变化，请重试")
            total = current_total
            batch = data[0]["content"]
            if total < 0 or not batch:
                raise RuntimeError("北交所未返回目标行情或分页提前结束")
            raw_rows.extend(batch)
            if len(raw_rows) >= total:
                break
            time.sleep(0.2)
        if len(raw_rows) != total:
            raise RuntimeError("北交所分页不完整，不能标记全板成功")
    fields = {
        "hqjrkp": "open",
        "hqzgcj": "high",
        "hqzdcj": "low",
        "hqzjcj": "close",
        "hqzrsp": "previous_close",
        "hqcjsl": "volume",
        "hqcjje": "amount",
    }
    rows = []
    for rec in raw_rows:
        if _official_date(rec.get("hqjsrq")) != trade_date:
            raise RuntimeError("北交所快照不是请求的交易日；本接口不提供历史回填")
        ticker = _official_code(rec.get("hqzqdm"))
        if not ticker.startswith(("4", "8", "92")) or (code is not None and ticker != code):
            raise RuntimeError("北交所返回了请求范围之外的标的")
        row = {
            "date": trade_date,
            "code": ticker,
            "name": rec.get("hqzqjc"),
            "exchange": "BJ",
            "quote_time": str(rec.get("hqgxsj", "")),
            "pe_source": _official_number(rec.get("hqsyl1")),
            **{dest: _official_number(rec.get(src), required=True) for src, dest in fields.items()},
        }
        for level in range(1, 6):
            for src, dest in (
                ("hqbjw", "bid_price"),
                ("hqbsl", "bid_volume"),
                ("hqsjw", "ask_price"),
                ("hqssl", "ask_volume"),
            ):
                row[f"{dest}_{level}"] = _official_number(rec.get(f"{src}{level}"), required=True)
        rows.append(row)
    return _official_frame(rows, ["date", "code"], "bse", url)


# ── 项目封装（V17.2.11）：降级源入口，供 get_margin_trading / get_em_quote_full* 调用 ──


def _recent_trade_dates(max_days: int = 14) -> list[str]:
    """从今天往前取最近 max_days 个自然日中的工作日（周一~周五），返回 ISO 日期列表。"""
    out: list[str] = []
    today = datetime.now().date()
    for i in range(max_days):
        d = today - timedelta(days=i)
        if d.weekday() < 5:  # 0=Mon ... 4=Fri
            out.append(d.isoformat())
        if len(out) >= 8:
            break
    return out


def get_margin_trading_backup(code: str) -> list[dict[str, Any]]:
    """V17.2.11: 沪深官方两融降级源（东财 datacenter 封禁/空结果时调用）。

    自动按代码判定交易所(SH/SZ)，遍历最近交易日取最近已发布快照；
    返回与 get_margin_trading 完全一致的 dict 形状
    [{date, rzye, rzmre, rzche, rqye, rqmcl, rqchl, rzrqye}, ...]。
    全部失败返回 []（不影响主流程）。
    """
    if not code or len(str(code)) != 6:
        return []
    exchange = "SH" if em_exchange_prefix(code, upper=True) == "SH" else "SZ"
    last_err = None
    for d in _recent_trade_dates():
        try:
            frame = margin_trading_backup(d, exchange, code)
        except Exception as _e:  # 该日未发布/结构变化/网络 → 试前一日
            last_err = _e
            continue
        if frame is None or len(frame) == 0:
            continue
        out = []
        for rec in frame.to_dict("records"):
            mb = float(rec.get("margin_balance") or 0.0)
            sb = float(rec.get("short_balance") or 0.0)
            out.append(
                {
                    "date": str(rec.get("date", ""))[:10],
                    "rzye": mb,
                    "rzmre": float(rec.get("margin_buy") or 0.0),
                    "rzche": 0.0,
                    "rqye": sb,
                    "rqmcl": float(rec.get("short_sell_volume") or 0.0),
                    "rqchl": 0.0,
                    "rzrqye": mb + sb,
                }
            )
        if out:
            return out
    if last_err is not None:
        _debug_log(f"sc_datasource margin_trading_backup({code}): 全部日期失败，末错 {last_err!r}")
    return []


def get_bse_quote_backup(code: str) -> dict[str, Any]:
    """V17.2.11: 北交所官方行情降级源（东财 push2 封禁/空结果时调用）。

    遍历最近交易日取北交所官方快照，归一化为与 get_em_quote_full 一致的字段形状
    （price/open/high/low/last_close/change_pct/change_amt/volume_hand/amount_wan/name/
     pe_source/data_date/quote_time + bid/ask 五档）。
    全部失败返回 {}。
    """
    if not code or not str(code).startswith(("4", "8", "92")):
        return {}
    last_err = None
    for d in _recent_trade_dates():
        try:
            frame = bse_quote_backup(d, code)
        except Exception as _e:
            last_err = _e
            continue
        if frame is None or len(frame) == 0:
            continue
        rec = frame.to_dict("records")[0]
        close = float(rec.get("close") or 0.0)
        prev = float(rec.get("previous_close") or 0.0)
        change_pct = ((close - prev) / prev * 100.0) if prev else 0.0
        out = {
            "price": close,
            "open": float(rec.get("open") or 0.0),
            "high": float(rec.get("high") or 0.0),
            "low": float(rec.get("low") or 0.0),
            "last_close": prev,
            "change_pct": change_pct,
            "change_amt": close - prev,
            "volume_hand": float(rec.get("volume") or 0.0) / 100.0,  # 北交所 100股/手
            "amount_wan": float(rec.get("amount") or 0.0) / 1e4,
            "name": rec.get("name"),
            "pe_source": rec.get("pe_source"),
            "data_date": str(rec.get("date", ""))[:10],
            "quote_time": rec.get("quote_time"),
            "source": "bse_official_backup",
        }
        for level in range(1, 6):
            out[f"bid_price_{level}"] = rec.get(f"bid_price_{level}")
            out[f"bid_volume_{level}"] = rec.get(f"bid_volume_{level}")
            out[f"ask_price_{level}"] = rec.get(f"ask_price_{level}")
            out[f"ask_volume_{level}"] = rec.get(f"ask_volume_{level}")
        return out
    if last_err is not None:
        _debug_log(f"sc_datasource bse_quote_backup({code}): 全部日期失败，末错 {last_err!r}")
    return {}


__all__ = [
    'BytesIO',
    '_debug_log',
    '_official_code',
    '_official_columns',
    '_official_date',
    '_official_excel',
    '_official_frame',
    '_official_get',
    '_official_margin_code',
    '_official_number',
    '_official_total',
    '_recent_trade_dates',
    'bse_quote_backup',
    'code',
    'datetime',
    'em_exchange_prefix',
    'get_bse_quote_backup',
    'get_margin_trading_backup',
    'json',
    'margin_trading_backup',
    'math',
    'pd',
    're',
    'requests',
    'time',
    'timedelta',
    'timezone',
]
