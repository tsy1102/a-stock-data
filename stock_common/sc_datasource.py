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

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import time
import re
import json
import asyncio

# 导入网络层
from stock_common.sc_network import (
    em_get,
    _quick_request,
    requires_push2,
    DATACENTER_URL,
    UA,
    _http_logger,
    _biz_logger,
    _debug_log,
    _async_request_with_retry,
    _async_quick_request,
)

# 导入配置加载
from stock_common.sc_utils import _load_settings, _safe_float, em_secid_prefix  # V17.0 S3: 统一 secid 前缀

# 导入缓存层
from core.stock_cache import TTL, cached, make_valid_if  # V15.2: 强化 valid_if

# ═══════════════════════════════════════════════════════════
# 东财数据中心核心函数
# ═══════════════════════════════════════════════════════════


def eastmoney_datacenter(
    code: str,
    report_name: str,
    columns: str = "ALL",
    filter_str: str = "",
    page_size: int = 50,
    sort_columns: str = "",
    sort_types: str = "-1",
    page_index: int = 1,
) -> List[Dict[str, Any]]:
    """东财数据中心统一查询（datacenter-web.eastmoney.com）。

    V7.5 新增：HTTP状态码非200时记录日志，业务错误码(status=-1)时记录日志，JSON解析失败时记录日志。
    """
    try:
        full_filter = filter_str if filter_str else f'(SECURITY_CODE="{code}")'
        r = _quick_request(
            DATACENTER_URL,
            params={
                "reportName": report_name,
                "columns": columns,
                "filter": full_filter,
                "pageNumber": str(page_index),
                "pageSize": str(page_size),
                "sortColumns": sort_columns,
                "sortTypes": sort_types,
                "source": "WEB",
                "client": "WEB",
            },
            headers={"User-Agent": UA},
            timeout=15,
        )
        if r is None:
            return []
        # HTTP状态码检查
        if r.status_code != 200:
            _http_logger.error(f"{r.status_code} | {DATACENTER_URL} | {report_name} | {code}")
            return []
        try:
            d = r.json()
        except Exception as _json_err:
            _http_logger.error(
                f"JSONDecodeError | {DATACENTER_URL} | {report_name} | {code} | {_json_err}"
            )
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


def _em_filter(
    code: str,
    report_name: str,
    extra_filter: str = "",
    page_size: int = 50,
    sort_columns: str = "",
    sort_types: str = "-1",
) -> List[Dict[str, Any]]:
    """东财数据中心查询便捷包装（自动拼接 SECURITY_CODE）。"""
    return eastmoney_datacenter(
        code,
        report_name,
        filter_str=f'(SECURITY_CODE="{code}"){extra_filter}' if extra_filter else "",
        page_size=page_size,
        sort_columns=sort_columns,
        sort_types=sort_types,
    )


async def eastmoney_datacenter_async(
    session: Any,
    code: str,
    report_name: str,
    columns: str = "ALL",
    filter_str: str = "",
    page_size: int = 50,
    sort_columns: str = "",
    sort_types: str = "-1",
) -> List[Dict[str, Any]]:
    """async 版：东财数据中心统一查询（datacenter-web.eastmoney.com）。

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    """
    try:
        full_filter = filter_str if filter_str else f'(SECURITY_CODE="{code}")'
        d = await _async_request_with_retry(
            session,
            DATACENTER_URL,
            params={
                "reportName": report_name,
                "columns": columns,
                "filter": full_filter,
                "pageNumber": "1",
                "pageSize": str(page_size),
                "sortColumns": sort_columns,
                "sortTypes": sort_types,
                "source": "WEB",
                "client": "WEB",
            },
            headers={"User-Agent": UA},
            timeout=15,
        )
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


async def _em_filter_async(
    session: Any,
    code: str,
    report_name: str,
    extra_filter: str = "",
    page_size: int = 50,
    sort_columns: str = "",
    sort_types: str = "-1",
) -> List[Dict[str, Any]]:
    """async 版：东财数据中心查询便捷包装（自动拼接 SECURITY_CODE）。

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    """
    return await eastmoney_datacenter_async(
        session,
        code,
        report_name,
        filter_str=f'(SECURITY_CODE="{code}"){extra_filter}' if extra_filter else "",
        page_size=page_size,
        sort_columns=sort_columns,
        sort_types=sort_types,
    )


# ═══════════════════════════════════════════════════════════
# 批次1完成：东财数据中心核心函数（3个函数）
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# 批次2：股东数据函数
# ═══════════════════════════════════════════════════════════

# 股东户数缓存（直接使用 SQLite，优化版）
_HOLDER_CACHE_TTL: int = 60 * 86400  # 60 天 — 新鲜阈值（同一季度内 TDX 增量更新）
_HOLDER_CACHE_REFRESH: int = 90 * 86400  # 90 天 — 强制刷新阈值（跨季度用东财补全）


def _holder_fetch_from_sqlite(code: str) -> Optional[Dict[str, Any]]:
    """从 SQLite 获取股东户数数据。"""
    try:
        from core.stock_cache import get_cache

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
        from core.stock_cache import set_cache

        cache_key = f"holder_data:{code}"
        data = {"records": records, "updated": timestamp}
        # 使用 holder_cache 的 TTL（60天）
        set_cache("holder", "holder_data", data, _HOLDER_CACHE_TTL, cache_key)
    except Exception as _e:
        _debug_log(f"datasource holder update sqlite error: {_e}")


def _holder_fetch_em(code: str, page_size: int) -> List[Dict[str, Any]]:
    """从东财获取股东户数 → 按日期升序的 records 列表。"""
    data = _em_filter(
        code, "RPT_F10_EH_HOLDERNUM", page_size=page_size, sort_columns="END_DATE", sort_types="-1"
    )
    if not data:
        return []
    records = []
    for r in data:
        records.append(
            {
                "date": str(r.get("END_DATE", ""))[:10],
                "holder_num": int(r.get("HOLDER_TOTAL_NUM") or 0),
                "avg_shares": _safe_float(r.get("AVG_FREE_SHARES")),
            }
        )
    records.sort(key=lambda x: x["date"])
    return records


def _holder_fetch_tdx_optimized(code: str, records: List[Dict[str, Any]], now: float) -> bool:
    """从 TDX 拿最新 1 期，去重后追加到 records（优化版：直接更新 SQLite）。"""
    from core.tdx_client import _get_tdx_client

    client = _get_tdx_client()
    if client is None:
        return False
    info = client.get_finance_info(1 if code.startswith("6") else 0, code)
    if info is None or info.empty:
        return False
    # V15.1: 修正股东户数 key（参考 docs/field_dict.md 第 7 章）
    # 正确 key: gudongrenshu（无下划线）
    hnum = int(info.iloc[0].get('gudongrenshu', 0))
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


def holder_change(code: str, local_only: bool = False) -> List[Dict[str, Any]]:
    """获取股东户数多期变化（优化版：直接使用 SQLite）。

    逻辑：
      - 缓存新鲜 < 60 天 → 直接返回
      - 缓存为空 → F10 优先（多期）→ 东财 10 期兜底
      - 缓存过期 ≥ 60 天且 < 90 天 → TDX 追加 1 期（同季度增量）
      - 缓存过期 ≥ 90 天 → F10 优先 → 东财 5 期兜底

    返回: [{date, holder_num, change_num, change_ratio, avg_shares}, ...] 最新在前

    V17.0(2026-08-15) H6 修复: 新增 local_only——缓存未命中时直接返回 []
    （val 策略23 全市场扫描禁逐股网络请求, 仅缓存命中判筹码集中）。
    """
    from core.stock_cache import get_cache, set_cache, TTL

    # 尝试从缓存获取
    cache_key = f"holder_data:{code}"
    cached_data = get_cache("holder", "holder_change", cache_key)

    if cached_data is not None:
        return cached_data
    if local_only:
        return []

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
        from core.tdx_client import tdx_get_shareholder_research

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
                if (
                    k.startswith('人均流通股')
                    or k.startswith('户均持股')
                    or k.startswith('户均流通股')
                    or k.startswith('人均持股')
                ):
                    avg_shares = _safe_float(v or 0)
                    break
            records.append(
                {
                    "date": str(period)[:10],
                    "holder_num": holder_num,
                    "avg_shares": avg_shares,
                }
            )
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
        result.append(
            {
                "date": r["date"],
                "holder_num": r["holder_num"],
                "change_num": change_num,
                "change_ratio": change_ratio,
                "avg_shares": r.get("avg_shares", 0),
            }
        )
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
def get_strategic_announcements(
    code: str, page_size: int = 50, days: Optional[int] = None,
    importance_filter: bool = False, keywords: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """巨潮公告查询 → orgId → searchkey → TDX F10 三层兜底（SKILL.md V3.2.2 增强：动态orgId查询）。

    Args:
        code: 股票代码
        page_size: 返回数量上限
        days: 限定最近 N 天，None=不限（长线），30=中线，7=短线
        importance_filter: V7.5新增，是否仅返回重要公告（True=仅重要，False=全部）
        keywords: V17.0 S4 新增——自定义关键词过滤（覆盖默认列表；mak 异动公告用 ["异常波动"]）
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
        "orgId": ext_org_id,
        "stock": f"{code},{ext_org_id}",
        "tabName": "fulltext",
        "pageSize": str(page_size),
        "pageNum": "1",
        "column": "",
        "category": "",
        "plate": "",
        "seDate": se_date,
        "searchkey": "",
        "secid": "",
        "sortName": "",
        "sortType": "",
        "isHLtitle": "true",
    }
    headers = {
        "User-Agent": UA,
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.cninfo.com.cn/new/disclosure",
    }
    _cfg = _load_settings()
    if keywords is None:
        keywords = _cfg.get(
            "announcement_keywords",
            [
                "回购",
                "增持",
                "减持",
                "年报",
                "分红",
                "派息",
                "激励",
                "员工持股",
                "战略合作",
                "业绩预告",
                "中标",
                "立案",
                "合同",
                "收购",
                "股权转让",
                "异动",
                "严重异动",
            ],
        )
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
            payload2 = {
                "orgId": "",
                "stock": "",
                "tabName": "fulltext",
                "pageSize": str(page_size),
                "pageNum": "1",
                "column": "",
                "category": "",
                "plate": "",
                "seDate": se_date,
                "searchkey": str(code),
                "secid": "",
                "sortName": "",
                "sortType": "",
                "isHLtitle": "true",
            }
            r2 = _quick_request(url, data=payload2, headers=headers, method="POST", timeout=15)
            if r2 is not None:
                d2 = r2.json()
                anns2 = d2.get("announcements", []) or []
                if anns2:
                    anns = anns2
        if not anns:
            # 巨潮双路径均失败 → TDX F10 兜底
            try:
                from core.tdx_client import tdx_get_latest_announcements

                tdx_anns = tdx_get_latest_announcements(code, days=7)
                if tdx_anns:
                    anns = [
                        {
                            "announcementTitle": a["title"],
                            "announcementTime": (
                                int(datetime.strptime(a["date"], "%Y-%m-%d").timestamp() * 1000)
                                if a.get("date")
                                else 0
                            ),
                        }
                        for a in tdx_anns
                    ]
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
                rows.append(
                    {
                        "title": title,
                        "date": date_str,
                        "type": item.get("announcementTypeName", "") or "",
                        "is_important": is_important,
                        # V16.1: 保留 PDF 直链/公告 ID（sht/med/lng 可下附件）
                        "adjunct_url": item.get("adjunctUrl", "") or "",
                        "announcement_id": item.get("announcementId", "") or "",
                    }
                )
        return rows
    except Exception as _e:
        _debug_log(f"datasource strategic_announcements ({code}): {_e}")
        return []


async def get_strategic_announcements_async(
    session, code: str, page_size: int = 50, days: Optional[int] = None
) -> List[Dict[str, Any]]:
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
    headers = {
        "User-Agent": UA,
        "Referer": "http://www.cninfo.com.cn/",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
    }

    try:
        payload = {
            "orgId": "",
            "stock": str(code),
            "tabName": "fulltext",
            "pageSize": str(page_size),
            "pageNum": "1",
            "column": "",
            "category": "",
            "plate": "",
            "seDate": se_date,
            "searchkey": "",
            "secid": "",
            "sortName": "",
            "sortType": "",
            "isHLtitle": "true",
        }
        d = await _async_quick_request(
            session, url, data=payload, headers=headers, method="POST", timeout=15
        )
        anns = []
        if d is not None:
            anns = d.get("announcements", []) or []

        if not anns:
            payload2 = {
                "orgId": "",
                "stock": "",
                "tabName": "fulltext",
                "pageSize": str(page_size),
                "pageNum": "1",
                "column": "",
                "category": "",
                "plate": "",
                "seDate": se_date,
                "searchkey": str(code),
                "secid": "",
                "sortName": "",
                "sortType": "",
                "isHLtitle": "true",
            }
            d2 = await _async_quick_request(
                session, url, data=payload2, headers=headers, method="POST", timeout=15
            )
            if d2 is not None:
                anns2 = d2.get("announcements", []) or []
                if anns2:
                    anns = anns2

        if not anns:
            try:
                import asyncio
                from core.tdx_client import tdx_get_latest_announcements

                tdx_anns = await asyncio.to_thread(tdx_get_latest_announcements, code, days=7)
                if tdx_anns:
                    anns = [
                        {
                            "announcementTitle": a["title"],
                            "announcementTime": (
                                int(datetime.strptime(a["date"], "%Y-%m-%d").timestamp() * 1000)
                                if a.get("date")
                                else 0
                            ),
                        }
                        for a in tdx_anns
                    ]
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
                rows.append(
                    {
                        "title": title,
                        "date": date_str,
                        "type": item.get("announcementTypeName", "") or "",
                        "is_important": is_important,
                        # V16.1: 保留 PDF 直链/公告 ID
                        "adjunct_url": item.get("adjunctUrl", "") or "",
                        "announcement_id": item.get("announcementId", "") or "",
                    }
                )
        return rows
    except Exception as _e:
        _debug_log(f"datasource strategic_announcements_async ({code}): {_e}")
        return []


# 机构持股结构分析（替代 get_institutional_holder_ratio）
_holder_structure_cache: Dict[str, List[Dict[str, Any]]] = {}


@cached(category="financial", ttl_seconds=TTL["financial"], cross_verify=True, trading_day=True, valid_if=make_valid_if())
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
    data = eastmoney_datacenter(
        code,
        "RPT_F10_EH_HOLDERS",
        columns="END_DATE,HOLDER_NAME,HOLD_NUM_RATIO",
        filter_str=f'(SECURITY_CODE="{code}")',
        page_size=50,
        sort_columns="END_DATE",
        sort_types="-1",
    )
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
                fe += ratio
                fc += 1
            elif (
                has_cn
                and len([c for c in name if '\u4e00' <= c <= '\u9fff']) <= 3
                and not any(
                    kw in name
                    for kw in [
                        '公司',
                        '基金',
                        '保险',
                        '银行',
                        '信托',
                        '证券',
                        '合伙',
                        '集团',
                        '投资',
                        '控股',
                    ]
                )
            ):
                ind += ratio
                ic += 1
            else:
                dm += ratio
                dc += 1
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

        result.append(
            {
                "date": date_key,
                "total": round(nb + fe + dm + ind, 1),
                "northbound": round(nb, 2),
                "foreign": round(fe, 1),
                "foreign_count": fc,
                "domestic": round(dm, 1),
                "domestic_count": dc,
                "individual": round(ind, 1),
                "individual_count": ic,
                "dm_detail": {k: round(v, 1) for k, v in dm_tags.items() if v > 0},
            }
        )

    _holder_structure_cache[code] = result
    return result


async def get_holder_structure_async(
    session: Any, code: str, today_str: str = ""
) -> Dict[str, Any]:
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
def get_historical_high_qfq(code: str, count: int = 640) -> Optional[float]:
    """V17.0.5 P2: 历史最高价（腾讯前复权日线, ~640 根≈2.6 年窗口）。

    参考仓库 v3.7.0/3.2.5#28 同源问题修复: TDX bars 为不复权原始价,
    长期分红股跨除权比较会低估真实回撤。qfq 口径与现价同基准可直接比。
    接口: web.ifzq.gtimg.cn fqkline(字典 §12.1 备胎——免费无鉴权, 与 TDX 实测一致)。
    """
    from stock_common.sc_network import _quick_request

    mkt = "bj" if code.startswith(("92", "8", "4", "43", "83", "87")) else (
        "sh" if code.startswith(("6", "9", "5")) else "sz")
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
    try:
        r = _quick_request(
            url,
            params={"param": f"{mkt}{code},day,,,{count},qfq"},
            headers={"Referer": "https://gu.qq.com/"},
            timeout=10,
        )
        if r is None:
            return None
        d = (r.json() or {}).get("data") or {}
        node = d.get(f"{mkt}{code}") or {}
        days = node.get("qfqday") or node.get("day") or []
        highs = [float(row[3]) for row in days if len(row) > 3 and float(row[3]) > 0]
        return max(highs) if highs else None
    except Exception as _e:
        _debug_log(f"datasource historical_high_qfq ({code}): {_e}")
        return None


def get_tencent_quote(code: str) -> Dict[str, Any]:
    """V4: 个股行情 → 腾讯 HTTP 实时（V16.0 修正名不副实问题）。

    V16.0: 原实现直接 return tdx_get_quote_full(code)，与 L1 TDX 是同一函数两次调用，
    导致 data_provider 的"腾讯 L2 fallback"完全冗余。现改为真正请求腾讯 qt.gtimg.cn，
    返回规范字段 dict（经 normalize_at_boundary 归一化）。
    """
    try:
        from stock_common.sc_schema import normalize_at_boundary, DataSource
        from stock_common import _quick_request, _safe_float
        from core.tdx_client import _TENCENT_FIELD_INDEX as _f, _TENCENT_MIN_FIELDS  # V16.2.4 (B5): 统一字段索引
        prefix = "sh" if code.startswith("6") else ("bj" if code.startswith(("8", "4", "92")) else "sz")
        r = _quick_request(f"https://qt.gtimg.cn/q={prefix}{code}", timeout=10)
        if r is None:
            return {}
        r.encoding = "gbk"
        text = r.text
        if "=" not in text or '"' not in text:
            return {}
        vals = text.split('"')[1].split("~")
        if len(vals) < _TENCENT_MIN_FIELDS:
            _debug_log(
                f"datasource tencent quote: 字段数 {len(vals)} < {_TENCENT_MIN_FIELDS} "
                f"（腾讯协议可能变更，需核对 tdx_client._TENCENT_FIELD_INDEX）"
            )
            return {}
        _price_v = _safe_float(vals[_f["price"]])
        _vol_v = _safe_float(vals[_f["volume_hand"]])
        # V16.3 O16: 北交所老号段僵尸数据检测（参考仓库 v3.6.0）——43/83/87 已迁 920xxx，
        # 腾讯对老码返回 HTTP 200 + 成交量 0 + 价格定格迁移日的僵尸数据——丢弃触发上游 fallback
        if code.startswith(("43", "83", "87")) and _vol_v == 0 and _price_v > 0:
            _debug_log(f"datasource tencent quote stale (老号段僵尸数据): {code}")
            return {}
        raw = {
            "code": code,
            "name": vals[_f["name"]],
            "price": _price_v,
            "prev_close": _safe_float(vals[_f["last_close"]]),
            "open": _safe_float(vals[_f["open"]]),
            "volume_hand": _vol_v,  # 手
            "change_pct": _safe_float(vals[_f["change_pct"]]),
            "amount_wan": _safe_float(vals[_f["amount_wan"]]),  # 万元
            "turnover_pct": _safe_float(vals[_f["turnover_pct"]]),
            "vol_ratio": _safe_float(vals[_f["vol_ratio"]]),  # V16.4.0: 量比 v49——val 策略 07 金叉依赖
            "pe_ttm": _safe_float(vals[_f["pe_ttm"]]),
            # V17.0 修复: 删 pe_dynamic←[52]——腾讯 [52] 实为静态 PE(2026-08-13 字典实锤), 非动态;
            # 腾讯无真动态 PE 字段, pe_dynamic 统一由 push2 f162 / fuyao pe_mrq 提供
            "mcap_yi": _safe_float(vals[_f["mcap_yi"]]),  # 亿元
            "pb": _safe_float(vals[_f["pb"]]),
            "high": _safe_float(vals[_f["high"]]),
            "low": _safe_float(vals[_f["low"]]),
            # V16.3 O20: 字典多源对齐（field_dict 12.1 破解）——52周/股息率 fallback 链补腾讯
            "high_52w": _safe_float(vals[_f["high_52w"]]),
            "low_52w": _safe_float(vals[_f["low_52w"]]),
            "dividend_yield": _safe_float(vals[_f["dividend_yield"]]),
            # V16.3.3 (2026-08-10 字典 12.1/12.15.5): 腾讯未知位破解接入
            # V17.0.5 正名: roa=TTM 滚动口径(~~年化~~)；新增 tx65=扣非加权ROE(TTM)——盈利质量对
            "roa": _safe_float(vals[_f["roa_ttm"]]),              # ROA(TTM 滚动, %)
            "roe_deduct_ttm": _safe_float(vals[_f["roe_deduct_ttm"]]),  # 扣非加权ROE(TTM, %)
            "change_180td_pct": _safe_float(vals[_f["change_180td_pct"]]),  # 近180交易日涨跌幅(%) — V17.0.7 定案(tx75, 前复权; ~~主力净流入(亿)~~证伪)
            "panel_price": _safe_float(vals[_f["panel_price"]]),  # 盘口参考价
            "bid1_vol": _safe_float(vals[_f["bid1_vol"]]),          # 买一量(手) — V16.3.4 新增（sht 封单资金用）
        }
        result = normalize_at_boundary(raw, DataSource.TENCENT)
        # V16.3.3: normalize 为白名单映射——腾讯独有字段（normalize 未定义）在此透传
        for _xk in ("roa", "roe_deduct_ttm", "change_180td_pct", "panel_price", "bid1_vol", "vol_ratio"):
            if raw.get(_xk) not in (None, 0, "", "0", "0.0"):
                result[_xk] = raw[_xk]
        return result
    except Exception as _e:
        _debug_log(f"datasource get_tencent_quote ({code}): {_e}")
        return {}


# V17.0.1a(2026-08-16): get_em_batch_quotes 当日进程缓存——mak 全市场主力(17 请求)/名称补全复用,
# 同进程多次调用去重(限流面+性能); 按日失效(盘中数据 T+0)
_EM_BATCH_CACHE: Dict[str, Dict[str, Any]] = {}
_EM_BATCH_CACHE_DATE: str = ""


def get_em_batch_quotes(codes: List[str]) -> Dict[str, Dict[str, Any]]:
    """V12.0: 东财批量行情查询（替代TDX批量查询，修复URL超长Bug）。

    V17.0(2026-08-15): 改 push2delay 镜像域 + secids 参数(原 fs 返回 data:null);
    V17.0.1a(2026-08-16): 当日进程缓存——增量拉取缺失代码, 命中直接返回。
    """
    if not codes:
        return {}
    # V17.0.1a: 当日缓存命中直接返回(增量)
    global _EM_BATCH_CACHE, _EM_BATCH_CACHE_DATE
    from datetime import datetime as _dt2
    _today2 = _dt2.now().strftime("%Y%m%d")
    if _EM_BATCH_CACHE_DATE != _today2:
        _EM_BATCH_CACHE.clear()
        _EM_BATCH_CACHE_DATE = _today2
    _missing = [c for c in codes if c not in _EM_BATCH_CACHE]
    if not _missing:
        return {c: _EM_BATCH_CACHE[c] for c in codes if c in _EM_BATCH_CACHE}

    # 东财市场代码前缀: 沪市为 1., 深市为 0.
    sh_codes = [f"{em_secid_prefix(c)}{c}" for c in codes if em_secid_prefix(c) == "1."]
    sz_codes = [f"{em_secid_prefix(c)}{c}" for c in codes if em_secid_prefix(c) == "0."]  # V17.0 S3: 统一前缀
    all_formatted_codes = sh_codes + sz_codes

    result = {}

    @requires_push2
    def _fetch_batch(code_chunk):
        if not code_chunk:
            return
        fs_str = ",".join(code_chunk)
        # V17.0(2026-08-15 运行前核查): push2 主域连接级封禁期整体失败+0.4rps 限流
        # (17 chunk × 2.5s = 42.5s)——改 push2delay 镜像域(1.0rps 独立风控, 与采集 ulist239/人气榜先例一致);
        # 盘后/盘中延时 15 分钟对 mak 全景报告可接受
        url = "https://push2delay.eastmoney.com/api/qt/ulist.np/get"
        # V15.2 P0 修复: 增加 mcap_yi 字段（f20 总市值=f116/1e8, f21=f117 流通市值）
        # 之前只拉 f2/f3，导致 val 报告 18 步策略 mcap_yi=0
        # V16.1: 扩展字段包 — f55 EPS/f92 BPS/f126 股息率/f162-167 PE/PB/f174-175 52周高低/f221 报告期
        # V17.0(2026-08-15): + f62/f66 主力净流入(ulist 索引=f137/f140 特大+大单净, 20/20 对齐实锤)
        params = {
            "fltt": "2",
            "invt": "2",
            "secids": fs_str,  # V17.0(2026-08-15 冒烟修复): ulist.np/get 参数为 secids(非 fs)——fs 返回 data:null
            "fields": (
                "f12,f14,f2,f3,f20,f21,"
                "f55,f92,f126,f162,f163,f167,f174,f175,f221,"
                "f62,f66"
            ),
        }
        try:
            r = em_get(url, params=params, headers={"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}, timeout=15)
            if r is None:
                return
            d = r.json()
            items = d.get("data", {}).get("diff", [])
            for item in items:
                code = str(item.get("f12", ""))
                name = str(item.get("f14", ""))
                price = _safe_float(item.get("f2", 0))
                change_pct = _safe_float(item.get("f3", 0))
                # V15.2 P0: mcap_yi (f20) 和 float_mcap_yi (f21)
                # V16.3 O17: ulist f20/f21 实测单位是**元**（茅台 1635794278989）——需 /1e8 转亿
                # （此前直接赋值导致批量路径 mcap 错 1e8 倍——canonical L3 单股路径无此问题）
                mcap_yi = _safe_float(item.get("f20", 0)) / 1e8
                float_mcap_yi = _safe_float(item.get("f21", 0)) / 1e8
                if code:
                    result[code] = {
                        "name": name,
                        "price": price,
                        "change_pct": change_pct,
                        "mcap_yi": mcap_yi,
                        "float_mcap_yi": float_mcap_yi,
                        # V16.1: 扩展字段（val 横截面初筛用）
                        "eps": _safe_float(item.get("f55", 0)),
                        "bps": _safe_float(item.get("f92", 0)),
                        "dividend_yield": _safe_float(item.get("f126", 0)),
                        "pe_dynamic": _safe_float(item.get("f162", 0)),
                        "pe_ttm": _safe_float(item.get("f163", 0)),
                        "pb": _safe_float(item.get("f167", 0)),
                        "high_52w": _safe_float(item.get("f174", 0)),
                        "low_52w": _safe_float(item.get("f175", 0)),
                        "report_period": str(item.get("f221", "")),
                        # V17.0(2026-08-15): 主力净流入(万元) = 特大单净(f62) + 大单净(f66)
                        # ulist f62/f66 索引 = push2 f137/f140(20/20 对齐实锤); 单位=元 → /1e4 万
                        "main_net_inflow_wan": (
                            _safe_float(item.get("f62", 0)) + _safe_float(item.get("f66", 0))
                        ) / 1e4,
                    }
        except Exception as _e:
            _debug_log(f"datasource get_em_batch_quotes error: {_e}")

    chunk_size = 300
    for i in range(0, len(all_formatted_codes), chunk_size):
        chunk = all_formatted_codes[i : i + chunk_size]
        _fetch_batch(chunk)

    for _c, _v in result.items():
        _EM_BATCH_CACHE[_c] = _v  # V17.0.1a: 写回当日缓存
    return result


@cached(category="kline", ttl_seconds=TTL["kline"], trading_day=True, valid_if=make_valid_if())
def baidu_kline_full(code, is_index=False, count=800):
    """全量K线 → tdx_client 适配器（纯 TDX 日K线）。

    V16.3 O16: 修正误导性 docstring——百度 PAE 已无实际调用（v3.1.0 起参考仓库同款
    下线 fundflow，本仓库 K 线全程 TDX），函数名保留向后兼容。
    V16.3 O19: 加 count 参数（脚本层直调 tdx_get_security_bars 统一入口，跨脚本共享缓存）。
    """
    from core.tdx_client import tdx_get_security_bars, tdx_get_index_bars

    if is_index:
        return tdx_get_index_bars(code)
    return tdx_get_security_bars(code, count=count)


async def get_tencent_quote_async(session: Any, code: str) -> Dict[str, Any]:
    """异步版 get_tencent_quote（复用 TDX 同步函数）"""
    import asyncio
    from core.tdx_client import tdx_get_quote_full

    return await asyncio.to_thread(tdx_get_quote_full, code)


@cached(
    category="basic_info",
    ttl_seconds=TTL["basic_info"],
    valid_if=lambda r: isinstance(r, dict) and bool(r.get("code")),
    cross_verify=True,
)
def get_stock_info(code: str) -> Dict[str, Any]:
    """V7.5: 个股基本信息 → 腾讯行情 + TDX"""
    from core.tdx_client import _get_tdx_client, tdx_get_belong_boards

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
            # V15.5.4: 统一用适配器 finance() 方法（easy_tdx/mootdx 兼容，列名去下划线）
            info = client.finance(symbol=code)
            if info is not None and not info.empty:
                # V15.1: 修正 0x0010 协议 key（参考 docs/field_dict.md 第 7 章）
                # 正确 key: zongguben / liutongguben（无下划线）
                total_shares = _safe_float(info.iloc[0].get('zongguben', 0))
                float_shares = _safe_float(info.iloc[0].get('liutongguben', 0))
                _ipo = info.iloc[0].get('ipo_date') or info.iloc[0].get('ipodate') or 0
                ipo = str(int(_ipo))
                if ipo and ipo != '0':
                    list_date = ipo
    except Exception as _e:
        _debug_log(f"datasource tdx finance info error: {_e}")
    # V15.5.4: 股本兜底 — sc_capital_cache（V10.1 全局股本缓存）
    if not total_shares or not float_shares:
        try:
            from stock_common.sc_capital_cache import get_share_capital as _get_cap

            _cap = _get_cap(code) or {}
            if not total_shares:
                total_shares = _safe_float(_cap.get('total_shares'))
            if not float_shares:
                float_shares = _safe_float(_cap.get('float_shares'))
        except Exception as _e:
            _debug_log(f"datasource get_stock_info share_capital fallback error: {_e}")

    # TDX 获取上市日期失败时，尝试东财 push2 fallback
    if not list_date:
        try:
            push2_info = eastmoney_stock_info_push2(code)
            if push2_info:
                list_date = push2_info.get("list_date", "")
        except Exception as _e:
            _debug_log(f"datasource eastmoney push2 list_date error: {_e}")

    if not total_shares and price > 0 and mcap > 0:
        total_shares = int(mcap / price)  # V16.2.3: 单位=股（与 TDX zongguben 股口径一致）
    if not float_shares and price > 0 and float_mcap > 0:
        float_shares = int(float_mcap / price)  # V16.2.3: 同上

    try:
        tdx_boards = tdx_get_belong_boards(code)
        if tdx_boards and tdx_boards.get("industry"):
            industry = tdx_boards["industry"][0]["name"]
    except Exception as _e:
        _debug_log(f"datasource tdx belong boards error: {_e}")

    return {
        "code": code,
        "name": name,
        "industry": industry,
        "total_shares": total_shares,
        "float_shares": float_shares,
        "mcap": mcap,
        "float_mcap": float_mcap,
        "list_date": list_date,
        "price": price,
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
            "pageSize": "50",
            "industry": "*",
            "rating": "*",
            "beginTime": "2000-01-01",
            "endTime": "2030-01-01",
            "pageNo": str(page),
            "code": code,
            "qType": "0",
        }
        try:
            r = _quick_request(api_url, params=params, timeout=30)
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


def extract_report_valuation(reports: List[Dict[str, Any]]) -> Dict[str, Any]:
    """V16.1: 从研报原始记录提取规范化估值/评级字段（med/lng 用）。

    输入为 get_reports()/get_reports_async() 返回的原始东财 record 列表，
    输出统一结构：
        {
            "eps_this": float,      # 今年 EPS 预测（取最新一份非空）
            "eps_next": float,      # 明年 EPS 预测
            "eps_next2": float,     # 后年 EPS 预测
            "pe_this": float,       # 今年 PE 预测
            "pe_next": float,       # 明年 PE 预测
            "pe_next2": float,      # 后年 PE 预测
            "rating": str,          # 最新评级（买入/增持/...）
            "rating_last": str,     # 上次评级（评级变化判断）
            "rating_change": int,   # 评级变化标记（ratingChange）
            "org_name": str,        # 最新机构简称
            "publish_date": str,    # 最新发布日期
            "attach_pages": int,    # PDF 页数
            "attach_size": int,     # PDF 大小(KB)
        }
    无数据时返回全默认值 dict。
    """
    out = {
        "eps_this": 0.0, "eps_next": 0.0, "eps_next2": 0.0,
        "pe_this": 0.0, "pe_next": 0.0, "pe_next2": 0.0,
        "rating": "", "rating_last": "", "rating_change": 0,
        "org_name": "", "publish_date": "", "attach_pages": 0, "attach_size": 0,
    }
    if not reports:
        return out
    latest = reports[0]
    for rec in reports:
        if rec.get("publishDate") and rec["publishDate"] > latest.get("publishDate", ""):
            latest = rec

    def _f(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return 0.0

    out["eps_this"] = _f(latest.get("predictThisYearEps"))
    out["eps_next"] = _f(latest.get("predictNextYearEps"))
    out["eps_next2"] = _f(latest.get("predictNextTwoYearEps"))
    out["pe_this"] = _f(latest.get("predictThisYearPe"))
    out["pe_next"] = _f(latest.get("predictNextYearPe"))
    out["pe_next2"] = _f(latest.get("predictNextTwoYearPe"))
    out["rating"] = str(latest.get("emRatingName", "") or "")
    out["rating_last"] = str(latest.get("lastEmRatingName", "") or "")
    out["rating_change"] = int(latest.get("ratingChange", 0) or 0)
    out["org_name"] = str(latest.get("orgSName", "") or "")
    out["publish_date"] = str((latest.get("publishDate") or "") or "")[:10]
    out["attach_pages"] = int(latest.get("attachPages", 0) or 0)
    out["attach_size"] = int(latest.get("attachSize", 0) or 0)
    return out


async def get_reports_async(session: Any, code: str, max_pages: int = 3) -> List[Dict[str, Any]]:
    """async 版: 东财研报列表

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    """
    api_url = "https://reportapi.eastmoney.com/report/list"
    all_records = []
    for page in range(1, max_pages + 1):
        params = {
            "pageSize": "50",
            "industry": "*",
            "rating": "*",
            "beginTime": "2000-01-01",
            "endTime": "2030-01-01",
            "pageNo": str(page),
            "code": code,
            "qType": "0",
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
def get_industry_reports(
    industry_code: str = "*", max_pages: int = 3, begin_time: str = "2024-01-01"
) -> List[Dict[str, Any]]:
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
            r = em_get(
                api_url,
                params=params,
                headers={"Referer": "https://data.eastmoney.com/"},
                timeout=30,
            )
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


def get_eps_forecast(code: str, local_only: bool = False) -> "pd.DataFrame":  # LOW 修复: 实际返回 DataFrame
    """V7.5: 机构一致预期EPS — 同花顺正则提取 + 东财研报兜底.

    V17.0(2026-08-15): **本机 ProfitForecast JSON 优先(零网络)**——东财客户端
    data/ProfitForecast.dat(5,607 只, 评级数+2025A/2026E-2029E EPS/PE)。
    命中返回 DataFrame[年度, 机构数, 最小值, 均值, 最大值, 行业均值](同构兼容原契约);
    未命中回退原同花顺网络抓取 → 东财研报兜底。

    ⚠️ V17.0(2026-08-15): 文件一次性加载缓存(模块级)——val 全市场逐股调用时避免 5000 次
    2.5MB JSON 重复读取(性能修复)。

    Returns:
        DataFrame [年度, 机构数, 最小值, 均值, 最大值, 行业均值].
    """
    try:
        import pandas as _pd

        _idx = _profit_forecast_index()
        _r = _idx.get(code + ".")
        if _r is None:
            # M7 修复: 去后缀二级索引 O(1) 命中(免全表 startswith 扫描)
            _r = _PROFIT_FORECAST_INDEX_SHORT.get(code)
        if _r is not None:
            _rows = []
            for _i in range(1, 5):
                _y = _r.get(f"YEAR{_i}")
                _e = _r.get(f"EPS{_i}")
                if _y and _e:
                    _rows.append(
                        [str(_y) + ("A" if _r.get(f"YEAR_MARK{_i}") == "A" else "E"),
                         _r.get("RATING_ORG_NUM") or 0, _e, _e, _e, 0]
                    )
            if _rows:
                return _pd.DataFrame(
                    _rows, columns=["年度", "机构数", "最小值", "均值", "最大值", "行业均值"]
                )
        if local_only:  # H4 修复: 全市场扫描路径禁止网络兜底(限流)
            return _pd.DataFrame()
    except Exception as _e:
        _debug_log(f"datasource local ProfitForecast read error: {_e}")
    try:
        import re as _re2

        r = _quick_request(
            f"https://basic.10jqka.com.cn/new/{code}/worth.html",
            headers={"User-Agent": UA, "Referer": "https://basic.10jqka.com.cn/"},
            timeout=15,
        )
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

                    return _pd.DataFrame(
                        data_rows,
                        columns=["年度", "机构数", "最小值", "均值", "最大值", "行业均值"],
                    )
    except Exception as _e:
        _debug_log(f"datasource ths eps forecast parse error: {_e}")
    # 东财研报兜底
    try:
        from core.tdx_client import tdx_get_eps_from_reports

        em_eps = tdx_get_eps_from_reports(code)
        if em_eps and em_eps.get("eps_cur"):
            import pandas as _pd

            return _pd.DataFrame(
                {
                    "年度": ["预测今年", "预测明年"],
                    "机构数": [1, 1],
                    "最小值": [0, 0],
                    "均值": [em_eps["eps_cur"], em_eps.get("eps_next") or 0],
                    "最大值": [0, 0],
                    "行业均值": [0, 0],
                }
            )
    except Exception as _e:
        _debug_log(f"datasource tdx eps reports fallback error: {_e}")
    import pandas as _pd

    return _pd.DataFrame()


async def get_eps_forecast_async(session: Any, code: str) -> Dict[str, Any]:
    """async 版: 机构一致预期EPS — 同花顺正则提取 + TDX兜底"""
    try:
        import re as _re2

        r = await _async_quick_request(
            session,
            f"https://basic.10jqka.com.cn/new/{code}/worth.html",
            headers={"User-Agent": UA, "Referer": "https://basic.10jqka.com.cn/"},
            timeout=15,
            is_json=False,
            encoding='gbk',
        )
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

                    return _pd.DataFrame(
                        data_rows,
                        columns=["年度", "机构数", "最小值", "均值", "最大值", "行业均值"],
                    )
    except Exception as _e:
        _debug_log(f"datasource ths eps forecast async parse error: {_e}")

    try:
        from core.tdx_client import tdx_get_eps_from_reports

        em_eps = tdx_get_eps_from_reports(code)
        if em_eps and em_eps.get("eps_cur"):
            import pandas as _pd

            return _pd.DataFrame(
                {
                    "年度": ["预测今年", "预测明年"],
                    "机构数": [1, 1],
                    "最小值": [0, 0],
                    "均值": [em_eps["eps_cur"], em_eps.get("eps_next") or 0],
                    "最大值": [0, 0],
                    "行业均值": [0, 0],
                }
            )
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

    data = eastmoney_datacenter(
        code,
        "RPT_MUTUAL_HOLDSTOCKNORTH_STA",
        filter_str=f'(SECURITY_CODE="{code}")',
        page_size=days,
        sort_columns="TRADE_DATE",
        sort_types="-1",
    )

    rows = []
    has_valid_data = False
    for row in data:
        hold_shares = float(row.get("HOLD_SHARES") or 0)
        hold_ratio = float(
            row.get("FREE_SHARES_RATIO")
            or row.get("A_SHARES_RATIO")
            or row.get("TOTAL_SHARES_RATIO")
            or row.get("HOLD_RATIO")
            or 0
        )
        if hold_shares > 0 or hold_ratio > 0:
            has_valid_data = True

        rows.append(
            {
                "date": str(row.get("TRADE_DATE", "") or "")[:10],
                "hold_shares": hold_shares,
                "market_cap": float(row.get("HOLD_MARKET_CAP") or row.get("MARKET_CAP") or 0),
                "hold_ratio": hold_ratio,
                "change_shares": float(row.get("CHANGE_SHARES") or 0),
                "change_ratio": float(row.get("CHANGE_RATE") or 0),
            }
        )

    if not has_valid_data and len(rows) == 0:
        return _load_northbound_cache(code, days)

    return rows


# ── 北向资金本地CSV缓存辅助函数 ──

# V17.0(2026-08-15) H4 修复: 移除 @cached(DataFrame 不可 JSON 序列化→缓存永不生效);
# 改用模块级 SECUCODE→row 索引(O(1) 查表) + local_only 开关(全市场扫描不触发网络兜底)
_PROFIT_FORECAST_CACHE = None  # V17.0: 本机 ProfitForecast 一次性加载缓存
_PROFIT_FORECAST_INDEX: dict = {}  # V17.0: {SECUCODE: row} O(1) 索引
_PROFIT_FORECAST_INDEX_SHORT: dict = {}  # V17.0 M7: {去后缀 code: row} 二级索引(600519→O(1), 免全表扫描)
_YJYG_ALL_CACHE = None  # V17.0: 全市场业绩预告当日缓存
_PROFIT_CACHE_LOCK = None  # V17.0 M8: 懒加载锁(初始化于 _profit_forecast_index 首次调用)
_YJYG_LOCK = None  # V17.0 M8: get_yjyg_all 缓存锁


def _profit_forecast_index() -> dict:
    """一次性加载 ProfitForecast.dat 并建 SECUCODE→row 索引(H4 修复: 5000 次线性扫描→O(1)).

    M7 修复: 同时建去后缀二级索引(SECUCODE 去 .SH/.SZ), "600519" 直接 O(1) 命中。
    M8 修复: threading.Lock 保证并发下索引原子可见(窗口期不读空索引)。
    """
    global _PROFIT_FORECAST_CACHE, _PROFIT_FORECAST_INDEX, _PROFIT_FORECAST_INDEX_SHORT, _PROFIT_CACHE_LOCK
    if _PROFIT_CACHE_LOCK is None:
        import threading as _th

        _PROFIT_CACHE_LOCK = _th.Lock()
    if _PROFIT_FORECAST_CACHE is None:
        with _PROFIT_CACHE_LOCK:
            if _PROFIT_FORECAST_CACHE is None:
                try:
                    import json as _json

                    with open(r"C:\eastmoney\dfcf\data\ProfitForecast.dat", encoding="utf-8") as _f:
                        _PROFIT_FORECAST_CACHE = _json.load(_f)
                    _idx = {
                        str(_r.get("SECUCODE", "")): _r
                        for _r in (_PROFIT_FORECAST_CACHE.get("result", {}).get("data") or [])
                    }
                    _PROFIT_FORECAST_INDEX = _idx
                    _PROFIT_FORECAST_INDEX_SHORT = {
                        str(_k).split(".")[0]: _v for _k, _v in _idx.items()
                    }
                except Exception as _e:
                    _debug_log(f"datasource ProfitForecast index load error: {_e}")
                    _PROFIT_FORECAST_CACHE = {}
    return _PROFIT_FORECAST_INDEX

def _today_str() -> str:
    """当日 YYYYMMDD(缓存日期口径用)."""
    import datetime as _dt

    return _dt.date.today().strftime("%Y%m%d")


def get_yjyg_all() -> Dict[str, Dict[str, Any]]:
    """全市场业绩预告(V17.0 2026-08-15) — 一次分页拉取 + 当日缓存.

    ⚠️ 修复: 原逐股 get_yjyg 在 val 全市场扫描下=5000 次请求(限流灾难);
    本函数单次分页拉全量(窗口期全市场预告 ~500-1000 条), 策略按 code 过滤。
    M3 修复: 单股版 get_yjyg 已删除(死代码), 统一走本函数。
    M4 定案: 幅度键=ADD_AMP_LOWER/UPPER(INCREASE_RATE 恒 None), IS_LATEST=1 去重。
    M8 修复: threading.Lock + global 原子写缓存; M9: 动态年份; M1: 5 页上限。

    Returns:
        dict: {code: {predict_type, increase_rate, inc_lower, inc_upper, notice_date, report_date}}
    """
    global _YJYG_ALL_CACHE, _YJYG_LOCK
    if _YJYG_LOCK is None:
        import threading as _th

        _YJYG_LOCK = _th.Lock()
    _today = _today_str()
    _c = _YJYG_ALL_CACHE
    if _c is not None and _c.get("date") == _today:
        return _c.get("data") or {}
    out: Dict[str, Dict[str, Any]] = {}
    try:
        with _YJYG_LOCK:
            if _YJYG_ALL_CACHE is not None and _YJYG_ALL_CACHE.get("date") == _today:
                return _YJYG_ALL_CACHE.get("data") or {}
            _year = _today[:4]
            for _page in (1, 2, 3, 4, 5):  # M1: 5 页上限(2500 条), 空页 break
                rows = eastmoney_datacenter(
                    "",
                    "RPT_PUBLIC_OP_NEWPREDICT",
                    columns="ALL",
                    filter_str=f"(REPORT_DATE>='{_year}-01-01')",  # M2/M9: 区间过滤+动态年份
                    page_size=500,
                    sort_columns="NOTICE_DATE",
                    sort_types="-1",
                    page_index=_page,
                )
                if not rows:
                    break
                for r in rows:
                    code = str(r.get("SECURITY_CODE", "") or "").strip()
                    if not code:
                        continue
                    if str(r.get("IS_LATEST", "") or "") == "1" or code not in out:
                        out[code] = {
                            "predict_type": str(r.get("PREDICT_TYPE", "") or ""),
                            "increase_rate": (
                                _safe_float(r.get("ADD_AMP_UPPER"))
                                or _safe_float(r.get("ADD_AMP_LOWER"))
                                or 0.0
                            ),
                            "inc_lower": _safe_float(r.get("ADD_AMP_LOWER")),
                            "inc_upper": _safe_float(r.get("ADD_AMP_UPPER")),
                            "notice_date": str(r.get("NOTICE_DATE", "") or "")[:10],
                            "report_date": str(r.get("REPORT_DATE", "") or "")[:10],
                        }
            _YJYG_ALL_CACHE = {"date": _today, "data": out}
    except Exception as _e:
        _debug_log(f"datasource get_yjyg_all error: {_e}")
    return dict(out)  # L4: 返回副本, 防调用方污染缓存



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
                    rows.append(
                        {
                            "date": parts[0],
                            "hold_shares": float(parts[1]),
                            "market_cap": float(parts[2]),
                            "hold_ratio": float(parts[3]),
                            "change_shares": float(parts[4]),
                            "change_ratio": float(parts[5]),
                        }
                    )
    except Exception as _e:
        _debug_log(f"datasource northbound cache load error: {_e}")

    return rows[-days:] if rows else rows


async def get_northbound_hold_async(
    session: Any, code: str, days: int = 20
) -> List[Dict[str, Any]]:
    """async 版: 北向资金持仓动态

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    """
    import os

    data = await eastmoney_datacenter_async(
        session,
        code,
        "RPT_MUTUAL_HOLDSTOCKNORTH_STA",
        filter_str=f'(SECURITY_CODE="{code}")',
        page_size=days,
        sort_columns="TRADE_DATE",
        sort_types="-1",
    )

    rows = []
    has_valid_data = False
    for row in data:
        hold_shares = float(row.get("HOLD_SHARES") or 0)
        hold_ratio = float(
            row.get("FREE_SHARES_RATIO")
            or row.get("A_SHARES_RATIO")
            or row.get("TOTAL_SHARES_RATIO")
            or row.get("HOLD_RATIO")
            or 0
        )
        if hold_shares > 0 or hold_ratio > 0:
            has_valid_data = True

        rows.append(
            {
                "date": str(row.get("TRADE_DATE", "") or "")[:10],
                "hold_shares": hold_shares,
                "market_cap": float(row.get("HOLD_MARKET_CAP") or row.get("MARKET_CAP") or 0),
                "hold_ratio": hold_ratio,
                "change_shares": float(row.get("CHANGE_SHARES") or 0),
                "change_ratio": float(row.get("CHANGE_RATE") or 0),
            }
        )

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
        from core.tdx_client import tdx_get_latest_reminders

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
                    rows.append(
                        {
                            "date": date_val,
                            "rzye": rzye_val,
                            "rzmre": rzmre_val,
                            "rzche": 0.0,
                            "rqye": rqye_val,
                            "rqmcl": rqmcl_val,
                            "rqchl": 0.0,
                            "rzrqye": rzrqye_val,
                        }
                    )
                if rows:
                    return rows
    except Exception as _e:
        _debug_log(f"datasource tdx margin trading f10 error: {_e}")
    # Fallback: 东财 HTTP
    data = eastmoney_datacenter(
        code,
        "RPTA_WEB_RZRQ_GGMX",
        filter_str=f'(SCODE="{code}")',
        page_size=15,
        sort_columns="DATE",
        sort_types="-1",
    )
    rows = []
    for row in data:
        r = {
            "date": str(row.get("DATE", "") or "")[:10],
            "rzye": float(row.get("RZYE") or 0),
            "rzmre": float(row.get("RZMRE") or 0),
            "rzche": float(row.get("RZCHE") or 0),
            "rqye": float(row.get("RQYE") or 0),
            "rqmcl": float(row.get("RQMCL") or 0),
            "rqchl": float(row.get("RQCHL") or 0),
            "rzrqye": float(row.get("RZRQYE") or 0),
        }
        # V16.1: 保留中线资金确认字段（med 用）
        if row.get("RZJME") is not None:
            r["rzjme"] = float(row["RZJME"])
        if row.get("RQJMG") is not None:
            r["rqjmg"] = float(row["RQJMG"])
        if row.get("RZCHE10D") is not None:
            r["rzche_10d"] = float(row["RZCHE10D"])
        if row.get("RZMRE10D") is not None:
            r["rzmre_10d"] = float(row["RZMRE10D"])
        if row.get("RZCHE5D") is not None:
            r["rzche_5d"] = float(row["RZCHE5D"])
        if row.get("RZMRE5D") is not None:
            r["rzmre_5d"] = float(row["RZMRE5D"])
        if row.get("RCHANGE5DCP") is not None:
            r["chg_5d"] = float(row["RCHANGE5DCP"])
        if row.get("RCHANGE10DCP") is not None:
            r["chg_10d"] = float(row["RCHANGE10DCP"])
        if row.get("FIN_BALANCE_GR") is not None:
            r["balance_gr"] = float(row["FIN_BALANCE_GR"])
        rows.append(r)
    return rows


async def get_margin_trading_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """async 版: 融资融券数据

    V9.0: 委托到同步版（已内置 F10 优先逻辑），保留 session 参数向后兼容。
    V17.0.9: 返回类型防御——to_thread 偶发返回非 list(dict/None)时置 [],
    防止批量消费端 for d in margin 遍历 dict keys 报 TypeError(300475 实测)。
    """
    import asyncio

    res = await asyncio.to_thread(get_margin_trading, code)
    if not isinstance(res, list):
        _debug_log(f"datasource margin_async({code}): 非 list 返回 {type(res).__name__}, 置 []")
        return []
    return res


@cached(category="block_trade", ttl_seconds=TTL["block_trade"])
def get_block_trade(code: str) -> List[Dict[str, Any]]:
    """大宗交易数据。

    Returns:
        list: [{date, price, close, premium_pct, vol, amount, buyer, seller}, ...]。

    V9.1: 移除 F10 优先逻辑（F10 缺 close_price 和 premium_pct，且 volume 单位
          与东财 HTTP 不一致）。保留东财 HTTP 为主力数据源。
    """
    # 东财 HTTP
    data = _em_filter(
        code, "RPT_DATA_BLOCKTRADE", page_size=15, sort_columns="TRADE_DATE", sort_types="-1"
    )
    rows = []
    for row in data:
        close = float(row.get("CLOSE_PRICE") or 0)
        deal_price = float(row.get("DEAL_PRICE") or 0)
        premium = ((deal_price / close - 1) * 100) if close else 0
        rows.append(
            {
                "date": str(row.get("TRADE_DATE", "") or "")[:10],
                "price": deal_price,
                "close": close,
                "premium_pct": round(premium, 2),
                "vol": float(row.get("DEAL_VOLUME") or 0),
                "amount": float(row.get("DEAL_AMT") or 0),
                "buyer": str(row.get("BUYER_NAME", "") or ""),
                "seller": str(row.get("SELLER_NAME", "") or ""),
            }
        )
    return rows


async def get_block_trade_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """async 版: 大宗交易数据

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    V17.0.9: data 类型防御——_em_filter_async 偶发返回 dict 时置 [].
    """
    data = await _em_filter_async(
        session,
        code,
        "RPT_DATA_BLOCKTRADE",
        page_size=15,
        sort_columns="TRADE_DATE",
        sort_types="-1",
    )
    if not isinstance(data, list):
        _debug_log(f"datasource block_trade_async({code}): 非 list 返回 {type(data).__name__}, 置 []")
        data = []
    rows = []
    for row in data:
        close = float(row.get("CLOSE_PRICE") or 0)
        deal_price = float(row.get("DEAL_PRICE") or 0)
        premium = ((deal_price / close - 1) * 100) if close else 0
        rows.append(
            {
                "date": str(row.get("TRADE_DATE", "") or "")[:10],
                "price": deal_price,
                "close": close,
                "premium_pct": round(premium, 2),
                "vol": float(row.get("DEAL_VOLUME") or 0),
                "amount": float(row.get("DEAL_AMT") or 0),
                "buyer": str(row.get("BUYER_NAME", "") or ""),
                "seller": str(row.get("SELLER_NAME", "") or ""),
            }
        )
    return rows


# ═══════════════════════════════════════════════════════════
# V17.0.7: datacenter 五类批量预取流水线(sht 30 只批量场景)
# ───────────────────────────────────────────────────────────
# 动机(2026-08-25 审计): datacenter-web 1.0rps × 每股5类调用(龙虎榜/两融/北向/
# 解禁/大宗) ≈ 每股5秒纯令牌桶等待, 是 sht 批量最大单项; 且 worker 只有 3 条,
# dc 等待会占住车道。预取流水线在批量启动时按域串行(1rps)拉全批, 与 3 条
# worker 的非 dc 部分(TCP F10/腾讯/巨潮/fuyao/CPU渲染)并行推进——
# 消费速率(~9s/只÷3)慢于生产速率(~5s/只), 预取始终领先。
_DC_PREFETCH_FUTURES: Dict[Any, Any] = {}  # (kind, code) -> asyncio.Future


def start_datacenter_prefetch(codes, session, dragon_kwargs=None) -> int:
    """调度五类 datacenter 数据的整批预取(幂等——已调度的 (kind,code) 跳过)。

    必须在事件循环内调用(execute_batch_pipeline 的 prefetch_async_fn 钩子)。
    消费侧用 resolve_datacenter('kind', code) 取结果; 未调度的键走调用方直调。

    Returns:
        本次新入队的 (kind, code) 项数
    """
    import asyncio as _aio

    dk = dragon_kwargs or {}
    specs = {
        "dragon_tiger": lambda c: get_dragon_tiger_board_async(
            session, c, days=180,
            include_seats=dk.get("include_seats", True),
            enhance_seats=dk.get("enhance_seats", True)),
        "northbound": lambda c: get_northbound_hold_async(session, c, 20),
        "margin": lambda c: get_margin_trading_async(session, c),
        "lockup": lambda c: get_lockup_expiry_async(
            session, c, days=90, include_history=True),
        "block_trade": lambda c: get_block_trade_async(session, c),
    }
    loop = _aio.get_event_loop()
    scheduled = 0
    for kind, fetch in specs.items():
        todo = [c for c in codes if (kind, c) not in _DC_PREFETCH_FUTURES]
        if not todo:
            continue
        futs = {c: loop.create_future() for c in todo}
        # 先注册后执行——消费方随时 await 不竞态
        _DC_PREFETCH_FUTURES.update(futs)

        async def _run(_todo=todo, _futs=futs, _fetch=fetch, _kind=kind):
            for c in _todo:
                try:
                    res = await _fetch(c)
                except Exception as e:
                    _debug_log(f"datasource dc prefetch {_kind}/{c}: {e}")
                    res = None
                if not _futs[c].done():
                    _futs[c].set_result(res)

        loop.create_task(_run())
        scheduled += len(todo)
    return scheduled


async def resolve_datacenter(kind: str, code: str, direct_fn=None):
    """取预取结果; 该键未参与预取时回退 direct_fn()(原直调协程工厂)。"""
    fut = _DC_PREFETCH_FUTURES.get((kind, code))
    if fut is not None:
        return await fut
    if direct_fn is not None:
        return await direct_fn()
    return None


@cached(category="dividend", ttl_seconds=TTL["dividend"], cross_verify=True)
def get_dividend_history(code):
    """V7.5: 分红历史 → TDX xdxr_info（东财 fallback 已删除）"""
    from core.tdx_client import tdx_get_dividend_history

    return tdx_get_dividend_history(code)


async def get_dividend_history_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """异步版 get_dividend_history"""
    import asyncio

    return await asyncio.to_thread(get_dividend_history, code)


@cached(category="concept_blocks", ttl_seconds=TTL["concept_blocks"], cross_verify=True)
def get_concept_blocks(code: str) -> Dict[str, Any]:
    """V7.5 + V15.4 方案 C: 概念板块 — TDX 优先, ZHB tdxchain.cfg 兜底。

    返回: {"industry": [...], "concept": [...], "region": [...], "concept_tags": [...]}

    V15.4 改进:
      - TDX boards concept 优先
      - 概念为空时 fallback 到 ZHB get_concept_from_zhb (解析 tdxchain.cfg)
      - 避免 V15.3 实测"概念板块 0 个"问题（sht 报告对比 V9.6 缺 16 个概念）
    """
    from core.tdx_client import tdx_get_belong_boards

    boards = tdx_get_belong_boards(code) or {}
    result = {
        "industry": boards.get("industry", []),
        "concept": boards.get("concept", []),
        "region": boards.get("area", []),
        "concept_tags": [c["name"] for c in boards.get("concept", []) if c.get("name")],
    }
    # V15.4: 概念为空时 fallback 到 ZHB concept_chain (tdxchain.cfg)
    if not result["concept"]:
        try:
            from core.data_provider import get_concept_from_zhb

            zhb_concepts = get_concept_from_zhb(code) or []
            if zhb_concepts:
                # ZHB 返回的是概念名列表, 包装成 TDX 同样的 dict 格式
                result["concept"] = [
                    {"name": cn, "code": "", "type": "concept"} for cn in zhb_concepts
                ]
                result["concept_tags"] = list(zhb_concepts)
                _debug_log(
                    f"get_concept_blocks ZHB fallback OK ({code}): {len(zhb_concepts)} concepts"
                )
        except Exception as _e:
            _debug_log(f"get_concept_blocks ZHB fallback error ({code}): {_e}")
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
_THS_HOT_REASON_CACHE: Dict[str, list] = {}  # V17.0 S4: {date_str: 原始行 list[dict]}(get_ths_hot_raw 缓存)


def get_ths_hot_raw(date_str: str) -> list:
    """V17.0 S4: 同花顺 getharden 原始列表(三版收敛的唯一请求入口)。

    返回当日强势股行列表 list[dict]（含 id/name/code/reason/date/market），失败返回 []。
    V17.0 探针实测(2026-08-13): 响应 UTF-8 JSON, r.json() 直接解析即可——原 mak 版
    GBK 重试分支永不触发(死分支); 失败不写负缓存(原 async 版写 {} 会毒化后续调用)。
    """
    _cached_rows = _THS_HOT_REASON_CACHE.get(date_str)
    if _cached_rows is not None:
        return _cached_rows
    url = f"http://zx.10jqka.com.cn/event/api/getharden/date/{date_str}/orderby/date/orderway/desc/charset/GBK/"
    try:
        r = _quick_request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"},
            timeout=10,
        )
        if r is None:
            return []
        d = r.json()
        if str(d.get("errocode", 0)) != "0":
            return []
        rows = d.get("data") or []
        _THS_HOT_REASON_CACHE[date_str] = rows
        return rows
    except Exception as _e:
        _debug_log(f"datasource ths hot raw error: {_e}")
    return []


def get_ths_hot_reason(code: str, date_str: str) -> Optional[Dict[str, Any]]:
    """V7.5: 同花顺热点题材归因（短线脚本抽取统一）。

    返回: {"reason": str} 或 None。
    V16.2: 进程级缓存 —— 按 date_str 缓存全市场结果（HTTP 接口一次返回当日全部涨停股原因，
    原逐股重复请求；sht 全市场 7000+ 只 → 1 次）。
    V17.0 S4: 底层统一走 get_ths_hot_raw（三版收敛, 缓存存原始行）。
    """
    rows = get_ths_hot_raw(date_str)
    for row in rows:
        if str(row.get("code")) == str(code) and row.get("reason"):
            return {"reason": row["reason"]}
    return None


async def get_ths_hot_reason_async(
    session: Any, code: str, date_str: str
) -> Optional[Dict[str, Any]]:
    """V7.5: 同花顺热点题材归因

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    V16.2: 复用同步版进程缓存（按 date_str 一次拉取）。
    V17.0 S4: 底层统一走同步 get_ths_hot_raw（to_thread 执行，三版收敛）。
    """
    rows = _THS_HOT_REASON_CACHE.get(date_str)
    if rows is None:
        import asyncio

        await asyncio.to_thread(get_ths_hot_raw, date_str)
        rows = _THS_HOT_REASON_CACHE.get(date_str) or []
    for row in rows:
        if str(row.get("code")) == str(code) and row.get("reason"):
            return {"reason": row["reason"]}
    return None


# 行业对比
@cached(
    category="industry_peers_v2",
    ttl_seconds=TTL["industry_peers_v2"],
    trading_day=True,
    valid_if=lambda r: isinstance(r, dict)
    and bool(r.get("peers"))
    and any(p.get("price", 0) > 0 for p in r["peers"] if isinstance(p, dict)),
)
def get_industry_peers(
    code: str, top_n: int = 3, info: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """V7.5: 同业对比 — TDX 三级兜底（belong_board → board_members → board_by_name）。

    返回: {
        "industry": str, "my_mcap": float, "my_rank": int, "industry_count": int,
        "peers": [...], "all_members": [...]
    }
    """
    from core.tdx_client import tdx_get_belong_boards, tdx_get_board_members, tdx_get_board_by_name
    from stock_common.sc_utils import _load_strategy_config

    _sc = _load_strategy_config()
    _mkt_cfg = _sc.get("market", {})
    _peers_low = _mkt_cfg.get("peers_mcap_low", 0.3)
    _peers_high = _mkt_cfg.get("peers_mcap_high", 3.0)

    # 0. V16.2.17: 东财申万二级优先（datacenter 一次性映射缓存，零逐股请求；
    # 成员市值用腾讯批量（进程内按交易日缓存，跨 mak/val/sht 复用））
    try:
        _l2 = get_em_industry_l2(code)
        if _l2:
            _l2_members = get_em_industry_members_l2(_l2)
            if _l2_members:
                from core.tdx_client import _tencent_batch_fallback

                _tq = _tencent_batch_fallback(_l2_members) or {}
                _rows = []
                for _mc in _l2_members:
                    # 过滤 B 股（200xxx/900xxx）与非 A 股代码，避免排行污染
                    if len(_mc) != 6 or not _mc.isdigit() or _mc[:2] not in ("00", "30", "60", "68", "92"):
                        continue
                    _q = _tq.get(_mc) or {}
                    _rows.append(
                        {
                            "code": _mc,
                            "name": _q.get("name", _mc),
                            "price": _q.get("price", 0) or 0,
                            "change_pct": _q.get("change_pct", 0) or 0,
                            "mcap_yi": _q.get("mcap_yi", 0) or 0,
                            "pe": _q.get("pe_ttm", 0) or 0,
                            "turnover": _q.get("turnover_pct", 0) or 0,
                        }
                    )
                _by_mcap = sorted(_rows, key=lambda x: x["mcap_yi"], reverse=True)
                _my_mcap = next((r["mcap_yi"] for r in _by_mcap if r["code"] == code), 0)
                _my_rank = next((i for i, r in enumerate(_by_mcap, 1) if r["code"] == code), 0)
                _others = [r for r in _by_mcap if r["code"] != code]
                _peers = []
                if _others:
                    _peers.append(_others[0])  # 行业龙头
                if _my_mcap > 0:
                    _similar = [
                        r
                        for r in _others[1:]
                        if _peers_low * _my_mcap <= r["mcap_yi"] <= _peers_high * _my_mcap
                    ]
                    _peers += _similar[: top_n - 1]
                if len(_peers) < top_n:
                    _peers += [r for r in _others if r not in _peers][: top_n - len(_peers)]
                return {
                    "industry": _l2,
                    "my_mcap": _my_mcap,
                    "my_rank": _my_rank,
                    "industry_count": len(_l2_members),
                    "peers": _peers[:top_n],
                    "all_members": _by_mcap,
                }
    except Exception as _e:
        _debug_log(f"datasource get_industry_peers em_l2 ({code}): {_e}")

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
                similar = [
                    m
                    for m in others[1:]
                    if _peers_low * my_mcap <= m.get("mcap_yi", 0) <= _peers_high * my_mcap
                ]
                peers += similar[: top_n - 1]
            if len(peers) < top_n:
                peers += [m for m in others if m not in peers][: top_n - len(peers)]

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
                similar = [
                    s
                    for s in others[1:]
                    if _peers_low * my_mcap <= s.get("mcap_yi", 0) <= _peers_high * my_mcap
                ]
                peers += similar[: top_n - 1]
            if len(peers) < top_n:
                peers += [s for s in others if s not in peers][: top_n - len(peers)]
            return {
                "industry": ind_name,
                "my_mcap": my_mcap,
                "my_rank": my_rank,
                "industry_count": len(st),
                "peers": peers[:top_n],
            }

    # 3. V9.0 Fallback: F10 行业分析（仅返回行业名 + 公司规模排名，无 peer 市值）
    try:
        from core.tdx_client import tdx_get_industry_analysis

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
                peers.append(
                    {
                        "code": r.get('代码', r.get('股票代码', '')),
                        "name": r.get('名称', r.get('股票简称', '')),
                        "price": 0,
                        "change_pct": 0,
                        "mcap_yi": 0,
                        "pe": 0,
                        "turnover": 0,
                    }
                )
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


@cached(category="industry_peers_v2", ttl_seconds=TTL["industry_peers_v2"], trading_day=True)
def get_stock_sector_rank(
    code: str, info: Optional[Dict[str, Any]] = None, q: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """V7.5: 板块内排名 — V16.2.17 东财申万二级优先（TDX 兜底）。

    返回: {"rank": int, "total": int, "change_pct": float} 或 None。
    """
    # 0. V16.2.17: 东财申万二级成员（datacenter 一次性映射缓存 + 腾讯实时涨跌幅）
    try:
        _l2 = get_em_industry_l2(code)
        if _l2:
            _l2_members = get_em_industry_members_l2(_l2)
            if _l2_members:
                from core.tdx_client import _tencent_batch_fallback

                _tq = _tencent_batch_fallback(_l2_members) or {}
                _rows = []
                for _mc in _l2_members:
                    if len(_mc) != 6 or not _mc.isdigit() or _mc[:2] not in ("00", "30", "60", "68", "92"):
                        continue
                    _q = _tq.get(_mc) or {}
                    _rows.append({"code": _mc, "change_pct": _q.get("change_pct", 0) or 0})
                _by_chg = sorted(_rows, key=lambda x: x["change_pct"], reverse=True)
                _chg = q.get("change_pct", 0) if q else 0
                if not _chg:
                    _chg = next((r["change_pct"] for r in _by_chg if r["code"] == code), 0)
                for i, _r in enumerate(_by_chg, 1):
                    if _r["code"] == code:
                        return {"rank": i, "total": len(_by_chg), "change_pct": _chg}
    except Exception as _e:
        _debug_log(f"datasource get_stock_sector_rank em_l2 ({code}): {_e}")

    from core.tdx_client import tdx_get_belong_boards, tdx_get_board_members, tdx_get_board_by_name

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
    ind_name = (industry_boards[0].get("name", "") if industry_boards else "") or (
        info.get("industry", "") if info else ""
    )
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


def get_industry_rank_from_zhb(top_n: int = 20) -> List[Dict[str, Any]]:
    """ZHB 本地行业排名（V16.3 O25——用户：行业可比/排名 ZHB 就能获取，参照系 T-1 可接受）。

    从 get_zhb_full_market_snapshot + 申万二级映射（_em_ind_map 缓存）自聚合：
    市值加权涨跌幅 + 涨跌家数 + 领涨股——零网络（ZHB 内存 + L2 JSON 缓存）。
    输出兼容 tdx_get_board_list 格式：[{rank, code, name, change_pct, up_count, down_count,
    leader_name, leader_change, amount_yi, _member_count}]——lng/med/sht 行业排名参照系直用。
    """
    try:
        from core.zhb_client import get_zhb

        snap = get_zhb_full_market_snapshot()
        if not snap:
            return []
        zhb = get_zhb()
        industry_map = zhb.industry_map or {}
        # 申万二级映射（东财 L2 缓存——7 天 JSON，不联网）
        _em_ind_map: Dict[str, str] = {}
        try:
            _em_ind_map, _ = get_em_industry_l2_data()
        except Exception:
            pass
        buckets: Dict[str, dict] = {}
        for code, stat in snap.items():
            ind_code = stat.get("industry_code", "")
            # 内联行业段判定（mak _is_industry_code 逻辑：8803/8804/881 通达信行业/申万段）
            _valid_ind = (
                bool(ind_code)
                and len(str(ind_code)) == 6
                and str(ind_code).isdigit()
                and str(ind_code).startswith(("8803", "8804", "881"))
            )
            ind_code = _em_ind_map.get(code, "") or (ind_code if _valid_ind else "")
            if not ind_code:
                continue
            chg = _safe_float(stat.get("change_pct", 0))
            mcap = _safe_float(stat.get("mcap_yi", 0))
            amt = (_safe_float(stat.get("amount", 0)) or 0) / 10000.0
            b = buckets.setdefault(
                ind_code,
                {"_chgs": [], "_mcaps": [], "_amts": [], "_up": 0, "_down": 0,
                 "_best_chg": -999.0, "_best_name": ""},
            )
            b["_chgs"].append(chg)
            b["_mcaps"].append(mcap)
            b["_amts"].append(amt)
            if chg > 0:
                b["_up"] += 1
            elif chg < 0:
                b["_down"] += 1
            if chg > b["_best_chg"]:
                b["_best_chg"] = chg
                b["_best_name"] = zhb.get_stock_name(code) or ""
        rows = []
        for ind_code, b in buckets.items():
            total_mcap = sum(b["_mcaps"])
            if total_mcap > 0 and b["_mcaps"]:
                wchg = sum(c * m for c, m in zip(b["_chgs"], b["_mcaps"])) / total_mcap
            elif b["_chgs"]:
                wchg = sum(b["_chgs"]) / len(b["_chgs"])
            else:
                wchg = 0
            rows.append(
                {
                    "rank": 0,
                    "code": ind_code,
                    "name": industry_map.get(ind_code, ind_code),
                    "change_pct": round(wchg, 2),
                    "up_count": b["_up"],
                    "down_count": b["_down"],
                    "amount_yi": round(sum(b["_amts"]), 2),
                    "leader_name": b["_best_name"],
                    "leader_change": round(b["_best_chg"], 2),
                    "_member_count": len(b["_chgs"]),
                }
            )
        rows.sort(key=lambda x: -x["change_pct"])
        for i, r in enumerate(rows):
            r["rank"] = i + 1
        return rows
    except Exception as _e:
        _debug_log(f"datasource get_industry_rank_from_zhb: {_e}")
        return []


@cached(category="industry_compare", ttl_seconds=TTL["industry_compare"], trading_day=True, valid_if=make_valid_if())
def get_industry_comparison(top_n: int = 20) -> Dict[str, Any]:
    """V4.2: 全行业排名 → ZHB 本地优先（V16.3 O25——用户：ZHB 就能获取，参照系 T-1 可接受），
    TDX board_list / 东财 push2 兜底。

    Args:
        top_n: 返回行业数量上限（当前未使用，保留参数兼容性）。

    Returns:
        dict: {"top": 涨幅TOP, "bottom": 跌幅TOP, "all": 全部行业, "total": 行业总数}。
    """
    # V16.3 O25: ZHB 本地聚合优先（零网络）——参照系 T-1 可接受
    _zhb_rows = get_industry_rank_from_zhb(top_n)
    if _zhb_rows:
        _top = _zhb_rows[:5]
        _bottom = _zhb_rows[-5:][::-1]
        return {"top": _top, "bottom": _bottom, "all": _zhb_rows, "total": len(_zhb_rows)}
    from core.tdx_client import tdx_get_board_list

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


@requires_push2
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
            sectors.append(
                {
                    "name": item.get("f14", ""),
                    "code": item.get("f12", ""),
                    "change_pct": item.get("f3", 0),
                    "up_count": item.get("f104", 0),
                    "down_count": item.get("f105", 0),
                    "leader": item.get("f140", ""),
                    "leader_change": item.get("f136", 0),
                }
            )

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
        from core.tdx_client import tdx_get_company_news_f10

        f10_news = tdx_get_company_news_f10(code, count=page_size)
        if f10_news:
            return [
                {
                    "title": n.get('title', ''),
                    "publish_time": n.get('date', ''),
                    "source": "F10",
                    "summary": n.get('summary', ''),
                    "url": n.get('url', ''),
                }
                for n in f10_news
            ]
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
        "client": "web",
        "biz": "web_724",
        "fastColumn": "102",
        "sortEnd": "",
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
            news_items.append(
                {
                    "title": item.get("title", ""),
                    "publish_time": item.get("showTime", ""),
                    "content": item.get("summary", "")[:200],
                    "type": item.get("type", ""),
                }
            )

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


def get_sina_financial_report(code: str, num_periods: int = 12) -> Dict[str, Any]:
    """新浪利润表 — 支持多期数（默认12期 ≈ 3年）
    V13.1: 彻底实现 ZHB 财报事件锁，抛弃 24小时 粗暴刷新。
    将 ZHB 的 report_date 拼入缓存 Key，实现永久缓存 + 瞬间刷新。
    """
    from core.stock_cache import get_cache, set_cache
    from stock_common import get_zhb_single_stock_data

    zhb = get_zhb_single_stock_data(code)
    report_date = zhb.get("report_date", "unknown") if zhb else "unknown"

    cache_value = get_cache(
        "financial",
        "get_sina_financial_report",
        code,
        num_periods,
        report_date=report_date,
        cross_verify=True,
    )
    if cache_value is not None:
        return cache_value

    # 新浪 HTTP
    # V16.3 O16: 北交所 920 号段走 bj 前缀（此前落 sz 静默查不到财报）
    prefix = "bj" if code.startswith(("92", "8", "4", "43", "83", "87")) else ("sh" if code.startswith("6") else "sz")
    paper_code = f"{prefix}{code}"
    url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
    params = {
        "paperCode": paper_code,
        "source": "lrb",
        "type": "0",
        "page": "1",
        "num": str(num_periods),
    }
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
            rows.append(
                {
                    "报告日": f"{date_key[:4]}-{date_key[4:6]}-{date_key[6:8]}",
                    "营业总收入": item_map.get("营业总收入") or "0",
                    "营业成本": item_map.get("营业成本") or "0",
                    "净利润": item_map.get("归属于母公司所有者的净利润")
                    or item_map.get("净利润")
                    or "0",
                }
            )
        if rows:
            # 永久缓存 (365天)，仅当 report_date 突变时 Key 变更
            set_cache(
                "financial",
                "get_sina_financial_report",
                rows,
                365 * 24 * 3600,
                code,
                num_periods,
                report_date=report_date,
                cross_verify=True,
            )
        return rows
    except Exception as _e:
        _debug_log(f"datasource get_sina_financial_report ({code}): {_e}")
        return []


async def get_sina_financial_report_async(
    session: Any, code: str, num_periods: int = 12
) -> Dict[str, Any]:
    """async 版: 新浪利润表

    V16.1: 委托同步版（复用 @cached SQLite 缓存 + report_date 事件锁），
    避免 async 直连绕过缓存导致 med/lng 重复请求。session 参数向后兼容。
    """
    import asyncio

    return await asyncio.to_thread(get_sina_financial_report, code, num_periods)


@cached(category="balance_sheet", ttl_seconds=TTL["balance_sheet"], cross_verify=True, trading_day=True, valid_if=make_valid_if())
def get_sina_balance_sheet(code: str) -> List[Dict[str, Any]]:
    """获取新浪资产负债表（fzb）最近5期数据

    V9.1: 移除 F10 优先逻辑（F10 是万元单位，与渲染代码按元处理不一致）。
          保留新浪 HTTP 为主力数据源（元单位，数据完整）。
    """
    # 新浪 HTTP
    try:
        # V16.3 O16: 北交所 920/8/4 号段走 bj 前缀
        prefix = "bj" if code.startswith(("92", "8", "4", "43", "83", "87")) else ("sh" if code.startswith("6") else "sz")
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
            rows.append(
                {
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
                    "归属于母公司股东权益合计": (
                        item_map.get("归属于母公司股东权益合计")
                        or item_map.get("归属于母公司股东的权益")
                        or item_map.get("股东权益")
                        or "0"
                    ),
                }
            )
        return rows if rows else None
    except Exception as _e:
        _debug_log(f"datasource get_sina_balance_sheet ({code}): {_e}")
        return None


async def get_sina_balance_sheet_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """async 版: 新浪资产负债表

    V16.1: 委托同步版（复用 @cached SQLite 缓存），避免 async 直连绕过缓存。
    session 参数向后兼容。
    """
    import asyncio

    return await asyncio.to_thread(get_sina_balance_sheet, code)


@cached(category="cash_flow", ttl_seconds=TTL["cash_flow"], cross_verify=True, trading_day=True, valid_if=make_valid_if())
def get_eastmoney_cash_flow(code: str) -> List[Dict[str, Any]]:
    """获取东财现金流量表（新浪xjllb接口已失效，使用东财数据中心替代）

    V9.6: 新增，使用东财数据中心RPT_CASHFLOW表获取现金流量数据。
    """
    data = eastmoney_datacenter(
        code,
        "RPT_CASHFLOW",
        filter_str=f"(SECURITY_CODE=\"{code}\")",
        page_size=5,
        sort_columns="REPORT_DATE",
        sort_types="-1",
    )
    if not data:
        return []

    rows = []
    for r in data:
        rows.append(
            {
                "报告日": str(r.get("REPORT_DATE", "") or "")[:10],
                "经营活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_OPERATING", "") or "0"),
                "投资活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_INVESTING", "") or "0"),
                "筹资活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_FINANCING", "") or "0"),
                "现金及现金等价物净增加额": str(r.get("NET_INCREASE_CASH_EQUIVALENTS", "") or "0"),
            }
        )
    return rows


async def get_eastmoney_cash_flow_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """async 版: 东财现金流量表

    V9.6: 新增，使用东财数据中心RPT_CASHFLOW表获取现金流量数据。
    """
    data = await eastmoney_datacenter_async(
        session,
        code,
        "RPT_CASHFLOW",
        filter_str=f"(SECURITY_CODE=\"{code}\")",
        page_size=5,
        sort_columns="REPORT_DATE",
        sort_types="-1",
    )
    if not data:
        return []

    rows = []
    for r in data:
        rows.append(
            {
                "报告日": str(r.get("REPORT_DATE", "") or "")[:10],
                "经营活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_OPERATING", "") or "0"),
                "投资活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_INVESTING", "") or "0"),
                "筹资活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_FINANCING", "") or "0"),
                "现金及现金等价物净增加额": str(r.get("NET_INCREASE_CASH_EQUIVALENTS", "") or "0"),
            }
        )
    return rows


@cached(
    category="hsgt_macro_flow", ttl_seconds=TTL["hsgt_macro_flow"], trading_day=True, use_args=False
)
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
        # V17.0.4(2026-08-19 实测): 同花顺接口字段错位——hgt=当日分时(262 点 09:10-15:00),
        # sgt=历史收盘序列(35 点), 长度不同步 → sgt[-1] 恒为陈旧值(8/12-8/19 冻结在 379.75,
        # 全仓 47 份 sht/med 报告北向恒 -9.28/+379.75 系此根因)。长度不一致即判 invalid 拒绝展示。
        if len(hgt) != len(sgt):
            _debug_log("hsgt_macro_flow: hgt/sgt 序列长度不一致({}/{})——数据源字段错位, 拒绝展示".format(len(hgt), len(sgt)))
            return {
                "hgt": 0.0, "sgt": 0.0, "total": 0.0,
                "data_quality": "invalid", "warning": "北向数据源 hgt/sgt 序列错位(字段长度不同步), 当日值暂缺",
            }
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

        return {
            "hgt": hgt_val,
            "sgt": sgt_val,
            "total": hgt_val + sgt_val,
            "data_quality": data_quality,
            "warning": warning,
        }
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


def _normalize_lockup_ratio(v) -> float:
    """V16.2: 统一解禁比例单位 → 百分数（%）。
    FREE_RATIO/解禁比例 可能为小数(0.05)或百分数(5)；0<值<=1 视为小数转 %。"""
    try:
        f = float(v)
        if 0 < f <= 1:
            return round(f * 100, 2)
        return round(f, 2)
    except (TypeError, ValueError):
        return 0.0


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
        from core.tdx_client import tdx_get_share_capital

        f10 = tdx_get_share_capital(code)
        if f10:
            raw_list = f10.get('lockup_expiry', [])
            if raw_list:
                history: List[Dict[str, Any]] = []
                upcoming: List[Dict[str, Any]] = []
                for r in raw_list:
                    # F10 字段名可能为 解禁日期/公告日期，解禁类型/类型，解禁股数/数量，解禁比例/比例
                    date_str = (
                        r.get('解禁日期') or r.get('公告日期') or r.get('日期') or ''
                    ).strip()
                    if not date_str:
                        continue
                    date_str = str(date_str)[:10]
                    # MEDIUM(审查 2026-08-16): F10 解禁数量单位为**万**, 东财 FREE_SHARES 为**股**——
                    # 统一 ×1e4 转股(下游按股处理: sht/med /1e4 显示万股, lng /1e8 算市值)
                    entry = {
                        "date": date_str,
                        "type": (r.get('解禁类型') or r.get('类型') or '').strip(),
                        "shares": _safe_float(
                            r.get('解禁数量(万)')
                            or r.get('解禁股数')
                            or r.get('解禁数量')
                            or r.get('数量')
                            or 0
                        ) * 1e4,
                        "ratio": _normalize_lockup_ratio(
                            r.get('解禁比例(%)') or r.get('解禁比例') or r.get('比例') or 0
                        ),
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

    # Fallback: 东财 HTTP（V16.2.3 单位修正: FREE_SHARES=**股**原样返回, FREE_RATIO=小数→转百分数）
    if include_history:
        data = _em_filter(
            code, "RPT_LIFT_STAGE", page_size=15, sort_columns="FREE_DATE", sort_types="-1"
        )
        history = [
            {
                "date": str(r.get("FREE_DATE", "") or "")[:10],
                "type": r.get("FREE_SHARES_TYPE", ""),
                "shares": _safe_float(r.get("FREE_SHARES")),          # 股
                "ratio": _normalize_lockup_ratio(r.get("FREE_RATIO")),  # 统一%
                "able_shares": _safe_float(r.get("ABLE_FREE_SHARES")),  # 股
            }
            for r in data
        ]
    else:
        history = []

    data2 = eastmoney_datacenter(
        code,
        "RPT_LIFT_STAGE",
        filter_str=f"(SECURITY_CODE=\"{code}\")(FREE_DATE>='{today_str}')(FREE_DATE<='{end_str}')",
        page_size=20,
        sort_columns="FREE_DATE",
        sort_types="1",
    )
    upcoming = [
        {
            "date": str(r.get("FREE_DATE", "") or "")[:10],
            "type": r.get("FREE_SHARES_TYPE", ""),
            "shares": float(r.get("FREE_SHARES") or 0),               # 股
            "ratio": _normalize_lockup_ratio(r.get("FREE_RATIO")),     # 统一%
            "able_shares": float(r.get("ABLE_FREE_SHARES") or 0),     # 万股
        }
        for r in data2
    ]

    if include_history:
        return {"history": history, "upcoming": upcoming}
    return upcoming


async def get_lockup_expiry_async(
    session: Any, code: str, days: int = 90, include_history: bool = False
) -> Any:
    """async 版: 限售解禁日历

    V9.0: 委托到同步版（已内置 F10 优先逻辑），保留 session 参数向后兼容。
    V10.2: 移除 today_str 参数（同步版已内部自动计算）。
    """
    import asyncio

    return await asyncio.to_thread(get_lockup_expiry, code, days, include_history)


@cached(category="financial", ttl_seconds=TTL["financial"], cross_verify=True, trading_day=True, valid_if=make_valid_if())
def get_roe_trend_series(
    code: str,
    num_periods: int = 8,
    financials: Any = None,
    bs_data: Any = None,
    total_shares: float = 0,
) -> List[Dict[str, Any]]:
    """ROE/EPS/BPS 多期趋势（统一层——V16.3 O19 从 get_lng_report 下沉）。

    F10 财务分析（TDX TCP 第 2 档）优先：加权净资产收益率/基本EPS/每股净资产（9 期）；
    新浪财报自算兜底（摊薄口径：净利/期末权益）——**口径差异以 roe_type 字段标注**
    （weighted=F10 加权 / diluted=新浪摊薄），消费端须显示口径或仅用 weighted 期数。

    Returns:
        [{date, roe, roe_kc, eps, bps, roe_type}]
    """
    # ① F10 优先（TDX，加权口径）
    try:
        from core.tdx_client import tdx_get_financial_analysis

        f10 = tdx_get_financial_analysis(code)
        if f10:
            pf = f10.get("profitability") or []
            mi = f10.get("main_indicators") or []
            if pf and mi:
                pf_map = {r.get("period"): r for r in pf}
                mi_map = {r.get("period"): r for r in mi}
                rows = []
                # V17.0.8: 扣非ROE 补全——F10 无直接扣非ROE 字段, 用同源推算:
                # 扣非ROE ≈ 加权ROE × (扣非EPS / 基本EPS)(同口径近似, 与 ROE 列可比)。
                # fuyao index_deduct_weighted_avg_roe 为 TTM 滚动口径, 与单期加权不可混排,
                # 故不作为表格列源(仅保留 TTM 双口径对照走 roe_deduct_ttm)。
                for period in [r.get("period") for r in mi[:num_periods]]:
                    if not period:
                        continue
                    p = pf_map.get(period) or {}
                    m = mi_map.get(period) or {}
                    _roe = _safe_float(p.get("加权净资产收益率"))
                    _eps = _safe_float(m.get("基本每股收益(元)"))
                    _eps_kc = _safe_float(m.get("每股收益-扣除(元)"))
                    _roe_kc = None
                    if _roe and _eps and _eps_kc:
                        _roe_kc = round(_roe * (_eps_kc / _eps), 2)
                    rows.append(
                        {
                            "date": period,
                            "roe": _roe,
                            "roe_kc": _roe_kc,
                            "eps": _eps,
                            "bps": _safe_float(m.get("每股净资产(元)")),
                            "roe_type": "weighted",
                        }
                    )
                if rows:
                    return rows
    except Exception as _e:
        _debug_log(f"datasource roe_trend_series f10 error ({code}): {_e}")
    # ② 新浪财报自算兜底（摊薄口径）
    if not financials or not bs_data or total_shares <= 0:
        return []
    bs_map = {b.get("报告日", ""): b for b in bs_data}
    rows = []
    for fin in financials[:num_periods]:
        rd = fin.get("报告日", "")
        bs = bs_map.get(rd)
        if not bs:
            continue
        profit = _safe_float(fin.get("净利润", 0))
        equity = _safe_float(bs.get("归属于母公司股东权益合计", 0))
        roe = round(profit / equity * 100, 2) if equity > 0 else None
        eps = round(profit / total_shares, 4) if total_shares > 0 else None
        bps = round(equity / total_shares, 2) if total_shares > 0 else None
        # V17.0.8: 扣非ROE 同源推算——新浪财报含扣非净利时按同口径近似
        profit_kc = _safe_float(fin.get("扣除非经常性损益后的净利润", 0))
        roe_kc = None
        if profit_kc and profit > 0 and roe is not None:
            roe_kc = round(roe * (profit_kc / profit), 2)
        rows.append(
            {
                "date": rd,
                "roe": roe,
                "roe_kc": roe_kc,
                "eps": eps,
                "bps": bps,
                "roe_type": "diluted",
            }
        )
    return rows


def get_gross_margin_and_roe(
    code: str, fin_report: Any = None, bs_data: Any = None
) -> Dict[str, Any]:
    """获取最新年度的毛利率和ROE"""
    # V9.0: 优先使用 F10 财务分析中的盈利能力指标
    try:
        from core.tdx_client import tdx_get_financial_analysis

        f10 = tdx_get_financial_analysis(code)
        if f10:
            profitability = f10.get('profitability', [])
            if profitability:
                latest = profitability[0]
                gross_margin = _safe_float(latest.get('营业毛利率'))
                roe = _safe_float(latest.get('加权净资产收益率'))
                # V16.3 O: 同一次 F10 拉取顺带取基本每股收益（main_indicators，
                # 与 ZHB tipinfo eps 交叉验证一致），canonical eps fallback 复用
                eps = None
                main_indicators = f10.get('main_indicators', [])
                if main_indicators:
                    eps = _safe_float(main_indicators[0].get('基本每股收益(元)'))
                # 任一字段有效即返回（避免 F10 缺字段时返回 None）
                if gross_margin or roe or eps:
                    return {"gross_margin": gross_margin, "roe": roe, "eps": eps}
    except Exception as _e:
        _debug_log(f"datasource tdx financial analysis profitability error: {_e}")
    # Fallback: 新浪 HTTP
    try:
        if fin_report is None:
            prefix = "BJ" if code.startswith(("92", "8", "4", "43", "83", "87")) else ("SH" if code.startswith("6") else "SZ")
            paper_code = f"{prefix}{code}"
            url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
            params = {
                "paperCode": paper_code,
                "source": "lrb",
                "type": "0",
                "page": "1",
                "num": "1",
            }
            r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=15)
            if r is None or r.status_code != 200:
                return None
            d = r.json()
            # V16.3 O17: 新浪财报结构是 result.data.report_list（按报告期 dict），
            # 非 result.data 列表——旧写法 items[0] 拿到日期键字符串导致 fallback 永远失败
            # （参考仓库 v3.2.1 同款修复）
            _rl = ((d.get("result") or {}).get("data") or {}).get("report_list") or {}
            if not _rl:
                return None
            _period = next(iter(_rl))
            _period_data = _rl[_period] or {}
            # V16.3 O22: report_list[period] 结构是 {"data": [{item_title,item_value},...]}——
            # 必须先构建 item_map（O17 直接 item.get("营业总收入") 取到 None → 假 ROE=0.0）
            item = {e.get("item_title", ""): e.get("item_value") for e in _period_data.get("data", [])}
            if not item:
                return None
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
            if equity_yi > 0 and profit:
                roe = (profit * 100) / equity_yi
        # V16.3 O22: 数据缺失时返回 None 而非假值 0.0（避免被标 tdx:f10 并缓存）
        if gross_margin is None and roe is None:
            return None
        # 契约：F10 分支返回 {"gross_margin", "roe", "eps"}（V16.3 O）；
        # 新浪 fallback 分支仅 {"gross_margin", "roe"}——调用方必须 .get() 容缺
        return {"gross_margin": gross_margin, "roe": roe, "eps": None}
    except Exception as _e:
        _debug_log(f"datasource get_gross_margin_and_roe ({code}): {_e}")
        return None


async def get_gross_margin_and_roe_async(
    session: Any, code: str, fin_report: Any = None, bs_data: Any = None
) -> Dict[str, Any]:
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
            capture_output=True,
            text=True,
            timeout=120,
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

            print(
                f"[警告] 交易日历降级为 weekday 判断（{reason}），节假日可能误判。"
                "请运行 python scripts/update_calendar.py 更新数据。",
                file=sys.stderr,
                flush=True,
            )

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
        result.append(
            {
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
            }
        )
    return result


@cached(category="limit_pool", ttl_seconds=TTL["limit_pool"], trading_day=True)
@requires_push2  # V16.0: push2ex 与东财共用风控面，标记审计
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


@cached(category="limit_pool", ttl_seconds=TTL["limit_pool"], trading_day=True)
@requires_push2  # V16.0: push2ex 与东财共用风控面，标记审计
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


def _query_dt_pool_tc(date_str: str = "") -> Optional[int]:
    """V17.0.8: 东财 getTopicDTPool 的 tc 权威总数——pool 明细可能为空但 tc>0。
    用于 get_limit_pool_summary 跌停兜底（替代会读到 T-1 的 ZHB 快照）。"""
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
            return None
        d = r.json()
        tc = (d.get("data") or {}).get("tc")
        return int(tc) if tc is not None else None
    except Exception as _e:
        _debug_log(f"datasource dt pool tc: {_e}")
        return None


@cached(category="limit_pool", ttl_seconds=TTL["limit_pool"], trading_day=True)
@requires_push2  # V16.0: push2ex 与东财共用风控面，标记审计
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


@cached(category="limit_pool", ttl_seconds=TTL["limit_pool"], trading_day=True)
@requires_push2  # V16.0: push2ex 与东财共用风控面，标记审计
def get_yesterday_limit_pool(date_str: str = "") -> List[Dict[str, Any]]:
    """V16.1: 东财昨日涨停池（getYesterdayZTPool）— 昨涨停今表现。

    用于计算晋级率/赚钱效应（sht/mak 打板情绪）。

    Args:
        date_str: 日期字符串，格式 YYYYMMDD，默认当天（昨涨停池按当日接口返回昨日涨停股今日表现）

    Returns:
        列表，每项含:
            code/name/price/change_pct(今日涨幅)/turnover_rate/amplitude_pct(振幅)/
            speed(涨速)/y_first_seal(昨封板时间)/y_limit_count(昨连板数)/
            sector(行业)/zt_days/zt_continuous(N天M板)
    """
    if not date_str:
        from datetime import datetime

        date_str = datetime.now().strftime("%Y%m%d")

    url = "https://push2ex.eastmoney.com/getYesterdayZTPool"
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
        result = []
        for item in pool:
            zttj = item.get("zttj", {}) or {}
            result.append(
                {
                    "code": item.get("c", ""),
                    "name": item.get("n", ""),
                    "price": _safe_float(item.get("p")),
                    "change_pct": _safe_float(item.get("zdp")),  # 今日涨幅
                    "turnover_rate": _safe_float(item.get("hs")),
                    "amplitude_pct": _safe_float(item.get("zf")),  # 振幅
                    "speed": _safe_float(item.get("zs")),          # 涨速
                    "y_first_seal": str(item.get("yfbt", "")),     # 昨封板时间
                    "y_limit_count": _safe_float(item.get("ylbc")),  # 昨连板数
                    "sector": item.get("hybk", ""),
                    "zt_days": _safe_float(zttj.get("days")) if isinstance(zttj, dict) else 0,
                    "zt_continuous": _safe_float(zttj.get("ct")) if isinstance(zttj, dict) else 0,
                }
            )
        return result
    except Exception as _e:
        _debug_log(f"datasource get_yesterday_limit_pool: {_e}")
        return []


_TDXHY_CACHE: Optional[Dict[str, str]] = None


def _tdxhy_industry_map() -> Dict[str, str]:
    """V17.0.1g(2026-08-16): TDX 本机行业映射 code→一级行业名(零网络, 进程缓存).

    数据源(field_dict 表头·行业/细分行业唯一来源):
      - tdxhy.cfg(文本 Pipe): 市场|代码|T一级|空|空|X细分 —— 5,641 只 A 股全量
      - hy_tree.xml(GBK): X 码三级树 → 一级名(2 位 X 码)
    用途: 同花顺涨停池(无 sector 字段)的涨停板块分布注入。
    M4(审查 2026-08-16): 异常时保持 None 不固化——允许下次调用重试(文件修复/路径恢复后生效)。
    """
    global _TDXHY_CACHE
    if _TDXHY_CACHE is not None:
        return _TDXHY_CACHE
    _m: Dict[str, str] = {}
    try:
        import re as _re
        # 1) hy_tree.xml: X码 → 一级名(层级栈: 2位=一级, 其下节点继承)
        _lvl1 = ""
        _text = open(r"C:\new_tdx64\T0002\cloud_cfg\hy_tree.xml", encoding="gbk", errors="ignore").read()
        for _mn in _re.finditer(r'<node\s[^>]*caption="([^"]*)"[^>]*blockid="X(\d+)"|<node\s[^>]*blockid="X(\d+)"[^>]*caption="([^"]*)"', _text):
            _cap = _mn.group(1) or _mn.group(4)
            _xc = _mn.group(2) or _mn.group(3)
            if len(_xc) == 2:
                _lvl1 = _cap
            else:
                _m["X" + _xc] = _lvl1
        # 2) tdxhy.cfg: code → X细分码(已带 X 前缀) → 一级名
        for _ln in open(r"C:\new_tdx64\T0002\hq_cache\tdxhy.cfg", encoding="gbk", errors="ignore"):
            _p = _ln.rstrip("\n").split("|")
            if len(_p) >= 6 and len(_p[1]) == 6 and _p[1].isdigit():
                _x = _p[5].strip()
                if _x:
                    _m[_p[1]] = _m.get(_x, "") or ""
    except Exception as _e:
        _debug_log(f"_tdxhy_industry_map: {_e}")
        return _m  # 异常不固化, 下次重试
    _TDXHY_CACHE = _m
    return _m


@cached(category="limit_pool_v2", ttl_seconds=TTL["limit_pool"], trading_day=True)
@requires_push2  # V17.0.1g: 涨停池同花顺优先, 炸板/跌停池仍走 push2ex → 保留审计
def get_limit_pool_summary(date_str: str = "") -> Dict[str, Any]:
    """获取打板数据汇总（涨停池+炸板池+跌停池）

    V17.0.1g(2026-08-16): 涨停池改**同花顺优先**（10jqka 官方 dataapi, 字段更丰富:
    涨停原因/板型/封板率/炸板次数; 与东财 push2ex 62 vs 63 只仅差北交所口径）;
    同花顺无 sector 字段 → 用 TDX 本机 tdxhy 行业注入（零网络, 权威一级行业）;
    失败兜底东财 push2ex。炸板池/跌停池无同花顺替代, 保持东财 push2ex（用户已确认）.

    Returns:
        包含涨停/炸板/跌停数量和详细数据的字典
    """
    # 涨停池: 同花顺优先(2026-08-16 实测 62 只/1.01s), 东财兜底
    zt = ths_limit_up_pool(date_str)
    zt_source = "ths"
    if not zt:
        zt = get_limit_up_pool(date_str)
        zt_source = "em"
    # H1(审查 2026-08-16): 休市日 ths 内部回退最近交易日, 炸板/跌停池若仍用当天(空) →
    # 封板率 100% 假象。统一口径: 回退后日期传给东财炸板/跌停池(东财对历史日期也有效)
    _zt_date = ""
    if zt_source == "ths":
        try:
            _zt_date = get_last_trading_day().strftime("%Y%m%d")
        except Exception:
            _zt_date = ""
    # 同花顺源无 sector → TDX 本机 tdxhy 一级行业注入(零网络)
    if zt_source == "ths" and zt:
        try:
            _ind_map = _tdxhy_industry_map()
            for item in zt:
                item["sector"] = _ind_map.get(item.get("code") or "", "") or ""
        except Exception as _e:
            _debug_log(f"get_limit_pool_summary tdxhy sector inject: {_e}")
    zb = get_limit_broken_pool(_zt_date or date_str)
    dt = get_limit_down_pool(_zt_date or date_str)
    # V17.0.8(2026-08-26 报告核查): 修复跌停兜底——旧逻辑(ZHB 快照涨跌幅口径)在盘中读到
    # T-1(前一日) 快照, 把昨日跌停误报为今日(8/26 实测 22 假跌停, 真实=0)。
    # 权威顺序: ① 东财 getTopicDTPool tc 总数(pool 可能空但 tc>0) → ② KPL RiseFallAnalysis dt
    # (独立匿名源) → ③ ZHB 快照仅当数据日期==目标日期才允许(ZHB 盘中恒为 T-1)
    _dt_fb = None
    if not dt:
        try:
            from datetime import datetime as _dtm

            _target = _zt_date or date_str or _dtm.now().strftime("%Y%m%d")
            # ① push2ex tc 权威总数
            try:
                from stock_common.sc_datasource import _query_dt_pool_tc

                _dt_tc = _query_dt_pool_tc(_target)
                if _dt_tc is not None:
                    _dt_fb = _dt_tc
            except Exception as _e1:
                _debug_log(f"get_limit_pool_summary dt tc: {_e1}")
            # ② KPL 独立匿名源(交叉验证)
            if _dt_fb is None:
                try:
                    from stock_common.sc_kpl import get_kpl_broken_ratio

                    _kpl_rf = get_kpl_broken_ratio()
                    if _kpl_rf and _kpl_rf.get("date") == _target[:4] + "-" + _target[4:6] + "-" + _target[6:]:
                        _dt_fb = int(_kpl_rf.get("dt") or 0)
                except Exception as _e2:
                    _debug_log(f"get_limit_pool_summary kpl dt: {_e2}")
            # ③ ZHB 兜底: 仅当快照日期==目标日期(零网络最后手段)
            if _dt_fb is None:
                try:
                    from stock_common import is_limit_down

                    _zhb_date = get_zhb_data_date().replace("-", "")
                    if _zhb_date == _target:
                        _snap = get_zhb_full_market_snapshot() or {}
                        _dt_fb = sum(
                            1
                            for _c, _d in _snap.items()
                            if _d
                            and isinstance(_d, dict)
                            and is_limit_down(_c, str(_d.get("name", "") or ""), _safe_float(_d.get("change_pct", 0)))
                        )
                    else:
                        _debug_log(
                            f"get_limit_pool_summary dt: zhb date {_zhb_date} != target {_target}, 跳过 T-1 误判兜底"
                        )
                except Exception as _e3:
                    _debug_log(f"get_limit_pool_summary zhb dt fallback: {_e3}")
            if _dt_fb is None:
                _dt_fb = 0
        except Exception as _e:
            _debug_log(f"get_limit_pool_summary dt fallback: {_e}")
            _dt_fb = 0

    # 按板块统计涨停分布(M4: 空 sector 归"其他", 不产生空键)
    sector_stats: Dict[str, int] = {}
    for item in zt:
        sec = item.get("sector") or "其他"
        sector_stats[sec] = sector_stats.get(sec, 0) + 1

    # 封板成功率
    total_attempt = len(zt) + len(zb)
    success_rate = len(zt) / total_attempt * 100 if total_attempt > 0 else 0

    return {
        "limit_up_count": len(zt),
        "limit_broken_count": len(zb),
        "limit_down_count": len(dt) or _dt_fb,
        "success_rate": round(success_rate, 1),
        "sector_stats": dict(sorted(sector_stats.items(), key=lambda x: x[1], reverse=True)[:10]),
        "limit_up_list": zt,
        "limit_broken_list": zb,
        "limit_down_list": dt,
    }


# ═══════════════════════════════════════════════════════════
# 同花顺涨停揭秘（V9.6 新增，打板层增强源）
# ═══════════════════════════════════════════════════════════


@cached(category="limit_pool_v2", ttl_seconds=TTL["limit_pool"], trading_day=True)
def ths_limit_up_pool(date_str: str = "") -> List[Dict[str, Any]]:
    """同花顺涨停揭秘（涨停原因 + 封板质量增强源）。

    V9.6 新增：与东财涨停池互为补充，提供东财没有的字段：
    - 涨停原因题材（reason）
    - 板型（一字板/换手板/T字板）
    - 封板成功率（seal_rate）
    - 炸板次数（break_times）

    V17.0.1g(2026-08-16): 升格为涨停池**优先源**(同花顺优先, push2ex 兜底);
    空日期自动回退最近交易日(休市传当日返回空)。
    V17.0.1h(2026-08-16): 新增 7 字段(turnover_rate/currency_value/order_volume/
    last_time/change_tag/market_type/is_new——同一次请求已返回, 零额外压力);
    **缓存 category 升 limit_pool_v2**(旧 pickle 无新字段, 强制失效)。

    Args:
        date_str: 交易日，格式 YYYYMMDD

    Returns:
        涨停列表，包含 code/name/price/pct/reason/board_type/seal_rate 等字段
    """
    from datetime import datetime

    # V17.0.1g(2026-08-16): 休市日(周末/节假日)传当日返回空 → 自动回退最近交易日
    if not date_str:
        try:
            from stock_common.stock_calendar import get_last_trading_day
            date_str = get_last_trading_day().strftime("%Y%m%d")
        except Exception:
            date_str = datetime.now().strftime("%Y%m%d")
    url = "https://data.10jqka.com.cn/dataapi/limit_up/limit_up_pool"
    params = {
        "page": 1,
        "limit": 200,
        "field": "199112,10,9001,330323,330324,330325,9002,330329,133971,133970,1968584,3475914,9003,9004",
        "filter": "HS,GEM2STAR",
        "order_field": "330324",
        "order_type": "0",
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
            # V17.0.1g: high_days 中文文本("首板"/"2板"/"3板"...) → 连板数; 东财契约兼容
            _hd = str(it.get("high_days", "") or "")
            _lc = 1
            if _hd.endswith("板"):
                _n = _hd[:-1]
                if _n.isdigit():
                    try:
                        _lc = int(_n)
                    except (ValueError, TypeError):
                        _lc = 1
            # V17.0.1h: 附加字段(同一次请求已返回, 零额外压力)——打板质量/弹性/风险分层
            # M2(审查 2026-08-16): 时间戳可能为 "0"/None/非数字 → 0 或异常会输出 1970-01-01
            # 或整池吞错; 先 _safe_float 再判 >0(精度 <1s 无影响)
            def _fmt_ts(_v: Any) -> str:
                _f = _safe_float(_v)
                if _f > 0:
                    try:
                        return datetime.fromtimestamp(int(_f)).strftime("%H:%M:%S")
                    except (ValueError, OverflowError, OSError):
                        pass
                return ""

            _lbt = it.get("last_limit_up_time")
            out.append(
                {
                    "code": it.get("code"),
                    "name": it.get("name"),
                    "price": _safe_float(it.get("latest")),
                    "change_pct": _safe_float(it.get("change_rate")),
                    "reason": it.get("reason_type", ""),
                    "board_type": it.get("limit_up_type", ""),
                    "seal_rate": _safe_float(it.get("limit_up_suc_rate")),  # 0-1 小数(实测全池 0-1, 1.0=完全封死)
                    "break_times": it.get("open_num") or 0,
                    "seal_amount": it.get("order_amount"),
                    "limit_fund": _safe_float(it.get("order_amount", 0)),  # 元, 东财契约同口径
                    "limit_count": _lc,
                    "zt_days": _lc,
                    "high_days": _hd,
                    "first_time": _fmt_ts(it.get("first_limit_up_time")),
                    "last_time": _fmt_ts(_lbt),
                    "is_again": it.get("is_again_limit"),
                    "turnover_rate": _safe_float(it.get("turnover_rate")),
                    "currency_value": _safe_float(it.get("currency_value")),  # 元
                    "order_volume": it.get("order_volume"),  # 股
                    "change_tag": it.get("change_tag", ""),
                    "market_type": it.get("market_type", ""),
                    "is_new": it.get("is_new"),
                }
            )
        return out
    except Exception as _e:
        _debug_log(f"datasource ths_limit_up_pool: {_e}")
        return []


# ═══════════════════════════════════════════════════════════
# 重点监控池（V16.0 新增，参考 a-stock-data V3.6 em_stock_monitor）
# ═══════════════════════════════════════════════════════════


@cached(category="limit_pool", ttl_seconds=TTL["limit_pool"], trading_day=True)
def em_stock_monitor(only_active: bool = True) -> List[Dict[str, Any]]:
    """获取交易所重点监控池（风险警示/重点监控名单）。

    V16.0 新增，参考 a-stock-data V3.6 `em_stock_monitor`。
    2026-08-03 联网验证：接口可用（实测 17 条）。

    Args:
        only_active: True=仅返回监控期内（VALIDATESTARTDATE~VALIDATEENDDATE）的标的

    Returns:
        [{code, name, market, start, end, link}]
        market: "SH"/"SZ"/"BJ"（注意 MARKET="B"=北交所，参考仓库实测 920575 *ST康乐）
    """
    url = "https://mobappconfig.securities.eastmoney.com/emcfg/stock_monitor.json"
    _mkt_map = {"1": "SH", "0": "SZ", "B": "BJ"}
    try:
        r = _quick_request(
            url,
            headers={"User-Agent": UA, "Referer": "https://vipmoney.eastmoney.com/"},
            timeout=15,
        )
        if r is None:
            return []
        rows = r.json()
        if not isinstance(rows, list):
            return []
        today = datetime.now().strftime("%Y-%m-%d")
        out = []
        for x in rows:
            start = str(x.get("VALIDATESTARTDATE", "") or "")
            end = str(x.get("VALIDATEENDDATE", "") or "")
            if only_active and not (start <= today <= end):
                continue
            raw_mkt = str(x.get("MARKET", "")).upper()
            out.append(
                {
                    "code": str(x.get("STKCODE", "")),
                    "name": str(x.get("STKNAME", "")),
                    "market": _mkt_map.get(raw_mkt, f"?{raw_mkt}"),
                    "start": start,
                    "end": end,
                    "link": str(x.get("LINK_URL", "") or ""),
                }
            )
        return out
    except Exception as _e:
        _debug_log(f"datasource em_stock_monitor: {_e}")
        return []


# ═══════════════════════════════════════════════════════════
# 板块资金流向（V16.0 新增，参考 a-stock-data V3.5 board_fund_flow）
# ═══════════════════════════════════════════════════════════


@cached(category="fund_flow", ttl_seconds=TTL["fund_flow"], trading_day=True)
@requires_push2
def get_board_fund_flow(board_type: str = "industry", top_n: int = 20) -> List[Dict[str, Any]]:
    """获取板块资金流向（行业/概念/地域板块的主力净流入排名）。

    V16.0 新增，参考 a-stock-data V3.5 `board_fund_flow`。
    2026-08-03 联网验证：83.push2 备用域名可用。
    注意：push2 有 IP 级风控，遇 RemoteDisconnected 需等待 30-60 分钟。

    Args:
        board_type: "industry"(行业 m:90 t:2) / "concept"(概念 m:90 t:3) / "area"(地域 m:90 t:1)
        top_n: 返回前 N 个板块

    Returns:
        [{code, name, change_pct, main_net_wan, super_net_wan, large_net_wan, medium_net_wan, small_net_wan, turnover}]
    """
    fs_map = {
        "industry": "m:90+t:2+f:!50",
        "concept": "m:90+t:3+f:!50",
        "area": "m:90+t:1+f:!50",
    }
    fs = fs_map.get(board_type, fs_map["industry"])
    # V16.3 O16: 翻页支持（参考仓库 v3.5.1）——先取首页拿真实 total，top_n>200 才翻页；
    # total 缺失按"不足一页即末页"收敛；提前返空即跳出防死循环。
    _PAGE = 200  # 东财 clist 单页上限
    params_tpl = {
        "po": "1", "np": "1", "fltt": "2", "invt": "2",
        "fs": fs,
        "fields": "f12,f14,f2,f3,f62,f66,f69,f72,f75,f184",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
    }

    def _fetch_page(pn: int, pz: int) -> dict:
        params = dict(params_tpl, pn=str(pn), pz=str(pz))
        try:
            r = _quick_request(
                "https://push2.eastmoney.com/api/qt/clist/get",
                params=params, headers={"User-Agent": UA}, timeout=10,
            )
            if r is None:
                # fallback: 备用域名（83.push2 实测可用）
                r = _quick_request(
                    "http://83.push2.eastmoney.com/api/qt/clist/get",
                    params=params, headers={"User-Agent": UA}, timeout=10,
                )
            if r is None:
                return {}
            d = r.json()
            return d.get("data") or {}
        except Exception as _e:
            _debug_log(f"datasource board_fund_flow page {pn}: {_e}")
            return {}

    try:
        data0 = _fetch_page(1, min(top_n, _PAGE))
        if not data0:
            return []
        total = data0.get("total")
        if isinstance(total, str):
            try:
                total = int(total)
            except ValueError:
                total = None
        diff0 = data0.get("diff") or []
        if isinstance(diff0, dict):
            diff0 = list(diff0.values())
        all_items = list(diff0)
        # 需要翻页：total 存在且 > 当前已取，且 top_n 超过单页
        need = top_n if total is None else min(top_n, total)
        while len(all_items) < need and len(diff0) > 0:
            pn = len(all_items) // _PAGE + 1
            data_n = _fetch_page(pn, _PAGE)
            diff_n = data_n.get("diff") or []
            if isinstance(diff_n, dict):
                diff_n = list(diff_n.values())
            if not diff_n:
                break  # 提前返空即末页（防死循环）
            all_items.extend(diff_n)
        out = []
        for item in all_items[:top_n]:
            out.append(
                {
                    "code": str(item.get("f12", "")),
                    "name": str(item.get("f14", "")),
                    "change_pct": _safe_float(item.get("f3", 0)),
                    "main_net_wan": _safe_float(item.get("f62", 0)) / 1e4,  # 元→万元
                    "super_net_wan": _safe_float(item.get("f66", 0)) / 1e4,
                    "large_net_wan": _safe_float(item.get("f69", 0)) / 1e4,
                    "medium_net_wan": _safe_float(item.get("f72", 0)) / 1e4,
                    "small_net_wan": _safe_float(item.get("f75", 0)) / 1e4,
                    "turnover": _safe_float(item.get("f184", 0)),
                }
            )
        return out
    except Exception as _e:
        _debug_log(f"datasource get_board_fund_flow: {_e}")
        return []


# ═══════════════════════════════════════════════════════════
# 东财分钟级资金流（V9.6 新增，用于资金流降权融合）
# ═══════════════════════════════════════════════════════════


@cached(category="fund_flow", ttl_seconds=TTL["fund_flow"], trading_day=True)
@requires_push2
def get_eastmoney_minute_fund_flow(code: str) -> List[Dict[str, Any]]:
    """获取东财个股分钟级资金流数据

    V9.6 新增：使用东财push2接口获取分钟级资金流，用于与TDX资金流加权融合。
    数据格式与同花顺/百度资金流不同，但覆盖更稳定。

    Returns:
        分钟级资金流列表，每项包含时间/主力净流入/小单净流入/中单净流入/大单净流入
    """
    secid = f"{em_secid_prefix(code)}{code}"  # V17.0 S3: 统一前缀(含北交所 92)

    params = {
        "lmt": "0",
        "klt": "1",  # 1分钟
        "secid": secid,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
    }
    try:
        # V16.2.4: 多域轮换（分钟级延时域可能无窗口，失败时返回空由调用方降级）
        r = _em_fflow_request("/api/qt/stock/fflow/kline/get", params)
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
                result.append(
                    {
                        "time": parts[0],
                        "main_net_inflow": _safe_float(parts[1]),  # 主力净流入
                        "small_net_inflow": _safe_float(parts[2]),  # 小单净流入
                        "medium_net_inflow": _safe_float(parts[3]),  # 中单净流入
                        "large_net_inflow": _safe_float(parts[4]),  # 大单净流入
                        "super_net_inflow": _safe_float(parts[5]),  # 超大单净流入
                    }
                )
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
            from core.tdx_client import tdx_get_fund_flow

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
        result["sources"]["eastmoney"] = {
            "weight": 0.6,
            "data_available": True,
            "count": len(em_ff),
        }

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


def news_matches_stock(title: str, code: str, name: str = "") -> bool:
    """V16.2.3: 快讯标题是否与个股相关（含代码 / 全名 / 简称）。

    财联社等全市场快讯必须经本过滤后才可展示在个股报告"舆情"章节
    （原实现直接展示全市场快讯，混入无关资讯）。"""
    if not title:
        return False
    t = str(title)
    if code and code in t:
        return True
    if name:
        n = str(name).strip()
        if n and n in t:
            return True
        # 简称匹配：去掉常见后缀（科技/股份/集团/控股/电子等）
        _short = re.sub(
            r"(科技|股份|集团|控股|电子|实业|国际|发展|证券|银行|医药|汽车|电力|能源|材料|化工)$",
            "",
            n,
        )
        if len(_short) >= 2 and _short in t:
            return True
    return False


def get_history_fund_flow_120d(code: str, days: int = 60, prefer: str = "auto") -> Dict[str, Any]:
    """V16.2.4 (D2): 统一 120 日资金流入口（消除 get_fund_flow_120d 在 sht/med 的双实现）。

    Args:
        code: 股票代码
        days: 天数（默认 60）
        prefer: "tdx"=TDX 优先→东财 fallback（sht 短线口径）；
                "em"=仅东财（med 中线口径）；"auto"=TDX 优先

    Returns:
        {"data": [dict(元)] 或 [], "error": str, "source": str}
        与 med/sht 原有 get_fund_flow_120d 返回结构完全一致。
    """
    def _norm_ff(data):
        """V16.3 O19: 强制归一为 dict 列表（单位元）——历史遗留 float 列表（万元）自动转 dict(元)。"""
        if data and isinstance(data[0], (int, float)):
            return [
                {
                    "date": "",
                    "main_net": v * 1e4,
                    "super_net": 0,
                    "large_net": 0,
                    "mid_net": 0,
                    "small_net": 0,
                }
                for v in data
            ]
        return data

    if prefer != "em":
        try:
            from core.tdx_client import tdx_get_history_fund_flow

            _tdx = tdx_get_history_fund_flow(code, days)
            if _tdx:
                return {"data": _norm_ff(_tdx), "error": "", "source": "tdx"}
        except Exception as _e:
            _debug_log(f"datasource get_history_fund_flow_120d tdx ({code}): {_e}")
    try:
        _em = get_em_history_fund_flow(code, days)
        if _em:
            return {"data": _norm_ff(_em), "error": "", "source": "eastmoney"}
    except Exception as _e:
        _debug_log(f"datasource get_history_fund_flow_120d em ({code}): {_e}")
    return {"data": [], "error": "资金流数据获取失败"}


# V16.2.17: 东财**申万二级**行业映射（datacenter-web 域，低风险；东财二级与申万二级同源，
# 如 半导体/白酒Ⅱ/光学光电子/白色家电 —— 用户要求全部脚本统一"申万二级"粒度）
# 全市场一次分页拉取（19 页 × 5000），进程内存 + 磁盘 JSON 双缓存（行业静态，7 天 TTL）。
# 缓存版本隔离: 文件名带 _l2 后缀，与 V16.2.16 一级缓存(em_industry_map.json)互不污染。
_EM_L2_MAP: Optional[Dict[str, str]] = None
_EM_L2_MEMBERS: Optional[Dict[str, List[str]]] = None
_EM_L2_LOADED_TS = 0.0
_EM_L2_TTL = 7 * 86400
# 东财行业一级名单（用于排除；二级 = 排除一级后 code 最小的行业板块）
_EM_INDUSTRY_L1_NAMES = frozenset({
    "农林牧渔", "基础化工", "钢铁", "有色金属", "电子", "家用电器", "食品饮料",
    "纺织服饰", "轻工制造", "医药生物", "公用事业", "交通运输", "房地产", "商贸零售",
    "社会服务", "综合", "建筑材料", "建筑装饰", "电力设备", "机械设备", "国防军工",
    "汽车", "计算机", "传媒", "通信", "银行", "非银金融", "煤炭", "石油石化",
    "环保", "美容护理",
})


def _em_l2_load_cached(_json, _os, _now) -> Optional[Dict[str, str]]:
    """读磁盘缓存（两级：code→二级名、name→成员）。返回 l2_map 或 None。"""
    _d = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    global _EM_L2_MEMBERS
    _mp = _os.path.join(_d, "cache", "em_industry_map_l2.json")
    _mb = _os.path.join(_d, "cache", "em_industry_members_l2.json")
    if not (_os.path.exists(_mp) and _os.path.exists(_mb)):
        return None
    try:
        if _now - _os.path.getmtime(_mp) > _EM_L2_TTL or _now - _os.path.getmtime(_mb) > _EM_L2_TTL:
            return None
        with open(_mp, encoding="utf-8") as _f:
            _m = _json.load(_f)
        with open(_mb, encoding="utf-8") as _f:
            _mbd = _json.load(_f)
        if isinstance(_m, dict) and isinstance(_mbd, dict):
            _EM_L2_MEMBERS = {k: list(v) for k, v in _mbd.items()}
            return _m
    except Exception as _e:
        _debug_log(f"datasource em_l2 cache read: {_e}")
    return None


def get_em_industry_l2_data(force_refresh: bool = False) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    """V16.2.17: 东财申万二级行业数据（全市场，一次性拉取缓存）。

    返回: (map_l2: {股票代码: 申万二级名}, members_l2: {申万二级名: [成分代码]})
    二级识别: type=2 行业板块中排除一级名单(_EM_INDUSTRY_L1_NAMES)后取 code 最小
    （实测 000100: 电子[1201一级]/光学光电子[1038]/面板[1335] → 光学光电子；
      600519: 食品饮料[438一级]/白酒Ⅱ[1277]/白酒Ⅲ[1575] → 白酒Ⅱ）。
    """
    import json as _json
    import os as _os
    import time as _time

    global _EM_L2_MAP, _EM_L2_MEMBERS, _EM_L2_LOADED_TS
    _now = _time.time()
    if not force_refresh and _EM_L2_MAP is not None and _now - _EM_L2_LOADED_TS < _EM_L2_TTL:
        return _EM_L2_MAP, (_EM_L2_MEMBERS or {})

    _cached = _em_l2_load_cached(_json, _os, _now)
    if not force_refresh and _cached is not None:
        _EM_L2_MAP = _cached
        _EM_L2_LOADED_TS = _now
        return _EM_L2_MAP, (_EM_L2_MEMBERS or {})

    _per_stock: Dict[str, List[Any]] = {}
    _url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    # V16.4.1: try 外初始化——异常路径 L4152 引用会 UnboundLocalError(被调用方吞掉掩盖真错)
    _map_l2: Dict[str, str] = {}
    _members_l2: Dict[str, List[str]] = {}
    try:
        _page = 1
        while True:
            _params = {
                "reportName": "RPT_EM_BOARD_CONSTITUENT", "columns": "ALL",
                "pageNumber": str(_page), "pageSize": "5000",
            }
            _r = em_get(_url, params=_params, headers={"User-Agent": UA}, timeout=30)
            if _r is None:
                break
            _d = _r.json()
            _res = _d.get("result") or {}
            _rows = _res.get("data") or []
            if not _rows:
                break
            for _row in _rows:
                if str(_row.get("BOARD_TYPE_NEW", "")) == "2":
                    _sc = str(_row.get("SECURITY_CODE", ""))
                    _bc = _row.get("BOARD_CODE")
                    _nm = str(_row.get("BOARD_NAME", "")).strip()
                    if _sc and _nm and _nm != "-":
                        try:
                            _per_stock.setdefault(_sc, []).append((int(_bc), _nm))
                        except (TypeError, ValueError):
                            _per_stock.setdefault(_sc, []).append((0, _nm))
            _pages = _res.get("pages") or 1
            if _page >= int(_pages):
                break
            _page += 1
        # 二级识别：排除一级名单后 code 最小；成员表反转
        for _sc, _boards in _per_stock.items():
            _sb = sorted(_boards)
            _l2 = next((nm for _c, nm in _sb if nm not in _EM_INDUSTRY_L1_NAMES), None)
            if not _l2:
                _l2 = _sb[0][1] if _sb else ""
            if _l2:
                _map_l2[_sc] = _l2
                _members_l2.setdefault(_l2, []).append(_sc)
        # 写磁盘缓存（版本隔离 _l2 后缀）
        try:
            _cache_dir = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "cache")
            _os.makedirs(_cache_dir, exist_ok=True)
            for _fn, _obj in (("em_industry_map_l2.json", _map_l2), ("em_industry_members_l2.json", _members_l2)):
                _tmp = _os.path.join(_cache_dir, _fn + ".tmp")
                with open(_tmp, "w", encoding="utf-8") as _f:
                    _json.dump(_obj, _f, ensure_ascii=False)
                _os.replace(_tmp, _os.path.join(_cache_dir, _fn))
        except Exception as _e:
            _debug_log(f"datasource em_l2 cache write: {_e}")
    except Exception as _e:
        _debug_log(f"datasource em_l2 fetch: {_e}")

    _EM_L2_MAP = _map_l2
    _EM_L2_MEMBERS = _members_l2
    _EM_L2_LOADED_TS = _now
    return _EM_L2_MAP, _EM_L2_MEMBERS


def get_em_industry_l2(code: str) -> str:
    """V16.2.17: 单只股票东财申万二级行业（映射缓存命中，零额外请求）。"""
    try:
        _m, _ = get_em_industry_l2_data()
        return _m.get(code, "")
    except Exception as _e:
        _debug_log(f"datasource get_em_industry_l2 ({code}): {_e}")
        return ""


def get_em_industry_members_l2(l2_name: str) -> List[str]:
    """V16.2.17: 东财申万二级板块成分（成员缓存命中，零额外请求）。"""
    try:
        _m, _mb = get_em_industry_l2_data()
        return _mb.get(l2_name, []) if _mb else []
    except Exception as _e:
        _debug_log(f"datasource get_em_industry_members_l2 ({l2_name}): {_e}")
        return []


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

    params = {
        "appName": "CailianpressWeb",
        "os": "web",
        "sv": "7.7.5",
        "last_time": "",
        "refresh_type": "1",
        "rn": str(page_size),
    }
    qs = "&".join(f"{k}={params[k]}" for k in sorted(params))
    sign = hashlib.md5(hashlib.sha1(qs.encode()).hexdigest().encode()).hexdigest()
    url = f"https://www.cls.cn/v1/roll/get_roll_list?{qs}&sign={sign}"

    try:
        r = _quick_request(
            url, headers={"User-Agent": UA, "Referer": "https://www.cls.cn/"}, timeout=10
        )
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
            # V16.1: 保留 stock_list/subjects（供 sht 关联股票分析）
            stock_list = item.get("stock_list") or []
            subjects = item.get("subjects") or []
            rows.append(
                {
                    "title": item.get("title", "") or item.get("brie", ""),
                    "content": item.get("content", "") or item.get("brie", ""),
                    "time": t,
                    "level": item.get("level", ""),
                    "reading_num": item.get("reading_num", 0),
                    "stock_list": [
                        {
                            "code": str(s.get("StockID", "") or s.get("stock_code", "")),
                            "name": str(s.get("name", "") or s.get("stock_name", "")),
                            "pct": s.get("RiseRange"),
                        }
                        for s in stock_list
                        if isinstance(s, dict)
                    ],
                    "subjects": [
                        {
                            "id": s.get("subject_id"),
                            "name": s.get("subject_name", ""),
                        }
                        for s in subjects
                        if isinstance(s, dict)
                    ],
                }
            )
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
    su = (
        "https://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON"
        f"&CATALOGID=1842_xxpl&TABKEY=tab1&txtStart={trade_date}&txtEnd={trade_date}&random=0.9"
    )
    try:
        req = urllib.request.Request(
            su,
            headers={
                "User-Agent": UA,
                "Referer": "https://www.szse.cn/disclosure/supervision/dealinfo/index.html",
            },
        )
        # V16.3 C1: 备胎源裸 urlopen 补节流（_DOMAIN_LIMITS 的 szse 域 3.0rps 不覆盖此直连路径）
        try:
            from stock_common.sc_network import _gen_wait_process_interval
            _gen_wait_process_interval()
        except Exception:
            pass
        # V16.3 O14: 备胎源强制直连（ProxyHandler({}) 忽略系统代理——GD 外全部直连）
        # V16.3 O22: OpenerDirector.open 不接受 context 关键字（原 TypeError 使备胎源永久失效）——
        # 自定义 SSL context 通过 HTTPSHandler 注入
        _opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            urllib.request.HTTPSHandler(context=_ctx),
        )
        with _opener.open(req, timeout=15) as r:
            d = json.loads(r.read())
        if isinstance(d, list) and d:
            for row in d[0].get("data", []):
                out["szse"].append(
                    {
                        "code": row.get("zqdm"),
                        "name": row.get("zqjc"),
                        "amount": row.get("cjje"),
                        "reason": row.get("plyy"),
                        "volume": row.get("cjsl"),
                        "note": row.get("bz"),
                    }
                )
    except Exception as _e:
        _debug_log(f"dragon_tiger_backup szse: {_e}")

    # 上交所龙虎榜（JSONP格式）
    eu = (
        "https://query.sse.com.cn/infodisplay/showTradePublicFile.do?"
        f"jsonCallBack=cb&isPagination=false&dateTx={trade_date}"
    )
    try:
        req = urllib.request.Request(
            eu,
            headers={
                "User-Agent": UA,
                "Referer": "https://www.sse.com.cn/disclosure/diclosure/public/",
            },
        )
        # V16.3 C1: 备胎源裸 urlopen 补节流
        try:
            from stock_common.sc_network import _gen_wait_process_interval
            _gen_wait_process_interval()
        except Exception:
            pass
        # V16.3 O14: 强制直连（忽略系统代理）
        _opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with _opener.open(req, timeout=15) as r:
            t = r.read().decode("utf-8", "ignore")
        if "(" in t and ")" in t:
            json_str = t[t.index("(") + 1 : t.rindex(")")]
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
    # V16.3 O16: 北交所 920/8/4 号段走 bj 前缀（此 URL 当前未用 prefix，保留统一口径）
    prefix = "bj" if code.startswith(("92", "8", "4", "43", "83", "87")) else ("sh" if code.startswith("6") else "sz")
    url = (
        "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/MoneyFlow.ssl_bkzj_bk"
    )
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

    # V16.2.3: 巨潮互动易无统一入口（交易所直连），加进程级礼貌限速（每次调用 2 个请求）
    try:
        from stock_common.sc_network import _gen_wait_process_interval
        _gen_wait_process_interval()
    except Exception:
        pass
    try:
        # V16.3 O14: 巨潮互动易强制直连（忽略系统代理——GD 外全部直连）
        _no_proxy = {"http": None, "https": None}
        r1 = requests.post(
            "https://irm.cninfo.com.cn/newircs/index/queryKeyboardInfo",
            data={"keyWord": code},
            headers={"User-Agent": UA},
            timeout=10,
            proxies=_no_proxy,
        )
        d1 = r1.json().get("data") or []
        if not d1:
            return []
        org_id = d1[0].get("secid")

        params = {
            "_t": 1,
            "stockcode": code,
            "orgId": org_id,
            "pageSize": page_size,
            "pageNum": page_num,
            "keyWord": "",
            "startDay": "",
            "endDay": "",
        }
        r2 = requests.post(
            "https://irm.cninfo.com.cn/newircs/company/question",
            params=params,
            headers={"User-Agent": UA},
            timeout=10,
            proxies=_no_proxy,
        )
        rows = r2.json().get("rows") or []

        out = []
        for it in rows:
            pd = it.get("pubDate")
            out.append(
                {
                    "code": it.get("stockCode"),
                    "company": it.get("companyShortName"),
                    "question": it.get("mainContent"),
                    "answer": it.get("attachedContent"),
                    "answerer": it.get("attachedAuthor"),
                    "ask_time": (
                        datetime.fromtimestamp(pd / 1000).strftime("%Y-%m-%d %H:%M") if pd else ""
                    ),
                }
            )
        return out
    except Exception as _e:
        _debug_log(f"datasource cninfo_irm ({code}): {_e}")
        return []


# ═══════════════════════════════════════════════════════════
# zhb 全局配置总包（V9.6 新增，基于通达信 0x06B9 协议）
# ═══════════════════════════════════════════════════════════








def get_zhb_industry_map() -> Dict[str, str]:
    """V9.6: 获取行业代码→名称映射（全类型，1000+条）。"""
    try:
        from core.zhb_client import get_industry_map

        return get_industry_map()
    except Exception as _e:
        _debug_log(f"datasource zhb industry_map: {_e}")
        return {}


def get_zhb_data_date() -> str:
    """V9.6: 获取 zhb 数据的日期（YYYYMMDD），用于报告中标注数据时效性。"""
    try:
        from core.zhb_client import get_zhb

        zhb = get_zhb()
        return zhb.date if zhb else ""
    except Exception as _e:
        _debug_log(f"datasource zhb data_date: {_e}")
        return ""


# ═══════════════════════════════════════════════════════════
# zhb B级数据集成（阶段二）
# ═══════════════════════════════════════════════════════════






def get_zhb_market_snapshot(codes: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """V9.6: 全市场（或指定股票）统计快照。

    一次调用拿到全市场7938只股票的统计快照，用于val脚本初筛。
    数据可能有1-2天延迟，仅用于盘后初筛。
    """
    try:
        from core.zhb_client import market_stat_snapshot

        return market_stat_snapshot(codes)
    except Exception as _e:
        _debug_log(f"datasource zhb market_snapshot: {_e}")
        return {}



def is_zhb_data_fresh(max_delay_days: int = 3) -> bool:
    """V9.6: 检查zhb数据是否新鲜（延迟在指定天数内）。

    数据过旧时调用方应降级到原有HTTP/TCP接口。
    """
    try:
        from core.zhb_client import is_data_fresh

        return is_data_fresh(max_delay_days)
    except Exception as _e:
        _debug_log(f"datasource zhb is_fresh: {_e}")
        return False


# V10.2 新增：zhb 字段时效性分级
# V10.3 更新：新增准实时字段分类（主力资金流向等，1天延迟可接受）
# V16.3.3 更新 (2026-08-10 字典 12.15.6 ABCD 缓存分级正式化——与统一层路由矩阵区分)：
#   A 实时字段：zhb 日期必须是今天（max_delay_days=0），否则 fallback 原接口
#   B 准实时字段：1天延迟可接受（max_delay_days=1）——资金流类 + streak_days 连板
#   C 日频字段：3天延迟可接受（max_delay_days=3）——区间涨跌幅/52周/pe/股息率等（滚动但慢变）
#   D 静态字段：90天延迟可接受（max_delay_days=90）——恒定数据（ipo_price/股本/行业等，长假容忍）
#   （注：ABCD 缓存分级管"zhb 数据能否使用"；统一层 ABCD 路由矩阵管"各源优先级"——两个维度）
_ZHB_REALTIME_FIELDS = frozenset(
    {
        "change_pct",
        "change_pct_1d",
        "change_pct_2d",
        "amount",
        "amount_1d",
        "amount_2d",
        "price",
        "open",
        "high",
        "low",
        "prev_close",
    }
)

_ZHB_NEAR_REALTIME_FIELDS = frozenset(
    {
        # V10.3: 主力资金流向字段 — 日频准实时，1天延迟可接受
        "main_net_buy_hands",
        "main_net_buy_hands_1d",
        "main_net_buy_amount",
        "main_net_buy_amount_1d",
        # V16.3.3: streak_days 连板天数 1 个交易日即变（8/7 涨停 → 8/8 可能断板）——
        # 原归静态(3天)严重失真，上移准实时
        "streak_days",
    }
)

# V16.3.3: D 级静态字段 — 恒定数据（90天容忍：长假/停更不触发无谓 fallback）
# 依据：ipo_price 上市至今不变（茅台 31.39）、股本/员工/行业/概念低频变化
_ZHB_STATIC_FIELDS = frozenset(
    {
        "ipo_price",
        "employee_count",
        "total_shares",
        "float_shares",
        "total_shares_wan",
        "float_shares_wan",
        "industry",
        "industry_code",
        "board",
        "concepts",
        "list_date",
        "name",
    }
)


def zhb_field_safe(field_name: str) -> bool:
    """V10.2: 判断 zhb 指定字段在当前数据滞后状态下是否安全可用。
    V10.3: 新增准实时字段分类（max_delay_days=1）。
    V16.3.3: ABCD 四级缓存分级正式化（字典 12.15.6 缓存维度）：
    - A 实时字段（change_pct/amount/price 等）：zhb 日期必须是今天（max_delay_days=0）
    - B 准实时字段（main_net_buy/streak_days 等）：1天延迟可接受（max_delay_days=1）
    - C 日频字段（pe_ttm/high_52w/dividend_yield 等）：3天延迟可接受（max_delay_days=3）
    - D 静态字段（ipo_price/股本/行业等恒定数据）：90天延迟可接受（max_delay_days=90）

    Args:
        field_name: zhb 字段名（如 "change_pct", "pe_ttm", "high_52w"）

    Returns:
        True=该字段当前可安全使用 zhb 数据，False=应 fallback 原接口
    """
    if field_name in _ZHB_REALTIME_FIELDS:
        # A 实时字段：zhb 日期必须是今天（max_delay_days=0）
        return is_zhb_data_fresh(max_delay_days=0)
    if field_name in _ZHB_NEAR_REALTIME_FIELDS:
        # B 准实时字段：1天延迟可接受（max_delay_days=1）
        return is_zhb_data_fresh(max_delay_days=1)
    if field_name in _ZHB_STATIC_FIELDS:
        # D 静态字段：90天延迟可接受（max_delay_days=90）——恒定数据长假容忍
        return is_zhb_data_fresh(max_delay_days=90)
    # C 日频字段：3天延迟可接受（max_delay_days=3）
    return is_zhb_data_fresh(max_delay_days=3)


# ═══════════════════════════════════════════════════════════
# zhb 辅助数据集成（阶段三）
# ═══════════════════════════════════════════════════════════


def get_zhb_tip_info(code: str) -> Optional[Dict[str, Any]]:
    """V9.6: 获取个股财报日历信息（财报期/EPS/披露日/除权日/分红日）。"""
    try:
        from core.zhb_client import get_tip_info

        return get_tip_info(code)
    except Exception as _e:
        _debug_log(f"datasource zhb tip_info ({code}): {_e}")
        return None








# ═══════════════════════════════════════════════════════════
# V10.0 新增接口
# ═══════════════════════════════════════════════════════════
















# ═══════════════════════════════════════════════════════════
# zhb V10.1 新增：全量字段 + 衍生指标
# ═══════════════════════════════════════════════════════════


def get_zhb_full_market_snapshot(codes: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """V10.1: 全市场合并快照（tdxstat + tdxstat2 合并）。

    一次调用拿到全市场7938只股票的完整统计+资金流向数据，
    包含涨跌幅、PE、股息率、52周高低价、成交额、行业代码等。
    """
    try:
        from core.zhb_client import full_market_snapshot

        return full_market_snapshot(codes)
    except Exception as _e:
        _debug_log(f"datasource zhb full_market_snapshot: {_e}")
        return {}


def get_zhb_market_stat2_snapshot(codes: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """V10.1: 全市场资金流向+板块归属快照（tdxstat2）。"""
    try:
        from core.zhb_client import market_stat2_snapshot

        return market_stat2_snapshot(codes)
    except Exception as _e:
        _debug_log(f"datasource zhb market_stat2_snapshot: {_e}")
        return {}


def get_zhb_dividend_yield(code: str) -> Optional[float]:
    """V10.1: 获取股息率(%)。"""
    try:
        from core.zhb_client import get_dividend_yield

        return get_dividend_yield(code)
    except Exception as _e:
        _debug_log(f"datasource zhb dividend_yield ({code}): {_e}")
        return None


def get_zhb_streak_days(code: str) -> Optional[int]:
    """V10.1: 获取连涨连跌天数（正=连涨，负=连跌）。"""
    try:
        from core.zhb_client import get_streak_days

        return get_streak_days(code)
    except Exception as _e:
        _debug_log(f"datasource zhb streak_days ({code}): {_e}")
        return None


def get_zhb_change_ytd(code: str) -> Optional[float]:
    """V10.1: 获取年初至今涨跌幅(%)。"""
    try:
        from core.zhb_client import get_change_ytd

        return get_change_ytd(code)
    except Exception as _e:
        _debug_log(f"datasource zhb change_ytd ({code}): {_e}")
        return None




def get_zhb_amount_wan(code: str) -> Optional[float]:
    """V10.1: 获取今日成交额(万元)。"""
    try:
        from core.zhb_client import get_amount_wan

        return get_amount_wan(code)
    except Exception as _e:
        _debug_log(f"datasource zhb amount_wan ({code}): {_e}")
        return None


def get_tdx_day_tail(code: str) -> Dict[str, Any]:
    """V17.0.1d(2026-08-16): TDX 本机 .day 尾部快速读(零网络毫秒级).

    新版 .day 32B 记录: date<uint32> + open/high/low/close<int32×0.01元(分)> +
    amount<float32 元> + volume<int32 股> + reserved。
    返回 {price, open, high, low, amount_wan, date}。
    ⚠️ C1 终审修复(2026-08-15): 价格刻度 ÷1000→÷100(实测 600519 close=134199→1341.99)。
    用途: 休市/盘前 canonical OHLC/成交额缺口兜底(与 TDX 快照同源, 零网络)。
    """
    try:
        import os as _os
        import struct as _st

        _mkt = "bj" if code.startswith(("92", "8", "4", "43", "83", "87")) else ("sh" if code.startswith(("6", "9")) else "sz")
        _path = _os.path.join(r"C:\new_tdx64\vipdoc", _mkt, "lday", f"{_mkt}{code}.day")
        with open(_path, "rb") as _f:
            _f.seek(-32, 2)
            _rec = _f.read(32)
        if len(_rec) < 32:
            return {}
        _date = _st.unpack_from("<I", _rec, 0)[0]
        _open = _st.unpack_from("<I", _rec, 4)[0] / 100.0
        _high = _st.unpack_from("<I", _rec, 8)[0] / 100.0
        _low = _st.unpack_from("<I", _rec, 12)[0] / 100.0
        _close = _st.unpack_from("<I", _rec, 16)[0] / 100.0
        if _close <= 0:
            return {}
        _amount = _st.unpack_from("<f", _rec, 20)[0]  # 元
        _volume = _st.unpack_from("<I", _rec, 24)[0]  # 股
        return {
            "price": _close,
            "open": _open,
            "high": _high,
            "low": _low,
            "amount_wan": (_amount / 1e4) if _amount and _amount > 0 else 0.0,
            "volume_hand": (_volume / 100.0) if _volume and _volume > 0 else 0.0,
            "date": _date,
        }
    except Exception as _e:
        _debug_log(f"get_tdx_day_tail ({code}): {_e}")
        return {}






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
        from core.zhb_client import get_main_net_buy

        return get_main_net_buy(code)
    except Exception as _e:
        _debug_log(f"datasource zhb main_net_buy ({code}): {_e}")
        return None






def get_zhb_single_stock_data(code: str) -> Optional[Dict[str, Any]]:
    """V10.1: 获取单只股票的完整zhb数据（tdxstat + tdxstat2合并）。

    V16.0: 合并 tipinfo 的 report_period 为 report_date 字段，
    修复 ZHB 财报事件锁失效（get_sina_financial_report 读 zhb["report_date"] 恒空问题）。

    Returns:
        合并后的股票数据字典，包含涨跌幅、PE、阶段涨幅、52周高低、
        股息率、行业代码、成交额、IPO发行价等字段。
        获取失败返回 None。
    """
    try:
        from core.zhb_client import get_stock_stat, get_stock_stat2, get_tip_info

        stat1 = get_stock_stat(code)
        stat2 = get_stock_stat2(code)
        if not stat1 and not stat2:
            return None
        result = dict(stat1) if stat1 else {}
        if stat2:
            result.update(stat2)
        # V16.0: 合并 tipinfo report_period → report_date（ZHB 财报事件锁核心 Key）
        try:
            tip = get_tip_info(code)
            if tip and tip.get("report_period"):
                result["report_date"] = str(tip["report_period"]).strip()
        except Exception as _e:
            _debug_log(f"datasource zhb tipinfo merge ({code}): {_e}")
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
    fg = [
        r
        for r in results
        if r["status"] in ("GD上传失败", "GD上传异常", "GD文件夹失败", "GD未连接")
    ]
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


@cached(
    category="dragon_tiger",
    ttl_seconds=TTL["dragon_tiger"],
    trading_day=True,
    valid_if=make_valid_if(min_size=1),
)  # V15.2: 至少 1 条记录才缓存
def get_dragon_tiger_board(
    code: str, days: int = 30, include_seats: bool = True, enhance_seats: bool = True
) -> Dict[str, Any]:
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
    start_str = (datetime.strptime(today_str, "%Y-%m-%d") - timedelta(days=days)).strftime(
        "%Y-%m-%d"
    )
    records = []
    data = eastmoney_datacenter(
        code,
        "RPT_DAILYBILLBOARD_DETAILSNEW",
        filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{start_str}')(TRADE_DATE<='{today_str}')",
        page_size=50,
        sort_columns="TRADE_DATE",
        sort_types="-1",
    )
    for row in data:
        rec = {
            "date": str(row.get("TRADE_DATE", "") or "")[:10],
            "reason": row.get("EXPLANATION", ""),
            "net_buy": round((row.get("BILLBOARD_NET_AMT") or 0) / 10000, 1),
            "turnover": round(_safe_float(row.get("TURNOVERRATE")), 2),
        }
        # V16.1: 保留高价值字段（sht 用：买卖占比/分析文本/偏离度）
        if row.get("EXPLAIN"):
            rec["explain"] = row["EXPLAIN"]
        if row.get("BUY_RATIO") is not None:
            rec["buy_ratio"] = round(_safe_float(row.get("BUY_RATIO")), 2)
        if row.get("SELL_RATIO") is not None:
            rec["sell_ratio"] = round(_safe_float(row.get("SELL_RATIO")), 2)
        if row.get("DEAL_NET_RATIO") is not None:
            rec["net_ratio"] = round(_safe_float(row.get("DEAL_NET_RATIO")), 2)
        if row.get("ACCUM_AMOUNT") is not None:
            rec["accum_amount"] = _safe_float(row.get("ACCUM_AMOUNT"))
        if row.get("FREE_MARKET_CAP") is not None:
            rec["free_market_cap"] = _safe_float(row.get("FREE_MARKET_CAP"))
        # D1-D5 涨跌偏离度（龙虎榜判定依据）
        for _dn in ("D1", "D2", "D5", "D10", "D20", "D30"):
            _k = f"{_dn}_CLOSE_ADJCHRATE"
            if row.get(_k) is not None:
                rec[f"dev_{_dn.lower()}"] = round(_safe_float(row.get(_k)), 3)
        records.append(rec)

    seats: Dict[str, List[Any]] = {"buy": [], "sell": []}
    institution: Dict[str, float] = {"buy_amt": 0.0, "sell_amt": 0.0, "net_amt": 0.0}

    if records and include_seats:
        latest_date = records[0]["date"]
        # 买入/卖出席席：用最新上榜日期 + SECURITY_CODE 过滤（单引号日期）
        buy_data = eastmoney_datacenter(
            code,
            "RPT_BILLBOARD_DAILYDETAILSBUY",
            filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{latest_date}')(TRADE_DATE<='{latest_date}')",
            page_size=50,
            sort_columns="BUY",
            sort_types="-1",
        )
        for row in buy_data[:5]:
            seats["buy"].append(
                {
                    "name": row.get("OPERATEDEPT_NAME", ""),
                    "code": str(row.get("OPERATEDEPT_CODE", "")),
                    "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                    "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                    "net": round((row.get("NET") or 0) / 10000, 1),
                }
            )
        sell_data = eastmoney_datacenter(
            code,
            "RPT_BILLBOARD_DAILYDETAILSSELL",
            filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{latest_date}')(TRADE_DATE<='{latest_date}')",
            page_size=50,
            sort_columns="SELL",
            sort_types="-1",
        )
        for row in sell_data[:5]:
            seats["sell"].append(
                {
                    "name": row.get("OPERATEDEPT_NAME", ""),
                    "code": str(row.get("OPERATEDEPT_CODE", "")),
                    "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                    "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                    "net": round((row.get("NET") or 0) / 10000, 1),
                }
            )
        # 机构专用席位（code == "0" 为机构专用）
        for row in buy_data:
            if str(row.get("OPERATEDEPT_CODE", "")) == "0":
                institution["buy_amt"] += row.get("BUY") or 0
        for row in sell_data:
            if str(row.get("OPERATEDEPT_CODE", "")) == "0":
                institution["sell_amt"] += row.get("SELL") or 0
        institution["buy_amt"] = round(institution["buy_amt"] / 10000, 1)
        institution["sell_amt"] = round(institution["sell_amt"] / 10000, 1)
        institution["net_amt"] = round(institution["buy_amt"] - institution["sell_amt"], 1)

    # V7.5新增：主力净额连续性统计
    net_sum_5d = round(sum(r["net_buy"] for r in records[:5]), 1)
    net_sum_30d_or_days = round(sum(r["net_buy"] for r in records), 1)
    consecutive_net_buy_days = sum(1 for r in records if r["net_buy"] > 0)

    result = {
        "records": records,
        "seats": seats,
        "institution": institution,
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


@cached(
    category="dragon_tiger",
    ttl_seconds=TTL["dragon_tiger"],
    trading_day=True,
    valid_if=make_valid_if(min_size=1),
)  # V15.2: 至少 1 条记录才缓存
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
            "pageNumber": "1",
            "pageSize": "200",
            "sortColumns": "TRADE_DATE",
            "sortTypes": "-1",
            "source": "WEB",
            "client": "WEB",
        }
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=15)
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


async def get_dragon_tiger_board_async(
    session, code: str, days: int = 30, include_seats: bool = True, enhance_seats: bool = True
) -> Dict[str, Any]:
    """异步版: 单只股票龙虎榜查询（代理到同步版）。

    V10.2: 移除 today_str 参数（同步版已内部自动计算）。
    """
    return await asyncio.to_thread(get_dragon_tiger_board, code, days, include_seats, enhance_seats)


async def get_recent_dragon_tiger_async(session, days: int = 5) -> Dict[str, Any]:
    """异步版: 全市场龙虎榜上榜记录（代理到同步版）。"""
    return await asyncio.to_thread(get_recent_dragon_tiger, days)


# ═══════════════════════════════════════════════════════════
# V15.2 P0: push2 完整行情 fallback (ZHB/TDX 都拿不到 price 时使用)
# ═══════════════════════════════════════════════════════════
@requires_push2
def get_em_quote_full(code: str) -> Dict[str, Any]:
    """V15.2 P0 修复: 通过东财 push2 stock/get 获取完整行情。

    V16.3.3: host 参数化重构——本函数走 push2 主域（风控最严，最后手段）；
    常规兜底请用 get_em_quote_full_delay（push2delay 镜像域，风控独立）。
    """
    return _em_quote_full_impl(code, "https://push2.eastmoney.com/api/qt/stock/get")


def get_em_quote_full_delay(code: str) -> Dict[str, Any]:
    """V16.3.3 (2026-08-10 字典 12.15.5): push2delay 镜像域版全字段行情。

    2026-08-10 实测：push2 主域连接级风控（RemoteDisconnected）；push2delay 风控独立、
    114 字段全量可用、延时 15 分钟非盘中无影响——统一层 L3 东财兜底应优先本函数。
    """
    return _em_quote_full_impl(code, "https://push2delay.eastmoney.com/api/qt/stock/get")


def _em_quote_full_impl(code: str, host: str = "https://push2delay.eastmoney.com/api/qt/stock/get") -> Dict[str, Any]:
    """内部实现：host 参数化的全字段行情获取（f43-f221，字典 12.9.1）。

    ZHB tdxstat.cfg 35 字段中无 price/change_pct/open/high/low/last_close 等行情字段，
    只能从 HTTP 接口拿。push2 stock/get 是最权威的实时行情源（盘后返回收盘价）。

    Returns:
        dict: {
            "price": float,           # f43  现价（盘后=昨收）
            "open": float,            # f46  今开
            "high": float,            # f44  最高
            "low": float,             # f45  最低
            "last_close": float,      # f60  昨收
            "change_pct": float,      # f170 涨跌幅(%)（push2 直接给出，不需要用 price-昨收 算）
            "amplitude_pct": float,   # f171 振幅(%)
            "change_amt": float,      # f169 涨跌额
            "volume_hand": float,     # f47  成交量(手)
            "amount_wan": float,      # f48  成交额(元→万元)
            "turnover_pct": float,    # f168 换手率(%)
            "pe_ttm": float,          # f163 PE(TTM) (fltt=2 下为浮点，无需 /100)
            "pe_dynamic": float,
            "pb": float,
            "mcap_yi": float,         # f116 总市值(元→亿元)
            "float_mcap_yi": float,   # f117 流通市值(元→亿元)
            "total_shares": float,    # f84  总股本(股→万股)
            "float_shares": float,    # f85  流通股本(股→万股)
            "name": str,              # f58  股票名称（最新）
            "industry": str,          # f127 行业名称
            "board": str,             # f128 地域板块名称
            "list_date": str,         # f189 上市日期
            "data_date": str,         # 行情快照日期
            # V17.0.7 财务 TTM 族（口径经 fuyao 官方报表终判）:
            "ocf_ttm": float,           # f103 经营活动现金流量净额 TTM (元)
            "revenue_ttm": float,       # f104 营业总收入 TTM (元)
            "net_profit_period": float, # f105 归母净利润 最新报告期 (元)
            "eps_deduct_ttm": float,    # f108 扣非每股收益 TTM (元/股)
            "net_profit_annual": float, # f109 归母净利润 最新年报 (元)
            "eps_annual": float,        # f160 年报EPS (=f109/f84) (元/股)
            "undist_profit_ps": float,  # f190 每股未分配利润 (元/股)
        }
    """
    if not code or len(code) != 6:
        return {}
    secid = f"{em_secid_prefix(code)}{code}"  # V17.0 S3: 统一前缀(含北交所 92)

    url = host
    # V16.1: 字段包从 19 个扩展为已验证字段包（2026-08-04 官方 TdxQuant 交叉验证）
    #   f51/f52=涨停/跌停价、f55=EPS、f92=BPS、f126=股息率、f162-167=PE×3/PB
    #   f174/f175=52周高低、f137-146=资金流12字段、f198=行业码、f80=交易时段
    #   f129=概念列表（V16.1.7: 概念链 push2 兜底源）
    # 生产字段包（固定，非 f1-f250 全量，防风控）
    params = {
        "fltt": "2",
        "invt": "2",
        "secid": secid,
        "fields": (
            "f43,f44,f45,f46,f47,f48,f57,f58,f60,f84,f85,"
            "f116,f117,f127,f128,f129,f168,f169,f170,f171,f189,"  # V16.2.3: f168 换手率补回（sht 换手率 0.00%）
            "f51,f52,f55,f92,f126,f162,f163,f164,f165,f166,f167,"
            "f174,f175,f198,f80,f221,"  # V16.2: f221 报告期
            "f135,f136,f137,f138,f139,f140,f141,f142,f143,f144,f145,f146,"
            "f178,"
            # V17.0.7(2026-08-25 字典终破): 财务 TTM 族——f103 经营现金流净额(TTM 元)/
            # f104 营业总收入(TTM 元)/f105 归母净利(最新报告期 元)/f108 扣非EPS(TTM)/
            # f109 归母净利(最新年报 元)/f160 年报EPS/f190 每股未分配利润
            "f103,f104,f105,f108,f109,f160,f190"
        ),
        "ut": "f057cbcbce2a86e2866ab8877db1d059",
    }
    headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
    try:
        r = em_get(url, params=params, headers=headers, timeout=10)
        if r is None:
            return {}
        d = r.json()
        if not d or "data" not in d or not d["data"]:
            return {}
        data = d["data"]
        result: Dict[str, Any] = {}

        # 价格类（push2 用 fltt=2/invt=2 时，f43/f44/f45/f46/f60/f169 直接是元为单位的 float）
        for src, dst in [
            ("f43", "price"),
            ("f44", "high"),
            ("f45", "low"),
            ("f46", "open"),
            ("f60", "last_close"),
            ("f169", "change_amt"),
        ]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # 涨跌幅/振幅/换手率（push2 直接给出数字，单位 %）
        for src, dst in [
            ("f170", "change_pct"),
            ("f171", "amplitude_pct"),
            ("f168", "turnover_pct"),
        ]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # 成交量(手) — push2 f47 单位是手
        vol_hand = data.get("f47")
        if vol_hand is not None and vol_hand != "-":
            try:
                result["volume_hand"] = float(vol_hand)
            except (TypeError, ValueError):
                pass
        # 成交额(元) — push2 f48 单位是元，转万元
        amt_yuan = data.get("f48")
        if amt_yuan is not None and amt_yuan != "-":
            try:
                result["amount_wan"] = float(amt_yuan) / 10000.0
            except (TypeError, ValueError):
                pass

        # 总市值/流通市值（push2 f116/f117 单位是元，转亿元）
        mcap_yuan = data.get("f116")
        if mcap_yuan is not None and mcap_yuan != "-":
            try:
                result["mcap_yi"] = float(mcap_yuan) / 1e8
            except (TypeError, ValueError):
                pass
        float_mcap_yuan = data.get("f117")
        if float_mcap_yuan is not None and float_mcap_yuan != "-":
            try:
                result["float_mcap_yi"] = float(float_mcap_yuan) / 1e8
            except (TypeError, ValueError):
                pass

        # 股本（push2 f84/f85 单位是股，转万股）
        total_shares = data.get("f84")
        if total_shares is not None and total_shares != "-":
            try:
                result["total_shares"] = float(total_shares) / 10000.0
            except (TypeError, ValueError):
                pass
        float_shares = data.get("f85")
        if float_shares is not None and float_shares != "-":
            try:
                result["float_shares"] = float(float_shares) / 10000.0
            except (TypeError, ValueError):
                pass

        # 名称/行业/地域/上市日期
        name = data.get("f58")
        if name and isinstance(name, str):
            result["name"] = name
        industry = data.get("f127")
        if industry and isinstance(industry, str):
            result["industry"] = industry
        board = data.get("f128")
        if board and isinstance(board, str):
            result["board"] = board
        # V16.1.7: f129 概念列表（逗号分隔 → list，概念链 push2 兜底源）
        concepts_raw = data.get("f129")
        if concepts_raw and isinstance(concepts_raw, str):
            result["concepts"] = [c.strip() for c in concepts_raw.split(",") if c.strip()]
        list_date = data.get("f189")
        if list_date:
            try:
                ld = str(int(list_date))
                if len(ld) == 8:
                    result["list_date"] = f"{ld[:4]}-{ld[4:6]}-{ld[6:8]}"
            except (TypeError, ValueError):
                pass

        # ─────────────────────────────────────────────
        # V16.1: push2 扩展字段（2026-08-04 官方 TdxQuant 交叉验证）
        # ─────────────────────────────────────────────
        # 涨停/跌停价（f51/f52，官方 ZTPrice/DTPrice 精确匹配）
        for src, dst in [("f51", "limit_up"), ("f52", "limit_down")]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # EPS/BPS（f55/f92，与东财 F10 精确匹配）
        for src, dst in [("f55", "eps"), ("f92", "bps")]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # 股息率（f126，官方 DYRatio 匹配）
        v = data.get("f126")
        if v is not None and v != "-":
            try:
                result["dividend_yield"] = float(v)
            except (TypeError, ValueError):
                pass

        # PE 三口径 + PB（f162=动态PE/f163=静态PE-TTM/f164=MorePE/f167=PB）
        pe_map = {
            "f162": "pe_dynamic",
            "f163": "pe_ttm",
            "f164": "pe_more",
            "f167": "pb",
        }
        for src, dst in pe_map.items():
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # 52周高低（f174/f175，官方 HisHigh/HisLow 精确匹配）
        for src, dst in [("f174", "high_52w"), ("f175", "low_52w")]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # 行业板块代码（f198，如 BK1277）
        v = data.get("f198")
        if v and isinstance(v, str):
            result["industry_code_push2"] = v

        # V16.2: 最新报告期（f221，YYYYMMDD）
        v = data.get("f221")
        if v and str(v).strip() and str(v).strip() != "-":
            result["report_period"] = str(v).strip()

        # 交易时段数组（f80，JSON 字符串 → 原样保留）
        v = data.get("f80")
        if v and isinstance(v, str):
            try:
                result["trading_periods"] = json.loads(v)
            except (TypeError, ValueError, json.JSONDecodeError):
                result["trading_periods"] = []

        # 资金流 12 字段(f135-f146)——V17.0(2026-08-14 同花顺表头+买卖差自洽定案):
        #   四档买卖结构: f135/136/137=特大(超大)单买/卖/净、f138/139/140=大单买/卖/净、
        #                  f141/142/143=中单买/卖/净、f144/145/146=小单买/卖/净
        #   (f137=f135-f136、f140=f138-f139、f143=f141-f142、f146=f144-f145 全自洽实测)
        #   **主力净额(同花顺/通达信定义=特大+大单买卖差)= f137+f140**(由 data_provider 聚合)
        #   单位: 元
        flow_map = {
            "f137": ("fund_super_today", "fund_flow"),   # 特大(超大)单净
            "f138": ("fund_super_buy", "fund_flow"),     # 特大单买入金额
            "f139": ("fund_super_sell", "fund_flow"),    # 特大单卖出金额
            "f140": ("fund_large_today", "fund_flow"),   # 大单净
            "f141": ("fund_mid_buy", "fund_flow"),       # 中单买入金额
            "f142": ("fund_mid_sell", "fund_flow"),      # 中单卖出金额
            "f143": ("fund_mid_today", "fund_flow"),     # 中单净
            "f144": ("fund_small_buy", "fund_flow"),     # 小单买入金额
            "f145": ("fund_small_sell", "fund_flow"),    # 小单卖出金额
            "f146": ("fund_small_today", "fund_flow"),   # 小单净
        }
        for src, (dst, _cat) in flow_map.items():
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # V17.0(2026-08-14): 主力净额 = 特大单净 + 大单净(同花顺/通达信"主力净额"官方定义)
        _sv = result.get("fund_super_today")
        _lv = result.get("fund_large_today")
        if _sv is not None and _lv is not None:
            result["fund_main_today"] = _sv + _lv

        # 近5日主力净流入数组（f178，JSON）
        v = data.get("f178")
        if v and isinstance(v, str):
            try:
                result["fund_5d_array"] = json.loads(v)
                # V17.0: 5日主力净由 f178 数组聚合(替代原 f141 误读)
                _s5 = sum(float(x.get("mainNetAmt", 0)) for x in result["fund_5d_array"] if isinstance(x, dict))
                if _s5:
                    result["fund_main_5d"] = _s5
            except (TypeError, ValueError, json.JSONDecodeError):
                pass

        # V17.0.7(2026-08-25 字典终破): 财务 TTM 族(单位见键注释; 口径经
        # fuyao 官方三大报表 5/5 终判 + 报告期切换动态双证——详见
        # docs/field_verification/20260825_cross_analysis.md)
        for src, dst in [
            ("f103", "ocf_ttm"),            # 经营活动现金流量净额 TTM (元)
            ("f104", "revenue_ttm"),        # 营业总收入 TTM (元)
            ("f105", "net_profit_period"),  # 归母净利润 最新报告期 (元)
            ("f108", "eps_deduct_ttm"),     # 扣非每股收益 TTM (元/股)
            ("f109", "net_profit_annual"),  # 归母净利润 最新年报 (元)
            ("f160", "eps_annual"),         # 年报EPS (=f109/f84) (元/股)
            ("f190", "undist_profit_ps"),   # 每股未分配利润 (元/股, ≡ulist f48)
        ]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        result["data_date"] = datetime.now().strftime("%Y-%m-%d")
        return result
    except Exception as _e:
        _debug_log(f"sc_datasource get_em_quote_full ({code}): {_e}")
        return {}


# ═══════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════
# V16.3.3 (2026-08-10 字典 12.15.5): 涨停池三源互校
# ═══════════════════════════════════════════════════════════
@cached(category="market_emotion_multi", ttl_seconds=TTL["market_emotion_multi"], trading_day=True,
        valid_if=lambda r: bool(r and r.get("sources")))
def get_limit_pool_multi_source(date: Optional[str] = None) -> Dict[str, Any]:
    """涨停池三源互校——财联社=KPL=复盘啦（2026-08-10 实测 99=99=99 三源一致）。

    源顺序（低风险优先）: 财联社 → KPL → 复盘啦 → push2ex(东财兜底)。
    每源 1 次调用（间隔 2s，失败自动跳过——不阻塞、不重复请求）。

    Args:
        date: 可选日期 YYYY-MM-DD（push2ex 历史；财联社/KPL/复盘啦用当日）

    Returns:
        dict: {
            "total": int,              # 涨停总数（多源一致值）
            "sources": {源: 数量},     # 各源实测值（None=源失败）
            "cross_verified": bool,    # ≥2 源一致
            "max_ladder": int,         # 最高连板
            "detail": dict,            # 复盘啦 StockList 全量等
        }
    """
    import time as _time
    from collections import Counter

    out: Dict[str, Any] = {"sources": {}, "cross_verified": False, "max_ladder": 0, "detail": {}}

    cls_n = None
    try:
        from stock_common import get_cls_market_emotion
        emo = get_cls_market_emotion() or {}
        try:
            cls_n = int(emo.get("up_ratio_num") or 0)
        except (ValueError, TypeError):
            cls_n = None
    except Exception as _e:
        _debug_log(f"multi_source cls: {_e}")
    out["sources"]["cls"] = cls_n
    _time.sleep(2.0)

    kpl_n = None
    try:
        from stock_common import get_kpl_market_sentiment
        sent = get_kpl_market_sentiment() or {}
        try:
            kpl_n = int(sent.get("ztjs") or 0)
        except (ValueError, TypeError):
            kpl_n = None
        try:
            out["max_ladder"] = max(out["max_ladder"], int(sent.get("lbgd") or 0))
        except (ValueError, TypeError):
            pass
    except Exception as _e:
        _debug_log(f"multi_source kpl: {_e}")
    out["sources"]["kpl"] = kpl_n
    _time.sleep(2.0)

    fupan_n = None
    fupan_list = []
    try:
        from levistock.stock.stock_fupanla_kph import get_zttt
        z = get_zttt() or {}
        sl = z.get("StockList") or []
        fupan_list = sl
        fupan_n = len(sl)
        for r in sl:
            if len(r) > 2:
                try:
                    out["max_ladder"] = max(out["max_ladder"], int(r[2]))
                except (ValueError, TypeError):
                    pass
    except Exception as _e:
        _debug_log(f"multi_source fupan: {_e}")
    out["sources"]["fupan"] = fupan_n
    out["detail"]["fupan_list"] = fupan_list[:200]
    _time.sleep(2.0)

    push2ex_n = None
    if cls_n is None and kpl_n is None and fupan_n is None:
        try:
            from stock_common import get_limit_up_pool
            pool = get_limit_up_pool(date) or []
            push2ex_n = len(pool)
        except Exception as _e:
            _debug_log(f"multi_source push2ex: {_e}")
    out["sources"]["push2ex"] = push2ex_n

    vals = [v for v in (cls_n, kpl_n, fupan_n, push2ex_n) if v is not None]
    if vals:
        cnt = Counter(vals)
        top_v, top_c = cnt.most_common(1)[0]
        if top_c >= 2:
            out["total"] = top_v
            out["cross_verified"] = True
        else:
            out["total"] = max(vals)
    else:
        out["total"] = 0

    return out
# ═══════════════════════════════════════════════════════════
# V16.3.3 (2026-08-10 字典 12.15.5): 复盘啦缓存包装（levistock 直连无缓存——mak B 段高频）
# ═══════════════════════════════════════════════════════════
@cached(category="fupan_review", ttl_seconds=TTL["fupan_review"], trading_day=True)
def get_fupan_zttt() -> Dict[str, Any]:
    """复盘啦涨停天梯（get_zttt 缓存包装）——StockList[99]/ZhuShuList[22] 完整结构。
    字典 12.10.4：涨停天梯；2026-08-10 实测 99 只与财联社/KPL 三源一致。
    """
    try:
        from levistock.stock.stock_fupanla_kph import get_zttt
        return get_zttt() or {}
    except Exception as _e:
        _debug_log(f"datasource fupan zttt: {_e}")
        return {}
@cached(category="fupan_review", ttl_seconds=TTL["fupan_review"], trading_day=True)
def get_fupan_pmsl() -> Dict[str, Any]:
    """复盘啦盘面梳理（get_pmsl 缓存包装）——List[30] 每条 6 字段（TimeMin/TagID/ZSCode/Detail/TagShuXing/TagName）。"""
    try:
        from levistock.stock.stock_fupanla_kph import get_pmsl
        return get_pmsl() or {}
    except Exception as _e:
        _debug_log(f"datasource fupan pmsl: {_e}")
        return {}


# ═══════════════════════════════════════════════════════════
# V16.3.3 (2026-08-10 字典 12.15.8): 永久字段独立缓存（10 年 TTL）
# ═══════════════════════════════════════════════════════════
@cached(category="static_permanent", ttl_seconds=TTL["static_permanent"])
def get_stock_permanent_info(code: str) -> Dict[str, Any]:
    """永久不变字段（10 年缓存——字典 12.15.8 static_permanent）。
    - list_date: push2 f189（东财基础信息——外层永久缓存吸收单次 HTTP 成本）
    - ipo_price: ZHB tdxstat2 Col[16]（本地零网络）
    - name_core: 由调用方 parse_stock_name 处理（核心名称永久）
    返回 {"list_date", "ipo_price"}（缺失字段省略）。
    """
    out: Dict[str, Any] = {}
    try:
        # V16.3.3: list_date 走 push2delay f189（push2 主域连接风控实测——f189 拿不到）
        # V16.4.1: "9" 前缀误命中 920 北交所(secid 1.920xxx 恒失败) → 北交所分支提前
        if code.startswith(("92", "8", "4", "43", "83", "87")):
            _mkt = "0"
        else:
            _mkt = "1" if code.startswith(("6", "9")) else "0"
        r = _quick_request(
            "https://push2delay.eastmoney.com/api/qt/stock/get",
            params={"secid": f"{_mkt}.{code}", "fields": "f189",
                    "ut": "f057cbcbce2a86e2866ab8877db1d059"},
            timeout=10,
        )
        if r is not None and r.status_code == 200:
            _d = r.json().get("data") or {}
            if _d.get("f189"):
                out["list_date"] = str(_d["f189"])
    except Exception as _e:
        _debug_log(f"permanent list_date ({code}): {_e}")
    if not out.get("list_date"):
        # TDX 0x0010 兜底（ipo_date 字段——字典 12.14 已录）
        try:
            from core.tdx_client import tdx_get_finance_info
            fin = tdx_get_finance_info(code) or {}
            if fin.get("ipo_date"):
                out["list_date"] = str(fin["ipo_date"])
        except Exception as _e:
            _debug_log(f"permanent list_date tdx ({code}): {_e}")
    try:
        from core.zhb_client import get_zhb_single_stock_data
        z = get_zhb_single_stock_data(code) or {}
        if z.get("ipo_price"):
            out["ipo_price"] = z["ipo_price"]
    except Exception as _e:
        _debug_log(f"permanent ipo_price ({code}): {_e}")
    return out
    """复盘啦盘面梳理（get_pmsl 缓存包装）——List[30] 每条 6 字段。"""
    try:
        from levistock.stock.stock_fupanla_kph import get_pmsl
        return get_pmsl() or {}
    except Exception as _e:
        _debug_log(f"datasource fupan pmsl: {_e}")
        return {}


# 数据源模块总计：68个函数（含同步+异步版本）
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# V8.9: 舆情互动层 — 同花顺热榜 / 东财人气榜 / 个股概念命中
# 接口来源：a-stock-data V3.3.0 Layer 10，全部零鉴权
# ═══════════════════════════════════════════════════════════


@cached(category="basic_info", ttl_seconds=TTL["basic_info"], cross_verify=True)
@requires_push2
def eastmoney_stock_info_push2(code: str) -> Dict[str, Any]:
    """东财 push2 个股基本面信息（含上市日期 f189，不走 TDX）。

    当 TDX 无法获取 list_date 时作为 fallback。
    返回: {code, name, industry, total_shares, float_shares, mcap, float_mcap, list_date}
    """
    market_code = 1 if em_secid_prefix(code) == "1." else 0  # V17.0 S3: 统一(含北交所 92)
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "fltt": "2",
        "invt": "2",
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


@cached(
    category="ths_hot_reason",
    ttl_seconds=TTL["ths_hot_reason"],
    trading_day=True,
    valid_if=make_valid_if(check_zeros=False, min_size=1),
)  # V15.2: 拒绝空 list；空时返回 [] 不缓存
def ths_hot_list(period: str = "hour") -> List[Dict[str, Any]]:
    """同花顺热榜。period: hour/day。
    返回每只: rank/code/name/heat(人气值)/pct/rank_chg(排名变化)/concepts(概念标签)/tag。

    V15.2 降级策略：HTTP 失败时返回 [] 而非抛异常，避免 val 9 个策略
    (01/02/03/05/06/07/08/16) 因 hot_pool 为空而 0 命中。
    """
    try:
        r = _quick_request(
            "https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/stock",
            params={"stock_type": "a", "type": period, "list_type": "normal"},
            headers={"User-Agent": UA},
            timeout=10,
        )
        if r is None:
            _debug_log(
                "ths_hot_list: HTTP 返回 None，网络可能限流（不影响 val 报告，hot_pool 降级为空）"
            )
            return []
        lst = (r.json().get("data") or {}).get("stock_list") or []
    except Exception as _e:
        _debug_log(f"ths_hot_list ({period}) HTTP 失败，降级返回空 list: {_e}")
        return []
    out = []
    for it in lst:
        tag = it.get("tag") or {}
        out.append(
            {
                "rank": it.get("order"),
                "code": it.get("code"),
                "name": it.get("name"),
                "heat": it.get("rate"),
                "pct": it.get("rise_and_fall"),
                "rank_chg": it.get("hot_rank_chg"),
                "concepts": tag.get("concept_tag") or [],
                "tag": tag.get("popularity_tag", ""),
            }
        )
    return out


@cached(category="hot_rank", ttl_seconds=TTL["hot_rank"])
@requires_push2
def em_hot_rank(top: int = 50) -> List[Dict[str, Any]]:
    """东财人气榜。返回 rank/code/name/price/pct/rank_chg。"""
    _hot_body = {"appId": "appId01", "globalId": "786e4c21-70dc-435a-93bb-38"}
    try:
        # V16.0.2: 改用 _quick_request（走 _DOMAIN_LIMITS 限流），
        # 原 EM_SESSION.post 直连绕过限流 → emappdata 10rps 封禁隐患
        import json as _json

        r = _quick_request(
            "https://emappdata.eastmoney.com/stockrank/getAllCurrentList",
            data=_json.dumps({**_hot_body, "marketType": "", "pageNo": 1, "pageSize": top}),
            headers={"User-Agent": UA, "Content-Type": "application/json"},
            timeout=10,
            method="POST",
        )
        if r is None:
            return []
        data = r.json().get("data") or []
        if not data:
            return []
        # 人气榜只给带前缀代码，用 push2delay 补名称/价格(V16.4.1: 原 push2 主域——
        # 连接级封禁期会整体失败 → 改 push2delay 镜像域,与采集脚本 ulist239 一致)
        secids = [("0." if it["sc"].startswith("SZ") else "1.") + it["sc"][2:] for it in data]
        u = _quick_request(
            "https://push2delay.eastmoney.com/api/qt/ulist.np/get",
            params={
                "ut": "f057cbcbce2a86e2866ab8877db1d059",
                "fltt": 2,
                "invt": 2,
                "fields": "f14,f3,f12,f2",
                "secids": ",".join(secids),
            },
            headers={"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"},
            timeout=10,
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
        out.append(
            {
                "rank": it["rk"],
                "code": code,
                "name": name,
                "price": price,
                "pct": pct,
                "rank_chg": it.get("hisRc"),
            }
        )
    return out


@cached(category="hot_concept", ttl_seconds=TTL["hot_concept"])
def em_hot_concept(code: str) -> List[Dict[str, Any]]:
    """东财个股热门概念命中（这只票当下被市场归到哪些概念在炒）。
    返回 [{concept, bk, hit(命中热度)}, ...]，按热度降序。
    """
    _hot_body = {"appId": "appId01", "globalId": "786e4c21-70dc-435a-93bb-38"}
    try:
        # V16.0.2: 改用 _quick_request（走限流），原 EM_SESSION.post 直连绕过限流
        import json as _json

        prefix = "BJ" if code.startswith(("92", "8", "4", "43", "83", "87")) else ("SH" if code.startswith("6") else "SZ")
        r = _quick_request(
            "https://emappdata.eastmoney.com/stockrank/getHotStockRankList",
            data=_json.dumps({**_hot_body, "srcSecurityCode": prefix + code}),
            headers={"User-Agent": UA, "Content-Type": "application/json"},
            timeout=10,
            method="POST",
        )
        if r is None:
            return []
        data = r.json().get("data") or []
    except Exception as _e:
        _debug_log(f"datasource em_hot_concept ({code}): {_e}")
        return []
    return [
        {"concept": x.get("conceptName"), "bk": x.get("conceptId"), "hit": x.get("hitCount")}
        for x in data
    ]


# ═══════════════════════════════════════════════════════════
# V12.0: 东财 HTTP 替代接口（完全移除 easy_tdx 依赖）
# ═══════════════════════════════════════════════════════════
# 这些函数替代原 TDX MacClient 的板块/资金流接口，使用东财 push2/datacenter HTTP 接口。
# tdx_client.py 中的 tdx_get_board_*/tdx_get_fund_flow 等函数将委托到这些 HTTP 函数。
# ═══════════════════════════════════════════════════════════


# 板块类型 → 东财 fs 参数映射（替代 easy_tdx BoardType 枚举）
_EM_BOARD_TYPE_FS_MAP = {
    0: "m:90+t:2",  # 行业一级
    1: "m:90+t:2",  # 行业二级（东财不区分，使用相同 fs）
    3: "m:90+t:1",  # 地域
    4: "m:90+t:3",  # 概念
}


@requires_push2
def get_em_board_list(board_type: int = 0) -> List[Dict[str, Any]]:
    """V12.0: 获取板块列表（替代 TDX MacClient.get_board_list）。

    使用东财 push2 clist 接口，支持行业/概念/地域板块。

    Args:
        board_type: 0=行业一级, 1=行业二级, 3=地域, 4=概念 (兼容 easy_tdx BoardType)

    Returns:
        list: [{"rank": int, "code": str, "name": str, "price": float,
                "change_pct": float, "leader_name": str, "leader_change": float,
                "up_count": int, "down_count": int}, ...]
    """
    fs = _EM_BOARD_TYPE_FS_MAP.get(board_type)
    if not fs:
        _debug_log(f"datasource get_em_board_list: unsupported board_type={board_type}")
        return []

    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "200",
        "po": "1",
        "np": "1",
        "fltt": "2",
        "invt": "2",
        "fs": fs,
        "fields": "f2,f3,f4,f12,f13,f14,f104,f105,f128,f136,f140,f184",
        "fid": "f3",  # 按涨跌幅排序
        "ut": "f057cbcbce2a86e2866ab8877db1d059",
    }
    try:
        r = em_get(url, params=params, headers={"User-Agent": UA}, timeout=15)
        if r is None:
            return []
        d = r.json()
        items = d.get("data", {}).get("diff", []) or []
        if isinstance(items, dict):
            items = list(items.values())
        sectors = []
        for i, item in enumerate(items):
            sectors.append(
                {
                    "rank": i + 1,
                    "code": str(item.get("f12", "")),
                    "name": str(item.get("f14", "")),
                    "price": _safe_float(item.get("f2", 0)),
                    "change_pct": _safe_float(item.get("f3", 0)),
                    "leader_name": str(item.get("f140", "")),
                    "leader_change": _safe_float(item.get("f136", 0)),
                    "up_count": int(item.get("f104", 0) or 0),
                    "down_count": int(item.get("f105", 0) or 0),
                }
            )
        return sectors
    except Exception as _e:
        _debug_log(f"datasource get_em_board_list type={board_type}: {_e}")
        return []


@requires_push2
def get_em_board_members(board_code: str) -> List[Dict[str, Any]]:
    """V12.0: 获取板块成员列表（替代 TDX MacClient.get_board_members）。

    使用东财 push2 clist 接口，fs 参数为 b:BK{code}。

    Args:
        board_code: 板块代码（如 "BK0447"）

    Returns:
        list: [{"code": str, "name": str, "price": float, "change_pct": float,
                "mcap_yi": float, "turnover": float, "pe": float,
                "main_net_amount": float}, ...]
    """
    # 规范化板块代码：纯数字 → 补 BK 前缀
    if not board_code:
        return []
    bc = board_code.strip()
    if bc.isdigit():
        bc = "BK" + bc
    elif not bc.upper().startswith("BK"):
        bc = "BK" + bc

    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "300",
        "po": "1",
        "np": "1",
        "fltt": "2",
        "invt": "2",
        "fs": f"b:{bc}",
        "fields": "f12,f14,f2,f3,f20,f21,f23,f62,f184",
        "fid": "f3",  # 按涨跌幅排序
        "ut": "f057cbcbce2a86e2866ab8877db1d059",
    }
    try:
        r = em_get(url, params=params, headers={"User-Agent": UA}, timeout=15)
        if r is None:
            return []
        d = r.json()
        items = d.get("data", {}).get("diff", []) or []
        if isinstance(items, dict):
            items = list(items.values())
        members = []
        for item in items:
            members.append(
                {
                    "code": str(item.get("f12", "")),
                    "name": str(item.get("f14", "")),
                    "price": _safe_float(item.get("f2", 0)),
                    "change_pct": _safe_float(item.get("f3", 0)),
                    # f20=总市值(元)，转换为亿元
                    "mcap_yi": _safe_float(item.get("f20", 0)) / 1e8,
                    "turnover": _safe_float(item.get("f184", 0)),  # 换手率
                    "pe": _safe_float(item.get("f23", 0)),  # PE(动)
                    "main_net_amount": _safe_float(item.get("f62", 0)),  # 主力净流入额
                }
            )
        return members
    except Exception as _e:
        _debug_log(f"datasource get_em_board_members {board_code}: {_e}")
        return []


@requires_push2
def get_em_belong_boards(code: str) -> Dict[str, List[Any]]:
    """V12.0: 获取股票所属板块（替代 TDX MacClient.get_belong_board）。

    使用东财 push2 stock/get 获取个股所属行业，再从板块列表匹配板块代码。
    注：东财 HTTP 接口仅返回行业，概念/地域返回空列表（如有需要可后续扩展）。

    V15.2 P0 修复：原注释错误地认为 f127=板块代码、f128=板块名称，实际：
      - f127 = 行业名称（如"光学光电子"）
      - f128 = 地域板块名称（如"广东板块"）
      - f135 = 数值（某种总市值/成交额，不是板块代码）
      - f136 = 数值（不是板块代码）
    修复后：industry 只用 f127（名称），area 只用 f128（名称），code 字段暂时用名称做 hash。

    Args:
        code: 股票代码（6位数字）

    Returns:
        dict: {"industry": [{"code": str, "name": str}, ...],
               "concept": [], "area": [], "style": []}
    """
    result: Dict[str, List[Any]] = {"industry": [], "concept": [], "area": [], "style": []}
    if not code or len(code) != 6:
        return result

    secid = f"{em_secid_prefix(code)}{code}"  # V17.0 S3: 统一前缀(含北交所 92)

    # V15.2 P0 修复: 字段含义纠正
    # f127 = 行业名称（字符串，如"光学光电子"）
    # f128 = 地域板块名称（字符串，如"广东板块"）
    # f135/f136 = 数值（不是板块代码/名称）
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "secid": secid,
        "fields": "f127,f128",
        "ut": "f057cbcbce2a86e2866ab8877db1d059",
    }
    try:
        r = em_get(url, params=params, headers={"User-Agent": UA}, timeout=10)
        if r is not None:
            d = r.json()
            data = d.get("data", {}) or {}
            ind_name = str(data.get("f127", "") or "").strip()
            if ind_name:
                # 名称作为 code（避免空 code），规范化供下游使用
                result["industry"].append({"code": ind_name, "name": ind_name})
            area_name = str(data.get("f128", "") or "").strip()
            if area_name:
                result["area"].append({"code": area_name, "name": area_name})
    except Exception as _e:
        _debug_log(f"datasource get_em_belong_boards stock/get ({code}): {_e}")

    return result


# V16.2.4: 东财 fflow 接口多域轮换 —— push2/push2his 对该 IP 连接级风控（RemoteDisconnected）时
# 自动切 push2delay 延时镜像（仅当日，无历史窗口）；风控恢复后自动回全窗口域。
# V17.0.2j(2026-08-17): 顺序调整——push2delay 优先(get_em_fund_flow 仅取当日 lmt=1,
# 无需历史窗口); 原 push2his/push2 优先导致 val 策略20 盘中 30+ 次逐股调用时
# 每次先打 2 次 push2 主域(共享风控面) → 封禁风险源
_FFLOW_HOSTS = (
    "push2delay.eastmoney.com", # 延时镜像优先(独立风控, 当日数据够用)
    "push2his.eastmoney.com",   # 历史资金流主域(全窗口, 兜底)
    "push2.eastmoney.com",      # 实时主域(最后兜底)
)


def _em_fflow_request(path: str, params: Dict[str, Any], timeout: int = 10, prefer_his: bool = False):
    """V16.2.4: 依次尝试 _FFLOW_HOSTS，返回首个非 None 的 Response（含 403/429 语义由 em_get 处理）。
    V17.0.4(2026-08-19): prefer_his=True(历史资金流) → push2his 全窗口优先——
    原顺序 push2delay 第 1(为 lmt=1 实时设计) 会把 daykline 历史请求截断成单日(8/18 全仓 sht 60日资金流仅 1 天根因)。
    """
    import random as _rand

    _hosts = list(_FFLOW_HOSTS)
    if prefer_his:
        _his = "push2his.eastmoney.com"
        _hosts = [_his] + [h for h in _hosts if h != _his]
    else:
        _rand.shuffle(_hosts[0:2])  # 前两域随机轮换（防固定域持续触发风控）
    for _h in _hosts:
        try:
            _r = em_get(f"https://{_h}{path}", params=params, headers={"User-Agent": UA}, timeout=timeout)
            if _r is not None:
                return _r
        except Exception as _e:
            _debug_log(f"datasource fflow host {_h} error: {type(_e).__name__} {str(_e)[:60]}")
    return None


@requires_push2
def get_em_fund_flow(code: str) -> Dict[str, Any]:
    """V12.0: 获取个股实时资金流（替代 TDX get_fund_flow）。

    使用东财 fflow daykline 接口，取最新一天的数据（即当日实时累计）。
    V16.2.4 修复: push2/push2his 域连接级风控时自动切 push2delay 延时镜像域
    （延时 15 分钟，盘后一致；风控面独立）。

    Returns:
        dict: {"main_net": float, "main_net_wan": float, "total_net": float,
               "super_in": float, "super_out": float,
               "large_in": float, "large_out": float,
               "medium_in": float, "medium_out": float,
               "small_in": float, "small_out": float}
    """
    secid = f"{em_secid_prefix(code)}{code}"  # V17.0 S3: 统一前缀(含北交所 92)

    params = {
        "lmt": "1",  # 只取最新一天
        "klt": "101",  # 日K线
        "secid": secid,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
    }
    try:
        r = _em_fflow_request("/api/qt/stock/fflow/daykline/get", params)
        if r is None:
            return {}
        d = r.json()
        klines = d.get("data", {}).get("klines", [])
        if not klines:
            return {}
        # klines 格式: "日期,主力净流入,小单净流入,中单净流入,大单净流入,超大单净流入"
        parts = klines[-1].split(",")
        if len(parts) < 6:
            return {}
        main_net = _safe_float(parts[1])
        small_net = _safe_float(parts[2])
        medium_net = _safe_float(parts[3])
        large_net = _safe_float(parts[4])
        super_net = _safe_float(parts[5])
        # 东财返回净额，TDX格式需要 in/out 分开
        # 转换规则：净额>0时in=净额,out=0；净额<0时in=0,out=|净额|
        return {
            "main_net": main_net,
            "main_net_wan": main_net / 10000.0,
            # V16.2 修复: total_net = 全部五档净额之和（原漏大单/超大单）
            "total_net": main_net + small_net + medium_net + large_net + super_net,
            "super_in": max(super_net, 0),
            "super_out": max(-super_net, 0),
            "large_in": max(large_net, 0),
            "large_out": max(-large_net, 0),
            "medium_in": max(medium_net, 0),
            "medium_out": max(-medium_net, 0),
            "small_in": max(small_net, 0),
            "small_out": max(-small_net, 0),
        }
    except Exception as _e:
        _debug_log(f"datasource get_em_fund_flow ({code}): {_e}")
        return {}


def get_index_kline_closes(index_code: str, days: int = 250) -> List[float]:
    """指数日K收盘价序列（V17.0.7 自 mak.get_index_returns._get_kline 下沉统一层）。

    四源链(与 mak 原实现逐行为等价迁移, 全走限流包装):
      TDX 指数K线(core.tdx_client) → 腾讯 ifzq 前复权日K → 新浪 getKLineData
      → 腾讯实时 2 值(仅 1 日回报兜底)。
    供 mak 行业轮动/异动偏离(ret_3d/10d/20d/60d) 与其他脚本指数区间收益复用。

    Args:
        index_code: 指数代码（如 sh000001 / sz399106）
        days: 需要的交易日数量

    Returns:
        收盘价列表（升序）；全部失败返回 []
    """
    import json as _json

    # L1: TDX 指数K线(TCP 不封 IP)
    try:
        from core.tdx_client import tdx_get_index_bars

        keys, rows = tdx_get_index_bars(index_code, count=days)
        if keys and rows:
            ci = next((i for i, k in enumerate(keys)
                       if k in ("close", "close_price")), -1)
            if ci >= 0:
                closes = [_safe_float(r[ci]) for r in rows if len(r) > ci]
                if closes:
                    return closes
    except Exception as _e:
        _debug_log(f"datasource index_kline tdx error {index_code}: {_e}")

    # L2: 腾讯 ifzq 前复权日K（完整序列）
    try:
        r = _quick_request(
            f"https://ifzq.gtimg.cn/appstock/app/fqkline/get?param={index_code},day,,,{days},qfq",
            timeout=10,
        )
        if r:
            d = (r.json().get("data") or {}).get(index_code, {})
            kline = d.get("qfqday") or d.get("day") or []
            closes = [_safe_float(row[2]) for row in kline if len(row) > 2 and row[2]]
            if closes:
                return closes
    except Exception as _e:
        _debug_log(f"datasource index_kline tencent error {index_code}: {_e}")

    # L3: 新浪日K（V17.0.4: 与腾讯 ifzq 实测一致 <0.01）
    try:
        r = _quick_request(
            "https://quotes.sina.cn/cn/api/jsonp_v2.php/var/CN_MarketDataService.getKLineData",
            params={"symbol": index_code, "scale": 240, "ma": "no", "datalen": days},
            headers={"User-Agent": UA,
                     "Referer": "https://finance.sina.com.cn"},
            timeout=10,
        )
        if r:
            _m = re.search(r"\((.*)\)", r.text, re.S)
            if _m:
                _arr = _m.group(1)
                if _arr.startswith("["):
                    _rows = _json.loads(_arr)
                    closes = [_safe_float(x.get("close")) for x in _rows if x.get("close")]
                    closes = [c for c in closes if c > 0]
                    if closes:
                        return closes
    except Exception as _e:
        _debug_log(f"datasource index_kline sina error {index_code}: {_e}")

    # L4: 腾讯实时 2 值（仅 1 日回报——指标静默 None 有提示）
    try:
        r = _quick_request(f"https://qt.gtimg.cn/q={index_code}", timeout=10)
        if r:
            r.encoding = "gbk"
            v = r.text.split('"')[1].split("~")
            close = _safe_float(v[3])
            pre_close = _safe_float(v[4])
            return [pre_close, close] if close > 0 else []
    except Exception as _e:
        _debug_log(f"datasource index_kline realtime error {index_code}: {_e}")
    return []


@requires_push2
def get_em_history_fund_flow(code: str, days: int = 120) -> List[Dict[str, Any]]:
    """V12.0: 获取个股历史资金流（替代 TDX get_history_fund_flow）。

    使用东财 push2 fflow daykline 接口，取最近 N 天的日级数据。

    Args:
        code: 股票代码
        days: 返回天数

    Returns:
        list: [{"date": str, "main_net": float, "super_net": float,
                "large_net": float, "mid_net": float, "small_net": float}, ...]
    """
    secid = f"{em_secid_prefix(code)}{code}"  # V17.0 S3: 统一前缀(含北交所 92)

    params = {
        "lmt": str(max(days, 1)),
        "klt": "101",  # 日K线
        "secid": secid,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
    }
    try:
        # V16.2.4: 多域轮换（push2his 全窗口 → push2 → push2delay 单日保底）
        # V17.0.4(2026-08-19): prefer_his=True 历史资金流优先 push2his 全窗口
        # (原顺序 push2delay 第 1 会把历史请求截断成单日——8/18 全仓 60日资金流仅 1 天根因)
        r = _em_fflow_request("/api/qt/stock/fflow/daykline/get", params, prefer_his=True)
        if r is None:
            return []
        d = r.json()
        klines = d.get("data", {}).get("klines", [])
        if not klines:
            return []
        rows = []
        for line in klines:
            parts = line.split(",")
            if len(parts) < 6:
                continue
            main_net = _safe_float(parts[1])
            small_net = _safe_float(parts[2])
            medium_net = _safe_float(parts[3])
            large_net = _safe_float(parts[4])
            super_net = _safe_float(parts[5])
            date_str = str(parts[0])[:10]
            rows.append(
                {
                    "date": date_str,
                    "main_net": main_net,
                    "super_net": super_net,
                    "large_net": large_net,
                    "mid_net": medium_net,
                    "small_net": small_net,
                }
            )
        # 按日期降序（最新在前），与原 TDX 行为保持一致
        rows.sort(key=lambda x: x["date"], reverse=True)
        return rows
    except Exception as _e:
        _debug_log(f"datasource get_em_history_fund_flow ({code}): {_e}")
        return []


# ═══════════════════════════════════════════════════════════
# V16.1.7: 新数据源封装（字典 §12.10/12.12 已实测确认，带缓存+限流）
# ═══════════════════════════════════════════════════════════


@cached(category="market_emotion", ttl_seconds=TTL["limit_pool"], trading_day=True)
def get_cls_market_emotion() -> Dict[str, Any]:
    """V16.1.7: 财联社市场情绪（字典 §12.10.2，实测可用）。

    返回: market_degree(热度0-100)/shsz_balance(两市成交额)/up_ratio(封板率)/
          up_open_num(炸板)/performance(昨涨停今表现)/up_open_ratio(高开率)/
          profit_ratio(获利率)/up_down_dis(涨跌分布)/limit_up_board(连板梯队)
    """
    try:
        import levistock as lk
        # V16.2: levistock 内部直连东财，绕过统一限流 → 调用前走进程级协调（全局 ≤1 rps）
        try:
            from stock_common.sc_network import _em_wait_process_interval
            _em_wait_process_interval()
        except Exception:
            pass
        d = lk.market_emotion_cls()
        if isinstance(d, dict) and d:
            return d
    except Exception as _e:
        _debug_log(f"datasource get_cls_market_emotion: {_e}")
    return {}


@cached(category="limit_pool", ttl_seconds=TTL["limit_pool"], trading_day=True)
def get_kph_limit_ladder(date_str: str = "") -> List[Dict[str, Any]]:
    """V16.1.7: 开盘红涨停天梯（字典 §12.10.4，实测 137 条）。

    返回: [{code/name/limit_count(连板)/limit_time/plate_name/
           one_word(大单一字)/popular(人气)/plate_limit_up_count/amount/plate_amount}]
    """
    try:
        import levistock as lk
        from datetime import date, timedelta
        # V16.2: 进程级节流（levistock 直连东财）
        try:
            from stock_common.sc_network import _em_wait_process_interval
            _em_wait_process_interval()
        except Exception:
            pass
        if not date_str:
            # V17.0.2g(2026-08-17): 开盘红复盘接口要求"已收盘交易日"(昨天或更早)——
            # 原 今天-1 在周一/节后运行取到休市日 → 接口空 → "涨停天梯获取失败"
            from stock_common.stock_calendar import get_last_trading_day
            from datetime import date as _date

            _ltd = get_last_trading_day()
            _d0 = _ltd if isinstance(_ltd, _date) else _ltd.date()
            # 最近交易日是今天(交易日盘中/盘前) → 回退到上一已收盘交易日
            if _d0 == _date.today():
                _d0 = _d0 - timedelta(days=1)
            date_str = _d0.strftime("%Y-%m-%d")
            # 回退日可能仍是休市日(周末) → 向前找首个有数据的日期(最多 7 天)
            for _try in range(7):
                data = lk.get_zttt(date=date_str)
                _cnt = len(data.get("StockList") or []) if isinstance(data, dict) else len(data or [])
                if _cnt > 0:
                    break
                date_str = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                data = lk.get_zttt(date=date_str)
        else:
            data = lk.get_zttt(date=date_str)
        # levistock get_zttt 返回 dict: {"StockList": [...], "ZhuShuList": [...]}
        if isinstance(data, dict):
            data = data.get("StockList") or []
        if isinstance(data, list):
            rows = []
            for item in data:
                if isinstance(item, dict):
                    rows.append(item)
                elif isinstance(item, (list, tuple)) and len(item) >= 11:
                    # 开盘红 zttt 返回 list 索引: [0]code [1]name [2]连板 [3]时间戳 [4]板块码 [5]板块名 [6]大单一字 [7]人气 [8]板块涨停数 [9]个股额 [10]板块额
                    rows.append({
                        "code": item[0], "name": item[1], "limit_count": item[2],
                        "limit_time": item[3], "plate_code": item[4], "plate_name": item[5],
                        "one_word": item[6], "popular": item[7],
                        "plate_limit_up_count": item[8], "amount": item[9], "plate_amount": item[10],
                    })
            return rows
    except Exception as _e:
        _debug_log(f"datasource get_kph_limit_ladder: {_e}")
    return []


@cached(category="market_emotion", ttl_seconds=TTL["limit_pool"], trading_day=True)
def get_stock_changes(change_type: str = "8201") -> List[Dict[str, Any]]:
    """V16.1.7: 东财盘口异动（字典 §12.10.1，levistock 实测 2782 条）。

    change_type: 8201 火箭发射 / 8193 大笔买入 / 8205 封涨停板 / 64 有大买盘 / 8202 快速反弹
    返回: [{code/name/market/time/change_pct/price/change_type/date}]
    V17.0.1e(2026-08-16): levistock 把原始字段 i 原样放入 change_pct——
    实际 i 为逗号串 "涨跌幅小数,价格,涨跌幅小数"(push2ex getAllStockChanges 原始结构),
    _safe_float 解析失败 → 涨幅恒 0。此处直接解析原始 JSON 修复。
    """
    try:
        import requests
        from stock_common import UA
        from stock_common.stock_calendar import get_last_trading_day
        from stock_common.sc_network import _em_wait_process_interval
        _em_wait_process_interval()
        _params = {
            "type": change_type,
            "ut": "7eea3edcaed734bea9cbfc24409ed989",
            "pageindex": 0,
            "pagesize": 10000,
            "dpt": "wzchanges",
        }
        resp = requests.get(
            "https://push2ex.eastmoney.com/getAllStockChanges",
            params=_params, headers={"User-Agent": UA}, timeout=10,
        )
        resp.raise_for_status()
        body = (resp.json().get("data") or {})
        items = body.get("allstock", []) or []
        _date = get_last_trading_day().strftime("%m-%d")
        rows = []
        for item in items:
            if not isinstance(item, dict):
                continue
            code = str(item.get("c", ""))
            name = str(item.get("n", ""))
            if name.startswith("ST") or name.startswith("*ST"):
                continue
            tm = str(item.get("tm", ""))
            if len(tm) == 5:
                tm = "0" + tm
            chg, px = 0.0, 0.0
            _i = str(item.get("i", ""))
            if _i and "," in _i:
                _parts = _i.split(",")
                try:
                    # i 结构: 8201 火箭发射=涨幅,价格,涨幅; 8193 大笔买入/64 有大买盘=量(手),价格,涨跌幅,金额
                    # 统一: 第三段=盘中触发时刻涨跌幅(小数→%), 第二段=触发价(实测 5 股全部自洽)
                    chg = float(_parts[2]) * 100.0 if len(_parts) >= 3 else 0.0
                    px = float(_parts[1]) if len(_parts) >= 2 else 0.0
                except (ValueError, IndexError):
                    pass
            rows.append({
                "code": code,
                "name": name,
                "market": str(item.get("m", "")),
                "time": tm,
                "change_pct": chg,
                "price": px,
                "change_type": change_type,
                "date": _date,
            })
        return rows
    except Exception as _e:
        _debug_log(f"datasource get_stock_changes: {_e}")
    return []


@cached(category="basic_info", ttl_seconds=TTL["basic_info"], trading_day=True)
def get_shortline_indicators(code: str) -> Dict[str, Any]:
    """V16.1.7: AxData 短线指标 34 字段（字典 §12.12.1，实测 stats_root 消费项目 zhb.zip）。

    stats_root 用项目 cache/zhb 最新包（零额外下载）。
    返回: open_volume_ratio(开盘量比)/auction_prev_volume_ratio(竞价昨比)/
          seal_to_amount_ratio(封成比)/seal_to_float_ratio(封流比)/
          limit_board_text(几天几板)/limit_up_streak_days(连板)/
          free_float_shares(自由流通股本Z)/year_limit_up_days 等 34 字段
    """
    import glob
    import os

    try:
        from axdata_core import request_interface
        # 找最新 zhb 包
        zhb_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache", "zhb")
        zips = sorted(glob.glob(os.path.join(zhb_dir, "zhb_*.zip")))
        if not zips:
            return {}
        stats_root = zips[-1]
        r = request_interface(
            "stock_shortline_indicators_tdx",
            params={"code": code, "stats_root": stats_root},
            fields=None, persist=False, data_root=None,
        )
        records = getattr(r, "records", None)
        if records and isinstance(records[0], dict):
            return records[0]
    except Exception as _e:
        _debug_log(f"datasource get_shortline_indicators ({code}): {_e}")
    return {}


# ═══════════════════════════════════════════════════════════
# 数据源模块总计：85个函数（V16.1.7 新增 4 个新数据源封装）
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# V17.0.7: 通达信早盘/尾盘抢筹 + 东财选股器服务端筛选（来源 myhhub/stock）
# ═══════════════════════════════════════════════════════════════

_TDX_QC_URL = "http://excalc.icfqs.com:7616/TQLEX?Entry=HQServ.hq_nlp"
_TDX_QC_TOKEN = "6679f5cadca97d68245a086793fc1bfc0a50b487487c812f"


def get_tdx_chip_race(period: int = 0, sort: int = 1) -> List[Dict[str, Any]]:
    """通达信早盘/尾盘抢筹数据（字典无此源——来源 myhhub/stock stock_chip_race.py）。

    Args:
        period: 0=早盘抢筹, 1=尾盘抢筹
        sort: 排序(1=委托金额/2=成交金额/3=开盘金额/4=幅度/5=占比)

    Returns:
        [{"code","name","price","change_rate","bid_rate","bid_trust_amount",...}]
    """
    from stock_common import _quick_request

    payload = json.dumps([{
        "funcId": 20, "offset": 0, "count": 100,
        "sort": sort, "period": period, "Token": _TDX_QC_TOKEN,
        "modname": "JJQC",
    }])
    r = _quick_request(_TDX_QC_URL, data=payload, timeout=10, method="POST",
                       headers={"Content-Type": "application/json; charset=UTF-8"})
    if r is None:
        return []
    try:
        rows = r.json()
        if isinstance(rows, list) and rows:
            inner = rows[0].get("data") or []
            out = []
            for d in inner:
                out.append({
                    "code": d.get("StockCode", ""),
                    "name": d.get("StockName", ""),
                    "pre_close": float(d.get("ZSJ", 0)) / 10000,
                    "open_price": float(d.get("KPJ", 0)) / 10000,
                    "price": float(d.get("ZJCJG", 0)) / 10000,
                    "change_rate": float(d.get("ZDF", 0)),
                    "deal_amount_wan": float(d.get("CJJE", 0)) / 1e4,
                    "bid_trust_amount_wan": float(d.get("QCWTJE", 0)) / 1e4,
                    "bid_deal_amount_wan": float(d.get("QCCJJE", 0)) / 1e4,
                    "bid_rate_pct": float(d.get("QCFD", 0)) * 100,
                    "bid_ratio_pct": float(d.get("QCZB", 0)) * 100,
                    "limitup_days": int(d.get("TJZT", 0)),
                    "limitup_boards": int(d.get("TJQB", 0)),
                })
            return out
    except Exception as _e:
        _debug_log(f"datasource get_tdx_chip_race: {_e}")
    return []


_EM_XUANGU_URL = "https://data.eastmoney.com/dataapi/xuangu/list"


def get_em_xuangu(sty_fields: str = "", filter_expr: str = "",
                  page: int = 1, page_size: int = 50) -> List[Dict[str, Any]]:
    """东财选股器服务端筛选（200+ 字段任意组合——来源 myhhub/stock stock_selection.py）。

    Args:
        sty_fields: 逗号分隔的字段代码串（如 SECURITY_CODE,TOTAL_MARKET_CAP,NEW_PRICE）
        filter_expr: 过滤表达式（如 (MARKET="上交所主板")(NEW_PRICE>10)）
        page/page_size: 分页

    Returns:
        [{"SECURITY_CODE":"600519","SECURITY_NAME_ABBR":"贵州茅台",...}]
    """
    import requests as _req
    from stock_common.sc_network import EM_SESSION

    headers = {
        "User-Agent": UA,
        "Referer": "https://data.eastmoney.com/xuangu/",
    }
    params = {
        "sty": sty_fields if sty_fields else "ALL",
        "p": page,
        "ps": page_size,
        "source": "SELECT_SECURITIES",
        "client": "WEB",
    }
    if filter_expr:
        params["filter"] = filter_expr
    try:
        r = EM_SESSION.get(_EM_XUANGU_URL, params=params, headers=headers, timeout=15)
        if r.status_code != 200:
            return []
        d = r.json()
        return (d.get("result") or {}).get("data") or []
    except Exception as _e:
        _debug_log(f"datasource get_em_xuangu: {_e}")
        return []


# ═══════════════════════════════════════════════════════════════
# V17.0.7: 开盘啦(KPL) 无 Token API 统一封装（字典 §12.21.5）
# 来源: jinhao2003/kaipanla-crawler 方法验证 + 穷尽实测
# 大部分端点无需 Token——直接 HTTP POST + Dalvik UA 即可获取数据
# 域名分工: apphwhq=实时行情 / apphis=历史+板块 / applhb=龙虎榜
# 限流: sc_network._DOMAIN_LIMITS 已注册 longhuvip.com 各子域 @3~5rps
# ═══════════════════════════════════════════════════════════════

_KPL_HQ = "https://apphwhq.longhuvip.com/w1/api/index.php"
_KPL_HIS = "https://apphis.longhuvip.com/w1/api/index.php"
_KPL_LHB = "https://applhb.longhuvip.com/w1/api/index.php"

_KPL_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; ALN-AL00 Build/W528JS)",
    "Connection": "Keep-Alive",
}

_KPL_BASE = {
    "PhoneOSNew": "1",
    "DeviceID": "80ca7d1b-2a24-3cd0-a915-99b61f6f88aa",
    "VerSion": "5.23.0.4",
    "apiv": "w44",
    "UserID": "",
    "Token": "",
}


_KPL_LAST_CALL: float = 0.0


def _kpl_post(url: str, action: str, controller: str, extra: dict = None) -> Optional[dict]:
    """KPL 统一 POST（直接 requests.post——必须用 Dalvik UA，_quick_request 会覆盖导致空数据）。
    自行限流 >=200ms。V17.0.7 字典 §12.21.5。"""
    import time as _time
    global _KPL_LAST_CALL
    el = _time.time() - _KPL_LAST_CALL
    if el < 0.2:
        _time.sleep(0.2 - el)
    _KPL_LAST_CALL = _time.time()

    params = dict(_KPL_BASE)
    params["a"] = action
    params["c"] = controller
    if extra:
        params.update(extra)
    body_parts = []
    for k, v in params.items():
        body_parts.append(f"{k}={v}")
    body = "&".join(body_parts) + "&"
    import requests as _req_mod
    try:
        r = _req_mod.post(url, data=body.encode("utf-8"),
                          headers=dict(_KPL_HEADERS), timeout=15)
        if r.status_code != 200:
            return None
        txt = r.text
        cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", txt)
        d = json.loads(cleaned)
        ec = str(d.get("errcode", ""))
        if ec != "0":
            _debug_log(f"kpl {action}/{controller}: errcode={ec} {d.get('errmsg','')[:60]}")
            return None
        return d.get("data") or d
    except Exception as e:
        _debug_log(f"kpl {action}/{controller}: {e}")
        return None





def kpl_get_market_emotion() -> Optional[Dict[str, Any]]:
    """市场情绪实时数据（涨停数/跌停数/强度/连板高度）。

    Returns:
        {"ztjs": 涨停数, "df_num": 跌停数, "strong": 强度,
         "lbgd": 连板高度, "Day": 日期}
    """
    return _kpl_post(_KPL_HQ, "ChangeStatistics", "HomeDingPan")


def kpl_get_rise_fall_analysis() -> Optional[List]:
    """涨跌分析 [涨停数,?,跌停数,?,涨跌比%,?,日期]。"""
    return _kpl_post(_KPL_HQ, "RiseFallAnalysis", "HomeDingPan")


def kpl_get_stock_zd_num() -> Optional[Dict[str, Any]]:
    """涨跌家数。"""
    return _kpl_post(_KPL_HQ, "MarketStockZDNum", "HomeDingPan")


def kpl_get_real_ranking_info(date: str = "", index: int = 0) -> Optional[Dict[str, Any]]:
    """板块排行列表(30只/页, 19列含 code/name/strength/change_pct/speed/
    turnover/main_net/main_buy/main_sell/vol_ratio/circ_mv/big_order_net/
    total_mv/pe_today/pe_next 等)。"""
    return _kpl_post(_KPL_HIS, "RealRankingInfo", "ZhiShuRanking", {
        "Type": "1", "ZSType": "7", "Index": str(index), "st": "30",
        "Date": date, "Order": "1",
    })


def kpl_get_stock_list_w8(plate_id: str, date: str = "",
                          stock_type: int = 0) -> Optional[Dict[str, Any]]:
    """板块成分股详情(63字段, 需遍历 Type 0~19 合并去重)。
    域名必须用 apphis.longhuvip.com；响应 key 是小写 list。"""
    return _kpl_post(_KPL_HIS, "ZhiShuStockList_W8", "ZhiShuRanking", {
        "PlateID": plate_id, "Date": date, "Type": str(stock_type),
        "Index": "0", "st": "30", "Order": "1", "TSZB": "0",
        "IsZZ": "0", "TSZB_Type": "0", "filterType": "0", "old": "1",
    })


def kpl_get_ytfp_bkhx(date: str = "") -> Optional[Dict[str, Any]]:
    """复盘啦板块核心(涨停原因+题材+个股明细)。"""
    extra = {}
    if date:
        extra["Date"] = date
    return _kpl_post(_KPL_HIS, "GetYTFP_BKHX", "FuPanLa", extra)


def kpl_get_ytfp_sctd(date: str = "") -> Optional[Dict[str, Any]]:
    """复盘啦市场题材(几天几板 Tips，如'3天2板')。"""
    extra = {}
    if date:
        extra["Date"] = date
    return _kpl_post(_KPL_HIS, "GetYTFP_SCTD", "FuPanLa", extra)


def kpl_get_lhb_stock_list() -> Optional[Dict[str, Any]]:
    """龙虎榜股票列表。"""
    return _kpl_post(_KPL_LHB, "GetStockList", "LongHuBang")


def kpl_get_info() -> Optional[Dict[str, Any]]:
    """首页聚合(ErBanList/JJJYList/TKGKList)。"""
    extra = {"View": "1"}
    return _kpl_post(_KPL_HQ, "GetInfo", "Index", extra)
