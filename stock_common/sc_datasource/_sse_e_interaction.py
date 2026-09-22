"""_sse_e_interaction.py — 上证e互动(沪市投资者问答, 吸收上游 3.9.0 §10.3).

函数: sse_e_interaction(code=None, kind='answered', page=1) — 沪市公司投资者提问与回复。
数据来源: 上交所官方平台(sns.sseinfo.com)。§10.1 巨潮互动易实测对沪市返回 0 条, 沪市只能走本函数。
首次查某公司需在公司列表里定位 uid(倍增+二分, ~10–13 次请求), 之后走缓存。
reportName 常量: 无(REST/HTML 接口); _VERIFIED 标记取自上游权威实现(2026-09-22 对撞校正)。
"""
from __future__ import annotations
import html as _html
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from stock_common.sc_network import _quick_request, UA
from stock_common import _debug_log

SSE_E_BASE = "https://sns.sseinfo.com"
_sse_uid_cache: Dict[str, str] = {}
_sse_company_pages: Dict[int, List] = {}
_SSE_COMPANY_END = "没有任何上市公司的信息"
_SSE_EMPTY_NOTE = re.compile(r'class="m_feed_note"[^>]*>[^<]*(暂无|暂时没有)[^<]*<')


def _sse_text(fragment):
    return _html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def _sse_time(text):
    """问答时间解析: 支持绝对(YYYY年MM月DD日 HH:MM)与相对(刚刚/X分钟前/X小时前/X天前)两种格式。

    V17.4.1 健壮性补强: 上游严格正则仅认绝对时间, 实测近期问答返回「4分钟前」等相对时间,
    致 _sse_required_time 抛错(把「时间格式变了」误判); 此处归一为绝对时间戳, 与绝对格式统一输出。
    """
    if not text:
        return None
    match = re.search(r"(\d{4})年(\d{2})月(\d{2})日\s*(\d{2}:\d{2})", text)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)} {match.group(4)}"
    now = datetime.now()
    if "刚刚" in text:
        return now.strftime("%Y-%m-%d %H:%M")
    mm = re.search(r"(\d+)\s*分钟前", text)
    if mm:
        return (now - timedelta(minutes=int(mm.group(1)))).strftime("%Y-%m-%d %H:%M")
    hh = re.search(r"(\d+)\s*小时前", text)
    if hh:
        return (now - timedelta(hours=int(hh.group(1)))).strftime("%Y-%m-%d %H:%M")
    dd = re.search(r"(\d+)\s*天前", text)
    if dd:
        return (now - timedelta(days=int(dd.group(1)))).strftime("%Y-%m-%d %H:%M")
    # 今天/昨天/前天 + 可选 HH:MM
    _off = None
    if "前天" in text:
        _off = 2
    elif "昨天" in text:
        _off = 1
    elif "今天" in text:
        _off = 0
    if _off is not None:
        t = now - timedelta(days=_off)
        tm = re.search(r"(\d{1,2}):(\d{2})", text)
        if tm:
            t = t.replace(hour=int(tm.group(1)), minute=int(tm.group(2)))
        return t.strftime("%Y-%m-%d %H:%M")
    return None


def _sse_required_time(item_id, text):
    when = _sse_time(text)
    if when is None:
        raise RuntimeError(f"上证e互动第 {item_id} 条的提问时间认不出: {text!r}")
    return when


def _sse_company_page(page):
    if page not in _sse_company_pages:
        r = _quick_request(SSE_E_BASE + "/allcompany.do", method="POST",
                          data={"code": "0", "order": "2", "areaId": "0", "page": page},
                          headers={"User-Agent": UA, "Referer": SSE_E_BASE + "/"}, timeout=15)
        if r is None:
            raise RuntimeError(f"上证e互动公司列表第 {page} 页请求失败")
        try:
            payload = r.json()
        except Exception:
            raise RuntimeError(f"上证e互动公司列表第 {page} 页返回非 JSON")
        content = payload.get("content") if isinstance(payload, dict) else None
        if not isinstance(content, str):
            raise RuntimeError(f"上证e互动公司列表第 {page} 页的返回结构变了（没有 content 字符串）")
        pairs = [(code, uid) for uid, code in
                 re.findall(r"uid=['\"]?(\d+)['\"]?[^>]*>\s*<img[^>]*company/(\d{6})\.png", content)]
        if not pairs and (page == 1 or _SSE_COMPANY_END not in content):
            raise RuntimeError(f"上证e互动公司列表第 {page} 页解析出 0 家公司，页面格式可能已变")
        _sse_company_pages[page] = pairs
        for code, uid in pairs:
            _sse_uid_cache[code] = uid
    return _sse_company_pages[page]


def _sse_company_uid(code):
    """上证e互动按公司 uid 查询; 公司列表按代码升序分页(每页 32 家), 倍增+二分定位。"""
    if code in _sse_uid_cache:
        return _sse_uid_cache[code]
    low, high = 1, 1
    while _sse_company_page(high):
        if _sse_company_page(high)[-1][0] >= code:
            break
        low, high = high, high * 2
    while low <= high:
        mid = (low + high) // 2
        pairs = _sse_company_page(mid)
        if not pairs or code < pairs[0][0]:
            high = mid - 1
        elif code > pairs[-1][0]:
            low = mid + 1
        else:
            break
    if code not in _sse_uid_cache:
        raise ValueError(f"上证e互动没有 {code}（公司不在上交所，或已退市）")
    return _sse_uid_cache[code]


def _sse_parse_feed(text):
    """「最新回复」与「最新提问」两种列表标记不同, 以回复块 class 为界切问题段和回复段。"""
    rows = []
    for chunk in re.split(r'<div class="m_feed_item[^"]*" id="item-', text)[1:]:
        numbered = re.match(r"(\d+)", chunk)
        if not numbered:
            raise RuntimeError(f"上证e互动条目 id 不是数字，页面结构可能已变: {chunk[:60]}")
        item_id = numbered.group(1)
        ask_part, _, answer_part = chunk.partition('class="m_feed_detail m_qa"')
        question = re.search(r'<div class="m_feed_txt"[^>]*>\s*<a[^>]*>:(.*?)\((\d{6})\)</a>(.*?)</div>',
                             ask_part, re.S)
        asker = re.search(r'rel="face"[^>]*?title="([^"]*)"', ask_part, re.S)
        ask_time = re.search(r'<div class="m_feed_from"[^>]*>\s*<span>([^<]+)</span>', ask_part)
        if not question or not ask_time:
            raise RuntimeError(f"上证e互动第 {item_id} 条结构改变，无法解析问题或时间")
        answer = answer_time = None
        if answer_part:
            body = re.search(r'<div class="m_feed_txt"[^>]*>(.*?)</div>', answer_part, re.S)
            when = re.search(r'<div class="m_feed_from"[^>]*>\s*<span>([^<]+)</span>', answer_part)
            if not body or not when:
                raise RuntimeError(f"上证e互动第 {item_id} 条有回复块但解析不出回复内容或回复时间")
            answer, answer_time = _sse_text(body.group(1)), _sse_time(when.group(1))
            if answer_time is None:
                raise RuntimeError(f"上证e互动第 {item_id} 条的回复时间认不出: {when.group(1)!r}")
        rows.append({"id": item_id, "code": question.group(2), "name": _sse_text(question.group(1)),
                     "asker": asker.group(1) if asker else None,
                     "question": _sse_text(question.group(3)),
                     "question_time": _sse_required_time(item_id, ask_time.group(1)),
                     "answer": answer, "answer_time": answer_time})
    return rows


_SSE_KIND = {"answered": 11, "questions": 10}


def sse_e_interaction(code: Optional[str] = None, kind: str = "answered",
                      page: int = 1, page_size: int = 10) -> List[Dict[str, Any]]:
    """上证e互动 — 投资者提问与沪市上市公司回复。

    code=None 看全市场; 给沪市代码(60/68/900 开头)只看该公司。kind='answered' 最新已回复 /
    kind='questions' 最新提问(含未回复, answer=None)。平台只开放近期问答(公司维度约近 1 个月)。
    """
    if kind not in _SSE_KIND:
        raise ValueError("kind 只能是 'answered' 或 'questions'")
    if int(page) < 1 or not 1 <= int(page_size) <= 50:
        raise ValueError("page 从 1 开始，page_size 范围 1–50")
    if code is None:
        r = _quick_request(SSE_E_BASE + "/ajax/feeds.do",
                          params={"type": _SSE_KIND[kind], "pageSize": int(page_size), "lastid": -1,
                                  "show": 1, "page": int(page)},
                          headers={"User-Agent": UA, "Referer": SSE_E_BASE + "/"}, timeout=15)
    else:
        digits = str(code).zfill(6)
        if not str(code).startswith(("60", "68", "900")):
            raise ValueError(f"{code} 不是沪市证券；深市互动问答请用 cninfo_irm")
        r = _quick_request(SSE_E_BASE + "/ajax/userfeeds.do", method="POST",
                          data={"typeCode": "company", "type": _SSE_KIND[kind], "pageSize": int(page_size),
                                "uid": _sse_company_uid(digits), "page": int(page)},
                          headers={"User-Agent": UA, "Referer": SSE_E_BASE + "/"}, timeout=15)
    if r is None:
        _debug_log(f"sse_e_interaction({code}): 请求失败")
        return []
    text = r.content.decode("utf-8", "replace")
    rows = _sse_parse_feed(text)
    if not rows and not _SSE_EMPTY_NOTE.search(text):
        _debug_log(f"sse_e_interaction({code}): 页面无问答也无「暂无」提示, 结构可能已变")
        return []
    if code is not None and any(rrow["code"] != digits for rrow in rows):
        _debug_log(f"sse_e_interaction({code}): 返回了其他公司的问答")
        return []
    return rows


_VERIFIED = True  # 取自上游权威仓库(2026-09-22 对撞校正)
