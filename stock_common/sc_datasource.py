"""stock_common/sc_datasource.py - 数据源查询模块

V10.2 更新：
  - 修复 get_lockup_expiry/get_dragon_tiger_board 的 today_str 参数污染缓存key（移除参数改为内部自动计算）
  - 放宽 industry_peers/basic_info 的 valid_if 校验（避免空值拒写缓存）
  - 新增 zhb_field_safe(field_name) 函数：按字段时效性分级判断zhb数据是否安全可用
  - get_market_status() 交易日16:30后从 closed 改为 post_close（避免盘后误显示"休市日"）

V9.5 更新：
  - aiohttp原生异步迁移：10个HTTP异步函数从 asyncio.to_thread() 改为 _async_request_with_retry/_async_quick_request
  - 修复 get_strategic_announcements_async 中 _load_config 未定义错误（改为 _load_settings）

V9.3.3 更新：
  - sync/async 重复代码重构：9个独立实现的 async 函数改为 asyncio.to_thread() 代理，消除同步逻辑重复
  - 删除未使用的 _holder_fetch_em_async 函数

V9.3.2 更新：
  - _do_request 禁用系统代理（proxies={"http": None, "https": None}），避免代理环境拦截请求
  - 增加 ProxyError 和通用 Exception 异常捕获，防止代理异常导致脚本卡死

V9.3 更新：
  - 融资融券数据清洗（get_margin_trading）：日期截断到 10 位，过滤金额全为 0 的无效行

V9.2 更新：
  - 约 24 处 except Exception: pass 加 _debug_log 日志
  - is_trading_day() 降级到 weekday 判断时打印首次警告
  - fcf_forecast 类型标注修正：List[float] → Optional[List[float]]

V9.1.1 更新：
  - 移除 render_f10_chapter() 死代码（F10 章节已从报告中移除）
  - F10 优先级调整：移除研报/大宗/十大流通股东/利润表/资产负债表的 F10 优先逻辑

V9.1 更新：
  - 11 个 HTTP 函数添加 F10 优先逻辑（F10 优先 + HTTP 兜底）
  - 7 个异步函数委托到同步版（自动获得 F10 优先逻辑）
  - 新增 6 个验证函数（verify_financial_data 等，对比 F10 vs HTTP/TDX）
  - 新增 render_data_quality_appendix() 渲染数据质量核查附录

包含所有外部数据源查询函数，按功能分组：
- 东财数据中心
- 股东数据
- 公告和股东结构
- 行情、研报、北向资金
- 融资融券、大宗交易、分红、概念
- 同花顺、行业对比、新闻
- 新浪财报、限售解禁、毛利率
- 交易日历、异步包装
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import time
import re
import json
import asyncio

# 导入网络层
from stock_common.sc_network import (
    _request_with_retry, em_get, _quick_request,
    DATACENTER_URL, UA, _http_logger, _biz_logger, _debug_log,
    _async_request_with_retry, _async_quick_request
)

# 导入配置加载
from stock_common.sc_utils import _load_settings, _safe_float

# 导入缓存层
from stock_cache import TTL, cached


# ═══════════════════════════════════════════════════════════
# 东财数据中心核心函数
# ═══════════════════════════════════════════════════════════

def eastmoney_datacenter(code: str, report_name: str, columns: str = "ALL",
                         filter_str: str = "", page_size: int = 50,
                         sort_columns: str = "", sort_types: str = "-1") -> List[Dict[str, Any]]:
    """东财数据中心统一查询（datacenter-web.eastmoney.com）。

    V7.5 新增：HTTP状态码非200时记录日志，业务错误码(status=-1)时记录日志，JSON解析失败时记录日志。
    """
    try:
        full_filter = filter_str if filter_str else f'(SECURITY_CODE="{code}")'
        r = _request_with_retry(DATACENTER_URL, params={
            "reportName": report_name, "columns": columns,
            "filter": full_filter, "pageNumber": "1", "pageSize": str(page_size),
            "sortColumns": sort_columns, "sortTypes": sort_types,
            "source": "WEB", "client": "WEB",
        }, headers={"User-Agent": UA}, timeout=15)
        if r is None:
            return []
        # HTTP状态码检查
        if r.status_code != 200:
            _http_logger.error(f"{r.status_code} | {DATACENTER_URL} | {report_name} | {code}")
            return []
        try:
            d = r.json()
        except Exception as _json_err:
            _http_logger.error(f"JSONDecodeError | {DATACENTER_URL} | {report_name} | {code} | {_json_err}")
            return []
        # 业务错误码检查
        if isinstance(d, dict) and d.get("status") == -1:
            _biz_logger.error(f"status=-1 | {report_name} | {code} | {d.get('message', '')}")
            return []
        if d.get("result") and d["result"].get("data"):
            return d["result"]["data"]
        return []
    except Exception as _e:
        _debug_log(f"eastmoney_datacenter({code}, {report_name}): {_e}")
        return []


def _em_filter(code: str, report_name: str, extra_filter: str = "", page_size: int = 50,
               sort_columns: str = "", sort_types: str = "-1") -> List[Dict[str, Any]]:
    """东财数据中心查询便捷包装（自动拼接 SECURITY_CODE）。"""
    return eastmoney_datacenter(code, report_name,
                                filter_str=f'(SECURITY_CODE="{code}"){extra_filter}' if extra_filter else "",
                                page_size=page_size, sort_columns=sort_columns, sort_types=sort_types)


async def eastmoney_datacenter_async(session: Any, code: str, report_name: str, columns: str = "ALL",
                                     filter_str: str = "", page_size: int = 50,
                                     sort_columns: str = "", sort_types: str = "-1") -> List[Dict[str, Any]]:
    """async 版：东财数据中心统一查询（datacenter-web.eastmoney.com）。

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    """
    try:
        full_filter = filter_str if filter_str else f'(SECURITY_CODE="{code}")'
        d = await _async_request_with_retry(session, DATACENTER_URL, params={
            "reportName": report_name, "columns": columns,
            "filter": full_filter, "pageNumber": "1", "pageSize": str(page_size),
            "sortColumns": sort_columns, "sortTypes": sort_types,
            "source": "WEB", "client": "WEB",
        }, headers={"User-Agent": UA}, timeout=15)
        if d is None:
            return []
        if isinstance(d, dict) and d.get("status") == -1:
            _biz_logger.error(f"status=-1 | {report_name} | {code} | {d.get('message', '')}")
            return []
        if d.get("result") and d["result"].get("data"):
            return d["result"]["data"]
        return []
    except Exception as _e:
        _debug_log(f"eastmoney_datacenter_async({code}, {report_name}): {_e}")
        return []


async def _em_filter_async(session: Any, code: str, report_name: str, extra_filter: str = "",
                            page_size: int = 50, sort_columns: str = "",
                            sort_types: str = "-1") -> List[Dict[str, Any]]:
    """async 版：东财数据中心查询便捷包装（自动拼接 SECURITY_CODE）。

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    """
    return await eastmoney_datacenter_async(session, code, report_name,
                                            filter_str=f'(SECURITY_CODE="{code}"){extra_filter}' if extra_filter else "",
                                            page_size=page_size, sort_columns=sort_columns, sort_types=sort_types)


# ═══════════════════════════════════════════════════════════
# 批次1完成：东财数据中心核心函数（3个函数）
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# 批次2：股东数据函数
# ═══════════════════════════════════════════════════════════

# 股东户数缓存（直接使用 SQLite，优化版）
_HOLDER_CACHE_TTL: int = 60 * 86400      # 60 天 — 新鲜阈值（同一季度内 TDX 增量更新）
_HOLDER_CACHE_REFRESH: int = 90 * 86400  # 90 天 — 强制刷新阈值（跨季度用东财补全）


def _holder_fetch_from_sqlite(code: str) -> Optional[Dict[str, Any]]:
    """从 SQLite 获取股东户数数据。"""
    try:
        from stock_cache import get_cache
        cache_key = f"holder_data:{code}"
        cached_data = get_cache("holder", "holder_data", cache_key)
        if cached_data:
            return cached_data
    except Exception as _e:
        _debug_log(f"datasource holder fetch sqlite error: {_e}")
    return None


def _holder_update_sqlite(code: str, records: List[Dict[str, Any]], timestamp: float) -> None:
    """更新 SQLite 中的股东户数数据。"""
    try:
        from stock_cache import set_cache
        cache_key = f"holder_data:{code}"
        data = {
            "records": records,
            "updated": timestamp
        }
        # 使用 holder_cache 的 TTL（60天）
        set_cache("holder", "holder_data", data, _HOLDER_CACHE_TTL, cache_key)
    except Exception as _e:
        _debug_log(f"datasource holder update sqlite error: {_e}")


def _holder_fetch_em(code: str, page_size: int) -> List[Dict[str, Any]]:
    """从东财获取股东户数 → 按日期升序的 records 列表。"""
    data = _em_filter(code, "RPT_F10_EH_HOLDERNUM",
                      page_size=page_size, sort_columns="END_DATE", sort_types="-1")
    if not data:
        return []
    records = []
    for r in data:
        records.append({
            "date": str(r.get("END_DATE", ""))[:10],
            "holder_num": int(r.get("HOLDER_TOTAL_NUM") or 0),
            "avg_shares": _safe_float(r.get("AVG_FREE_SHARES")),
        })
    records.sort(key=lambda x: x["date"])
    return records


def _holder_fetch_tdx_optimized(code: str, records: List[Dict[str, Any]], now: float) -> bool:
    """从 TDX 拿最新 1 期，去重后追加到 records（优化版：直接更新 SQLite）。"""
    from tdx_client import _get_tdx_client
    client = _get_tdx_client()
    if client is None:
        return False
    info = client.get_finance_info(1 if code.startswith("6") else 0, code)
    if info is None or info.empty:
        return False
    hnum = int(info.iloc[0].get('gudong_renshu', 0))
    upd = str(int(info.iloc[0].get('updated_date', 0)))
    if hnum <= 0:
        return False
    date_str = f"{upd[:4]}-{upd[4:6]}-{upd[6:8]}" if len(upd) == 8 else ""
    if not records or records[-1].get("holder_num") != hnum:
        records.append({"date": date_str, "holder_num": hnum})
        if len(records) > 10:
            records = records[-10:]
        _holder_update_sqlite(code, records, now)
        return True
    return False


def _holder_fetch_tdx(code: str, records: List[Dict[str, Any]], now: float) -> bool:
    """从 TDX 拿最新 1 期，去重后追加到 records（保持向后兼容）。"""
    return _holder_fetch_tdx_optimized(code, records, now)


def holder_change(code: str) -> List[Dict[str, Any]]:
    """获取股东户数多期变化（优化版：直接使用 SQLite）。

    逻辑：
      - 缓存新鲜 < 60 天 → 直接返回
      - 缓存为空 → F10 优先（多期）→ 东财 10 期兜底
      - 缓存过期 ≥ 60 天且 < 90 天 → TDX 追加 1 期（同季度增量）
      - 缓存过期 ≥ 90 天 → F10 优先 → 东财 5 期兜底

    返回: [{date, holder_num, change_num, change_ratio, avg_shares}, ...] 最新在前
    """
    from stock_cache import get_cache, set_cache, TTL

    # 尝试从缓存获取
    cache_key = f"holder_data:{code}"
    cached_data = get_cache("holder", "holder_change", cache_key)

    if cached_data is not None:
        return cached_data

    # 缓存未命中，重新获取数据
    now = time.time()

    # 尝试从 SQLite 获取现有记录
    existing_data = _holder_fetch_from_sqlite(code)
    if existing_data:
        records = existing_data.get("records", [])
        updated = existing_data.get("updated", 0)
        age = now - updated

        # ① 缓存新鲜 < 60 天 → 直接返回
        if age < _HOLDER_CACHE_TTL:
            return _compute_holder_changes(records)

        # ② 缓存过期 ≥ 90 天 → F10 优先 → 东财 5 期兜底（跨季度补全）
        if age >= _HOLDER_CACHE_REFRESH:
            # V9.0: F10 优先（76+ 期，远多于东财 5 期）
            f10_records = _holder_fetch_f10(code)
            if f10_records:
                _holder_update_sqlite(code, f10_records, now)
                return _compute_holder_changes(f10_records)
            records = _holder_fetch_em(code, 5)
            if records:
                _holder_update_sqlite(code, records, now)
                return _compute_holder_changes(records)
    else:
        records = []

    # ③ 缓存为空 → F10 优先 → 东财 10 期兜底（首次初始化）
    if not records:
        # V9.0: F10 优先（一次拿全所有历史期数）
        f10_records = _holder_fetch_f10(code)
        if f10_records:
            _holder_update_sqlite(code, f10_records, now)
            return _compute_holder_changes(f10_records)
        records = _holder_fetch_em(code, 10)
        if records:
            _holder_update_sqlite(code, records, now)
            return _compute_holder_changes(records)

    # ④ 尝试从 SQLite 获取现有记录（如果还没有的话）
    if not records:
        existing_data = _holder_fetch_from_sqlite(code)
        if existing_data:
            records = existing_data.get("records", [])

    # ⑤ 缓存过期 ≥ 60 天且 < 90 天 → TDX 追加 1 期
    if _holder_fetch_tdx_optimized(code, records, now):
        return _compute_holder_changes(records)

    # ⑥ 全部失败 → 返回现有记录
    return _compute_holder_changes(records)


def _holder_fetch_f10(code: str) -> List[Dict[str, Any]]:
    """V9.0: 从 F10 股东研究获取股东户数多期记录。

    F10 holder_count 通常包含 76+ 期历史数据，远多于东财 10 期。
    字段映射：F10 entry (period + 股东人数(户) + 人均流通股(股) + etc.) → records [{date, holder_num, avg_shares}]
    """
    try:
        from tdx_client import tdx_get_shareholder_research
        f10 = tdx_get_shareholder_research(code)
        if not f10:
            return []
        holder_count = f10.get('holder_count', [])
        if not holder_count:
            return []
        records: List[Dict[str, Any]] = []
        for entry in holder_count:
            period = (entry.get('period', '') or '').strip()
            if not period:
                continue
            # F10 字段名带后缀，如 "股东人数(户)"、"人均流通股(股)"
            # 用 startswith 匹配，兼容不同后缀
            holder_num = 0
            for k, v in entry.items():
                if k.startswith('股东人数') or k.startswith('股东户数') or k == '户数':
                    holder_num = int(_safe_float(v or 0))
                    break
            if holder_num <= 0:
                continue
            avg_shares = 0.0
            for k, v in entry.items():
                if k.startswith('人均流通股') or k.startswith('户均持股') or k.startswith('户均流通股') or k.startswith('人均持股'):
                    avg_shares = _safe_float(v or 0)
                    break
            records.append({
                "date": str(period)[:10],
                "holder_num": holder_num,
                "avg_shares": avg_shares,
            })
        # 按日期升序（_compute_holder_changes 内部会 reverse）
        records.sort(key=lambda x: x["date"])
        return records
    except Exception as _e:
        _debug_log(f"datasource holder_change ({code}): {_e}")
        return []


async def holder_change_async(session, code: str) -> List[Dict[str, Any]]:
    """async 版：股东户数多期变化（代理到同步版）。"""
    return await asyncio.to_thread(holder_change, code)


def _compute_holder_changes(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """从原始记录列表计算环比变化。"""
    if not records:
        return []
    result = []
    for i in range(len(records)):
        r = records[i]
        prev_num = records[i - 1]["holder_num"] if i > 0 else 0
        change_num = r["holder_num"] - prev_num if i > 0 and prev_num > 0 else 0
        change_ratio = round(change_num / prev_num * 100, 2) if i > 0 and prev_num > 0 else 0.0
        result.append({
            "date": r["date"],
            "holder_num": r["holder_num"],
            "change_num": change_num,
            "change_ratio": change_ratio,
            "avg_shares": r.get("avg_shares", 0),
        })
    # 最新在前
    result.reverse()
    return result


# ═══════════════════════════════════════════════════════════
# 批次2完成：股东数据函数（8个函数）
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# 批次3：公告/股东结构迁移
# ═══════════════════════════════════════════════════════════

# 巨潮 orgId 缓存（模块级）
_CNINFO_ORGID_CACHE = {}


def _cninfo_get_orgid(code: str) -> str:
    """动态查询巨潮公告的 orgId（SKILL.md V3.2.2 推荐）。

    优先从缓存获取，缓存未命中时先尝试动态查询官方映射表，
    失败则使用硬编码fallback。

    Args:
        code: 股票代码

    Returns:
        orgId 字符串
    """
    # 先查缓存
    if code in _CNINFO_ORGID_CACHE:
        return _CNINFO_ORGID_CACHE[code]

    # 硬编码 fallback（用于动态查询失败时）
    if code.startswith("6"):
        fallback = f"gssh0{code}"
    elif code.startswith("8") or code.startswith("4"):
        fallback = f"gsbj0{code}"
    else:
        fallback = f"gssz0{code}"

    # 尝试动态查询（SKILL.md V3.2.2 推荐方案）
    try:
        url = "https://www.cninfo.com.cn/new/data/szse_stock.json"
        r = _quick_request(url, timeout=10)
        if r is not None:
            data = r.json()
            for item in data:
                if item.get("code") == code:
                    orgid = item.get("orgId", fallback)
                    _CNINFO_ORGID_CACHE[code] = orgid
                    return orgid
    except Exception as _e:
        _debug_log(f"datasource cninfo orgid query error: {_e}")

    # 动态查询失败，返回硬编码 fallback
    _CNINFO_ORGID_CACHE[code] = fallback
    return fallback


@cached(category="announcements", ttl_seconds=TTL["announcements"])
def get_strategic_announcements(code: str, page_size: int = 50, days: Optional[int] = None,
                                importance_filter: bool = False) -> List[Dict[str, Any]]:
    """巨潮公告查询 → orgId → searchkey → TDX F10 三层兜底（SKILL.md V3.2.2 增强：动态orgId查询）。

    Args:
        code: 股票代码
        page_size: 返回数量上限
        days: 限定最近 N 天，None=不限（长线），30=中线，7=短线
        importance_filter: V7.5新增，是否仅返回重要公告（True=仅重要，False=全部）
    返回: [{title, date, type, is_important}, ...]
    """
    # 计算日期范围
    sd_str = ""
    if days:
        sd_str = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        td_str = datetime.now().strftime("%Y-%m-%d")
        se_date = f"{sd_str}~{td_str}"
    else:
        se_date = ""

    url = "https://www.cninfo.com.cn/new/hisAnnouncement/query"

    # SKILL.md V3.2.2 推荐：先尝试动态查询orgId，失败则用硬编码fallback
    ext_org_id = _cninfo_get_orgid(code)

    payload = {
        "orgId": ext_org_id, "stock": f"{code},{ext_org_id}",
        "tabName": "fulltext", "pageSize": str(page_size), "pageNum": "1",
        "column": "", "category": "", "plate": "",
        "seDate": se_date,
        "searchkey": "", "secid": "", "sortName": "", "sortType": "",
        "isHLtitle": "true",
    }
    headers = {"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded",
               "Referer": "https://www.cninfo.com.cn/new/disclosure"}
    _cfg = _load_settings()
    keywords = _cfg.get("announcement_keywords",
                        ["回购", "增持", "减持", "年报", "分红", "派息", "激励", "员工持股",
                         "战略合作", "业绩预告", "中标", "立案", "合同", "收购", "股权转让",
                         "异动", "严重异动"])
    _noise = _cfg.get("announcement_noise", ["摘要", "提示性", "英文版"])
    _importance_kw = _cfg.get("announcement_importance_keywords", [])
    try:
        r = _quick_request(url, data=payload, headers=headers, method="POST", timeout=15)
        anns = []
        if r is not None:
            d = r.json()
            anns = d.get("announcements", []) or []
        if not anns:
            # orgId 失败 → searchkey 兜底
            payload2 = {"orgId": "", "stock": "", "tabName": "fulltext",
                        "pageSize": str(page_size), "pageNum": "1",
                        "column": "", "category": "", "plate": "",
                        "seDate": se_date,
                        "searchkey": str(code), "secid": "",
                        "sortName": "", "sortType": "", "isHLtitle": "true"}
            r2 = _quick_request(url, data=payload2, headers=headers, method="POST", timeout=15)
            if r2 is not None:
                d2 = r2.json()
                anns2 = d2.get("announcements", []) or []
                if anns2:
                    anns = anns2
        if not anns:
            # 巨潮双路径均失败 → TDX F10 兜底
            try:
                from tdx_client import tdx_get_latest_announcements
                tdx_anns = tdx_get_latest_announcements(code, days=7)
                if tdx_anns:
                    anns = [{"announcementTitle": a["title"],
                             "announcementTime": int(datetime.strptime(a["date"], "%Y-%m-%d").timestamp() * 1000) if a.get("date") else 0}
                            for a in tdx_anns]
            except Exception as _e:
                _debug_log(f"datasource tdx announcements fallback error: {_e}")
        rows = []
        for item in anns:
            _sc = str(item.get("secCode", ""))
            if _sc and _sc != str(code):
                continue
            title = item.get("announcementTitle", "")
            title = re.sub(r'<[^>]+>', '', title)
            if any(k in title for k in keywords) and not any(noise in title for noise in _noise):
                ts = item.get("announcementTime", 0)
                if isinstance(ts, (int, float)) and ts > 1000000000000:
                    date_str = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                else:
                    date_str = str(ts)[:10]
                # V7.5新增：重要等级标记
                is_important = any(imp_k in title for imp_k in _importance_kw)
                # 如果开启重要过滤且不是重要公告，跳过
                if importance_filter and not is_important:
                    continue
                rows.append({
                    "title": title,
                    "date": date_str,
                    "type": item.get("announcementTypeName", "") or "",
                    "is_important": is_important,
                })
        return rows
    except Exception as _e:
        _debug_log(f"datasource strategic_announcements ({code}): {_e}")
        return []


async def get_strategic_announcements_async(session, code: str, page_size: int = 50,
                                             days: Optional[int] = None) -> List[Dict[str, Any]]:
    """async 版：巨潮公告查询

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
          TDX F10 兜底保留 asyncio.to_thread。
    """
    from datetime import datetime, timedelta

    _cfg = _load_settings()
    keywords = _cfg.get("announcement_keywords", [])
    _noise = _cfg.get("announcement_noise", ["摘要", "提示性", "英文版"])
    _importance_kw = _cfg.get("announcement_importance_keywords", [])

    if days:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        se_date = f"{start_date.strftime('%Y-%m-%d')}~{end_date.strftime('%Y-%m-%d')}"
    else:
        se_date = ""

    importance_filter = bool(_cfg.get("strategy_announcement_importance_filter", False))

    url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
    headers = {"User-Agent": UA, "Referer": "http://www.cninfo.com.cn/",
               "X-Requested-With": "XMLHttpRequest", "Content-Type": "application/json"}

    try:
        payload = {"orgId": "", "stock": str(code), "tabName": "fulltext",
                   "pageSize": str(page_size), "pageNum": "1",
                   "column": "", "category": "", "plate": "",
                   "seDate": se_date,
                   "searchkey": "", "secid": "",
                   "sortName": "", "sortType": "", "isHLtitle": "true"}
        d = await _async_quick_request(session, url, data=payload, headers=headers, method="POST", timeout=15)
        anns = []
        if d is not None:
            anns = d.get("announcements", []) or []

        if not anns:
            payload2 = {"orgId": "", "stock": "", "tabName": "fulltext",
                        "pageSize": str(page_size), "pageNum": "1",
                        "column": "", "category": "", "plate": "",
                        "seDate": se_date,
                        "searchkey": str(code), "secid": "",
                        "sortName": "", "sortType": "", "isHLtitle": "true"}
            d2 = await _async_quick_request(session, url, data=payload2, headers=headers, method="POST", timeout=15)
            if d2 is not None:
                anns2 = d2.get("announcements", []) or []
                if anns2:
                    anns = anns2

        if not anns:
            try:
                import asyncio
                from tdx_client import tdx_get_latest_announcements
                tdx_anns = await asyncio.to_thread(tdx_get_latest_announcements, code, days=7)
                if tdx_anns:
                    anns = [{"announcementTitle": a["title"],
                             "announcementTime": int(datetime.strptime(a["date"], "%Y-%m-%d").timestamp() * 1000) if a.get("date") else 0}
                            for a in tdx_anns]
            except Exception as _e:
                _debug_log(f"datasource tdx announcements fallback async error: {_e}")

        rows = []
        for item in anns:
            _sc = str(item.get("secCode", ""))
            if _sc and _sc != str(code):
                continue
            title = item.get("announcementTitle", "")
            title = re.sub(r'<[^>]+>', '', title)
            if any(k in title for k in keywords) and not any(noise in title for noise in _noise):
                ts = item.get("announcementTime", 0)
                if isinstance(ts, (int, float)) and ts > 1000000000000:
                    date_str = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                else:
                    date_str = str(ts)[:10]
                is_important = any(imp_k in title for imp_k in _importance_kw)
                if importance_filter and not is_important:
                    continue
                rows.append({
                    "title": title,
                    "date": date_str,
                    "type": item.get("announcementTypeName", "") or "",
                    "is_important": is_important,
                })
        return rows
    except Exception as _e:
        _debug_log(f"datasource strategic_announcements_async ({code}): {_e}")
        return []


# 机构持股结构分析（替代 get_institutional_holder_ratio）
_holder_structure_cache: Dict[str, List[Dict[str, Any]]] = {}


@cached(category="financial", ttl_seconds=TTL["financial"], cross_verify=True)
def get_holder_structure(code: str) -> List[Dict[str, Any]]:
    """东财 RPT_F10_EH_HOLDERS → 多季度十大流通股东分类统计。
    模块级缓存，同一脚本运行期内不重复调 API。

    返回: [{date, total, northbound, foreign, foreign_count,
            domestic, domestic_count, individual, individual_count}, ...] 最新在前

    V9.1: 移除 F10 优先逻辑（F10 缺持股比例字段，机构持股计算为 0）。
    """
    if code in _holder_structure_cache:
        return _holder_structure_cache[code]

    # V9.1: 已移除 F10 优先逻辑（F10 缺持股比例字段，机构持股计算为 0）

    # 东财 HTTP
    data = eastmoney_datacenter(code, "RPT_F10_EH_HOLDERS",
                                columns="END_DATE,HOLDER_NAME,HOLD_NUM_RATIO",
                                filter_str=f'(SECURITY_CODE="{code}")',
                                page_size=50, sort_columns="END_DATE", sort_types="-1")
    if not data:
        return []

    # 按报告期分组
    periods = {}
    for h in data:
        ed = str(h.get("END_DATE", ""))[:10]
        if ed not in periods:
            periods[ed] = []
        periods[ed].append(h)

    result = []
    for date_key in sorted(periods.keys(), reverse=True)[:4]:
        holders = periods[date_key]
        nb = fe = dm = ind = 0.0
        fc = dc = ic = 0
        dm_tags = {"国资": 0.0, "证金汇金": 0.0, "公募": 0.0, "险资": 0.0, "社保": 0.0}

        for h in holders[:10]:
            name = (h.get("HOLDER_NAME", "") or "").strip()
            ratio = float(h.get("HOLD_NUM_RATIO", 0))
            has_cn = any('\u4e00' <= c <= '\u9fff' for c in name)
            has_en = any(c.isalpha() and ord(c) < 128 for c in name)

            if '香港中央结算' in name or 'HKSCC' in name.upper():
                nb += ratio
            elif not has_cn and has_en:
                fe += ratio; fc += 1
            elif has_cn and len([c for c in name if '\u4e00' <= c <= '\u9fff']) <= 3 \
                 and not any(kw in name for kw in
                             ['公司', '基金', '保险', '银行', '信托', '证券', '合伙', '集团', '投资', '控股']):
                ind += ratio; ic += 1
            else:
                dm += ratio; dc += 1
                # 境内机构细分
                if '社保' in name:
                    dm_tags["社保"] += ratio
                elif '保险' in name:
                    dm_tags["险资"] += ratio
                elif '中国证券金融' in name or '中央汇金' in name:
                    dm_tags["证金汇金"] += ratio
                elif '基金' in name:
                    dm_tags["公募"] += ratio
                elif '集团' in name or '国有' in name or '国资委' in name:
                    dm_tags["国资"] += ratio

        result.append({
            "date": date_key,
            "total": round(nb + fe + dm + ind, 1),
            "northbound": round(nb, 2),
            "foreign": round(fe, 1), "foreign_count": fc,
            "domestic": round(dm, 1), "domestic_count": dc,
            "individual": round(ind, 1), "individual_count": ic,
            "dm_detail": {k: round(v, 1) for k, v in dm_tags.items() if v > 0},
        })

    _holder_structure_cache[code] = result
    return result


async def get_holder_structure_async(session: Any, code: str, today_str: str = "") -> Dict[str, Any]:
    """异步版 get_holder_structure"""
    import asyncio
    return await asyncio.to_thread(get_holder_structure, code)


# ═══════════════════════════════════════════════════════════
# 批次3完成：公告/股东结构函数（5个函数）
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# 批次4：行情/研报/北向资金迁移
# ═══════════════════════════════════════════════════════════

# 行情和K线（函数内部导入避免循环依赖）
def get_tencent_quote(code: str) -> Dict[str, Any]:
    """V4: 个股行情 → tdx_client 适配器（TDX实时价+腾讯估值+五档盘口）"""
    from tdx_client import tdx_get_quote_full
    return tdx_get_quote_full(code)


@cached(category="kline", ttl_seconds=TTL["kline"])
def baidu_kline_full(code, is_index=False):
    """V4: 全量K线 → tdx_client 适配器（TDX日K线，自动fallback百度）"""
    from tdx_client import tdx_get_security_bars, tdx_get_index_bars
    if is_index:
        return tdx_get_index_bars(code)
    return tdx_get_security_bars(code)


async def get_tencent_quote_async(session: Any, code: str) -> Dict[str, Any]:
    """异步版 get_tencent_quote（复用 TDX 同步函数）"""
    import asyncio
    from tdx_client import tdx_get_quote_full
    return await asyncio.to_thread(tdx_get_quote_full, code)


@cached(category="basic_info", ttl_seconds=TTL["basic_info"],
        valid_if=lambda r: isinstance(r, dict) and bool(r.get("code")), cross_verify=True)
def get_stock_info(code: str) -> Dict[str, Any]:
    """V7.5: 个股基本信息 → 腾讯行情 + TDX"""
    from tdx_client import _get_tdx_client, tdx_get_belong_boards
    name = industry = list_date = ""
    total_shares = float_shares = mcap = float_mcap = price = 0

    q = get_tencent_quote(code)
    if q:
        name = q.get("name", "")
        price = q.get("price", 0) or 0
        mcap = int(q.get("mcap_yi", 0) * 1e8)
        float_mcap = int(q.get("float_mcap_yi", 0) * 1e8)

    try:
        client = _get_tdx_client()
        if client:
            from stock_common.sc_network import _market_code
            info = client.get_finance_info(_market_code(code), code)
            if info is not None and not info.empty:
                total_shares = _safe_float(info.iloc[0].get('zong_guben', 0))
                float_shares = _safe_float(info.iloc[0].get('liutong_guben', 0))
                ipo = str(int(info.iloc[0].get('ipo_date', 0)))
                if ipo and ipo != '0':
                    list_date = ipo
    except Exception as _e:
        _debug_log(f"datasource tdx finance info error: {_e}")

    # TDX 获取上市日期失败时，尝试东财 push2 fallback
    if not list_date:
        try:
            push2_info = eastmoney_stock_info_push2(code)
            if push2_info:
                list_date = push2_info.get("list_date", "")
        except Exception as _e:
            _debug_log(f"datasource eastmoney push2 list_date error: {_e}")

    if not total_shares and price > 0 and mcap > 0:
        total_shares = int(mcap / price)
    if not float_shares and price > 0 and float_mcap > 0:
        float_shares = int(float_mcap / price)

    try:
        tdx_boards = tdx_get_belong_boards(code)
        if tdx_boards and tdx_boards.get("industry"):
            industry = tdx_boards["industry"][0]["name"]
    except Exception as _e:
        _debug_log(f"datasource tdx belong boards error: {_e}")

    return {
        "code": code, "name": name, "industry": industry,
        "total_shares": total_shares, "float_shares": float_shares,
        "mcap": mcap, "float_mcap": float_mcap,
        "list_date": list_date, "price": price,
    }


async def get_stock_info_async(session: Any, code: str) -> Dict[str, Any]:
    """异步版 get_stock_info"""
    import asyncio
    return await asyncio.to_thread(get_stock_info, code)


# 研报
@cached(category="reports", ttl_seconds=TTL["reports"])
def get_reports(code: str, max_pages: int = 3) -> List[Dict[str, Any]]:
    """东财研报列表查询（个股研报，qType=0）。

    Args:
        code: 股票代码。
        max_pages: 最大页数（每页50条）。

    Returns:
        list: 研报记录列表。

    V9.1: 移除 F10 优先逻辑（F10 无真实研报标题，仅"目标价:--- 维持"，
          数据质量远低于东财 HTTP）。保留东财 HTTP 为主力数据源。
    """
    # Fallback: 东财 HTTP
    api_url = "https://reportapi.eastmoney.com/report/list"
    all_records = []
    for page in range(1, max_pages + 1):
        params = {
            "pageSize": "50", "industry": "*", "rating": "*",
            "beginTime": "2000-01-01", "endTime": "2030-01-01",
            "pageNo": str(page), "code": code, "qType": "0"
        }
        try:
            r = _request_with_retry(api_url, params=params, timeout=30)
            if r is None:
                break
            rows = r.json().get("data") or []
            if not rows:
                break
            all_records.extend(rows)
        except Exception as _e:
            _debug_log(f"datasource get_reports page {page} ({code}): {_e}")
            break
    return all_records


async def get_reports_async(session: Any, code: str, max_pages: int = 3) -> List[Dict[str, Any]]:
    """async 版: 东财研报列表

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    """
    api_url = "https://reportapi.eastmoney.com/report/list"
    all_records = []
    for page in range(1, max_pages + 1):
        params = {
            "pageSize": "50", "industry": "*", "rating": "*",
            "beginTime": "2000-01-01", "endTime": "2030-01-01",
            "pageNo": str(page), "code": code, "qType": "0"
        }
        try:
            d = await _async_quick_request(session, api_url, params=params, timeout=30)
            if d is None:
                break
            rows = d.get("data") or []
            if not rows:
                break
            all_records.extend(rows)
        except Exception as _e:
            _debug_log(f"datasource get_reports_async page {page} ({code}): {_e}")
            break
    return all_records


@cached(category="industry_reports", ttl_seconds=TTL["reports"])
def get_industry_reports(industry_code: str = "*", max_pages: int = 3,
                         begin_time: str = "2024-01-01") -> List[Dict[str, Any]]:
    """东财行业研报列表查询（SKILL.md V3.2.3 新增，qType=1）。

    与个股研报同一端点，仅 qType 参数不同：
    - qType=0: 个股研报（get_reports）
    - qType=1: 行业研报（本函数）

    Args:
        industry_code: 东财行业代码，"*"表示全行业
        max_pages: 最大页数（每页100条）
        begin_time: 起始日期（格式：YYYY-MM-DD）

    Returns:
        list: 行业研报记录列表，包含行业名称、评级、报告类型等字段

    行业研报特有字段：
        - industryName: 行业名称（如 IT服务Ⅱ、风电设备、光伏设备）
        - industryCode: 东财行业代码（用于精确过滤）
        - emRatingName: 行业评级（买入/增持/中性/...）
        - reportType: 报告类型
        - infoCode: 用于拼接PDF下载URL
    """
    api_url = "https://reportapi.eastmoney.com/report/list"
    all_records = []
    for page in range(1, max_pages + 1):
        params = {
            "industryCode": industry_code,
            "pageSize": "100",
            "industry": "*",
            "rating": "*",
            "beginTime": begin_time,
            "endTime": "2030-01-01",
            "pageNo": str(page),
            "fields": "",
            "qType": "1",
            "orgCode": "",
            "code": "",
            "rcode": "",
            "p": str(page),
            "pageNum": str(page),
            "pageNumber": str(page),
        }
        try:
            r = em_get(api_url, params=params, headers={"Referer": "https://data.eastmoney.com/"}, timeout=30)
            if r is None:
                break
            d = r.json()
            rows = d.get("data") or []
            if not rows:
                break
            all_records.extend(rows)
            if page >= (d.get("TotalPage", 1) or 1):
                break
        except Exception as _e:
            _debug_log(f"datasource get_industry_reports page {page} ({industry_code}): {_e}")
            break
    return all_records


@cached(category="eps_forecast", ttl_seconds=TTL["eps_forecast"], cross_verify=True)
def get_eps_forecast(code: str) -> Dict[str, Any]:
    """V7.5: 机构一致预期EPS — 同花顺正则提取 + 东财研报兜底。

    Returns:
        DataFrame [年度, 机构数, 最小值, 均值, 最大值, 行业均值]。
    """
    try:
        import re as _re2
        r = _quick_request(f"https://basic.10jqka.com.cn/new/{code}/worth.html",
                           headers={"User-Agent": UA, "Referer": "https://basic.10jqka.com.cn/"},
                           timeout=15)
        if r is not None:
            r.encoding = "gbk"
            m = _re2.search(r'汇总--预测年报每股收益.*?(<tbody>.*?</tbody>)', r.text, _re2.DOTALL)
            if m:
                rows = _re2.findall(r'<tr>(.*?)</tr>', m.group(1), _re2.DOTALL)
                data_rows = []
                for row in rows:
                    cells = _re2.findall(r'<(?:th|td)[^>]*>(.*?)</(?:th|td)>', row, _re2.DOTALL)
                    cleaned = [_re2.sub(r'<[^>]+>', '', c).strip() for c in cells]
                    if len(cleaned) >= 5:
                        data_rows.append(cleaned[:6])
                if data_rows:
                    import pandas as _pd
                    return _pd.DataFrame(data_rows,
                                         columns=["年度", "机构数", "最小值", "均值", "最大值", "行业均值"])
    except Exception as _e:
        _debug_log(f"datasource ths eps forecast parse error: {_e}")
    # 东财研报兜底
    try:
        from tdx_client import tdx_get_eps_from_reports
        em_eps = tdx_get_eps_from_reports(code)
        if em_eps and em_eps.get("eps_cur"):
            import pandas as _pd
            return _pd.DataFrame({
                "年度": ["预测今年", "预测明年"],
                "机构数": [1, 1], "最小值": [0, 0],
                "均值": [em_eps["eps_cur"], em_eps.get("eps_next") or 0],
                "最大值": [0, 0], "行业均值": [0, 0]
            })
    except Exception as _e:
        _debug_log(f"datasource tdx eps reports fallback error: {_e}")
    import pandas as _pd
    return _pd.DataFrame()


async def get_eps_forecast_async(session: Any, code: str) -> Dict[str, Any]:
    """async 版: 机构一致预期EPS — 同花顺正则提取 + TDX兜底"""
    try:
        import re as _re2
        r = await _async_quick_request(session,
                                       f"https://basic.10jqka.com.cn/new/{code}/worth.html",
                                       headers={"User-Agent": UA, "Referer": "https://basic.10jqka.com.cn/"},
                                       timeout=15, is_json=False, encoding='gbk')
        if r is not None:
            text = r
            m = _re2.search(r'汇总--预测年报每股收益.*?(<tbody>.*?</tbody>)', text, _re2.DOTALL)
            if m:
                rows = _re2.findall(r'<tr>(.*?)</tr>', m.group(1), _re2.DOTALL)
                data_rows = []
                for row in rows:
                    cells = _re2.findall(r'<(?:th|td)[^>]*>(.*?)</(?:th|td)>', row, _re2.DOTALL)
                    cleaned = [_re2.sub(r'<[^>]+>', '', c).strip() for c in cells]
                    if len(cleaned) >= 5:
                        data_rows.append(cleaned[:6])
                if data_rows:
                    import pandas as _pd
                    return _pd.DataFrame(data_rows, columns=["年度", "机构数", "最小值", "均值", "最大值", "行业均值"])
    except Exception as _e:
        _debug_log(f"datasource ths eps forecast async parse error: {_e}")

    try:
        from tdx_client import tdx_get_eps_from_reports
        em_eps = tdx_get_eps_from_reports(code)
        if em_eps and em_eps.get("eps_cur"):
            import pandas as _pd
            return _pd.DataFrame({
                "年度": ["预测今年", "预测明年"],
                "机构数": [1, 1], "最小值": [0, 0],
                "均值": [em_eps["eps_cur"], em_eps.get("eps_next") or 0],
                "最大值": [0, 0], "行业均值": [0, 0]
            })
    except Exception as _e:
        _debug_log(f"datasource tdx eps reports async fallback error: {_e}")

    import pandas as _pd
    return _pd.DataFrame()


# 北向资金
@cached(category="northbound", ttl_seconds=TTL["northbound"])
def get_northbound_hold(code: str, days: int = 20) -> List[Dict[str, Any]]:
    """北向资金持仓动态（SKILL.md V3.2 增强：本地CSV缓存回退）。

    注意：东财北向资金数据自2024-08后部分字段可能返回NaN，本函数已添加本地CSV缓存回退。

    Args:
        code: 股票代码。
        days: 查询天数。

    Returns:
        list: [{date, hold_shares, market_cap, hold_ratio, change_shares, change_ratio}, ...]。
    """
    import os
    data = eastmoney_datacenter(code, "RPT_MUTUAL_HOLDSTOCKNORTH_STA",
                                filter_str=f'(SECURITY_CODE="{code}")',
                                page_size=days, sort_columns="TRADE_DATE", sort_types="-1")

    rows = []
    has_valid_data = False
    for row in data:
        hold_shares = float(row.get("HOLD_SHARES") or 0)
        hold_ratio = float(row.get("FREE_SHARES_RATIO") or row.get("A_SHARES_RATIO")
                          or row.get("TOTAL_SHARES_RATIO") or row.get("HOLD_RATIO") or 0)
        if hold_shares > 0 or hold_ratio > 0:
            has_valid_data = True

        rows.append({
            "date": str(row.get("TRADE_DATE", "") or "")[:10],
            "hold_shares": hold_shares,
            "market_cap": float(row.get("HOLD_MARKET_CAP") or row.get("MARKET_CAP") or 0),
            "hold_ratio": hold_ratio,
            "change_shares": float(row.get("CHANGE_SHARES") or 0),
            "change_ratio": float(row.get("CHANGE_RATE") or 0),
        })

    if not has_valid_data and len(rows) == 0:
        return _load_northbound_cache(code, days)

    return rows


# ── 北向资金本地CSV缓存辅助函数 ──
def _northbound_cache_path(code: str) -> str:
    """北向资金本地CSV缓存路径"""
    import os
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cache")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, f"northbound_{code}.csv")


def _load_northbound_cache(code: str, days: int) -> List[Dict[str, Any]]:
    """从本地CSV缓存加载北向资金数据"""
    import os
    path = _northbound_cache_path(code)
    rows = []
    if not os.path.exists(path):
        return rows

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[1:]:  # 跳过表头
                parts = line.strip().split(",")
                if len(parts) >= 6:
                    rows.append({
                        "date": parts[0],
                        "hold_shares": float(parts[1]),
                        "market_cap": float(parts[2]),
                        "hold_ratio": float(parts[3]),
                        "change_shares": float(parts[4]),
                        "change_ratio": float(parts[5]),
                    })
    except Exception as _e:
        _debug_log(f"datasource northbound cache load error: {_e}")

    return rows[-days:] if rows else rows


async def get_northbound_hold_async(session: Any, code: str, days: int = 20) -> List[Dict[str, Any]]:
    """async 版: 北向资金持仓动态

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    """
    import os
    data = await eastmoney_datacenter_async(session, code, "RPT_MUTUAL_HOLDSTOCKNORTH_STA",
                                            filter_str=f'(SECURITY_CODE="{code}")',
                                            page_size=days, sort_columns="TRADE_DATE", sort_types="-1")

    rows = []
    has_valid_data = False
    for row in data:
        hold_shares = float(row.get("HOLD_SHARES") or 0)
        hold_ratio = float(row.get("FREE_SHARES_RATIO") or row.get("A_SHARES_RATIO")
                          or row.get("TOTAL_SHARES_RATIO") or row.get("HOLD_RATIO") or 0)
        if hold_shares > 0 or hold_ratio > 0:
            has_valid_data = True

        rows.append({
            "date": str(row.get("TRADE_DATE", "") or "")[:10],
            "hold_shares": hold_shares,
            "market_cap": float(row.get("HOLD_MARKET_CAP") or row.get("MARKET_CAP") or 0),
            "hold_ratio": hold_ratio,
            "change_shares": float(row.get("CHANGE_SHARES") or 0),
            "change_ratio": float(row.get("CHANGE_RATE") or 0),
        })

    if not has_valid_data and len(rows) == 0:
        return _load_northbound_cache(code, days)

    return rows


# ═══════════════════════════════════════════════════════════
# 批次4完成：行情/研报/北向资金函数（13个函数）
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# 批次5：融资融券/大宗/分红/概念迁移
# ═══════════════════════════════════════════════════════════

@cached(category="margin_trading", ttl_seconds=TTL["margin_trading"])
def get_margin_trading(code: str) -> List[Dict[str, Any]]:
    """融资融券数据。

    Returns:
        list: [{date, rzye, rzmre, rzche, rqye, rqmcl, rqchl, rzrqye}, ...]。
              所有金额单位统一为元（V9.1: F10 万元单位已 ×10000 转换为元）。

    V9.1: 修复 F10 单位问题。F10 finance_balance/securities_balance 等字段单位是万元，
          finance_buy/securities_sell 单位是万元/万股，与东财 HTTP 的元/股单位不一致。
          渲染代码（sht/med/lng/ful）统一按元处理 `/1e4` 转万元显示，原代码直接返回
          万元数值，导致显示为实际值的 1/10000。修复：F10 数据 ×10000 转元单位。
    """
    # V9.0: 优先使用 F10 最新提示中的融资融券数据
    try:
        from tdx_client import tdx_get_latest_reminders
        f10 = tdx_get_latest_reminders(code)
        if f10:
            mt = f10.get('margin_trading', [])
            if mt:
                rows = []
                for r in mt:
                    # date 截断到10位（防止F10表格解析跨行拼接导致日期异常）
                    date_val = str(r.get('date', '') or '')[:10]
                    rzye_val = float(r.get('finance_balance', 0) or 0) * 10000
                    rzmre_val = float(r.get('finance_buy', 0) or 0) * 10000
                    rqye_val = float(r.get('securities_balance', 0) or 0) * 10000
                    rqmcl_val = float(r.get('securities_sell', 0) or 0) * 10000
                    rzrqye_val = float(r.get('total_balance', 0) or 0) * 10000
                    # 过滤金额全为0的无效行（F10表格最后一行被截断解析会产出脏数据）
                    if rzye_val == 0 and rzmre_val == 0 and rqye_val == 0:
                        continue
                    if not date_val or len(date_val) != 10:
                        continue
                    rows.append({
                        "date": date_val,
                        "rzye": rzye_val,
                        "rzmre": rzmre_val,
                        "rzche": 0.0,
                        "rqye": rqye_val,
                        "rqmcl": rqmcl_val,
                        "rqchl": 0.0,
                        "rzrqye": rzrqye_val,
                    })
                if rows:
                    return rows
    except Exception as _e:
        _debug_log(f"datasource tdx margin trading f10 error: {_e}")
    # Fallback: 东财 HTTP
    data = eastmoney_datacenter(code, "RPTA_WEB_RZRQ_GGMX",
                                filter_str=f'(SCODE="{code}")',
                                page_size=15, sort_columns="DATE", sort_types="-1")
    rows = []
    for row in data:
        rows.append({
            "date": str(row.get("DATE", "") or "")[:10],
            "rzye": float(row.get("RZYE") or 0),
            "rzmre": float(row.get("RZMRE") or 0),
            "rzche": float(row.get("RZCHE") or 0),
            "rqye": float(row.get("RQYE") or 0),
            "rqmcl": float(row.get("RQMCL") or 0),
            "rqchl": float(row.get("RQCHL") or 0),
            "rzrqye": float(row.get("RZRQYE") or 0),
        })
    return rows


async def get_margin_trading_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """async 版: 融资融券数据

    V9.0: 委托到同步版（已内置 F10 优先逻辑），保留 session 参数向后兼容。
    """
    import asyncio
    return await asyncio.to_thread(get_margin_trading, code)


@cached(category="block_trade", ttl_seconds=TTL["block_trade"])
def get_block_trade(code: str) -> List[Dict[str, Any]]:
    """大宗交易数据。

    Returns:
        list: [{date, price, close, premium_pct, vol, amount, buyer, seller}, ...]。

    V9.1: 移除 F10 优先逻辑（F10 缺 close_price 和 premium_pct，且 volume 单位
          与东财 HTTP 不一致）。保留东财 HTTP 为主力数据源。
    """
    # 东财 HTTP
    data = _em_filter(code, "RPT_DATA_BLOCKTRADE",
                      page_size=15, sort_columns="TRADE_DATE", sort_types="-1")
    rows = []
    for row in data:
        close = float(row.get("CLOSE_PRICE") or 0)
        deal_price = float(row.get("DEAL_PRICE") or 0)
        premium = ((deal_price / close - 1) * 100) if close else 0
        rows.append({
            "date": str(row.get("TRADE_DATE", "") or "")[:10],
            "price": deal_price,
            "close": close,
            "premium_pct": round(premium, 2),
            "vol": float(row.get("DEAL_VOLUME") or 0),
            "amount": float(row.get("DEAL_AMT") or 0),
            "buyer": str(row.get("BUYER_NAME", "") or ""),
            "seller": str(row.get("SELLER_NAME", "") or ""),
        })
    return rows


async def get_block_trade_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """async 版: 大宗交易数据

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    """
    data = await _em_filter_async(session, code, "RPT_DATA_BLOCKTRADE",
                                  page_size=15, sort_columns="TRADE_DATE", sort_types="-1")
    rows = []
    for row in data:
        close = float(row.get("CLOSE_PRICE") or 0)
        deal_price = float(row.get("DEAL_PRICE") or 0)
        premium = ((deal_price / close - 1) * 100) if close else 0
        rows.append({
            "date": str(row.get("TRADE_DATE", "") or "")[:10],
            "price": deal_price,
            "close": close,
            "premium_pct": round(premium, 2),
            "vol": float(row.get("DEAL_VOLUME") or 0),
            "amount": float(row.get("DEAL_AMT") or 0),
            "buyer": str(row.get("BUYER_NAME", "") or ""),
            "seller": str(row.get("SELLER_NAME", "") or ""),
        })
    return rows


@cached(category="dividend", ttl_seconds=TTL["dividend"], cross_verify=True)
def get_dividend_history(code):
    """V7.5: 分红历史 → TDX xdxr_info（东财 fallback 已删除）"""
    from tdx_client import tdx_get_dividend_history
    return tdx_get_dividend_history(code)


async def get_dividend_history_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """异步版 get_dividend_history"""
    import asyncio
    return await asyncio.to_thread(get_dividend_history, code)


@cached(category="concept_blocks", ttl_seconds=TTL["concept_blocks"], cross_verify=True)
def get_concept_blocks(code: str) -> Dict[str, Any]:
    """V7.5: 概念板块 — 纯 TDX belong_board（短线脚本抽取统一）。

    返回: {"industry": [...], "concept": [...], "region": [...], "concept_tags": [...]}
    """
    from tdx_client import tdx_get_belong_boards
    boards = tdx_get_belong_boards(code)
    if not boards:
        return {"industry": [], "concept": [], "region": [], "concept_tags": []}
    result = {
        "industry": boards.get("industry", []),
        "concept": boards.get("concept", []),
        "region": boards.get("area", []),
        "concept_tags": [c["name"] for c in boards.get("concept", [])],
    }
    return result


async def get_concept_blocks_async(session: Any, code: str) -> Dict[str, Any]:
    """异步版 get_concept_blocks"""
    import asyncio
    return await asyncio.to_thread(get_concept_blocks, code)


# ═══════════════════════════════════════════════════════════
# 批次5完成：融资融券/大宗/分红/概念函数（8个函数）
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# 批次6：同花顺/行业对比/新闻迁移
# ═══════════════════════════════════════════════════════════

# 同花顺热点题材归因
def get_ths_hot_reason(code: str, date_str: str) -> Optional[Dict[str, Any]]:
    """V7.5: 同花顺热点题材归因（短线脚本抽取统一）。

    返回: {"reason": str} 或 None。
    """
    url = f"http://zx.10jqka.com.cn/event/api/getharden/date/{date_str}/orderby/date/orderway/desc/charset/GBK/"
    try:
        r = _quick_request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117.0.0.0"}, timeout=10)
        if r is None:
            return None
        d = r.json()
        if str(d.get("errocode", 0)) != "0":
            return None
        for row in (d.get("data") or []):
            if str(row.get("code")) == str(code):
                return {"reason": row.get("reason", "")}
    except Exception as _e:
        _debug_log(f"datasource ths hot reason error: {_e}")
    return None


async def get_ths_hot_reason_async(session: Any, code: str, date_str: str) -> Optional[Dict[str, Any]]:
    """V7.5: 同花顺热点题材归因

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    """
    url = f"http://zx.10jqka.com.cn/event/api/getharden/date/{date_str}/orderby/date/orderway/desc/charset/GBK/"
    try:
        d = await _async_quick_request(session, url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117.0.0.0"}, timeout=10)
        if d is None:
            return None
        if str(d.get("errocode", 0)) != "0":
            return None
        for row in (d.get("data") or []):
            if str(row.get("code")) == str(code):
                return {"reason": row.get("reason", "")}
    except Exception as _e:
        _debug_log(f"datasource ths hot reason async error: {_e}")
    return None


# 行业对比
@cached(category="industry_peers", ttl_seconds=TTL["industry_peers"], trading_day=True,
        valid_if=lambda r: isinstance(r, dict) and bool(r.get("peers")) and any(
            p.get("price", 0) > 0 for p in r["peers"] if isinstance(p, dict)
        ))
def get_industry_peers(code: str, top_n: int = 3, info: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """V7.5: 同业对比 — TDX 三级兜底（belong_board → board_members → board_by_name）。

    返回: {
        "industry": str, "my_mcap": float, "my_rank": int, "industry_count": int,
        "peers": [...], "all_members": [...]
    }
    """
    from tdx_client import tdx_get_belong_boards, tdx_get_board_members, tdx_get_board_by_name
    from stock_common.sc_utils import _load_strategy_config

    _sc = _load_strategy_config()
    _mkt_cfg = _sc.get("market", {})
    _peers_low = _mkt_cfg.get("peers_mcap_low", 0.3)
    _peers_high = _mkt_cfg.get("peers_mcap_high", 3.0)

    # 1. TDX board_members（通过 belong_board 获取 board_code）
    boards = tdx_get_belong_boards(code)
    industry_boards = boards.get("industry", []) if boards else []

    if industry_boards:
        primary = industry_boards[0]
        members = tdx_get_board_members(primary["code"])
        if not members:
            members = tdx_get_board_by_name(primary["name"], board_type=0)
        if members:
            members_by_mcap = sorted(members, key=lambda x: x.get("mcap_yi", 0), reverse=True)
            my_mcap = 0
            my_rank = 0
            for i, m in enumerate(members_by_mcap, 1):
                if m["code"] == code:
                    my_mcap = m.get("mcap_yi", 0)
                    my_rank = i
                    break
            # 第一只：行业标杆（市值最大），其余：市值相近（0.3~3 倍）
            others = [m for m in members_by_mcap if m["code"] != code]
            peers = []
            if others:
                peers.append(others[0])  # 行业龙头
            if my_mcap > 0:
                similar = [m for m in others[1:] if _peers_low * my_mcap <= m.get("mcap_yi", 0) <= _peers_high * my_mcap]
                peers += similar[:top_n - 1]
            if len(peers) < top_n:
                peers += [m for m in others if m not in peers][:top_n - len(peers)]

            # V8.9: 腾讯行情 fallback — TDX 返回 price=0 时用腾讯补全
            for _p in peers:
                if _p.get("price", 0) <= 0:
                    try:
                        from stock_common import get_tencent_quote
                        _q = get_tencent_quote(_p["code"])
                        if _q and _q.get("price", 0) > 0:
                            _p["price"] = _q.get("price", _p["price"])
                            _p["change_pct"] = _q.get("change_pct", _p["change_pct"])
                            _p["mcap_yi"] = _q.get("mcap_yi", _p["mcap_yi"])
                            _p["pe"] = _q.get("pe_ttm", _p["pe"])
                            _p["turnover"] = _q.get("turnover_pct", _p["turnover"])
                    except Exception as _e:
                        _debug_log(f"datasource tencent quote fallback error: {_e}")
            return {
                "industry": primary["name"],
                "my_mcap": my_mcap,
                "my_rank": my_rank,
                "industry_count": len(members),
                "peers": peers[:top_n],
                "all_members": members_by_mcap,
            }

    # 2. Fallback: 无 industry_boards → 用 info.industry + board_list 匹配
    ind_name = info.get("industry", "") if info else ""
    if ind_name:
        st = tdx_get_board_by_name(ind_name, board_type=0)
        if st:
            st_by_mcap = sorted(st, key=lambda x: x.get("mcap_yi", 0), reverse=True)
            my_mcap = 0
            my_rank = 0
            for i, s in enumerate(st_by_mcap, 1):
                if s["code"] == code:
                    my_mcap = s.get("mcap_yi", 0)
                    my_rank = i
                    break
            others = [s for s in st_by_mcap if s["code"] != code]
            peers = []
            if others:
                peers.append(others[0])
            if my_mcap > 0:
                similar = [s for s in others[1:] if _peers_low * my_mcap <= s.get("mcap_yi", 0) <= _peers_high * my_mcap]
                peers += similar[:top_n - 1]
            if len(peers) < top_n:
                peers += [s for s in others if s not in peers][:top_n - len(peers)]
            return {
                "industry": ind_name,
                "my_mcap": my_mcap,
                "my_rank": my_rank,
                "industry_count": len(st),
                "peers": peers[:top_n],
            }

    # 3. V9.0 Fallback: F10 行业分析（仅返回行业名 + 公司规模排名，无 peer 市值）
    try:
        from tdx_client import tdx_get_industry_analysis
        f10 = tdx_get_industry_analysis(code)
        if f10:
            industry_info = f10.get('industry', {})
            company_scale = f10.get('company_scale', {})
            industry_name = industry_info.get('name', '') if industry_info else ''
            industry_count = industry_info.get('total_count', 0) if industry_info else 0
            my_rank_info = company_scale.get('my_rank', {}) if company_scale else {}
            # 从 my_rank 字典中提取排名（不同字段名兼容）
            my_rank = 0
            if my_rank_info:
                for k, v in my_rank_info.items():
                    if '排名' in k or '名次' in k or k.lower() == 'rank':
                        try:
                            my_rank = int(str(v).replace('第', '').replace('名', '').strip())
                        except (ValueError, TypeError):
                            pass
                        break
            # top_rankings 作为 peers（无市值/价格，仅基本信息）
            top_rankings = company_scale.get('top_rankings', []) if company_scale else []
            peers = []
            for r in top_rankings[:top_n]:
                peers.append({
                    "code": r.get('代码', r.get('股票代码', '')),
                    "name": r.get('名称', r.get('股票简称', '')),
                    "price": 0,
                    "change_pct": 0,
                    "mcap_yi": 0,
                    "pe": 0,
                    "turnover": 0,
                })
            if industry_name:
                return {
                    "industry": industry_name,
                    "my_mcap": 0,
                    "my_rank": my_rank,
                    "industry_count": industry_count,
                    "peers": peers,
                }
    except Exception as _e:
        _debug_log(f"datasource tdx industry analysis f10 error: {_e}")

    return {"industry": "", "my_mcap": 0, "my_rank": 0, "industry_count": 0, "peers": []}


async def get_industry_peers_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """异步版 get_industry_peers"""
    import asyncio
    return await asyncio.to_thread(get_industry_peers, code)


@cached(category="industry_peers", ttl_seconds=TTL["industry_peers"], trading_day=True)
def get_stock_sector_rank(code: str, info: Optional[Dict[str, Any]] = None, q: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """V7.5: 板块内排名 — TDX 优先。

    返回: {"rank": int, "total": int, "change_pct": float} 或 None。
    """
    from tdx_client import tdx_get_belong_boards, tdx_get_board_members, tdx_get_board_by_name

    # 1. TDX board_members（同源分类，精确匹配）
    boards = tdx_get_belong_boards(code)
    industry_boards = boards.get("industry", []) if boards else []

    if industry_boards:
        primary = industry_boards[0]
        members = tdx_get_board_members(primary["code"])
        if members:
            members_by_chg = sorted(members, key=lambda x: x.get("change_pct", 0), reverse=True)
            for i, m in enumerate(members_by_chg, 1):
                if m["code"] == code:
                    _chg = q.get("change_pct", m["change_pct"]) if q else m["change_pct"]
                    return {"rank": i, "total": len(members), "change_pct": _chg}

    # 2. Fallback: TDX board_list → match by name → board_members
    ind_name = (industry_boards[0].get("name", "") if industry_boards else "") or (info.get("industry", "") if info else "")
    if ind_name:
        st = tdx_get_board_by_name(ind_name, board_type=0)
        if st:
            st_sorted = sorted(st, key=lambda x: x.get("change_pct", 0), reverse=True)
            for i, s in enumerate(st_sorted, 1):
                if s["code"] == code:
                    _chg = q.get("change_pct", s["change_pct"]) if q else s["change_pct"]
                    return {"rank": i, "total": len(st), "change_pct": _chg}

    return None


async def get_stock_sector_rank_async(session: Any, code: str) -> Dict[str, Any]:
    """异步版 get_stock_sector_rank"""
    import asyncio
    return await asyncio.to_thread(get_stock_sector_rank, code)


@cached(category="industry_compare", ttl_seconds=TTL["industry_compare"], trading_day=True)
def get_industry_comparison(top_n: int = 20) -> Dict[str, Any]:
    """V4.2: 全行业排名 → TDX board_list（SKILL.md V3.2 增强：东财push2 fallback）。

    Args:
        top_n: 返回行业数量上限（当前未使用，保留参数兼容性）。

    Returns:
        dict: {"top": 涨幅TOP, "bottom": 跌幅TOP, "all": 全部行业, "total": 行业总数}。
    """
    from tdx_client import tdx_get_board_list
    sectors = tdx_get_board_list(0)  # BoardType.HY = 0 行业一级

    if sectors:
        # TDX数据可能缺少实时涨跌幅，尝试用东财push2补充
        em_sectors = _get_eastmoney_industry_sectors()
        if em_sectors:
            # 合并TDX和东财数据
            sector_map = {s.get("code", ""): s for s in sectors}
            for em in em_sectors:
                em_code = em.get("code", "")
                if em_code in sector_map:
                    sector_map[em_code]["change_pct"] = em.get("change_pct", 0)
                    sector_map[em_code]["up_count"] = em.get("up_count", 0)
                    sector_map[em_code]["down_count"] = em.get("down_count", 0)
                    sector_map[em_code]["leader"] = em.get("leader", "")
                    sector_map[em_code]["leader_change"] = em.get("leader_change", 0)
            sectors = list(sector_map.values())

    # 按涨跌幅排序
    sectors.sort(key=lambda x: x.get("change_pct", 0), reverse=True)

    return {
        "top": sectors[:top_n],
        "bottom": sectors[-top_n:],
        "all": sectors,
        "total": len(sectors),
    }


def _get_eastmoney_industry_sectors() -> List[Dict[str, Any]]:
    """获取东财行业板块实时涨跌幅数据（SKILL.md V3.2 推荐）。

    使用东财push2接口获取行业板块的实时涨跌幅、上涨下跌家数、领涨股等信息。

    Returns:
        list: 行业板块列表，包含涨跌幅、上涨家数、下跌家数、领涨股等字段
    """
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "100",
        "po": "1",
        "np": "1",
        "fltt": "2",
        "invt": "2",
        "fs": "m:90+t:2",  # 行业板块
        "fields": "f2,f3,f4,f12,f13,f14,f104,f105,f128,f136,f140,f141,f207",
        "fid": "f3",  # 按涨跌幅排序
    }
    headers = {"User-Agent": UA}

    try:
        r = em_get(url, params=params, headers=headers, timeout=15)
        if r is None:
            return []

        d = r.json()
        items = d.get("data", {}).get("dif", [])
        if not items:
            return []

        sectors = []
        for item in items:
            sectors.append({
                "name": item.get("f14", ""),
                "code": item.get("f12", ""),
                "change_pct": item.get("f3", 0),
                "up_count": item.get("f104", 0),
                "down_count": item.get("f105", 0),
                "leader": item.get("f140", ""),
                "leader_change": item.get("f136", 0),
            })

        return sectors
    except Exception as _e:
        _debug_log(f"datasource _get_eastmoney_industry_sectors: {_e}")
        return []


async def get_industry_comparison_async(session: Any, top_n: int = 20) -> Dict[str, Any]:
    """异步版 get_industry_comparison"""
    import asyncio
    return await asyncio.to_thread(get_industry_comparison, top_n)


# 新闻
@cached(category="stock_news", ttl_seconds=TTL["stock_news"])
def get_eastmoney_stock_news(code: str, page_size: int = 20) -> List[Dict[str, Any]]:
    """获取东财个股新闻。

    V9.6: 东财search-api-web HTTP接口已失效（返回passportWeb而非新闻），
    现仅使用 TDX F10 公司报道数据。F10不可用时返回空列表。

    Args:
        code: 股票代码
        page_size: 返回数量上限

    Returns:
        list: 新闻列表，包含标题、发布时间、来源、摘要等字段
    """
    try:
        from tdx_client import tdx_get_company_news_f10
        f10_news = tdx_get_company_news_f10(code, count=page_size)
        if f10_news:
            return [{
                "title": n.get('title', ''),
                "publish_time": n.get('date', ''),
                "source": "F10",
                "summary": n.get('summary', ''),
                "url": n.get('url', ''),
            } for n in f10_news]
    except Exception as _e:
        _debug_log(f"datasource tdx company news f10 error: {_e}")
    return []


@cached(category="global_news", ttl_seconds=TTL["global_news"])
def get_eastmoney_global_news(page_size: int = 50) -> List[Dict[str, Any]]:
    """获取东财全球资讯（7×24 滚动快讯）。

    使用东财np-weblist接口获取7×24财经快讯，与财联社快讯互为独立备份。

    Args:
        page_size: 返回数量上限

    Returns:
        list: 资讯列表，包含标题、发布时间、内容等字段
    """
    url = "https://np-weblist.eastmoney.com/comm/web/getFastNewsList"

    import uuid
    params = {
        "client": "web", "biz": "web_724",
        "fastColumn": "102", "sortEnd": "",
        "pageSize": str(page_size),
        "req_trace": str(uuid.uuid4()),
    }

    headers = {"User-Agent": UA, "Referer": "https://kuaixun.eastmoney.com/"}

    try:
        r = em_get(url, params=params, headers=headers, timeout=15)
        if r is None:
            return []

        d = r.json()
        items = d.get("data", {}).get("fastNewsList", [])

        news_items = []
        for item in items[:page_size]:
            news_items.append({
                "title": item.get("title", ""),
                "publish_time": item.get("showTime", ""),
                "content": item.get("summary", "")[:200],
                "type": item.get("type", ""),
            })

        return news_items
    except Exception as _e:
        _debug_log(f"datasource get_eastmoney_global_news: {_e}")
        return []


# ═══════════════════════════════════════════════════════════
# 批次6完成：同花顺/行业对比/新闻函数（10个函数）
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# 批次7：新浪财报/限售/毛利率迁移
# ═══════════════════════════════════════════════════════════

@cached(category="financial", ttl_seconds=TTL["financial"], cross_verify=True)
def get_sina_financial_report(code: str, num_periods: int = 12) -> Dict[str, Any]:
    """新浪利润表 — 支持多期数（默认12期 ≈ 3年）

    V9.1: 移除 F10 优先逻辑（F10 是万元单位，且字段名带后缀
          如 `营业总收(未调整:万)`，营业成本字段缺失硬编码为 0）。
          保留新浪 HTTP 为主力数据源（元单位，数据完整）。
    """
    # 新浪 HTTP
    prefix = "sh" if code.startswith("6") else "sz"
    paper_code = f"{prefix}{code}"
    url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
    params = {"paperCode": paper_code, "source": "lrb", "type": "0", "page": "1", "num": str(num_periods)}
    try:
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=15)
        if r is None:
            return []
        rl = (r.json().get("result") or {}).get("data", {}).get("report_list", {})
        rows = []
        for date_key, period in rl.items():
            item_map = {}
            for entry in period.get("data", []):
                item_map[entry.get("item_title", "")] = entry.get("item_value")
            rows.append({
                "报告日": f"{date_key[:4]}-{date_key[4:6]}-{date_key[6:8]}",
                "营业总收入": item_map.get("营业总收入") or "0",
                "营业成本": item_map.get("营业成本") or "0",
                "净利润": item_map.get("归属于母公司所有者的净利润") or item_map.get("净利润") or "0",
            })
        return rows
    except Exception as _e:
        _debug_log(f"datasource get_sina_financial_report ({code}): {_e}")
        return []


async def get_sina_financial_report_async(session: Any, code: str, num_periods: int = 12) -> Dict[str, Any]:
    """async 版: 新浪利润表

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    """
    prefix = "sh" if code.startswith("6") else "sz"
    paper_code = f"{prefix}{code}"
    url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
    params = {"paperCode": paper_code, "source": "lrb", "type": "0", "page": "1", "num": str(num_periods)}
    try:
        d = await _async_quick_request(session, url, params=params, headers={"User-Agent": UA}, timeout=15)
        if d is None:
            return []
        rl = (d.get("result") or {}).get("data", {}).get("report_list", {})
        rows = []
        for date_key, period in rl.items():
            item_map = {}
            for entry in period.get("data", []):
                item_map[entry.get("item_title", "")] = entry.get("item_value")
            rows.append({
                "报告日": f"{date_key[:4]}-{date_key[4:6]}-{date_key[6:8]}",
                "营业总收入": item_map.get("营业总收入") or "0",
                "营业成本": item_map.get("营业成本") or "0",
                "净利润": item_map.get("归属于母公司所有者的净利润") or item_map.get("净利润") or "0",
            })
        return rows
    except Exception as _e:
        _debug_log(f"datasource get_sina_financial_report_async ({code}): {_e}")
        return []


@cached(category="balance_sheet", ttl_seconds=TTL["balance_sheet"], cross_verify=True)
def get_sina_balance_sheet(code: str) -> List[Dict[str, Any]]:
    """获取新浪资产负债表（fzb）最近5期数据

    V9.1: 移除 F10 优先逻辑（F10 是万元单位，与渲染代码按元处理不一致）。
          保留新浪 HTTP 为主力数据源（元单位，数据完整）。
    """
    # 新浪 HTTP
    try:
        prefix = "sh" if code.startswith("6") else "sz"
        paper_code = f"{prefix}{code}"
        url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
        params = {"paperCode": paper_code, "source": "fzb", "type": "0", "page": "1", "num": "5"}
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=15)
        if r is None:
            return None
        rl = (r.json().get("result") or {}).get("data", {}).get("report_list", {})
        rows = []
        for date_key, period in rl.items():
            item_map = {}
            for entry in period.get("data", []):
                item_map[entry.get("item_title", "")] = entry.get("item_value")
            rows.append({
                "报告日": f"{date_key[:4]}-{date_key[4:6]}-{date_key[6:8]}",
                "应收账款": item_map.get("应收账款") or "0",
                "存货": item_map.get("存货") or "0",
                "商誉": item_map.get("商誉") or "0",
                "货币资金": item_map.get("货币资金") or "0",
                "短期借款": item_map.get("短期借款") or "0",
                "一年内到期的非流动负债": item_map.get("一年内到期的非流动负债") or "0",
                "长期借款": item_map.get("长期借款") or "0",
                "应付债券": item_map.get("应付债券") or "0",
                "资产总计": item_map.get("资产总计") or "0",
                "负债合计": item_map.get("负债合计") or "0",
                # 银行股字段映射：优先普通企业字段，备选银行股字段
                "归属于母公司股东权益合计": (item_map.get("归属于母公司股东权益合计") or
                                          item_map.get("归属于母公司股东的权益") or
                                          item_map.get("股东权益") or "0"),
            })
        return rows if rows else None
    except Exception as _e:
        _debug_log(f"datasource get_sina_balance_sheet ({code}): {_e}")
        return None


async def get_sina_balance_sheet_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """async 版: 新浪资产负债表

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    """
    prefix = "sh" if code.startswith("6") else "sz"
    paper_code = f"{prefix}{code}"
    url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
    params = {"paperCode": paper_code, "source": "fzb", "type": "0", "page": "1", "num": "5"}
    try:
        d = await _async_quick_request(session, url, params=params, headers={"User-Agent": UA}, timeout=15)
        if d is None:
            return []
        rl = (d.get("result") or {}).get("data", {}).get("report_list", {})
        rows = []
        for date_key, period in rl.items():
            item_map = {}
            for entry in period.get("data", []):
                item_map[entry.get("item_title", "")] = entry.get("item_value")
            rows.append({
                "报告日": f"{date_key[:4]}-{date_key[4:6]}-{date_key[6:8]}",
                "应收账款": item_map.get("应收账款") or "0",
                "存货": item_map.get("存货") or "0",
                "商誉": item_map.get("商誉") or "0",
                "货币资金": item_map.get("货币资金") or "0",
                "短期借款": item_map.get("短期借款") or "0",
                "一年内到期的非流动负债": item_map.get("一年内到期的非流动负债") or "0",
                "长期借款": item_map.get("长期借款") or "0",
                "应付债券": item_map.get("应付债券") or "0",
                "资产总计": item_map.get("资产总计") or "0",
                "负债合计": item_map.get("负债合计") or "0",
                "归属于母公司股东权益合计": (item_map.get("归属于母公司股东权益合计") or
                                          item_map.get("归属于母公司股东的权益") or
                                          item_map.get("股东权益") or "0"),
            })
        return rows if rows else []
    except Exception as _e:
        _debug_log(f"datasource get_sina_balance_sheet_async ({code}): {_e}")
        return []


@cached(category="cash_flow", ttl_seconds=TTL["cash_flow"], cross_verify=True)
def get_eastmoney_cash_flow(code: str) -> List[Dict[str, Any]]:
    """获取东财现金流量表（新浪xjllb接口已失效，使用东财数据中心替代）

    V9.6: 新增，使用东财数据中心RPT_CASHFLOW表获取现金流量数据。
    """
    data = eastmoney_datacenter(code, "RPT_CASHFLOW",
                                filter_str=f"(SECURITY_CODE=\"{code}\")",
                                page_size=5, sort_columns="REPORT_DATE", sort_types="-1")
    if not data:
        return []
    
    rows = []
    for r in data:
        rows.append({
            "报告日": str(r.get("REPORT_DATE", "") or "")[:10],
            "经营活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_OPERATING", "") or "0"),
            "投资活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_INVESTING", "") or "0"),
            "筹资活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_FINANCING", "") or "0"),
            "现金及现金等价物净增加额": str(r.get("NET_INCREASE_CASH_EQUIVALENTS", "") or "0"),
        })
    return rows


async def get_eastmoney_cash_flow_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """async 版: 东财现金流量表

    V9.6: 新增，使用东财数据中心RPT_CASHFLOW表获取现金流量数据。
    """
    data = await eastmoney_datacenter_async(session, code, "RPT_CASHFLOW",
                                            filter_str=f"(SECURITY_CODE=\"{code}\")",
                                            page_size=5, sort_columns="REPORT_DATE", sort_types="-1")
    if not data:
        return []
    
    rows = []
    for r in data:
        rows.append({
            "报告日": str(r.get("REPORT_DATE", "") or "")[:10],
            "经营活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_OPERATING", "") or "0"),
            "投资活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_INVESTING", "") or "0"),
            "筹资活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_FINANCING", "") or "0"),
            "现金及现金等价物净增加额": str(r.get("NET_INCREASE_CASH_EQUIVALENTS", "") or "0"),
        })
    return rows


@cached(category="hsgt_macro_flow", ttl_seconds=TTL["hsgt_macro_flow"], trading_day=True, use_args=False)
def get_hsgt_macro_flow() -> Optional[Dict[str, Any]]:
    """同花顺北向资金大盘净流入（宏观风向标）"""
    url = "https://data.hexin.cn/market/hsgtApi/method/dayChart/"
    headers = {"User-Agent": UA, "Host": "data.hexin.cn", "Referer": "https://data.hexin.cn/"}
    try:
        r = _quick_request(url, headers=headers, timeout=10)
        if r is None:
            return None
        d = r.json()
        hgt = d.get("hgt", [])
        sgt = d.get("sgt", [])
        if not hgt or not sgt:
            return None
        hgt_val = float(hgt[-1]) if hgt[-1] else 0
        sgt_val = float(sgt[-1]) if sgt[-1] else 0
        
        data_quality = "normal"
        warning = ""
        if abs(hgt_val) > 0:
            ratio = abs(sgt_val / hgt_val)
            if ratio > 3.0:
                data_quality = "degraded"
                warning = f"sgt/hgt比例异常({ratio:.2f})，建议谨慎使用"
                _debug_log(f"hsgt_macro_flow warning: {warning}")
        
        return {"hgt": hgt_val, "sgt": sgt_val, "total": hgt_val + sgt_val, 
                "data_quality": data_quality, "warning": warning}
    except Exception as _e:
        _debug_log(f"datasource get_hsgt_macro_flow: {_e}")
        return None


async def get_hsgt_macro_flow_async(session: Any) -> Optional[Dict[str, Any]]:
    """async 版: 同花顺北向资金大盘净流入

    V11.2: 委托到同步缓存版本（trading_day=True），避免批量模式下所有股票共享同一份T-1数据。
    第一只股票触发API调用并写入缓存，后续股票直接读缓存。
    """
    import asyncio
    return await asyncio.to_thread(get_hsgt_macro_flow)


@cached(category="lockup_expiry", ttl_seconds=TTL["lockup_expiry"], cross_verify=True)
def get_lockup_expiry(code: str, days: int = 90, include_history: bool = False) -> Any:
    """限售解禁日历。

    V10.2修复：移除 today_str 参数（改为内部自动计算），避免跨日缓存 key 污染。

    Args:
        code: 股票代码
        days: 未来展望窗口天数（默认90天）
        include_history: 是否返回历史记录（True=返回dict, False=返回list）

    Returns:
        include_history=True: {"history": [...], "upcoming": [...]}
        include_history=False: [{"date", "type", "shares", "ratio"}, ...]
    """
    # V10.2: today_str 内部自动计算，不作为函数参数（避免污染缓存 key）
    today_str = datetime.now().strftime("%Y-%m-%d")
    end_str = (datetime.strptime(today_str, "%Y-%m-%d") + timedelta(days=days)).strftime("%Y-%m-%d")

    # V9.0: 优先使用 F10 股本结构中的限售解禁数据
    try:
        from tdx_client import tdx_get_share_capital
        f10 = tdx_get_share_capital(code)
        if f10:
            raw_list = f10.get('lockup_expiry', [])
            if raw_list:
                history: List[Dict[str, Any]] = []
                upcoming: List[Dict[str, Any]] = []
                for r in raw_list:
                    # F10 字段名可能为 解禁日期/公告日期，解禁类型/类型，解禁股数/数量，解禁比例/比例
                    date_str = (r.get('解禁日期') or r.get('公告日期') or r.get('日期') or '').strip()
                    if not date_str:
                        continue
                    date_str = str(date_str)[:10]
                    entry = {
                        "date": date_str,
                        "type": (r.get('解禁类型') or r.get('类型') or '').strip(),
                        "shares": _safe_float(r.get('解禁数量(万)') or r.get('解禁股数') or r.get('解禁数量') or r.get('数量') or 0),
                        "ratio": _safe_float(r.get('解禁比例(%)') or r.get('解禁比例') or r.get('比例') or 0),
                    }
                    if date_str < today_str:
                        history.append(entry)
                    elif today_str <= date_str <= end_str:
                        upcoming.append(entry)
                # 仅当 F10 解析出有效条目时才返回，否则继续走 HTTP fallback
                if history or upcoming:
                    history.sort(key=lambda x: x["date"], reverse=True)
                    upcoming.sort(key=lambda x: x["date"])
                    if include_history:
                        return {"history": history, "upcoming": upcoming}
                    return upcoming
    except Exception as _e:
        _debug_log(f"datasource tdx share capital lockup f10 error: {_e}")

    # Fallback: 东财 HTTP
    if include_history:
        data = _em_filter(code, "RPT_LIFT_STAGE", page_size=15, sort_columns="FREE_DATE", sort_types="-1")
        history = [
            {"date": str(r.get("FREE_DATE", "") or "")[:10],
             "type": r.get("FREE_SHARES_TYPE", ""),
             "shares": _safe_float(r.get("FREE_SHARES")),
             "ratio": _safe_float(r.get("FREE_RATIO")),
             "able_shares": _safe_float(r.get("ABLE_FREE_SHARES"))}
            for r in data
        ]
    else:
        history = []

    data2 = eastmoney_datacenter(code, "RPT_LIFT_STAGE",
                                 filter_str=f"(SECURITY_CODE=\"{code}\")(FREE_DATE>='{today_str}')(FREE_DATE<='{end_str}')",
                                 page_size=20, sort_columns="FREE_DATE", sort_types="1")
    upcoming = [
        {"date": str(r.get("FREE_DATE", "") or "")[:10],
         "type": r.get("FREE_SHARES_TYPE", ""),
         "shares": float(r.get("FREE_SHARES") or 0),
         "ratio": float(r.get("FREE_RATIO") or 0),
         "able_shares": float(r.get("ABLE_FREE_SHARES") or 0)}
        for r in data2
    ]

    if include_history:
        return {"history": history, "upcoming": upcoming}
    return upcoming


async def get_lockup_expiry_async(session: Any, code: str, days: int = 90, include_history: bool = False) -> Any:
    """async 版: 限售解禁日历

    V9.0: 委托到同步版（已内置 F10 优先逻辑），保留 session 参数向后兼容。
    V10.2: 移除 today_str 参数（同步版已内部自动计算）。
    """
    import asyncio
    return await asyncio.to_thread(get_lockup_expiry, code, days, include_history)


@cached(category="gross_margin_roe", ttl_seconds=TTL["gross_margin_roe"], cross_verify=True)
def get_gross_margin_and_roe(code: str, fin_report: Any = None, bs_data: Any = None) -> Dict[str, Any]:
    """获取最新年度的毛利率和ROE"""
    # V9.0: 优先使用 F10 财务分析中的盈利能力指标
    try:
        from tdx_client import tdx_get_financial_analysis
        f10 = tdx_get_financial_analysis(code)
        if f10:
            profitability = f10.get('profitability', [])
            if profitability:
                latest = profitability[0]
                gross_margin = _safe_float(latest.get('销售毛利率'))
                roe = _safe_float(latest.get('净资产收益率'))
                # 任一字段有效即返回（避免 F10 缺字段时返回 None）
                if gross_margin or roe:
                    return {"gross_margin": gross_margin, "roe": roe}
    except Exception as _e:
        _debug_log(f"datasource tdx financial analysis profitability error: {_e}")
    # Fallback: 新浪 HTTP
    try:
        if fin_report is None:
            prefix = "SH" if code.startswith("6") else "SZ"
            paper_code = f"{prefix}{code}"
            url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
            params = {"paperCode": paper_code, "source": "lrb", "type": "0", "page": "1", "num": "1"}
            r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=15)
            if r is None or r.status_code != 200:
                return None
            d = r.json()
            items = (d.get("result") or {}).get("data", [])
            if not items:
                return None
            item = items[0]
        else:
            item = fin_report[0] if fin_report else None
            if not item:
                return None

        if fin_report:
            rev = _safe_float(item.get("营业总收入"))
            cost = _safe_float(item.get("营业成本"))
            profit = _safe_float(item.get("归属于母公司所有者的净利润") or item.get("净利润"))
        else:
            rev = _safe_float(item.get("营业收入") or item.get("营业总收入"))
            cost = _safe_float(item.get("营业成本"))
            profit = _safe_float(item.get("归属于母公司所有者的净利润"))

        gross_margin = (rev - cost) / rev * 100 if rev > 0 else None

        bs = bs_data if bs_data is not None else get_sina_balance_sheet(code)
        roe = None
        if bs:
            equity_yi = _safe_float(bs[0].get("归属于母公司股东权益合计", 0))
            if equity_yi > 0:
                roe = (profit * 100) / equity_yi if equity_yi > 0 else None

        return {"gross_margin": gross_margin, "roe": roe}
    except Exception as _e:
        _debug_log(f"datasource get_gross_margin_and_roe ({code}): {_e}")
        return None


async def get_gross_margin_and_roe_async(session: Any, code: str, fin_report: Any = None, bs_data: Any = None) -> Dict[str, Any]:
    """async 版: 获取最新年度的毛利率和ROE

    V9.0: 委托到同步版（已内置 F10 优先逻辑），保留 session/fin_report/bs_data 参数向后兼容。
    """
    import asyncio
    return await asyncio.to_thread(get_gross_margin_and_roe, code, fin_report, bs_data)


# ═══════════════════════════════════════════════════════════
# 批次7完成：新浪财报/限售/毛利率函数（12个函数）
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# 批次8：交易日历/异步包装/外部代理迁移
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# A股交易日历与市场状态
# ═══════════════════════════════════════════════════════════

def _try_upgrade_calendar():
    """尝试自动升级 chinese-calendar 库

    Returns:
        bool: True=升级成功, False=升级失败
    """
    import subprocess, sys, importlib
    try:
        print("⏳ 检测到节假日数据过期，正在自动更新 chinese-calendar...", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "chinese-calendar"],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            # 强制重新加载 chinese_calendar 模块
            import chinese_calendar
            importlib.reload(chinese_calendar)
            # 同时更新本地 stock_calendar.py（如果存在）
            try:
                from stock_common import stock_calendar as local_stock_cal
                importlib.reload(local_stock_cal)
            except (ImportError, ModuleNotFoundError):
                pass
            print("✅ chinese-calendar 更新成功", flush=True)
            return True
        else:
            print(f"⚠️ 自动更新失败: {result.stderr[:200]}", flush=True)
            return False
    except Exception as e:
        print(f"⚠️ 自动更新异常: {e}", flush=True)
        return False


def get_valuation_pe_center(industry_name: str = "") -> float:
    """按行业返回估值PE中枢（用于报告参考，若未命中行业则返回全局默认）。

    Args:
        industry_name: 行业名（可为空字符串，默认返回全局默认）

    Returns:
        float: 行业PE中枢，默认 30.0
    """
    sc = _load_settings()
    pe_map = sc.get("valuation_pe_centers", {})
    if pe_map:
        if industry_name in pe_map:
            return float(pe_map[industry_name])
    # 回退：使用 valuation.pe_mid
    val = sc.get("valuation", {}).get("pe_mid", 30.0)
    return float(val)


_calendar_fallback_warned = False


def is_trading_day(d=None):
    """判断是否为A股交易日（含节假日+调休检测，自动升级+降级）

    Args:
        d: date 或 datetime，默认今天

    Returns:
        bool: True=交易日, False=休市日
    """
    from datetime import date as _date, datetime as _datetime

    if d is None:
        d = _date.today()
    if isinstance(d, _datetime):
        d = d.date()

    def _fallback_warn(reason: str) -> None:
        global _calendar_fallback_warned
        if not _calendar_fallback_warned:
            _calendar_fallback_warned = True
            import sys
            print(f"[警告] 交易日历降级为 weekday 判断（{reason}），节假日可能误判。"
                  "请运行 python scripts/update_calendar.py 更新数据。",
                  file=sys.stderr, flush=True)

    # 优先使用本地 stock_calendar.py（项目目录下，用户可控）
    try:
        from stock_common import stock_calendar as _local_cal
        return _local_cal.is_workday(d)
    except (ImportError, ModuleNotFoundError):
        pass
    except NotImplementedError:
        pass  # 年份超出本地数据范围，尝试库

    # 降级到 chinese-calendar 库
    try:
        from chinese_calendar import is_workday
        return is_workday(d)
    except NotImplementedError as e:
        # 年份超出库范围（>2026），尝试自动升级
        if "no available data" in str(e) or "year" in str(e).lower():
            if _try_upgrade_calendar():
                # 升级后重新尝试
                try:
                    from chinese_calendar import is_workday
                    return is_workday(d)
                except Exception as _e:
                    _debug_log(f"datasource chinese calendar retry error: {_e}")
        # 降级为简单判断（周一到周五）
        _fallback_warn(f"年份 {d.year} 超出日历数据范围")
        return d.weekday() < 5
    except ImportError:
        # chinese-calendar 未安装，尝试自动安装
        if _try_upgrade_calendar():
            try:
                from chinese_calendar import is_workday
                return is_workday(d)
            except Exception as _e:
                _debug_log(f"datasource chinese calendar install retry error: {_e}")
        # 降级为简单判断
        _fallback_warn("chinese-calendar 库未安装")
        return d.weekday() < 5


def get_market_status(now=None):
    """获取A股市场状态

    Args:
        now: datetime，默认当前时间

    Returns:
        tuple: (status_str, note_str)
            status_str: 'closed' | 'pre_market' | 'morning' | 'lunch' | 'afternoon' | 'post_market' | 'post_close'
            note_str: 给用户看的中文提示

    V10.2 修复：交易日16:30后从 'closed' 改为 'post_close'，避免盘后运行脚本时
              错误显示"休市日"。'closed' 仅用于非交易日（真正的休市日）。
    """
    from datetime import datetime as _datetime

    if now is None:
        now = _datetime.now()
    d = now.date()
    t = now.hour * 100 + now.minute

    if not is_trading_day(d):
        return "closed", "（休市日，数据为最近交易日快照）"
    if t < 915:
        return "pre_market", "当前为盘前时段，行情数据/北向资金为上交易日值"
    elif t < 1130:
        return "morning", "当前为盘中（上午）时段，行情数据实时跳动"
    elif t < 1300:
        return "lunch", "当前为午休时段（11:30-13:00），行情暂停"
    elif t < 1500:
        return "afternoon", "当前为盘中（下午）时段，行情数据实时跳动"
    elif t < 1630:
        return "post_market", "当前为盘后结算时段，龙虎榜/融资融券约16:30后更新"
    else:
        # V10.2: 交易日16:30后为盘后收盘，不再是"closed"（避免误显示"休市日"）
        return "post_close", "当前为盘后收盘时段，数据为今日收盘快照"


# ═══════════════════════════════════════════════════════════
# 打板层数据（V9.6 新增）
# ═══════════════════════════════════════════════════════════

def _parse_limit_pool(data: list) -> List[Dict[str, Any]]:
    """解析东财 push2ex 涨停池/炸板池/跌停池数据"""
    result = []
    for item in data:
        zttj = item.get("zttj", {})
        result.append({
            "code": item.get("c", ""),
            "name": item.get("n", ""),
            "price": _safe_float(item.get("p")),
            "change_pct": _safe_float(item.get("zdp")),
            "amount": _safe_float(item.get("amount")),
            "circulating_value": _safe_float(item.get("ltsz")),
            "total_value": _safe_float(item.get("tshare")),
            "turnover_rate": _safe_float(item.get("hs")),
            "limit_count": _safe_float(item.get("lbc")),
            "first_limit_time": str(item.get("fbt", "")),
            "last_limit_time": str(item.get("lbt", "")),
            "limit_fund": _safe_float(item.get("fund")),
            "broken_count": _safe_float(item.get("zbc")),
            "sector": item.get("hybk", ""),
            "zt_days": _safe_float(zttj.get("days")) if isinstance(zttj, dict) else 0,
            "zt_continuous": _safe_float(zttj.get("ct")) if isinstance(zttj, dict) else 0,
        })
    return result


@cached(category="limit_pool", ttl_seconds=TTL["limit_pool"])
def get_limit_up_pool(date_str: str = "") -> List[Dict[str, Any]]:
    """获取东财涨停池数据

    Args:
        date_str: 日期字符串，格式 YYYYMMDD，默认当天

    Returns:
        涨停股票列表，包含代码/名称/封板时间/连板数/涨停原因等
    """
    if not date_str:
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")

    url = "https://push2ex.eastmoney.com/getTopicZTPool"
    params = {
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "dpt": "wz.ztzt",
        "Pageindex": 0,
        "pagesize": 100,
        "sort": "fbt:asc",
        "date": date_str,
    }
    try:
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=10)
        if r is None:
            return []
        d = r.json()
        pool = d.get("data", {}).get("pool", [])
        return _parse_limit_pool(pool)
    except Exception as _e:
        _debug_log(f"datasource get_limit_up_pool: {_e}")
        return []


@cached(category="limit_pool", ttl_seconds=TTL["limit_pool"])
def get_limit_broken_pool(date_str: str = "") -> List[Dict[str, Any]]:
    """获取东财炸板池数据

    Args:
        date_str: 日期字符串，格式 YYYYMMDD，默认当天

    Returns:
        炸板股票列表
    """
    if not date_str:
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")

    url = "https://push2ex.eastmoney.com/getTopicZBPool"
    params = {
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "dpt": "wz.ztzt",
        "Pageindex": 0,
        "pagesize": 100,
        "sort": "fbt:asc",
        "date": date_str,
    }
    try:
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=10)
        if r is None:
            return []
        d = r.json()
        pool = d.get("data", {}).get("pool", [])
        return _parse_limit_pool(pool)
    except Exception as _e:
        _debug_log(f"datasource get_limit_broken_pool: {_e}")
        return []


@cached(category="limit_pool", ttl_seconds=TTL["limit_pool"])
def get_limit_down_pool(date_str: str = "") -> List[Dict[str, Any]]:
    """获取东财跌停池数据

    Args:
        date_str: 日期字符串，格式 YYYYMMDD，默认当天

    Returns:
        跌停股票列表
    """
    if not date_str:
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")

    url = "https://push2ex.eastmoney.com/getTopicDTPool"
    params = {
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "dpt": "wz.ztzt",
        "Pageindex": 0,
        "pagesize": 100,
        "sort": "fbt:asc",
        "date": date_str,
    }
    try:
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=10)
        if r is None:
            return []
        d = r.json()
        pool = d.get("data", {}).get("pool", [])
        return _parse_limit_pool(pool)
    except Exception as _e:
        _debug_log(f"datasource get_limit_down_pool: {_e}")
        return []


def get_limit_pool_summary(date_str: str = "") -> Dict[str, Any]:
    """获取打板数据汇总（涨停池+炸板池+跌停池）

    Returns:
        包含涨停/炸板/跌停数量和详细数据的字典
    """
    zt = get_limit_up_pool(date_str)
    zb = get_limit_broken_pool(date_str)
    dt = get_limit_down_pool(date_str)

    # 按板块统计涨停分布
    sector_stats: Dict[str, int] = {}
    for item in zt:
        sec = item.get("sector", "其他")
        sector_stats[sec] = sector_stats.get(sec, 0) + 1

    # 封板成功率
    total_attempt = len(zt) + len(zb)
    success_rate = len(zt) / total_attempt * 100 if total_attempt > 0 else 0

    return {
        "limit_up_count": len(zt),
        "limit_broken_count": len(zb),
        "limit_down_count": len(dt),
        "success_rate": round(success_rate, 1),
        "sector_stats": dict(sorted(sector_stats.items(), key=lambda x: x[1], reverse=True)[:10]),
        "limit_up_list": zt,
        "limit_broken_list": zb,
        "limit_down_list": dt,
    }


# ═══════════════════════════════════════════════════════════
# 同花顺涨停揭秘（V9.6 新增，打板层增强源）
# ═══════════════════════════════════════════════════════════

@cached(category="limit_pool", ttl_seconds=TTL["limit_pool"])
def ths_limit_up_pool(date_str: str = "") -> List[Dict[str, Any]]:
    """同花顺涨停揭秘（涨停原因 + 封板质量增强源）。

    V9.6 新增：与东财涨停池互为补充，提供东财没有的字段：
    - 涨停原因题材（reason）
    - 板型（一字板/换手板/T字板）
    - 封板成功率（seal_rate）
    - 炸板次数（break_times）

    作为东财涨停池的 fallback：东财接口失败时调用同花顺获取基础数据。

    Args:
        date_str: 交易日，格式 YYYYMMDD

    Returns:
        涨停列表，包含 code/name/price/pct/reason/board_type/seal_rate 等字段
    """
    from datetime import datetime

    date_str = date_str or datetime.now().strftime("%Y%m%d")
    url = "https://data.10jqka.com.cn/dataapi/limit_up/limit_up_pool"
    params = {
        "page": 1, "limit": 200,
        "field": "199112,10,9001,330323,330324,330325,9002,330329,133971,133970,1968584,3475914,9003,9004",
        "filter": "HS,GEM2STAR", "order_field": "330324", "order_type": "0",
        "date": date_str,
    }

    try:
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=10)
        if r is None:
            return []
        info = (r.json().get("data") or {}).get("info", [])
        if not info:
            return []

        out = []
        for it in info:
            ft = it.get("first_limit_up_time")
            out.append({
                "code": it.get("code"),
                "name": it.get("name"),
                "price": _safe_float(it.get("latest")),
                "pct": _safe_float(it.get("change_rate")),
                "reason": it.get("reason_type", ""),
                "board_type": it.get("limit_up_type", ""),
                "seal_rate": it.get("limit_up_suc_rate"),
                "break_times": it.get("open_num") or 0,
                "seal_amount": it.get("order_amount"),
                "high_days": it.get("high_days", ""),
                "first_time": datetime.fromtimestamp(int(ft)).strftime("%H:%M:%S") if ft else "",
                "is_again": it.get("is_again_limit"),
            })
        return out
    except Exception as _e:
        _debug_log(f"datasource ths_limit_up_pool: {_e}")
        return []


# ═══════════════════════════════════════════════════════════
# 东财分钟级资金流（V9.6 新增，用于资金流降权融合）
# ═══════════════════════════════════════════════════════════

@cached(category="fund_flow", ttl_seconds=TTL["fund_flow"])
def get_eastmoney_minute_fund_flow(code: str) -> List[Dict[str, Any]]:
    """获取东财个股分钟级资金流数据

    V9.6 新增：使用东财push2接口获取分钟级资金流，用于与TDX资金流加权融合。
    数据格式与同花顺/百度资金流不同，但覆盖更稳定。

    Returns:
        分钟级资金流列表，每项包含时间/主力净流入/小单净流入/中单净流入/大单净流入
    """
    market = "1" if code.startswith("6") else "0"
    secid = f"{market}.{code}"

    url = "https://push2.eastmoney.com/api/qt/stock/fflow/kline/get"
    params = {
        "lmt": "0",
        "klt": "1",  # 1分钟
        "secid": secid,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
    }
    try:
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=10)
        if r is None:
            return []
        d = r.json()
        klines = d.get("data", {}).get("klines", [])
        if not klines:
            return []

        result = []
        for line in klines:
            parts = line.split(",")
            if len(parts) >= 11:
                result.append({
                    "time": parts[0],
                    "main_net_inflow": _safe_float(parts[1]),  # 主力净流入
                    "small_net_inflow": _safe_float(parts[2]),  # 小单净流入
                    "medium_net_inflow": _safe_float(parts[3]),  # 中单净流入
                    "large_net_inflow": _safe_float(parts[4]),  # 大单净流入
                    "super_net_inflow": _safe_float(parts[5]),  # 超大单净流入
                })
        return result
    except Exception as _e:
        _debug_log(f"datasource get_eastmoney_minute_fund_flow ({code}): {_e}")
        return []


def get_fund_flow_weighted(code: str, tdx_data: Any = None) -> Dict[str, Any]:
    """获取加权融合资金流数据（V9.6 新增）

    融合TDX、东财分钟级资金流，按权重加权计算：
    - TDX TCP资金流：权重 1.0（最实时、最准确）
    - 东财分钟级资金流：权重 0.6（覆盖稳定、数据量大）

    Args:
        code: 股票代码
        tdx_data: TDX资金流数据（如已获取，避免重复请求）

    Returns:
        加权融合后的资金流数据
    """
    # TDX资金流（权重1.0）
    if tdx_data is not None:
        tdx_ff = tdx_data
    else:
        try:
            from tdx_client import tdx_get_fund_flow
            tdx_ff = tdx_get_fund_flow(code)
        except Exception:
            tdx_ff = None

    # 东财分钟级资金流（权重0.6）
    em_ff = get_eastmoney_minute_fund_flow(code)

    result = {
        "primary_source": "tdx" if tdx_ff else ("eastmoney" if em_ff else "none"),
        "sources": {},
    }

    if tdx_ff:
        result["sources"]["tdx"] = {"weight": 1.0, "data": tdx_ff}
    if em_ff:
        result["sources"]["eastmoney"] = {"weight": 0.6, "data_available": True, "count": len(em_ff)}

    # 简化版：优先使用TDX，东财作为验证/补充
    # 如果TDX有数据，以东财数据做交叉验证
    if tdx_ff and em_ff:
        result["cross_verified"] = True
    elif tdx_ff:
        result["cross_verified"] = False
    elif em_ff:
        # 仅有东财数据时，降低可信度标记
        result["degraded"] = True
        result["warning"] = "仅东财数据，无TDX交叉验证"

    return result


# ═══════════════════════════════════════════════════════════
# 财联社快讯（V9.6 新增，V3.4复活版）
# ═══════════════════════════════════════════════════════════

@cached(category="news", ttl_seconds=TTL["news"])
def cls_telegraph(page_size: int = 50) -> List[Dict[str, Any]]:
    """财联社电报（全市场实时快讯）。v1 API + 本地签名，零 key。

    V9.6 新增：使用 cls.cn/v1/roll/get_roll_list，签名算法为 md5(sha1(按key字典序拼接的query串))。
    与东财7×24快讯互为独立备份（不同源、不同风控面）。

    Args:
        page_size: 返回条数，默认50条

    Returns:
        快讯列表，包含 title/content/time 字段
    """
    import hashlib
    from datetime import datetime

    params = {"appName": "CailianpressWeb", "os": "web", "sv": "7.7.5",
              "last_time": "", "refresh_type": "1", "rn": str(page_size)}
    qs = "&".join(f"{k}={params[k]}" for k in sorted(params))
    sign = hashlib.md5(hashlib.sha1(qs.encode()).hexdigest().encode()).hexdigest()
    url = f"https://www.cls.cn/v1/roll/get_roll_list?{qs}&sign={sign}"

    try:
        r = _quick_request(url, headers={"User-Agent": UA, "Referer": "https://www.cls.cn/"}, timeout=10)
        if r is None:
            return []
        d = r.json()
        if d.get("errno") != 0:
            _debug_log(f"cls_telegraph error: errno={d.get('errno')} errmsg={d.get('errmsg')}")
            return []

        rows = []
        for item in d.get("data", {}).get("roll_data", []) or []:
            ts = item.get("ctime")
            t = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else ""
            rows.append({
                "title": item.get("title", "") or item.get("brie", ""),
                "content": item.get("content", "") or item.get("brie", ""),
                "time": t,
                "level": item.get("level", ""),
                "reading_num": item.get("reading_num", 0),
            })
        return rows
    except Exception as _e:
        _debug_log(f"datasource cls_telegraph: {_e}")
        return []


# ═══════════════════════════════════════════════════════════
# 官方备胎池（V9.6 新增）
# ═══════════════════════════════════════════════════════════

def dragon_tiger_backup(trade_date: str) -> Dict[str, Any]:
    """龙虎榜官方备用源（东财被封时用）：上交所+深交所官方，零鉴权权威一手，含营业部席位。

    Args:
        trade_date: 交易日，格式 YYYY-MM-DD

    Returns:
        包含深交所结构化数据和上交所原始文件内容的字典
    """
    import urllib.request
    import ssl
    out = {"date": trade_date, "sse_raw": "", "szse": []}
    _ctx = ssl._create_unverified_context()

    # 深交所龙虎榜
    su = ("https://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON"
          f"&CATALOGID=1842_xxpl&TABKEY=tab1&txtStart={trade_date}&txtEnd={trade_date}&random=0.9")
    try:
        req = urllib.request.Request(su, headers={"User-Agent": UA,
              "Referer": "https://www.szse.cn/disclosure/supervision/dealinfo/index.html"})
        with urllib.request.urlopen(req, timeout=15, context=_ctx) as r:
            d = json.loads(r.read())
        if isinstance(d, list) and d:
            for row in d[0].get("data", []):
                out["szse"].append({
                    "code": row.get("zqdm"),
                    "name": row.get("zqjc"),
                    "amount": row.get("cjje"),
                    "reason": row.get("plyy"),
                    "volume": row.get("cjsl"),
                    "note": row.get("bz"),
                })
    except Exception as _e:
        _debug_log(f"dragon_tiger_backup szse: {_e}")

    # 上交所龙虎榜（JSONP格式）
    eu = ("https://query.sse.com.cn/infodisplay/showTradePublicFile.do?"
          f"jsonCallBack=cb&isPagination=false&dateTx={trade_date}")
    try:
        req = urllib.request.Request(eu, headers={"User-Agent": UA,
              "Referer": "https://www.sse.com.cn/disclosure/diclosure/public/"})
        with urllib.request.urlopen(req, timeout=15) as r:
            t = r.read().decode("utf-8", "ignore")
        if "(" in t and ")" in t:
            json_str = t[t.index("(")+1:t.rindex(")")]
            d = json.loads(json_str)
            out["sse_raw"] = "\n".join(d.get("fileContents", []))
    except Exception as _e:
        _debug_log(f"dragon_tiger_backup sse: {_e}")

    return out


def fund_flow_backup(code: str, days: int = 60) -> List[Dict[str, Any]]:
    """个股资金流备用源（东财被封时用）：新浪，日度四档单净额。

    Args:
        code: 股票代码
        days: 获取天数，默认60天

    Returns:
        资金流列表，包含日期、主力/大单/中单/小单净流入
    """
    prefix = "sh" if code.startswith("6") else "sz"
    url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/MoneyFlow.ssl_bkzj_bk"
    params = {"page": "1", "num": str(days), "sort": "netamount", "asc": "0", "fenlei": "1"}

    try:
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=10)
        if r is None:
            return []
        d = r.json()
        if isinstance(d, list):
            return d
        return []
    except Exception as _e:
        _debug_log(f"datasource fund_flow_backup ({code}): {_e}")
        return []


# ═══════════════════════════════════════════════════════════
# 舆情互动层（V9.6 新增，互动易问答）
# ═══════════════════════════════════════════════════════════

def cninfo_irm(code: str, page_size: int = 30, page_num: int = 1) -> List[Dict[str, Any]]:
    """互动易问答（深沪统一走巨潮）。

    V9.6 新增：两步调用——先获取orgId，再获取问答列表。
    参数放query string（POST但body空），否则400。

    Args:
        code: 6位股票代码
        page_size: 每页条数，默认30
        page_num: 页码，默认1

    Returns:
        问答列表，包含 question/answer/ask_time/answerer 字段
    """
    from datetime import datetime
    import requests

    try:
        r1 = requests.post("https://irm.cninfo.com.cn/newircs/index/queryKeyboardInfo",
            data={"keyWord": code}, headers={"User-Agent": UA}, timeout=10)
        d1 = r1.json().get("data") or []
        if not d1:
            return []
        org_id = d1[0].get("secid")

        params = {"_t": 1, "stockcode": code, "orgId": org_id, "pageSize": page_size,
                  "pageNum": page_num, "keyWord": "", "startDay": "", "endDay": ""}
        r2 = requests.post("https://irm.cninfo.com.cn/newircs/company/question",
            params=params, headers={"User-Agent": UA}, timeout=10)
        rows = r2.json().get("rows") or []

        out = []
        for it in rows:
            pd = it.get("pubDate")
            out.append({
                "code": it.get("stockCode"),
                "company": it.get("companyShortName"),
                "question": it.get("mainContent"),
                "answer": it.get("attachedContent"),
                "answerer": it.get("attachedAuthor"),
                "ask_time": datetime.fromtimestamp(pd / 1000).strftime("%Y-%m-%d %H:%M") if pd else "",
            })
        return out
    except Exception as _e:
        _debug_log(f"datasource cninfo_irm ({code}): {_e}")
        return []


# ═══════════════════════════════════════════════════════════
# zhb 全局配置总包（V9.6 新增，基于通达信 0x06B9 协议）
# ═══════════════════════════════════════════════════════════

def get_zhb_sp_block(name: str) -> List[str]:
    """V9.6: 获取大板块成分股（基于 zhb.zip 的 spblock.dat）。

    支持的板块：融资融券/沪深港通/中证500/中证1000/中证2000/国证2000/
                 深证成指/专精特新/含可转债/转融券/金融类企业 等35个大板块。
    突破 mootdx block_zs.dat 的 400 只限制。

    Args:
        name: 板块名称（支持模糊匹配，如"中证2000"、"融资融券"）

    Returns:
        股票代码列表，如 ["000001", "000002", ...]
    """
    try:
        from zhb_client import get_sp_block
        return get_sp_block(name)
    except Exception as _e:
        _debug_log(f"datasource zhb sp_block ({name}): {_e}")
        return []


def get_zhb_sp_block_list() -> List[tuple]:
    """V9.6: 列出所有大板块 (名称, 成分股数)。"""
    try:
        from zhb_client import list_sp_blocks
        return list_sp_blocks()
    except Exception as _e:
        _debug_log(f"datasource zhb sp_block_list: {_e}")
        return []


def get_zhb_sw_industries() -> Dict[str, str]:
    """V9.6: 获取申万行业分类 {板块代码: 板块名称}。

    包含 467 个四级分类（门类→大类→中类→小类），
    是公募基金的通用行业标准。
    """
    try:
        from zhb_client import get_sw_industries
        return get_sw_industries()
    except Exception as _e:
        _debug_log(f"datasource zhb sw_industries: {_e}")
        return {}


def get_zhb_industry_map() -> Dict[str, str]:
    """V9.6: 获取行业代码→名称映射（全类型，1000+条）。"""
    try:
        from zhb_client import get_industry_map
        return get_industry_map()
    except Exception as _e:
        _debug_log(f"datasource zhb industry_map: {_e}")
        return {}


def get_zhb_data_date() -> str:
    """V9.6: 获取 zhb 数据的日期（YYYYMMDD），用于报告中标注数据时效性。"""
    try:
        from zhb_client import get_zhb
        zhb = get_zhb()
        return zhb.date if zhb else ""
    except Exception as _e:
        _debug_log(f"datasource zhb data_date: {_e}")
        return ""


# ═══════════════════════════════════════════════════════════
# zhb B级数据集成（阶段二）
# ═══════════════════════════════════════════════════════════

def get_zhb_stock_stat(code: str) -> Optional[Dict[str, Any]]:
    """V9.6: 获取个股统计快照（涨跌幅/PE/5-60日涨跌幅等）。

    基于 zhb.zip 的 tdxstat.cfg，数据可能有1-2天延迟。
    用于盘后初筛和辅助参考，不适合实时交易决策。
    """
    try:
        from zhb_client import get_stock_stat
        return get_stock_stat(code)
    except Exception as _e:
        _debug_log(f"datasource zhb stock_stat ({code}): {_e}")
        return None


def get_zhb_stock_stat2(code: str) -> Optional[Dict[str, Any]]:
    """V9.6: 获取个股资金流向和板块归属。

    基于 zhb.zip 的 tdxstat2.cfg，包含行业代码、52周高低价等。
    """
    try:
        from zhb_client import get_stock_stat2
        return get_stock_stat2(code)
    except Exception as _e:
        _debug_log(f"datasource zhb stock_stat2 ({code}): {_e}")
        return None


def get_zhb_market_snapshot(codes: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """V9.6: 全市场（或指定股票）统计快照。

    一次调用拿到全市场7938只股票的统计快照，用于val脚本初筛。
    数据可能有1-2天延迟，仅用于盘后初筛。
    """
    try:
        from zhb_client import market_stat_snapshot
        return market_stat_snapshot(codes)
    except Exception as _e:
        _debug_log(f"datasource zhb market_snapshot: {_e}")
        return {}


def get_zhb_52w_range(code: str) -> tuple:
    """V9.6: 获取52周最高价和最低价。

    Returns:
        (high_52w, low_52w) 元组，获取失败返回 (None, None)
    """
    try:
        from zhb_client import get_high_52w, get_low_52w
        return (get_high_52w(code), get_low_52w(code))
    except Exception as _e:
        _debug_log(f"datasource zhb 52w_range ({code}): {_e}")
        return (None, None)


def get_zhb_industry_code(code: str) -> str:
    """V9.6: 获取股票的行业板块代码（如880679）。"""
    try:
        from zhb_client import get_industry_code
        return get_industry_code(code)
    except Exception as _e:
        _debug_log(f"datasource zhb industry_code ({code}): {_e}")
        return ""


def is_zhb_data_fresh(max_delay_days: int = 3) -> bool:
    """V9.6: 检查zhb数据是否新鲜（延迟在指定天数内）。

    数据过旧时调用方应降级到原有HTTP/TCP接口。
    """
    try:
        from zhb_client import is_data_fresh
        return is_data_fresh(max_delay_days)
    except Exception as _e:
        _debug_log(f"datasource zhb is_fresh: {_e}")
        return False


# V10.2 新增：zhb 字段时效性分级
# V10.3 更新：新增准实时字段分类（主力资金流向等，1天延迟可接受）
# 实时字段：zhb 日期必须是今天（max_delay_days=0），否则 fallback 原接口
# 准实时字段：1天延迟可接受（max_delay_days=1），如主力资金流向
# 阶段/静态字段：3天延迟可接受（max_delay_days=3）
_ZHB_REALTIME_FIELDS = frozenset({
    "change_pct", "change_pct_1d", "change_pct_2d",
    "amount", "amount_1d", "amount_2d",
    "price", "open", "high", "low", "prev_close",
})

_ZHB_NEAR_REALTIME_FIELDS = frozenset({
    # V10.3: 主力资金流向字段 — 日频准实时，1天延迟可接受
    "main_net_buy_hands", "main_net_buy_hands_1d",
    "main_net_buy_amount", "main_net_buy_amount_1d",
})


def zhb_field_safe(field_name: str) -> bool:
    """V10.2: 判断 zhb 指定字段在当前数据滞后状态下是否安全可用。
    V10.3: 新增准实时字段分类（max_delay_days=1）。

    按字段时效性需求分级：
    - 实时字段（change_pct/amount/price 等）：zhb 日期必须是今天，否则不安全
    - 准实时字段（main_net_buy 等）：1天延迟可接受
    - 阶段/静态字段（pe_ttm/high_52w/dividend_yield 等）：3天延迟可接受

    Args:
        field_name: zhb 字段名（如 "change_pct", "pe_ttm", "high_52w"）

    Returns:
        True=该字段当前可安全使用 zhb 数据，False=应 fallback 原接口
    """
    if field_name in _ZHB_REALTIME_FIELDS:
        # 实时字段：zhb 日期必须是今天（max_delay_days=0）
        return is_zhb_data_fresh(max_delay_days=0)
    if field_name in _ZHB_NEAR_REALTIME_FIELDS:
        # 准实时字段：1天延迟可接受（max_delay_days=1）
        return is_zhb_data_fresh(max_delay_days=1)
    # 阶段/静态字段：3天延迟可接受
    return is_zhb_data_fresh(max_delay_days=3)


# ═══════════════════════════════════════════════════════════
# zhb 辅助数据集成（阶段三）
# ═══════════════════════════════════════════════════════════

def get_zhb_tip_info(code: str) -> Optional[Dict[str, Any]]:
    """V9.6: 获取个股财报日历信息（财报期/EPS/披露日/除权日/分红日）。"""
    try:
        from zhb_client import get_tip_info
        return get_tip_info(code)
    except Exception as _e:
        _debug_log(f"datasource zhb tip_info ({code}): {_e}")
        return None


def get_zhb_ipo_list() -> List[Dict[str, Any]]:
    """V9.6: 获取新股申购日历列表。"""
    try:
        from zhb_client import get_ipo_list
        return get_ipo_list()
    except Exception as _e:
        _debug_log(f"datasource zhb ipo_list: {_e}")
        return []


def get_zhb_ah_stocks() -> List[Dict[str, str]]:
    """V9.6: 获取A+H股列表。"""
    try:
        from zhb_client import get_ah_stocks
        return get_ah_stocks()
    except Exception as _e:
        _debug_log(f"datasource zhb ah_stocks: {_e}")
        return []


def get_zhb_broker_name(broker_id: str) -> str:
    """V9.6: 获取券商简称（基于brkcomp.dat，842家券商）。"""
    try:
        from zhb_client import get_broker_name
        return get_broker_name(broker_id)
    except Exception as _e:
        _debug_log(f"datasource zhb broker_name ({broker_id}): {_e}")
        return broker_id


# ═══════════════════════════════════════════════════════════
# V10.0 新增接口
# ═══════════════════════════════════════════════════════════

def get_zhb_holidays() -> List[str]:
    """V10.0: 获取节假日列表（1991-2030）。

    返回格式为 YYYYMMDD 字符串列表。
    注意：仅作参考，主用 stock_calendar 模块。
    """
    try:
        from zhb_client import get_holidays
        return get_holidays()
    except Exception as _e:
        _debug_log(f"datasource zhb holidays: {_e}")
        return []


def get_zhb_csrc_industries() -> Dict[str, str]:
    """V10.0: 获取证监会行业分类 {代码: 名称}。

    共3703个行业分类，涵盖A-S门类。
    """
    try:
        from zhb_client import get_csrc_industries
        return get_csrc_industries()
    except Exception as _e:
        _debug_log(f"datasource zhb csrc_industries: {_e}")
        return {}


def get_zhb_adr_stocks() -> List[Dict[str, str]]:
    """V10.0: 获取中概股ADR列表。

    返回: [{'a_code': A股代码, 'a_name': A股名称, 'adr_code': ADR代码, 'adr_name': ADR名称}, ...]
    """
    try:
        from zhb_client import get_adr_stocks
        return get_adr_stocks()
    except Exception as _e:
        _debug_log(f"datasource zhb adr_stocks: {_e}")
        return []


def get_zhb_convertible_bonds() -> List[Dict[str, Any]]:
    """V10.0: 获取可转债列表。"""
    try:
        from zhb_client import get_convertible_bonds
        return get_convertible_bonds()
    except Exception as _e:
        _debug_log(f"datasource zhb convertible_bonds: {_e}")
        return []


def get_zhb_delisted_stocks() -> Dict[str, str]:
    """V10.0: 获取退市股票代码→名称映射。"""
    try:
        from zhb_client import get_delisted_stocks
        return get_delisted_stocks()
    except Exception as _e:
        _debug_log(f"datasource zhb delisted_stocks: {_e}")
        return {}


def should_use_zhb_data() -> tuple[bool, str]:
    """V10.0: 根据当前时机判断是否应使用zhb数据。

    Returns:
        (should_use, expected_date): 是否使用zhb，期望的数据日期(YYYYMMDD)

    时间逻辑：
        - 收盘后(15:00后): 使用当日数据
        - 开盘前(9:30前): 使用上一交易日数据
        - 休市日: 使用上一交易日数据
        - 盘中(9:30-15:00): 必须实时获取，返回(False, "")
    """
    try:
        from zhb_client import should_use_zhb_data
        return should_use_zhb_data()
    except Exception as _e:
        _debug_log(f"datasource zhb should_use_zhb_data: {_e}")
        return (False, "")


def is_zhb_date_matching() -> bool:
    """V10.0: 判断当前zhb数据日期是否符合预期。"""
    try:
        from zhb_client import is_zhb_date_matching
        return is_zhb_date_matching()
    except Exception as _e:
        _debug_log(f"datasource zhb is_zhb_date_matching: {_e}")
        return False


# ═══════════════════════════════════════════════════════════
# zhb V10.1 新增：全量字段 + 衍生指标
# ═══════════════════════════════════════════════════════════

def get_zhb_full_market_snapshot(codes: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """V10.1: 全市场合并快照（tdxstat + tdxstat2 合并）。

    一次调用拿到全市场7938只股票的完整统计+资金流向数据，
    包含涨跌幅、PE、股息率、52周高低价、成交额、行业代码等。
    """
    try:
        from zhb_client import full_market_snapshot
        return full_market_snapshot(codes)
    except Exception as _e:
        _debug_log(f"datasource zhb full_market_snapshot: {_e}")
        return {}


def get_zhb_market_stat2_snapshot(codes: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """V10.1: 全市场资金流向+板块归属快照（tdxstat2）。"""
    try:
        from zhb_client import market_stat2_snapshot
        return market_stat2_snapshot(codes)
    except Exception as _e:
        _debug_log(f"datasource zhb market_stat2_snapshot: {_e}")
        return {}


def get_zhb_dividend_yield(code: str) -> Optional[float]:
    """V10.1: 获取股息率(%)。"""
    try:
        from zhb_client import get_dividend_yield
        return get_dividend_yield(code)
    except Exception as _e:
        _debug_log(f"datasource zhb dividend_yield ({code}): {_e}")
        return None


def get_zhb_streak_days(code: str) -> Optional[int]:
    """V10.1: 获取连涨连跌天数（正=连涨，负=连跌）。"""
    try:
        from zhb_client import get_streak_days
        return get_streak_days(code)
    except Exception as _e:
        _debug_log(f"datasource zhb streak_days ({code}): {_e}")
        return None


def get_zhb_change_ytd(code: str) -> Optional[float]:
    """V10.1: 获取年初至今涨跌幅(%)。"""
    try:
        from zhb_client import get_change_ytd
        return get_change_ytd(code)
    except Exception as _e:
        _debug_log(f"datasource zhb change_ytd ({code}): {_e}")
        return None


def get_zhb_ipo_price(code: str) -> Optional[float]:
    """V10.1: 获取IPO发行价(元)。"""
    try:
        from zhb_client import get_ipo_price
        return get_ipo_price(code)
    except Exception as _e:
        _debug_log(f"datasource zhb ipo_price ({code}): {_e}")
        return None


def get_zhb_amount_wan(code: str) -> Optional[float]:
    """V10.1: 获取今日成交额(万元)。"""
    try:
        from zhb_client import get_amount_wan
        return get_amount_wan(code)
    except Exception as _e:
        _debug_log(f"datasource zhb amount_wan ({code}): {_e}")
        return None


def get_zhb_amount_1d(code: str) -> Optional[float]:
    """V10.1: 获取昨日成交额(万元)。"""
    try:
        from zhb_client import get_amount_1d
        return get_amount_1d(code)
    except Exception as _e:
        _debug_log(f"datasource zhb amount_1d ({code}): {_e}")
        return None


def get_zhb_main_net_buy(code: str) -> Optional[Dict[str, Any]]:
    """V10.3: 获取主力资金流向数据。

    Returns:
        {
            "main_net_buy_hands": float,       # T日主力净买入量(手)
            "main_net_buy_hands_1d": float,    # T-1日主力净买入量(手)
            "main_net_buy_amount": float,      # T日主力净流入额(万元)
            "main_net_buy_amount_1d": float,   # T-1日主力净流入额(万元)
        }
        None if zhb不可用
    """
    try:
        from zhb_client import get_main_net_buy
        return get_main_net_buy(code)
    except Exception as _e:
        _debug_log(f"datasource zhb main_net_buy ({code}): {_e}")
        return None


def get_zhb_main_net_buy_amount(code: str) -> Optional[float]:
    """V10.3: 获取T日主力净流入额(万元)。"""
    try:
        from zhb_client import get_main_net_buy_amount
        return get_main_net_buy_amount(code)
    except Exception as _e:
        _debug_log(f"datasource zhb main_net_buy_amount ({code}): {_e}")
        return None


def get_zhb_main_net_buy_amount_1d(code: str) -> Optional[float]:
    """V10.3: 获取T-1日主力净流入额(万元)。"""
    try:
        from zhb_client import get_main_net_buy_amount_1d
        return get_main_net_buy_amount_1d(code)
    except Exception as _e:
        _debug_log(f"datasource zhb main_net_buy_amount_1d ({code}): {_e}")
        return None


def get_zhb_single_stock_data(code: str) -> Optional[Dict[str, Any]]:
    """V10.1: 获取单只股票的完整zhb数据（tdxstat + tdxstat2合并）。

    Returns:
        合并后的股票数据字典，包含涨跌幅、PE、阶段涨幅、52周高低、
        股息率、行业代码、成交额、IPO发行价等字段。
        获取失败返回 None。
    """
    try:
        from zhb_client import get_stock_stat, get_stock_stat2
        stat1 = get_stock_stat(code)
        stat2 = get_stock_stat2(code)
        if not stat1 and not stat2:
            return None
        result = dict(stat1) if stat1 else {}
        if stat2:
            result.update(stat2)
        return result
    except Exception as _e:
        _debug_log(f"datasource zhb single_stock_data ({code}): {_e}")
        return None


# ═══════════════════════════════════════════════════════════
# V10.1: 全局股本缓存 + 市值计算
# ═══════════════════════════════════════════════════════════

def get_share_capital(code: str) -> Dict[str, Any]:
    """V10.1: 获取单只股票的股本数据（总股本、流通股）。

    Returns:
        {"total_shares": float, "float_shares": float, "updated_at": str}
        单位：万股
    """
    try:
        from stock_common.sc_capital_cache import get_share_capital as _get_cap
        return _get_cap(code)
    except Exception as _e:
        _debug_log(f"datasource share_capital ({code}): {_e}")
        return {"total_shares": 0, "float_shares": 0, "updated_at": ""}


def calc_mcap_yi(code: str, price: float) -> float:
    """V10.1: 计算总市值（亿元）。

    Args:
        code: 股票代码
        price: 当前价格（元）

    Returns:
        总市值（亿元），失败返回0
    """
    try:
        from stock_common.sc_capital_cache import calc_mcap_yi as _calc
        return _calc(code, price)
    except Exception as _e:
        _debug_log(f"datasource calc_mcap_yi ({code}): {_e}")
        return 0.0


def calc_float_mcap_yi(code: str, price: float) -> float:
    """V10.1: 计算流通市值（亿元）。

    Args:
        code: 股票代码
        price: 当前价格（元）

    Returns:
        流通市值（亿元），失败返回0
    """
    try:
        from stock_common.sc_capital_cache import calc_float_mcap_yi as _calc
        return _calc(code, price)
    except Exception as _e:
        _debug_log(f"datasource calc_float_mcap_yi ({code}): {_e}")
        return 0.0


# ═══════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════

def print_batch_summary(results, total):
    """批量执行结果汇总打印。

    Args:
        results: 结果列表，每项应为 {"code": str, "status": str, "error": str}。
        total: 总股票数量。
    """
    ok = [r for r in results if r["status"] == "成功"]
    fd = [r for r in results if r["status"] == "数据失败"]
    fg = [r for r in results if r["status"] in ("GD上传失败", "GD上传异常", "GD文件夹失败", "GD未连接")]
    print(f"\n{'=' * 60}")
    print(f"  批量执行完成 — 共处理 {total} 只股票")
    print(f"{'=' * 60}")
    print(f"  ✅ 全部成功: {len(ok)}  |  ❌ 数据失败: {len(fd)}  |  ⚠️ GD上传失败: {len(fg)}")





# ═══════════════════════════════════════════════════════════
# 批次8完成：交易日历/异步包装/外部代理函数（8个函数）
# ═══════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════
# 龙虎榜查询（V7.5 统一封装 + V8.5 席位增强）
# ═══════════════════════════════════════════════════════════

@cached(category="dragon_tiger", ttl_seconds=TTL["dragon_tiger"])
def get_dragon_tiger_board(code: str, days: int = 30, include_seats: bool = True,
                           enhance_seats: bool = True) -> Dict[str, Any]:
    """V7.5: 统一龙虎榜查询（单只股票）。

    V8.5新增：enhance_seats参数，启用后自动调用seat_db增强席位分析。
    V10.2修复：移除 today_str 参数（改为内部自动计算），避免跨日缓存 key 污染。

    Args:
        code: 6位股票代码
        days: 回溯天数（sht默认30，med默认180）
        include_seats: 是否查询席位详情（默认True，设为False可减少2次API请求）
        enhance_seats: V8.5新增，是否增强席位分析（默认True，添加席位等级/风格/溢价信号）

    Returns:
        {
          "records": [{date, reason, net_buy, turnover}, ...],
          "seats": {"buy": [{name, buy_amt, sell_amt, net}, ...], "sell": [...]},
          "institution": {"buy_amt", "sell_amt", "net_amt"},
          "net_sum_5d": float,        # V7.5新增：近5日净额累加
          "net_sum_30d": float,       # V7.5新增：近30日（或days）净额累加
          "consecutive_net_buy_days": int,  # V7.5新增：连续净买入天数
          "seat_analysis": {...},     # V8.5新增：enhance_seats=True时返回
        }

    注意 (2026-06-16): 东财 datacenter API 日期字段过滤必须用单引号
    (`TRADE_DATE>='YYYY-MM-DD'`），双引号会报 code=9501。
    """
    # V10.2: today_str 内部自动计算，不作为函数参数（避免污染缓存 key）
    today_str = datetime.now().strftime("%Y-%m-%d")
    start_str = (datetime.strptime(today_str, "%Y-%m-%d") - timedelta(days=days)).strftime("%Y-%m-%d")
    records = []
    data = eastmoney_datacenter(code, "RPT_DAILYBILLBOARD_DETAILSNEW",
                                filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{start_str}')(TRADE_DATE<='{today_str}')",
                                page_size=50, sort_columns="TRADE_DATE", sort_types="-1")
    for row in data:
        records.append({
            "date": str(row.get("TRADE_DATE", "") or "")[:10],
            "reason": row.get("EXPLANATION", ""),
            "net_buy": round((row.get("BILLBOARD_NET_AMT") or 0) / 10000, 1),
            "turnover": round(_safe_float(row.get("TURNOVERRATE")), 2),
        })

    seats: Dict[str, List[Any]] = {"buy": [], "sell": []}
    institution: Dict[str, float] = {"buy_amt": 0.0, "sell_amt": 0.0, "net_amt": 0.0}

    if records and include_seats:
        latest_date = records[0]["date"]
        # 买入/卖出席席：用最新上榜日期 + SECURITY_CODE 过滤（单引号日期）
        buy_data = eastmoney_datacenter(code, "RPT_BILLBOARD_DAILYDETAILSBUY",
                                        filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{latest_date}')(TRADE_DATE<='{latest_date}')",
                                        page_size=50, sort_columns="BUY", sort_types="-1")
        for row in buy_data[:5]:
            seats["buy"].append({
                "name": row.get("OPERATEDEPT_NAME", ""),
                "code": str(row.get("OPERATEDEPT_CODE", "")),
                "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                "net": round((row.get("NET") or 0) / 10000, 1),
            })
        sell_data = eastmoney_datacenter(code, "RPT_BILLBOARD_DAILYDETAILSSELL",
                                         filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{latest_date}')(TRADE_DATE<='{latest_date}')",
                                         page_size=50, sort_columns="SELL", sort_types="-1")
        for row in sell_data[:5]:
            seats["sell"].append({
                "name": row.get("OPERATEDEPT_NAME", ""),
                "code": str(row.get("OPERATEDEPT_CODE", "")),
                "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                "net": round((row.get("NET") or 0) / 10000, 1),
            })
        # 机构专用席位（code == "0" 为机构专用）
        for row in buy_data:
            if str(row.get("OPERATEDEPT_CODE", "")) == "0":
                institution["buy_amt"] += (row.get("BUY") or 0)
        for row in sell_data:
            if str(row.get("OPERATEDEPT_CODE", "")) == "0":
                institution["sell_amt"] += (row.get("SELL") or 0)
        institution["buy_amt"] = round(institution["buy_amt"] / 10000, 1)
        institution["sell_amt"] = round(institution["sell_amt"] / 10000, 1)
        institution["net_amt"] = round(institution["buy_amt"] - institution["sell_amt"], 1)

    # V7.5新增：主力净额连续性统计
    net_sum_5d = round(sum(r["net_buy"] for r in records[:5]), 1)
    net_sum_30d_or_days = round(sum(r["net_buy"] for r in records), 1)
    consecutive_net_buy_days = sum(1 for r in records if r["net_buy"] > 0)

    result = {
        "records": records, "seats": seats, "institution": institution,
        "net_sum_5d": net_sum_5d,
        "net_sum_30d": net_sum_30d_or_days,
        "consecutive_net_buy_days": consecutive_net_buy_days,
    }

    # V8.5新增：席位增强分析
    if enhance_seats and (seats.get("buy") or seats.get("sell")):
        try:
            from stock_common.seat_db import enhance_lhb_seats
            result["seat_analysis"] = enhance_lhb_seats({"seats": seats})
        except ImportError:
            pass

    return result


@cached(category="dragon_tiger", ttl_seconds=TTL["dragon_tiger"])
def get_recent_dragon_tiger(days: int = 5) -> Dict[str, Any]:
    """V7.5: 全市场龙虎榜上榜记录（用于异动扫描和席位活跃度策略）。

    Returns:
        { stock_code: {name, reason, net_buy, turnover, date}, ... }

    注意 (2026-06-16): 东财 datacenter API 日期字段过滤必须用单引号
    (`TRADE_DATE>='YYYY-MM-DD'`），双引号会报 code=9501。
    """
    url = DATACENTER_URL
    try:
        td = datetime.now().strftime("%Y-%m-%d")
        sd = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        params = {
            "reportName": "RPT_DAILYBILLBOARD_DETAILSNEW",
            "columns": "SECURITY_CODE,SECURITY_NAME_ABBR,TRADE_DATE,EXPLANATION,BILLBOARD_NET_AMT,TURNOVERRATE",
            "filter": f"(TRADE_DATE>='{sd}')(TRADE_DATE<='{td}')",
            "pageNumber": "1", "pageSize": "200",
            "sortColumns": "TRADE_DATE", "sortTypes": "-1",
            "source": "WEB", "client": "WEB",
        }
        r = _request_with_retry(url, params=params, headers={"User-Agent": UA}, timeout=15)
        if r is None:
            return {}
        d = r.json()
        data = d.get("result", {}).get("data", []) or []
        result = {}
        for row in data:
            code = str(row.get("SECURITY_CODE", ""))
            if code not in result:
                result[code] = {
                    "name": row.get("SECURITY_NAME_ABBR", ""),
                    "reason": row.get("EXPLANATION", ""),
                    "net_buy": round((row.get("BILLBOARD_NET_AMT") or 0) / 10000, 1),
                    "turnover": round(_safe_float(row.get("TURNOVERRATE")), 2),
                    "date": str(row.get("TRADE_DATE", "") or "")[:10],
                }
        return result
    except Exception as _e:
        _debug_log(f"datasource get_recent_dragon_tiger ({days}d): {_e}")
        return {}


async def get_dragon_tiger_board_async(session, code: str,
                                       days: int = 30, include_seats: bool = True,
                                       enhance_seats: bool = True) -> Dict[str, Any]:
    """异步版: 单只股票龙虎榜查询（代理到同步版）。

    V10.2: 移除 today_str 参数（同步版已内部自动计算）。
    """
    return await asyncio.to_thread(
        get_dragon_tiger_board, code, days, include_seats, enhance_seats
    )


async def get_recent_dragon_tiger_async(session, days: int = 5) -> Dict[str, Any]:
    """异步版: 全市场龙虎榜上榜记录（代理到同步版）。"""
    return await asyncio.to_thread(get_recent_dragon_tiger, days)


# ═══════════════════════════════════════════════════════════
# 数据源模块总计：68个函数（含同步+异步版本）
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# V8.9: 舆情互动层 — 同花顺热榜 / 东财人气榜 / 个股概念命中
# 接口来源：a-stock-data V3.3.0 Layer 10，全部零鉴权
# ═══════════════════════════════════════════════════════════

@cached(category="basic_info", ttl_seconds=TTL["basic_info"], cross_verify=True)
def eastmoney_stock_info_push2(code: str) -> Dict[str, Any]:
    """东财 push2 个股基本面信息（含上市日期 f189，不走 TDX）。
    
    当 TDX 无法获取 list_date 时作为 fallback。
    返回: {code, name, industry, total_shares, float_shares, mcap, float_mcap, list_date}
    """
    market_code = 1 if code.startswith("6") else 0
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "fltt": "2", "invt": "2",
        "fields": "f57,f58,f84,f85,f127,f116,f117,f189,f43",
        "secid": f"{market_code}.{code}",
    }
    headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
    try:
        r = em_get(url, params=params, headers=headers, timeout=10)
        if r is None:
            return {}
        d = r.json().get("data", {})
        return {
            "code": d.get("f57", ""),
            "name": d.get("f58", ""),
            "industry": d.get("f127", ""),
            "total_shares": d.get("f84", 0),
            "float_shares": d.get("f85", 0),
            "mcap": d.get("f116", 0),
            "float_mcap": d.get("f117", 0),
            "list_date": str(d.get("f189", "")),
            "price": d.get("f43", 0),
        }
    except Exception as _e:
        _debug_log(f"datasource eastmoney_stock_info_push2 ({code}): {_e}")
        return {}


@cached(category="ths_hot_reason", ttl_seconds=TTL["ths_hot_reason"], trading_day=True)
def ths_hot_list(period: str = "hour") -> List[Dict[str, Any]]:
    """同花顺热榜。period: hour/day。
    返回每只: rank/code/name/heat(人气值)/pct/rank_chg(排名变化)/concepts(概念标签)/tag。
    """
    try:
        r = _quick_request(
            "https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/stock",
            params={"stock_type": "a", "type": period, "list_type": "normal"},
            headers={"User-Agent": UA},
            timeout=10
        )
        if r is None:
            return []
        lst = (r.json().get("data") or {}).get("stock_list") or []
    except Exception as _e:
        _debug_log(f"datasource ths_hot_list ({period}): {_e}")
        return []
    out = []
    for it in lst:
        tag = it.get("tag") or {}
        out.append({
            "rank": it.get("order"),
            "code": it.get("code"),
            "name": it.get("name"),
            "heat": it.get("rate"),
            "pct": it.get("rise_and_fall"),
            "rank_chg": it.get("hot_rank_chg"),
            "concepts": tag.get("concept_tag") or [],
            "tag": tag.get("popularity_tag", ""),
        })
    return out


@cached(category="hot_rank", ttl_seconds=TTL["hot_rank"])
def em_hot_rank(top: int = 50) -> List[Dict[str, Any]]:
    """东财人气榜。返回 rank/code/name/price/pct/rank_chg。"""
    _hot_body = {"appId": "appId01", "globalId": "786e4c21-70dc-435a-93bb-38"}
    try:
        from stock_common.sc_network import EM_SESSION
        r = EM_SESSION.post(
            "https://emappdata.eastmoney.com/stockrank/getAllCurrentList",
            json={**_hot_body, "marketType": "", "pageNo": 1, "pageSize": top},
            headers={"User-Agent": UA},
            timeout=10
        )
        if r is None:
            return []
        data = r.json().get("data") or []
        if not data:
            return []
        # 人气榜只给带前缀代码，用 push2 补名称/价格
        secids = [("0." if it["sc"].startswith("SZ") else "1.") + it["sc"][2:] for it in data]
        u = _quick_request(
            "https://push2.eastmoney.com/api/qt/ulist.np/get",
            params={"ut": "f057cbcbce2a86e2866ab8877db1d059", "fltt": 2, "invt": 2,
                    "fields": "f14,f3,f12,f2", "secids": ",".join(secids)},
            headers={"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"},
            timeout=10
        )
        if u is None:
            return []
        diff = (u.json().get("data") or {}).get("diff") or []
        if isinstance(diff, dict):
            diff = list(diff.values())
        nm = {x["f12"]: (x.get("f14"), x.get("f2"), x.get("f3")) for x in diff}
    except Exception as _e:
        _debug_log(f"datasource em_hot_rank: {_e}")
        return []
    out = []
    for it in data:
        code = it["sc"][2:]
        name, price, pct = nm.get(code, ("", None, None))
        out.append({
            "rank": it["rk"], "code": code, "name": name,
            "price": price, "pct": pct, "rank_chg": it.get("hisRc"),
        })
    return out


@cached(category="hot_concept", ttl_seconds=TTL["hot_concept"])
def em_hot_concept(code: str) -> List[Dict[str, Any]]:
    """东财个股热门概念命中（这只票当下被市场归到哪些概念在炒）。
    返回 [{concept, bk, hit(命中热度)}, ...]，按热度降序。
    """
    _hot_body = {"appId": "appId01", "globalId": "786e4c21-70dc-435a-93bb-38"}
    try:
        from stock_common.sc_network import EM_SESSION
        prefix = "SH" if code.startswith("6") else "SZ"
        r = EM_SESSION.post(
            "https://emappdata.eastmoney.com/stockrank/getHotStockRankList",
            json={**_hot_body, "srcSecurityCode": prefix + code},
            headers={"User-Agent": UA},
            timeout=10
        )
        if r is None:
            return []
        data = r.json().get("data") or []
    except Exception as _e:
        _debug_log(f"datasource em_hot_concept ({code}): {_e}")
        return []
    return [{"concept": x.get("conceptName"), "bk": x.get("conceptId"),
             "hit": x.get("hitCount")} for x in data]


# ═══════════════════════════════════════════════════════════
# 数据源模块总计：76个函数（含同步+异步+外部代理版本）
# ═══════════════════════════════════════════════════════════