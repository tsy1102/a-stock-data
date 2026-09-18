"""_financials.py — V17.2 拆包子模块（共享命名空间片段，由 __init__ 载入）

本文件不是独立可导入模块；其源码被 stock_common/sc_datasource/__init__.py
exec 进包命名空间，与包内其他函数/状态共享同一 globals()。
"""
from __future__ import annotations
from datetime import datetime, timedelta
import asyncio
import code
import re
import subprocess
import sys
from stock_common.sc_network import UA, _async_quick_request, _debug_log, _quick_request
from stock_common.sc_utils import _load_settings, _safe_float, em_exchange_prefix
from core.stock_cache import TTL, cached, get_cache, make_valid_if, set_cache
from ._shared import _PROFIT_CACHE_LOCK, _PROFIT_FORECAST_CACHE, _PROFIT_FORECAST_INDEX, _PROFIT_FORECAST_INDEX_SHORT, _YJYG_ALL_CACHE, _YJYG_LOCK, _calendar_fallback_warned
from stock_common.sc_fuyao import get_fuyao_financials
from stock_common.sc_kpl import _f
from stock_common.stock_calendar import is_workday


@cached(
    category="basic_info",
    ttl_seconds=TTL["basic_info"],
    valid_if=lambda r: isinstance(r, dict) and bool(r.get("code")),
    cross_verify=True,
)
def get_stock_info(code: str) -> Dict[str, Any]:
    """V7.5: 个股基本信息 → 腾讯行情 + TDX"""
    from ._eastmoney import eastmoney_stock_info_push2
    from ._quotes import get_tencent_quote
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
    from ._eastmoney import eastmoney_datacenter
    from ._misc import _today_str
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
    from ._eastmoney import eastmoney_datacenter
    from ._official_backup import get_margin_trading_backup
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
    if not rows:
        # V17.2.11: 东财 datacenter 封禁/空结果 → 沪深官方两融降级源（不依赖东财）
        try:
            _backup = get_margin_trading_backup(code)
            if _backup:
                rows = _backup
        except Exception as _e:
            _debug_log(f"sc_datasource get_margin_trading fallback error ({code}): {_e}")
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
    from ._eastmoney import _em_filter
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
    from ._eastmoney import _em_filter_async
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


@cached(category="dividend", ttl_seconds=TTL["dividend"], cross_verify=True)
def get_dividend_history(code):
    """V7.5: 分红历史 → TDX xdxr_info（东财 fallback 已删除）"""
    from core.tdx_client import tdx_get_dividend_history

    return tdx_get_dividend_history(code)


async def get_dividend_history_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """异步版 get_dividend_history"""
    import asyncio

    return await asyncio.to_thread(get_dividend_history, code)


def get_sina_financial_report(code: str, num_periods: int = 12) -> Dict[str, Any]:
    """新浪利润表 — 支持多期数（默认12期 ≈ 3年）
    V13.1: 彻底实现 ZHB 财报事件锁，抛弃 24小时 粗暴刷新。
    将 ZHB 的 report_date 拼入缓存 Key，实现永久缓存 + 瞬间刷新。
    """
    from ._zhb import get_zhb_single_stock_data
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
    prefix = em_exchange_prefix(code)  # V17.2.11: 收敛散点 startswith("6") 路由
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


def get_financial_report_with_fallback(code: str, num_periods: int = 12) -> Dict[str, Any]:
    """B: 新浪利润表为主源；新浪缺失/空 → fuyao 利润表兜底。

    返回与 get_sina_financial_report 完全同构的 List[Dict]：
    {"报告日","营业总收入","营业成本","净利润"}，值均为字符串(元)，
    下游 float() 解析逻辑不变。fuyao 英文键→新浪中文键映射据
    docs/field_verification/20260901/raw_fuyao.json 的 income_q 实测键名校准
    （report_date_ms / operating_income / parent_holder_net_profit / basic_eps）。
    """
    sina = get_sina_financial_report(code, num_periods)
    if sina:
        return sina
    try:
        from stock_common.sc_fuyao import get_fuyao_financials
        fy = get_fuyao_financials("income", code, limit=num_periods, period="quarterly")
        if not fy:
            return []
        out = []
        for it in fy:
            rdm = (it.get("report_date_ms") or it.get("report_date")
                   or it.get("end_date") or it.get("accper"))
            rdate = ""
            if rdm:
                try:
                    _ms = float(rdm)
                    if _ms > 1e12:  # epoch 毫秒
                        _ms /= 1000.0
                    from datetime import datetime
                    rdate = datetime.fromtimestamp(_ms).strftime("%Y-%m-%d")
                except Exception:
                    rdate = str(rdm)
            ni = it.get("parent_holder_net_profit",
                        it.get("net_profit", it.get("归属母公司净利润", "0")))
            rev = it.get("operating_income",
                         it.get("total_operate_income", it.get("revenue", "0")))
            cost = it.get("operating_cost", it.get("operating_cost_total", "0"))
            out.append({
                "报告日": rdate,
                "营业总收入": _fin_str(rev),
                "营业成本": _fin_str(cost),
                "净利润": _fin_str(ni),
            })
        return out
    except Exception as _e:
        _debug_log(f"financial fallback fuyao ({code}): {_e}")
        return []


def _fin_str(v) -> str:
    """fuyao 数值(元) → 字符串，保持与新浪一致(下游 float 解析)。"""
    if v is None or isinstance(v, bool):
        return "0"
    return str(v)


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
        prefix = em_exchange_prefix(code)  # V17.2.11: 收敛散点 startswith("6") 路由
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
    from ._eastmoney import _em_filter
    from ._eastmoney import eastmoney_datacenter
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
            # 与 history 分支同表同字段(RPT_LIFT_STAGE.ABLE_FREE_SHARES)，单位一致为"股"；
            # 原注释误标"万股"造成与 history 分支单位矛盾（两分支均未做除法，实际存同一原始值）。
            # TODO(2026-08-30): 东财该字段真实单位需实盘采样一次确认(股/万股)，当前与 FREE_SHARES 对齐为"股"。
            "able_shares": float(r.get("ABLE_FREE_SHARES") or 0),     # 股
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
            prefix = em_exchange_prefix(code, upper=True)  # V17.2.11: 收敛散点 startswith("6") 路由
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

