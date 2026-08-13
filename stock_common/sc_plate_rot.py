"""sc_plate_rot.py — 板块轮动矩阵适配器（V16.3 O35，字典 §12.18）。

数据源：duanxianxia.com（短线侠）——无 API key，仅 Referer 注入。
返回：HTML 片段嵌在 JSON 的 html 字段（前端 innerHTML 渲染）——正则解析。

接口：/api/getPlateRotatData（from=ths/kaipan, days）
- ths 源：数值=板块涨幅%（当日 + N 天矩阵）
- kaipan 源：数值=强度分（多因子）
板块代码体系：88x=同花顺概念；80x/803x=开盘啦（与 KPL §12.17 同体系）

⚠️ 私有接口，字段可能变更；HTML 结构变化时解析失效需重试。
"""
from __future__ import annotations

import json
import logging
import re
import threading
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

# V16.3.3: 板块轮动缓存（字典 12.15.5——mak D 段高频，矩阵数据收盘后不变）
try:
    from core.stock_cache import cached, TTL

    _HAS_CACHE = True
except ImportError:  # pragma: no cover
    _HAS_CACHE = False

_logger = logging.getLogger("sc_plate_rot")

_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
       "(KHTML, like Gecko) Version/17.0 Safari/605.1.15")
_BASE = "https://duanxianxia.com"
_QUERY_INTERVAL = 0.6

_last_request = 0.0
# V16.4.1: 节流时间戳加锁(多线程并发下原间隔被打穿)
_throttle_lock = threading.Lock()


def _throttle():
    global _last_request
    with _throttle_lock:
        now = time.time()
        wait = _QUERY_INTERVAL - (now - _last_request)
        if wait > 0:
            time.sleep(wait)
        _last_request = time.time()


def _post(path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    _throttle()
    body = urllib.parse.urlencode(params, doseq=True).encode("utf-8")
    req = urllib.request.Request(_BASE + path, data=body, headers={
        "User-Agent": _UA,
        "Referer": f"{_BASE}/web/main",
        "Origin": _BASE,
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8", errors="ignore"))
    except Exception as e:
        _logger.warning(f"plate_rot {path}: {e}")
        return {"_err": str(e)[:120]}


def _parse_dates(html: str) -> List[str]:
    """表头日期（newest→oldest）：line-height:160%;'>YYYY-MM-DD"""
    return re.findall(r"line-height:160%;'>(\d{4}-\d{2}-\d{2})", html)


@cached(category="plate_rotation", ttl_seconds=TTL["plate_rotation"], trading_day=True)
def get_plate_rotation_matrix(
    source: str = "kaipan", days: int = 20, top_n: int = 30
) -> Dict[str, Any]:
    """板块轮动矩阵（N 天 × TopN 板块）。

    Args:
        source: 'ths'（涨幅%）/ 'kaipan'（强度分）
        days: 回溯天数（10/20/30/50）
        top_n: 返回前 N 名板块

    Returns:
        {
          'dates': ['2026-08-07', '2026-08-06', ...],   # newest first
          'source': 'kaipan',
          'plates': [{'rank': 1, 'cells': [{'date','code','name','value','color'}...]}...]
        }
    """
    d = _post("/api/getPlateRotatData", {"from": source, "days": days})
    if "_err" in d:
        return {"dates": [], "source": source, "plates": []}
    html = d.get("html", "")
    dates = _parse_dates(html)
    cell_re = re.compile(
        r"<td class='plate plate\d+'\s*code='(\d+)'\s*name='([^']+)'[^>]*>"
        r".*?<span style='color:(red|green);'>([\d.\-]+%?)</span>",
        re.S,
    )
    out = []
    rows = re.split(r"<span class='rank'[^>]*>(\d+)</span>", html)
    for i in range(1, len(rows), 2):
        if len(out) >= top_n:
            break
        rank = int(rows[i])
        rest = rows[i + 1] if i + 1 < len(rows) else ""
        cells = []
        for di, m in enumerate(cell_re.finditer(rest)):
            if di >= len(dates):
                break
            code, name, color, value = m.groups()
            cells.append({"date": dates[di], "code": code, "name": name,
                          "value": value, "color": color})
        if cells:
            out.append({"rank": rank, "cells": cells})
    return {"dates": dates, "source": source, "plates": out}


def get_plate_rotation_top(source: str = "kaipan", days: int = 20,
                           n: int = 10) -> List[Dict[str, Any]]:
    """今日 Top N 板块（轻量——只取矩阵第一列 = 当日）。"""
    m = get_plate_rotation_matrix(source=source, days=days, top_n=n)
    out = []
    for p in m.get("plates", []):
        if p["cells"]:
            c = p["cells"][0]
            out.append({"rank": p["rank"], "code": c["code"], "name": c["name"],
                        "value": c["value"], "color": c["color"]})
    return out


if __name__ == "__main__":
    top = get_plate_rotation_top("kaipan", 20, 5)
    print("今日 Top5（开盘啦强度分）:")
    for t in top:
        print(f"  #{t['rank']} {t['code']} {t['name']} {t['value']} {t['color']}")
    m = get_plate_rotation_matrix("ths", 10, 3)
    print(f"矩阵: {len(m['dates'])} 天 × {len(m['plates'])} 板块")
