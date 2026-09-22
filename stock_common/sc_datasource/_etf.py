"""_etf.py — ETF 份额(万份, 吸收上游 3.9.0 §4.7).

函数: etf_shares(date, exchange='SH') — 上交所按日归档 / 深交所当前快照; 单位万份。
数据来源: 上交所 query.sse.com.cn / 深交所 fund.szse.cn。两所类别字段口径不同, 不硬并一列。
reportName 常量: 无(REST JSON 接口); _VERIFIED 标记取自上游权威实现(2026-09-22 对撞校正)。
"""
from __future__ import annotations
import re
import time
from typing import Any, Dict, List, Optional

from stock_common.sc_network import _quick_request, UA
from stock_common import _debug_log

SSE_ETF_SHARES_URL = "https://query.sse.com.cn/commonQuery.do"
SZSE_FUND_LIST_URL = "https://fund.szse.cn/api/report/ShowReport/data"


def _v39_num(value):
    if value is None or value == "":
        return None
    t = str(value).replace(",", "").strip()
    if t in ("", "-", "--", "None", "null"):
        return None
    try:
        return float(t)
    except ValueError:
        return None


def _v39_date(value):
    t = str(value).strip()
    if re.fullmatch(r"[0-9]{8}", t):
        return f"{t[0:4]}-{t[4:6]}-{t[6:8]}"
    return t


def _etf_shares_sse(day):
    params = {"sqlId": "COMMON_SSE_ZQPZ_ETFZL_XXPL_ETFGM_SEARCH_L", "STAT_DATE": day,
              "isPagination": "true", "pageHelp.pageSize": 10000, "pageHelp.pageNo": 1,
              "pageHelp.beginPage": 1, "pageHelp.cacheSize": 1, "pageHelp.endPage": 1}
    r = _quick_request(SSE_ETF_SHARES_URL, params=params,
                       headers={"User-Agent": UA, "Referer": "https://www.sse.com.cn/"}, timeout=15)
    if r is None:
        raise RuntimeError("上交所 ETF 规模接口请求失败")
    try:
        payload = r.json()
    except Exception:
        raise RuntimeError("上交所 ETF 规模接口返回非 JSON")
    result = payload.get("result") if isinstance(payload, dict) else None
    page_help = payload.get("pageHelp") if isinstance(payload, dict) else None
    if not isinstance(result, list) or not all(isinstance(x, dict) for x in result) or not isinstance(page_help, dict):
        raise RuntimeError("上交所 ETF 规模接口返回结构改变")
    try:
        total = int(page_help.get("total"))
    except (TypeError, ValueError):
        raise RuntimeError("上交所 ETF 规模 total 异常")
    if len(result) != total:
        raise RuntimeError(f"上交所 ETF 规模返回 {len(result)} 条与 total={total} 不符")
    rows = []
    for rec in result:
        if rec.get("STAT_DATE") != day:
            raise RuntimeError("上交所返回了其他日期的数据")
        rows.append({"date": day, "exchange": "SH", "code": rec.get("SEC_CODE"),
                     "name": rec.get("SEC_NAME"), "etf_type": rec.get("ETF_TYPE"),
                     "shares_10k": _v39_num(rec.get("TOT_VOL"))})
    return rows


def _etf_shares_szse(day):
    rows, page, first = [], 1, None
    while first is None or page <= first[1]:
        r = _quick_request(SZSE_FUND_LIST_URL, params={"SHOWTYPE": "JSON", "CATALOGID": "1000_lf",
                                     "TABKEY": "tab1", "selectJjlb": "ETF", "PAGENO": page},
                           headers={"User-Agent": UA, "Referer": "https://fund.szse.cn/"}, timeout=15)
        if r is None:
            raise RuntimeError("深交所 ETF 列表请求失败")
        try:
            payload = r.json()
        except Exception:
            raise RuntimeError("深交所 ETF 列表返回非 JSON")
        table = payload[0] if isinstance(payload, list) and payload else None
        meta = table.get("metadata") if isinstance(table, dict) else None
        data = table.get("data") if isinstance(table, dict) else None
        if not isinstance(meta, dict) or not isinstance(data, list):
            raise RuntimeError(f"深交所基金列表第 {page} 页结构变了")
        try:
            snap = (_v39_date(meta.get("subname")), int(meta.get("pagecount")), int(meta.get("recordcount")))
        except (TypeError, ValueError):
            raise RuntimeError("深交所基金列表分页信息异常")
        if snap[1] < 1:
            raise RuntimeError(f"深交所基金列表 pagecount={snap[1]} 异常")
        if first is None:
            if snap[0] != day:
                raise ValueError(f"深交所当前规模快照日期是 {snap[0]}，非 {day}（深市只能取最新一天）")
            first = snap
        elif snap != first:
            raise RuntimeError(f"深交所 ETF 列表翻页时快照从 {first} 变成 {snap}")
        if not data:
            raise RuntimeError(f"深交所 ETF 列表第 {page}/{first[1]} 页为空")
        for rec in data:
            try:
                code = re.search(r"<u>(\d{6})</u>", rec["sys_key"])
                name = re.search(r"<u>(.*?)</u>", rec["jjjcurl"])
                shares = re.search(r">([\d,\.]+)</a>", rec["dqgm"])
            except (KeyError, TypeError):
                raise RuntimeError("深交所基金列表字段缺失")
            if not (code and name and shares):
                raise RuntimeError("深交所基金列表字段格式改变")
            rows.append({"date": day, "exchange": "SZ", "code": code.group(1),
                         "name": name.group(1), "fund_category": rec.get("tzlb"),
                         "shares_10k": _v39_num(shares.group(1)),
                         "manager": rec.get("glrmc"), "listing_date": rec.get("ssrq")})
        page += 1
        time.sleep(0.3)
    if len(rows) != first[2]:
        raise RuntimeError(f"深交所 ETF 列表取到 {len(rows)} 条与总数 {first[2]} 不符")
    return rows


def etf_shares(date: str, exchange: str = "SH") -> List[Dict[str, Any]]:
    """ETF 份额(万份) — 上交所按日归档, 深交所当前快照。date: 'YYYY-MM-DD'。exchange: 'SH'/'SZ'。"""
    day = _v39_date(date)
    exchange = str(exchange).upper()
    if exchange == "SH":
        return _etf_shares_sse(day)
    if exchange == "SZ":
        return _etf_shares_szse(day)
    raise ValueError("exchange 只能是 'SH' 或 'SZ'")


_VERIFIED = True  # 取自上游权威仓库(2026-09-22 对撞校正)
