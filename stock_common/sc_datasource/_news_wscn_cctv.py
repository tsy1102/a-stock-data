"""_news_wscn_cctv.py — 新闻层(吸收上游 3.9.0 §5.4/§5.5).

函数: cctv_news(date, with_content=False) — 央视《新闻联播》当日条目(标题/链接/正文).
数据来源: 央视网(tv.cctv.com). 注: 华尔街见闻宏观日历已落在 _macro.macro_calendar(§5.4),
本模块聚焦央视新闻联播文本(政策信号研究用, 做短视频文案勿引用)。
reportName 常量: 无(HTML 页面解析); _VERIFIED 标记取自上游权威实现(2026-09-22 对撞校正)。
"""

from __future__ import annotations
import html as _html
import re
import time
from typing import Any, Dict, List, Optional

from stock_common.sc_network import _quick_request, UA
from stock_common import _debug_log

CCTV_DAY_URL = "https://tv.cctv.com/lm/xwlb/day/{ymd}.shtml"


def _v39_date(value: str) -> str:
    t = str(value).strip()
    if re.fullmatch(r"[0-9]{8}", t):
        return f"{t[0:4]}-{t[4:6]}-{t[6:8]}"
    return t


def _cctv_body(url: str) -> str | None:
    r = _quick_request(url, headers={"User-Agent": UA}, timeout=15)
    if r is None:
        return None
    text = r.content.decode("utf-8", "replace")
    if len(text) < 1000 and "error.html" in text:
        return None
    match = re.search(r'<div class="content_area"[^>]*>(.*?)</div>', text, re.S) or re.search(
        r'<div class="cnt_bd"[^>]*>(.*?)</div>', text, re.S
    )
    if not match:
        _debug_log(f"cctv body 结构改变: {url}")
        return None
    body = re.sub(r"</p>|<br\s*/?>", "\n", match.group(1))
    body = _html.unescape(re.sub(r"<[^>]+>", "", body))
    body = "\n".join(line.strip() for line in body.splitlines() if line.strip())
    return re.sub(r"^央视网消息\s*[（(]新闻联播[)）]\s*[：:]", "", body)


def cctv_news(date: str, with_content: bool = False) -> List[Dict[str, Any]]:
    """央视《新闻联播》当日条目 — 标题 + 文字稿。with_content=True 逐条打开详情页取正文(~15 次请求)。"""
    ymd = _v39_date(date).replace("-", "")
    url = CCTV_DAY_URL.format(ymd=ymd)
    r = _quick_request(url, headers={"User-Agent": UA}, timeout=15)
    if r is None:
        _debug_log(f"cctv_news({date}): 请求失败")
        return []
    if getattr(r, "status_code", None) == 404:
        _debug_log(f"cctv_news({date}): 无新闻联播页面(日期过早或未发布)")
        return []
    text = r.content.decode("utf-8", "replace")
    rows: list[dict[str, Any]] = []
    for chunk in text.split("<li")[1:]:
        link = re.search(r'href="([^"]*/VIDE[^"]+)"', chunk)
        if not link:
            continue
        href = link.group(1)
        title_match = (
            re.search(r'title="([^"]+)"', chunk)
            or re.search(r'class="title">(.*?)</div>', chunk, re.S)
            or re.search(r"<a[^>]*>(.*?)</a>", chunk, re.S)
        )
        title = (
            _html.unescape(re.sub(r"<[^>]+>", "", title_match.group(1))).strip()
            if title_match
            else ""
        )
        if not title or re.match(r"《新闻联播》\s*\d{8}|新闻联播完整版", title):
            continue
        title = re.sub(r"^\[视频\]", "", title).strip()
        rows.append(
            {
                "date": _v39_date(ymd),
                "title": title,
                "url": ("https:" + href) if href.startswith("//") else href,
            }
        )
    if not rows:
        _debug_log(f"cctv_news({ymd}): 未解析出条目, 结构可能已变")
        return []
    if with_content:
        for row in rows:
            row["content"] = _cctv_body(row["url"])
            time.sleep(0.2)
    return rows


_VERIFIED = True  # 取自上游权威仓库(2026-09-22 对撞校正)
