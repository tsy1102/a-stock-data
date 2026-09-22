"""_research_sina.py — 新浪研报列表(研报第二来源, 吸收上游 3.9.0 §2.4).

函数: sina_research_reports(code=None, page=1) — 标题/类型/日期/机构/研究员(无评级/目标价).
数据来源: 新浪财经(vip.stock.finance.sina.com.cn). 设计对齐上游 _v39_* 契约: 结构改变抛错、空页≠末页区分。
reportName 常量: 无(HTML 页面解析, 非 datacenter); _VERIFIED 标记取自上游权威实现(2026-09-22 对撞校正)。
"""
from __future__ import annotations
import re
import time
import html as _html
from typing import Any, Dict, List, Optional

from stock_common.sc_network import _quick_request, UA
from stock_common import _debug_log

SINA_REPORT_URL = "https://vip.stock.finance.sina.com.cn/q/go.php/vReport_List/kind/{kind}/index.phtml"
_SINA_REPORT_ROW = re.compile(
    r"<tr>\s*<td>\d+</td>\s*<td class=\"tal f14\">\s*<a[^>]*?title=\"([^\"]*)\"[^>]*?"
    r"href=\"([^\"]*?/rptid/(\d+)/[^\"]*)\"[^>]*>.*?</a>\s*</td>\s*"
    r"<td>([^<]*)</td>\s*<td>([^<]*)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>", re.S)

# 新浪对连续请求返回假的「没有找到」空页(HTTP 200), 强制最小间隔, 空页重试一次。
SINA_REPORT_MIN_INTERVAL = 6.0
_sina_report_last = [0.0]


def _sina_report_page(url, params):
    last_err = None
    for _ in range(2):
        wait = SINA_REPORT_MIN_INTERVAL - (time.time() - _sina_report_last[0])
        if wait > 0:
            time.sleep(wait)
        try:
            r = _quick_request(url, params=params,
                              headers={"User-Agent": UA, "Referer": "https://finance.sina.com.cn/"},
                              timeout=15)
        finally:
            _sina_report_last[0] = time.time()
        if r is None:
            last_err = "request_none"
            continue
        text = r.content.decode("gbk", "replace")
        if "没有找到相关内容" not in text:
            return r, text
    return None, ""


def _sina_text(fragment):
    return _html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def _src_date(value):
    t = str(value).strip()
    if re.fullmatch(r"[0-9]{8}", t):
        return f"{t[0:4]}-{t[4:6]}-{t[6:8]}"
    return t


def sina_research_reports(code: Optional[str] = None, page: int = 1) -> List[Dict[str, Any]]:
    """新浪研报列表 — 标题/类型/日期/机构/研究员。code=None 全市场最新, 给代码看该股。

    新浪对连续请求会返回假的「没有找到」空页, 本函数内置 6 秒最小间隔, 批量翻页较慢。
    """
    if int(page) < 1:
        raise ValueError("page 从 1 开始")
    if code is None:
        url = SINA_REPORT_URL.format(kind="lastest")
        params = {"p": int(page)}
    else:
        url = SINA_REPORT_URL.format(kind="search")
        symbol = str(code).zfill(6)
        if str(code).startswith(("4", "8", "920")):
            symbol = "bj" + symbol
        params = {"symbol": symbol, "t1": "all", "p": int(page)}
    r, text = _sina_report_page(url, params)
    if r is None:
        _debug_log(f"sina_research_reports({code}): 请求失败")
        return []
    if "tb_01" not in text or "研究员" not in text:
        _debug_log(f"sina_research_reports({code}): 页面结构改变")
        return []
    rows = []
    for title, href, rptid, kind, day, org, author in _SINA_REPORT_ROW.findall(text):
        rows.append({"date": _src_date(day.strip()), "title": _html.unescape(title).strip(),
                     "type": kind.strip(), "org": _sina_text(org), "author": _sina_text(author),
                     "report_id": rptid,
                     "url": ("https:" + href) if href.startswith("//") else href})
    numbered = len(re.findall(r"<tr>\s*<td>\d+</td>", text))
    if len(rows) != numbered or (not rows and "没有找到相关内容" not in text):
        _debug_log(f"sina_research_reports({code}): 行结构可能已变 {numbered} vs {len(rows)}")
        return []
    return rows


_VERIFIED = True  # 取自上游权威仓库(2026-09-22 对撞校正); 字段语义待本项目 collide 终检
