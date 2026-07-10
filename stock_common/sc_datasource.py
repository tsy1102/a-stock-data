"""stock_common/sc_datasource.py - 数据源查询模块 (V9.3.3)

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


async def _em_filter_async(session, code: str, report_name: str, extra_filter: str = "",
                            page_size: int = 50, sort_columns: str = "",
                            sort_types: str = "-1") -> List[Dict[str, Any]]:
    """async 版：东财数据中心查询便捷包装（代理到同步版）。"""
    return await asyncio.to_thread(
        _em_filter, code, report_name, extra_filter, page_size, sort_columns, sort_types
    )


async def eastmoney_datacenter_async(session, code: str, report_name: str, columns: str = "ALL",
                                     filter_str: str = "", page_size: int = 50,
                                     sort_columns: str = "", sort_types: str = "-1") -> List[Dict[str, Any]]:
    """async 版：东财数据中心统一查询（代理到同步版）。"""
    return await asyncio.to_thread(
        eastmoney_datacenter, code, report_name, columns,
        filter_str, page_size, sort_columns, sort_types
    )


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
    except Exception:
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
        url = f"https://www.cninfo.com.cn/new/data/szse_stock.json"
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
    except Exception:
        return []


async def get_strategic_announcements_async(session, code: str, page_size: int = 50,
                                             days: Optional[int] = None) -> List[Dict[str, Any]]:
    """async 版：巨潮公告查询（代理到同步版）。"""
    return await asyncio.to_thread(
        get_strategic_announcements, code, page_size, days
    )


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
    return await asyncio.to_thread(tdx_get_quote_full, code)


@cached(category="basic_info", ttl_seconds=TTL["basic_info"],
        valid_if=lambda r: bool(r.get("list_date")), cross_verify=True)
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
        except Exception:
            break
    return all_records


async def get_reports_async(session: Any, code: str, max_pages: int = 3) -> List[Dict[str, Any]]:
    """async 版: 东财研报列表

    V9.0: 委托到同步版（已内置 F10 优先逻辑），保留 session 参数向后兼容。
    """
    import asyncio
    return await asyncio.to_thread(get_reports, code, max_pages)


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
        except Exception:
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
    """async 版: 北向资金持仓动态（代理到同步版）。"""
    return await asyncio.to_thread(get_northbound_hold, code, days)


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

    V9.0: 委托到同步版（已内置 F10 优先逻辑），保留 session 参数向后兼容。
    """
    import asyncio
    return await asyncio.to_thread(get_block_trade, code)


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
    """V7.5: 同花顺热点题材归因（代理到同步版）。"""
    return await asyncio.to_thread(get_ths_hot_reason, code, date_str)


# 行业对比
@cached(category="industry_peers", ttl_seconds=TTL["industry_peers"],
        valid_if=lambda r: r is not None and bool(r.get("peers")) and all(
            p.get("price", 0) > 0 for p in r["peers"] if isinstance(p, dict)
        ) if isinstance(r, dict) else False)
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


@cached(category="industry_peers", ttl_seconds=TTL["industry_peers"])
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


@cached(category="industry_compare", ttl_seconds=TTL["industry_compare"])
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
    }
    headers = {"User-Agent": UA}

    try:
        r = em_get(url, params=params, headers=headers, timeout=15)
        if r is None:
            return []

        d = r.json()
        items = d.get("data", {}).get("diff", [])
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
    except Exception:
        return []


async def get_industry_comparison_async(session: Any, top_n: int = 20) -> Dict[str, Any]:
    """异步版 get_industry_comparison"""
    import asyncio
    return await asyncio.to_thread(get_industry_comparison, top_n)


# 新闻
@cached(category="stock_news", ttl_seconds=TTL["stock_news"])
def get_eastmoney_stock_news(code: str, page_size: int = 20) -> List[Dict[str, Any]]:
    """获取东财个股新闻（SKILL.md V3.2 推荐）。

    使用东财search-api-web接口获取个股相关新闻，作为社交舆情的补充数据源。

    Args:
        code: 股票代码
        page_size: 返回数量上限

    Returns:
        list: 新闻列表，包含标题、发布时间、来源、摘要等字段
    """
    # V9.0: 优先使用 F10 公司报道数据
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
    # Fallback: 东财 HTTP
    url = "https://search-api-web.eastmoney.com/search/jsonp"

    # 根据代码确定市场
    market = "sh" if code.startswith("6") else "sz"

    params = {
        "keyword": code,
        "type": "news",
        "pageSize": str(page_size),
        "pageNo": "1",
        "client": "web",
        "market": market,
        "code": code,
    }

    headers = {
        "User-Agent": UA,
        "Referer": "https://so.eastmoney.com/",
        "Origin": "https://so.eastmoney.com",
    }

    try:
        r = em_get(url, params=params, headers=headers, timeout=15)
        if r is None:
            return []

        # 处理JSONP格式响应
        text = r.text
        if text.startswith("jQuery(") and text.endswith(")"):
            text = text[7:-1]

        d = json.loads(text)
        result = d.get("result", {})
        news_list = result.get("list", [])

        news_items = []
        for news in news_list[:page_size]:
            news_items.append({
                "title": news.get("title", ""),
                "publish_time": news.get("publishTime", ""),
                "source": news.get("source", ""),
                "summary": news.get("summary", ""),
                "url": news.get("url", ""),
            })

        return news_items
    except Exception:
        return []


@cached(category="global_news", ttl_seconds=TTL["global_news"])
def get_eastmoney_global_news(page_size: int = 50) -> List[Dict[str, Any]]:
    """获取东财全球资讯（SKILL.md V3.2 推荐，财联社替代）。

    使用东财np-weblist接口获取7×24财经快讯，作为财联社下线后的替代方案。

    Args:
        page_size: 返回数量上限

    Returns:
        list: 资讯列表，包含标题、发布时间、内容等字段
    """
    url = "https://np-listapi.eastmoney.com/comm/ws/build/list"

    params = {
        "type": "flsh",  # 快讯类型
        "pageIndex": "1",
        "pageSize": str(page_size),
        "callback": "",
    }

    headers = {"User-Agent": UA}

    try:
        r = em_get(url, params=params, headers=headers, timeout=15)
        if r is None:
            return []

        d = r.json()
        data = d.get("data", {})
        items = data.get("items", [])

        news_items = []
        for item in items[:page_size]:
            news_items.append({
                "title": item.get("title", ""),
                "publish_time": item.get("publishTime", ""),
                "content": item.get("content", ""),
                "type": item.get("type", ""),
            })

        return news_items
    except Exception:
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
    except Exception:
        return []


async def get_sina_financial_report_async(session: Any, code: str, num_periods: int = 12) -> Dict[str, Any]:
    """async 版: 新浪利润表

    V9.0: 委托到同步版（已内置 F10 优先逻辑），保留 session 参数向后兼容。
    """
    import asyncio
    return await asyncio.to_thread(get_sina_financial_report, code, num_periods)


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
    except Exception:
        return None


async def get_sina_balance_sheet_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """async 版: 新浪资产负债表

    V9.0: 委托到同步版（已内置 F10 优先逻辑），保留 session 参数向后兼容。
    """
    import asyncio
    return await asyncio.to_thread(get_sina_balance_sheet, code)


@cached(category="hsgt_flow", ttl_seconds=TTL["hsgt_flow"], use_args=False)
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
        return {"hgt": hgt_val, "sgt": sgt_val, "total": hgt_val + sgt_val}
    except Exception:
        return None


async def get_hsgt_macro_flow_async(session: Any) -> Optional[Dict[str, Any]]:
    """async 版: 同花顺北向资金大盘净流入（代理到同步版）。"""
    return await asyncio.to_thread(get_hsgt_macro_flow)


@cached(category="lockup_expiry", ttl_seconds=TTL["lockup_expiry"], cross_verify=True)
def get_lockup_expiry(code: str, today_str: str, days: int = 90, include_history: bool = False) -> Any:
    """限售解禁日历。

    Args:
        code: 股票代码
        today_str: 当前日期 YYYY-MM-DD
        days: 未来展望窗口天数（默认90天）
        include_history: 是否返回历史记录（True=返回dict, False=返回list）

    Returns:
        include_history=True: {"history": [...], "upcoming": [...]}
        include_history=False: [{"date", "type", "shares", "ratio"}, ...]
    """
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
             "ratio": _safe_float(r.get("FREE_RATIO"))}
            for r in data
        ]
    else:
        history = []

    data2 = eastmoney_datacenter(code, "RPT_LIFT_STAGE",
                                 filter_str=f"(SECURITY_CODE=\"{code}\")(FREE_DATE>='{today_str}')(FREE_DATE<='{end_str}')",
                                 page_size=20, sort_columns="FREE_DATE", sort_types="1")
    upcoming = [
        {"date": str(r.get("FREE_DATE", "")[:10]),
         "type": r.get("FREE_SHARES_TYPE", ""),
         "shares": float(r.get("FREE_SHARES") or 0),
         "ratio": float(r.get("FREE_RATIO") or 0)}
        for r in data2
    ]

    if include_history:
        return {"history": history, "upcoming": upcoming}
    return upcoming


async def get_lockup_expiry_async(session: Any, code: str, today_str: str, days: int = 90, include_history: bool = False) -> Any:
    """async 版: 限售解禁日历

    V9.0: 委托到同步版（已内置 F10 优先逻辑），保留 session 参数向后兼容。
    """
    import asyncio
    return await asyncio.to_thread(get_lockup_expiry, code, today_str, days, include_history)


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
    except Exception:
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
    global _calendar_fallback_warned
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
                  f"请运行 python scripts/update_calendar.py 更新数据。",
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
            status_str: 'closed' | 'pre_market' | 'morning' | 'lunch' | 'afternoon' | 'post_market'
            note_str: 给用户看的中文提示
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
        return "closed", ""




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
def get_dragon_tiger_board(code: str, today_str: str, days: int = 30, include_seats: bool = True,
                           enhance_seats: bool = True) -> Dict[str, Any]:
    """V7.5: 统一龙虎榜查询（单只股票）。

    V8.5新增：enhance_seats参数，启用后自动调用seat_db增强席位分析。

    Args:
        code: 6位股票代码
        today_str: 今日日期 YYYY-MM-DD
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
    start_str = (datetime.strptime(today_str, "%Y-%m-%d") - timedelta(days=days)).strftime("%Y-%m-%d")
    records = []
    data = eastmoney_datacenter(code, "RPT_DAILYBILLBOARD_DETAILSNEW",
                                filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{start_str}')(TRADE_DATE<='{today_str}')",
                                page_size=50, sort_columns="TRADE_DATE", sort_types="-1")
    for row in data:
        records.append({
            "date": str(row.get("TRADE_DATE", ""))[:10],
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
                    "date": str(row.get("TRADE_DATE", ""))[:10],
                }
        return result
    except Exception:
        return {}


async def get_dragon_tiger_board_async(session, code: str, today_str: str,
                                       days: int = 30, include_seats: bool = True,
                                       enhance_seats: bool = True) -> Dict[str, Any]:
    """异步版: 单只股票龙虎榜查询（代理到同步版）。"""
    return await asyncio.to_thread(
        get_dragon_tiger_board, code, today_str, days, include_seats, enhance_seats
    )


async def get_recent_dragon_tiger_async(session, days: int = 5) -> Dict[str, Any]:
    """异步版: 全市场龙虎榜上榜记录（代理到同步版）。"""
    return await asyncio.to_thread(get_recent_dragon_tiger, days)


# ═══════════════════════════════════════════════════════════
# 数据源模块总计：68个函数（含同步+异步版本）
# ═══════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════
# V8.5: 外部分析模块代理函数
#   - get_trap_detection:     杀猪盘检测（trap_detector.py）
#   - get_valuation:          机构估值（valuation_methods.py）
#   - analyze_ai_chain_position: AI产业链卡位（ai_chain_analyzer.py）
# 这些是便捷封装函数，内部 import 外部模块以避免循环依赖。
# ═══════════════════════════════════════════════════════════


def get_trap_detection(code: str, name: str,
                      info: Optional[Dict[str, Any]] = None,
                      kline_data: Optional[Dict[str, Any]] = None,
                      sentiment_data: Optional[Dict[str, Any]] = None,
                      social_data: Optional[Dict[str, Any]] = None,
                      reports: Optional[List[Dict]] = None,
                      announcements: Optional[List[Dict]] = None,
                      news_titles: Optional[List[str]] = None,
                      price_change_pct: float = 0,
                      user_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
    """V8.5: 杀猪盘检测便捷函数

    对外统一的杀猪盘检测接口，封装trap_detector.py的8维检测逻辑。

    Args:
        code: 股票代码
        name: 股票名称
        info: 基本面信息 {"roe": float, "net_profit": float, "industry": str}
        kline_data: K线数据 {"prices": [float], "volumes": [float], "ma5": float, "ma20": float}
        sentiment_data: 情绪数据 {"hot_score": int, "hot_trend": str}
        social_data: 社交平台数据 {"active_platforms": [str]}
        reports: 研报列表 [{"title": str, "broker": str, "analyst": str}]
        announcements: 公告列表 [{"title": str, "date": str}]
        news_titles: 新闻/帖子标题列表
        price_change_pct: 近期涨跌幅
        user_keywords: 用户输入的关键词 ["朋友推荐", "群里", "老师", ...]

    Returns:
        dict: {
            "trap_score": int,  # 1-10, 10=最安全
            "level": str,       # 安全/注意/警惕/高度可疑
            "summary": str,     # 检测结论
            "recommendations": [str],  # 建议列表
            "signals": dict     # 各信号检测结果
        }
    """
    try:
        from stock_common.trap_detector import detect_trap_signals
        result = detect_trap_signals(
            code=code,
            name=name,
            info=info,
            kline_data=kline_data,
            sentiment_data=sentiment_data,
            social_data=social_data,
            reports=reports,
            announcements=announcements,
            news_titles=news_titles,
            price_change_pct=price_change_pct,
            user_keywords=user_keywords
        )
        return {
            "trap_score": result.trap_score,
            "level": result.level,
            "summary": result.summary,
            "recommendations": result.recommendations,
            "signals": {
                k: {"hit": v.hit, "evidence": v.evidence, "description": v.description}
                for k, v in result.signals.items()
            },
            "is_trap_suspected": result.is_trap_suspected(),
            "warning_level": result.get_warning_level()
        }
    except ImportError:
        return {
            "trap_score": 10,
            "level": "未知",
            "summary": "杀猪盘检测模块未安装",
            "recommendations": [],
            "signals": {},
            "is_trap_suspected": False,
            "warning_level": 0,
            "error": "trap_detector模块未找到"
        }
    except Exception as e:
        return {
            "trap_score": 10,
            "level": "错误",
            "summary": f"杀猪盘检测执行异常: {str(e)}",
            "recommendations": ["检测执行异常，建议人工复核"],
            "signals": {},
            "is_trap_suspected": False,
            "warning_level": 0,
            "error": str(e)
        }


def get_valuation(code: str, current_price: float,
                  pe_ttm: float, eps_ttm: float, eps_growth_rate: float,
                  roe: float, pb: float, industry_pe: float,
                  dividend_yield: float = 0.0,
                  shares_outstanding: float = 1.0,
                  fcf_forecast: Optional[List[float]] = None) -> Dict[str, Any]:
    """V8.5: 机构估值便捷函数

    对外统一的估值接口，封装valuation_methods.py的多种估值方法。

    Args:
        code: 股票代码
        current_price: 当前股价
        pe_ttm: 市盈率(TTM)
        eps_ttm: EPS(TTM)
        eps_growth_rate: EPS增长率 (如0.20表示20%)
        roe: 净资产收益率 (如0.15表示15%)
        pb: 市净率
        industry_pe: 行业平均PE
        dividend_yield: 股息率 (如0.03表示3%)
        shares_outstanding: 流通股数(亿股)
        fcf_forecast: 自由现金流预测 [year1, year2, year3, ...] (可选)

    Returns:
        dict: {
            "verdict": str,  # 综合判断
            "upside_avg": float,  # 平均上涨空间
            "dominant_verdict": str,  # 多数方法判断
            "confidence": str,  # 置信度
            "methods": [dict],  # 各方法结果列表
            "summary": str  # 摘要
        }
    """
    try:
        from stock_common.valuation_methods import get_intrinsic_value, format_valuation_report, ValuationResult

        result = get_intrinsic_value(
            code=code,
            current_price=current_price,
            pe_ttm=pe_ttm,
            eps_ttm=eps_ttm,
            eps_growth_rate=eps_growth_rate,
            roe=roe,
            pb=pb,
            industry_pe=industry_pe,
            dividend_yield=dividend_yield,
            shares_outstanding=shares_outstanding,
            fcf_forecast=fcf_forecast
        )

        # 格式化方法结果
        methods_formatted = []
        for m in result.get("methods", []):
            if isinstance(m, ValuationResult):
                methods_formatted.append({
                    "method": m.method,
                    "intrinsic_value": m.intrinsic_value,
                    "current_price": m.current_price,
                    "upside": m.upside,
                    "downside": m.downside,
                    "verdict": m.verdict,
                    "confidence": m.confidence,
                    "notes": m.notes
                })

        summary = f"{result['verdict']}，平均上涨空间{result['upside_avg']}%，{result['confidence']}置信度"

        return {
            "verdict": result["verdict"],
            "upside_avg": result["upside_avg"],
            "dominant_verdict": result["dominant_verdict"],
            "confidence": result["confidence"],
            "methods": methods_formatted,
            "summary": summary,
            "error": ""
        }
    except ImportError:
        return {
            "verdict": "无法估值",
            "upside_avg": 0,
            "dominant_verdict": "无法估值",
            "confidence": "低",
            "methods": [],
            "summary": "估值模块未安装",
            "error": "valuation_methods模块未找到"
        }
    except Exception as e:
        return {
            "verdict": "估值异常",
            "upside_avg": 0,
            "dominant_verdict": "估值异常",
            "confidence": "低",
            "methods": [],
            "summary": f"估值执行异常: {str(e)}",
            "error": str(e)
        }


def analyze_ai_chain_position(code: str, name: str,
                             concept_blocks: List[str] = None,
                             industry: str = "") -> Dict[str, Any]:
    """V8.5: AI产业链卡位分析便捷函数

    注意：ai_chain_analyzer.py 模块尚未实现，此函数始终返回 ImportError 兜底结果。
    对外统一的AI产业链分析接口，封装ai_chain_analyzer.py的分析逻辑。

    Args:
        code: 股票代码
        name: 股票名称
        concept_blocks: 概念板块列表
        industry: 所属行业

    Returns:
        dict: {
            "in_ai_chain": bool,  # 是否在AI产业链
            "bottleneck_level": str,  # critical/important/normal
            "upstream_exposure": float,  # 上游暴露度 0-1
            "bottleneck_segments": [str],  # 卡脖子环节列表
            "position_score": int,  # 位置评分 1-100
            "ai_relevance": float,  # AI相关度 0-1
            "summary": str,  # 摘要
            "details": dict  # 详细信息
        }
    """
    try:
        from ai_chain_analyzer import analyze_ai_chain_position as _analyze

        position = _analyze(code, name, concept_blocks, industry)

        return {
            "in_ai_chain": position.in_ai_chain,
            "bottleneck_level": position.bottleneck_level,
            "upstream_exposure": position.upstream_exposure,
            "bottleneck_segments": position.bottleneck_segments,
            "position_score": position.position_score,
            "ai_relevance": position.ai_relevance,
            "details": position.details,
            "summary": f"{'在' if position.in_ai_chain else '不在'}AI产业链，卡位{'🔴'+position.bottleneck_level if position.in_ai_chain else '无'}"
        }
    except ImportError:
        return {
            "in_ai_chain": False,
            "bottleneck_level": "unknown",
            "upstream_exposure": 0.0,
            "bottleneck_segments": [],
            "position_score": 0,
            "ai_relevance": 0.0,
            "details": {},
            "summary": "AI产业链分析模块未安装",
            "error": "ai_chain_analyzer模块未找到"
        }
    except Exception as e:
        return {
            "in_ai_chain": False,
            "bottleneck_level": "error",
            "upstream_exposure": 0.0,
            "bottleneck_segments": [],
            "position_score": 0,
            "ai_relevance": 0.0,
            "details": {},
            "summary": f"AI产业链分析异常: {str(e)}",
            "error": str(e)
        }


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
    except Exception:
        return {}


@cached(category="ths_hot_reason", ttl_seconds=TTL["ths_hot_reason"])
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
    except Exception:
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
    except Exception:
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
    except Exception:
        return []
    return [{"concept": x.get("conceptName"), "bk": x.get("conceptId"),
             "hit": x.get("hitCount")} for x in data]


# ═══════════════════════════════════════════════════════════
# 数据源模块总计：76个函数（含同步+异步+外部代理版本）
# ═══════════════════════════════════════════════════════════