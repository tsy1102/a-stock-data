#!/usr/bin/env python3
"""
get_lng_report.py — A股长线价投专属深度体检报告

版本信息:
    V15.2  2026-07-28 - V15.2 P0 崩溃修复 + industry 字段改用 TDX boards + 0x0010 协议 jingyingxianjinliu key 修正
    V15.1  2026-07-26 - V15.1 全局 ZHB 旁路普及：52周高低位与历史分红数据 100% 优先走 ZHB 本地快照解析，分析耗时缩短 70%
    V15.0  2026-07-26 - 接入 CanonicalStockData 强类型数据合约，实施基于真实周期的 ZHB-First 离线优先路由
    V14.0  2026-07-22 - 文档同步：docstring 版本信息更新到 V14.0；is_workday() Bug 修复由 stock_common 上游提供
    V13.x  2026-07-22 - 受益于 stock_cache.py dataclass 透明序列化（脚本无改动）
    V12.6  2026-07-22 - 受益于字段路由简化（移除估值字段 HTTP fallback）
    V12.4  2026-07-22 - 抽象 BaseReportRunner 基类
    V9.5   2026-07-11 - 基础设施修复：aiohttp原生异步迁移、静默异常日志化（脚本本身无改动，受益于底层修复）
    V9.3.3 2026-07-11 - 流通股东显示统一为0%；休市提示移至标题下方；休市提示文案统一
    V9.3.2 2026-07-09 - 基础设施修复：TDX K线假数据防护、SQLite WAL死锁修复、代理环境兼容（脚本本身无改动，受益于底层修复）
    V9.3 2026-07-07 - 盘前行情模式：9:30前使用上一交易日日K线数据；删除报告标题硬编码版本号
    V9.2 2026-07-05 - 异常处理规范化；缓存交叉验证机制启用
    V9.1 2026-07-04 - F10 全覆盖：新增【财务深度/股东行为/治理结构/研发创新/主营构成】5章节+数据质量附录
    V9.0 2026-07-02 - 舆情互动层（Layer 10）；上市日期 push2 fallback；valid_if 校验；_has_zero_price 拦截
    V8.9 2026-06-29 - 快照架构改进（批量结束统一写入）；清理冗余快照逻辑；模块版本统一
    V8.8 2026-06-25 - GD上传逻辑统一化 & 快照格式升级（TXT+自动上传）
    V8.7 2026-06-25 - 死代码清理：同步版替换为薄包装
    V8.5 2026-06-22 - 新增多档分析深度
    V8.4 2026-06-22 - 统一缓存层+异步函数族
    V8.3 2026-06-18 - 细节修复
    V8.2 2026-06-18 - 统一评分接口+快照功能
    V8.0 2026-06-17 - 初始版本
"""

# V16.4.1: 强制 UTF-8 输出（下沉到代码自身——任何 agent/机器/直接运行均 UTF-8，
# 不再依赖 main.py 注入的 PYTHONIOENCODING 环境变量）
from stock_common.env_setup import ensure_utf8_stdio

ensure_utf8_stdio()

import math, pandas as pd
import asyncio
from datetime import date, datetime, timedelta
import os

# V15.3 修复: 4 个报告模块同名 _SNAPSHOT_DATA 全局变量冲突
# 抽出到 stock_common.sc_snapshot 统一管理
# V15.3.1: 直接 import 共享的 SnapshotProxy 类，删除 20 行重复定义
from stock_common.sc_snapshot import SnapshotProxy as _SnapshotProxy  # noqa: E402

_SNAPSHOT_DATA = _SnapshotProxy()

from core.tdx_client import (
    tdx_get_historical_high,
)
from core.data_provider import (
    get_canonical_stock_data,  # V15.3 强类型合约推广; V17.0 R3: 唯一综合数据入口(替代已删 get_stock_composite_async)
)
from stock_common import (
    _safe_float,
    _debug_log,
    _load_strategy_config,
    BaseReportRunner,
    get_holder_structure,
    get_strategic_announcements_async,
    baidu_kline_full,
    get_dividend_history,
    get_stock_info,
    get_eps_forecast_async,
    get_reports_async,
    resolve_eps_forecast,
    get_lockup_expiry_async,
    get_industry_peers,
    get_sina_financial_report_async,
    get_sina_balance_sheet_async,
    get_financial_report_with_fallback,  # B: 新浪缺失 → fuyao 利润表兜底
    get_market_status,
    get_zhb_single_stock_data,
    is_zhb_data_fresh,
    get_zhb_industry_map,
    get_zhb_data_date,
    get_zhb_tip_info,
    cls_telegraph,
    news_matches_stock,
    get_irm_qa,
    sec_type_market_label,
)  # V10.3, V16.2.3; V17.0.32 DEBT-016 露出 sec_type

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# ==================== 长线价投核心数据模块 ====================


def industry_comparison(top_n=20):
    """V17.2.x(2026-09-10): 已下沉至 `stock_common.sc_datasource.get_industry_ranking`，此处仅薄转发。

    保留本名是为兼容既有调用点；实现见共享层（lng/val 原两份近乎重复的实现已合并）。
    返回 list[dict]（ZHB 行业榜行 或 TDX board_list 板块）。
    """
    from stock_common.sc_datasource import get_industry_ranking

    return get_industry_ranking(top_n, "lng")


def get_roe_trend(code, num_periods=8, financials=None, bs_data=None, total_shares=0):
    """V16.3 O19: 薄包装——统一层 get_roe_trend_series（sc_datasource）。

    F10 加权 ROE 优先（TDX 第 2 档），新浪摊薄口径兜底；口径以 roe_type 标注。
    """
    try:
        from stock_common.sc_datasource import get_roe_trend_series

        return get_roe_trend_series(code, num_periods, financials, bs_data, total_shares)
    except Exception as _e:
        try:
            from stock_common import _debug_log as _dl

            _dl(f"lng get_roe_trend wrapper error ({code}): {_e}")
        except Exception:
            pass
        return []


def get_historical_high(code):
    """V17.0.5 P2: 历史最高价——腾讯前复权(qfq)优先, TDX 不复权兜底。

    参考仓库 v3.7.0 警示同步: 不复权价跨除权比价必错(长期分红股回撤被低估)。
    qfq 窗口 ~640 根(≈2.6 年); TDX 兜底为 8000 根不复权, 渲染层有口径注。
    """
    try:
        from stock_common.sc_datasource import get_historical_high_qfq as _qfq

        _v = _qfq(code)
        if _v and _v > 0:
            return _v
    except Exception as _e:
        _debug_log(f"lng qfq high fallback tdx ({code}): {_e}")
    return tdx_get_historical_high(code)


async def _get_eps_from_em_reports_async(session, code):
    try:
        reports = await get_reports_async(session, code, max_pages=1)
        if not reports:
            return None
        this_year = next_year = None
        for r in reports:
            ty = r.get("predictThisYearEps")
            ny = r.get("predictNextYearEps")
            if ty is not None:
                this_year = float(ty)
            if ny is not None:
                next_year = float(ny)
            if this_year is not None:
                return {
                    "eps_cur": this_year,
                    "eps_next": next_year,
                    "analyst_count": 1,
                    "source": "东财研报",
                }
        return None
    except Exception as _e:
        _debug_log(f"lng industry_comp: {_e}")
        return None


# ==================== 报告生成引擎 ====================


async def generate_report_async(session, code, output_path, ind_comp=None):
    """async 版: 长线价值体检报告生成引擎"""
    today_str = date.today().strftime("%Y-%m-%d")
    lines = []
    gm_rows = []

    def L(s=""):
        lines.append(s)

    L("=" * 72)
    # V17.0.2i: 头部拆分(参照 mak 规则)
    L(f"  **{code} 长线价投专属深度体检报告**")
    L(f"  ⏱ {today_str} {datetime.now().strftime('%H.%M.%S')}")
    L("=" * 72)
    L("")

    _mkt_status, _mkt_note = get_market_status()
    if _mkt_status == "closed":
        L("  ⚠️ 休市日：数据为最近交易日快照，基本面数据不受影响")
    elif _mkt_status == "lunch":
        L("  ⚠️ 午休时段（11:30-13:00）：行情暂停但基本面数据正常")
    elif _mkt_status in ("post_market", "pre_market"):
        L("  ⚠️ 非交易时段：数据为最近交易日快照，基本面数据不受影响")
    elif _mkt_status == "post_close":
        L("  ℹ️ 盘后收盘：数据为今日收盘快照，基本面数据不受影响")
    L("")

    # V17.4: 宏观利率层接入(吸收上游 3.9.0 §11) —— 长线视角: 利率/货币/政策环境
    try:
        from stock_common.sc_datasource import get_macro_context

        _mc = get_macro_context()
        _mc_lines = []
        if _mc.get("lpr_1y") is not None or _mc.get("lpr_5y") is not None:
            _mc_lines.append(
                f"  LPR(最新): 1年 {_mc.get('lpr_1y') if _mc.get('lpr_1y') is not None else 'N/A'} / 5年 {_mc.get('lpr_5y') if _mc.get('lpr_5y') is not None else 'N/A'}"
            )
        if _mc.get("repo_fr") is not None or _mc.get("repo_fdr") is not None:
            _mc_lines.append(f"  回购定盘利率: FR {_mc.get('repo_fr')} / FDR {_mc.get('repo_fdr')}")
        if _mc.get("calendar_count"):
            _mc_lines.append(f"  近期宏观事件日历: {_mc.get('calendar_count')} 条")
        if _mc_lines:
            L("\n## 【零、宏观利率与政策环境】")
            L("---")
            for _ml in _mc_lines:
                L(_ml)
        else:
            L("  ℹ️ 宏观利率层(吸收上游 §11): LPR/回购定盘/中债曲线/宏观日历 待对撞验证接入")
    except Exception as _e:
        _debug_log(f"lng macro_context error: {_e}")

    # V17.4: 事件驱动层接入(吸收上游 3.9.0 §14) — 业绩预告/机构调研; 可转债可选; 增减持/质押见九之二
    try:
        from stock_common.sc_datasource import render_event_driven_section

        _ev = await asyncio.to_thread(
            render_event_driven_section, code, ("业绩预告", "机构调研"), True
        )
        if _ev:
            L("\n## 【零之二、事件驱动与基本面催化 (业绩预告/机构调研)】")
            L("---")
            for _l in _ev:
                L(_l)
            L("  💡 股东增减持/股权质押风险详见【九之二、风险扫描】章节。")
    except Exception as _e:
        _debug_log(f"lng event_driven({code}) error: {_e}")

    L("\n## 【一、企业基本盘与绝对估值锚点】")
    L("---")

    # V11.5: 优先使用 data_provider 统一数据中心层获取综合数据
    # V17.0 R3: get_stock_composite_async 链已删除(220 行)——统一走
    # get_canonical_stock_data(CanonicalStockData 覆盖全部原 composite 字段, 已逐一核对)
    _dp_composite = None
    _cdata = None
    try:
        _cdata = await asyncio.to_thread(get_canonical_stock_data, code)
    except Exception as _e:
        _debug_log(f"lng cdata error: {_e}")
    if _cdata is not None:
        # 兼容 dict 读取面: 由强类型合约构建(原 _dp_composite 字段全集)
        _dp_composite = {
            "price": _cdata.price,
            "change_pct": _cdata.change_pct,
            "mcap_yi": _cdata.mcap_yi,
            "float_mcap_yi": _cdata.float_mcap_yi,
            "industry": _cdata.industry,
            "board": _cdata.board,
            "name": _cdata.name,
            "change_ytd": _cdata.change_ytd,
            "high_52w": _cdata.high_52w,
            "low_52w": _cdata.low_52w,
            "dividend_yield": _cdata.dividend_yield,
            "pe_ttm": _cdata.pe_ttm,
            "pb": _cdata.pb,
        }

    # V10.1: zhb优先获取估值、阶段涨幅、52周高低、股息率，原有路径降为fallback
    # V10.2: zhb数据日期标注（延迟时提示用户）
    # V16.3 M: 数据新鲜度分级——C 类静态（估值/52周/股本/行业）无条件用 ZHB（T-1 无影响，
    #   不做 fresh 拦截）；阶段涨幅（A/B 类）挂 fresh（≤3 天）避免盘中精度损失
    _zhb_data = None
    _zhb_date = ""
    _zhb_data = get_zhb_single_stock_data(code)
    _zhb_fresh = is_zhb_data_fresh()
    if not _zhb_fresh:
        _zhb_date = get_zhb_data_date() or ""
        if _zhb_date:
            L(f"  ℹ️ zhb数据日期: {_zhb_date}（延迟，阶段涨幅/52周高低等数据可能有1-2天滞后）")

    info = await asyncio.to_thread(get_stock_info, code)
    # V11.5: 优先从 data_provider 综合数据获取行情，fallback 到腾讯行情
    q = None
    # V15 统一数据中心：通过 get_canonical_stock_data 获取强类型标准化数据
    # V15.2 修正: async 上下文必须包 to_thread，否则阻塞主事件循环
    # V16.1: 复用上方 _cdata（避免同一股票两次 get_canonical_stock_data）
    cdata = _cdata
    if cdata is None:
        # V17.0 审查: 首次失败二次获取——成功后同步重建 _dp_composite(原遗漏导致与 price 不同源)
        from core.data_provider import get_canonical_stock_data

        cdata = await asyncio.to_thread(get_canonical_stock_data, code)
        if cdata is None:
            # MEDIUM(审查 2026-08-16): 二次获取仍失败 → 零值占位继续(不中断报告),
            # 后续展示自动降级为 0/缺失
            L("  ⚠️ 行情数据获取失败(连续两次), 估值与行情分析降级为空")
            from types import SimpleNamespace

            cdata = SimpleNamespace(
                price=0,
                change_pct=0,
                pe_ttm=0,
                pb=0,
                mcap_yi=0,
                float_mcap_yi=0,
                industry="",
                board="",
                name="",
                change_ytd=0,
                high_52w=0,
                low_52w=0,
                dividend_yield=0,
            )
        _dp_composite = {
            "price": cdata.price,
            "change_pct": cdata.change_pct,
            "mcap_yi": cdata.mcap_yi,
            "float_mcap_yi": cdata.float_mcap_yi,
            "industry": cdata.industry,
            "board": cdata.board,
            "name": cdata.name,
            "change_ytd": cdata.change_ytd,
            "high_52w": cdata.high_52w,
            "low_52w": cdata.low_52w,
            "dividend_yield": cdata.dividend_yield,
            "pe_ttm": cdata.pe_ttm,
            "pb": cdata.pb,
        }

    _quote = {
        "price": cdata.price,
        "change_pct": cdata.change_pct,
        "pe_ttm": cdata.pe_ttm,
        "pb": cdata.pb,
        "mcap_yi": cdata.mcap_yi,
        "float_mcap_yi": cdata.float_mcap_yi,
    }
    q = _quote
    price_today = cdata.price

    L(f"  企业名称: {info.get('name', 'N/A')} ({info.get('code', code)})")
    # V17.0.32(2026-09-06) DEBT-016: 露出 sec_type（与 board 地域字段正交）→ 市场板块 + 涨跌幅限制
    L(
        f"  市场板块: {sec_type_market_label(getattr(cdata, 'sec_type', 0), code, info.get('name', ''))}"
    )

    # 行业归属：info.get('industry') → TDX boards → ZHB industry_code 映射
    # V15.1: ZHB dict 不含 industry 字段；改用 TDX boards（参考 docs/field_dict.md）
    _industry = info.get('industry', 'N/A')
    if _industry in ('N/A', '', None):
        # Fallback 1: TDX boards
        try:
            from core.tdx_client import tdx_get_belong_boards

            # V15.4.2: 同步 TDX 包 to_thread
            boards = await asyncio.to_thread(tdx_get_belong_boards, code)
            if boards and boards.get("industry"):
                _industry = boards["industry"][0].get("name", "N/A")
                info["industry"] = _industry
        except Exception:
            pass
    if _industry in ('N/A', '', None) and _zhb_data:
        # Fallback 2: ZHB industry_code 映射（tdxzs3.cfg 已有 1000+ 行业映射）
        # V17.0 修复: 仅认 881 段=通达信行业板块(实锤); 880 段=概念/风格(股权转让/微盘股等,
        # 今日字典定案)不可当行业——否则妖股会显示"股权转让"类概念名
        _zhb_ind_code = _zhb_data.get("industry_code", "")
        if _zhb_ind_code and _zhb_ind_code.startswith("881"):
            _zhb_industry_map = get_zhb_industry_map()
            _zhb_ind_name = _zhb_industry_map.get(_zhb_ind_code, "")
            if _zhb_ind_name:
                _industry = _zhb_ind_name
                info["industry"] = _zhb_ind_name
    # V16.3.3 (2026-08-10 字典 12.15.8): ST/次新风险信号（结构化名称——ST 不剔除仅标注，涨跌幅已统一 10%）
    if getattr(_cdata, "is_st", False):
        L("  ⚠️ 风险标记: **ST/*ST**（退市风险——长期价值需严格财务验证）")
    if getattr(_cdata, "is_new", False):
        L("  🆕 次新标记: 上市 ≤5 日（历史数据不足，长线谨慎）")
    L(f"  所属板块: {_industry}")

    # V15.4.2: 同步同业对比包 to_thread
    peer_data_lng = await asyncio.to_thread(get_industry_peers, code, 3, info=info)
    _ic_d = None  # V16.4.1: try 前初始化——原 L420 `'_ic_d' in dir()` 防御脆弱
    try:
        _ind_name = info.get("industry", "")
        _ic_d = ind_comp if ind_comp is not None else industry_comparison(20)
        if _ic_d:
            for _id in _ic_d:
                if _id.get("name") == _ind_name or _ind_name in _id.get("name", ""):
                    _ind_rank = _id.get("rank", "?")
                    _ind_chg = _id.get("change_pct", 0)
                    _all_m = peer_data_lng.get("all_members", [])
                    if _all_m:
                        _ind_up = sum(1 for m in _all_m if m.get("change_pct", 0) > 0)
                        _ind_down = sum(1 for m in _all_m if m.get("change_pct", 0) < 0)
                    else:
                        _ind_up = _id.get("up_count", 0)
                        _ind_down = _id.get("down_count", 0)
                    L(
                        f"  📊 行业周期定位: 全市场排名#{_ind_rank} | 涨幅{_ind_chg:+.2f}% | 上涨{_ind_up}家/下跌{_ind_down}家"
                    )
                    break
    except Exception as _e:
        _debug_log(f"lng industry_cycle error: {_e}")

    # V17.2.21 修复: 优先 cdata.list_date（push2delay+10年缓存, 实测可用）, info 兜底（主域 push2 被风控拦截恒空）
    # V17.3.5 修正(报告审查 #362): 改用 normalize_list_date 归一化（避免切片对残缺值生成乱码）
    from core._accessors import normalize_list_date

    ext_list_date_raw = cdata.list_date or info.get("list_date", "")
    ext_list_fmt = normalize_list_date(ext_list_date_raw)
    if ext_list_fmt and len(ext_list_fmt) == 10 and ext_list_fmt[4] == "-":
        ext_list_year = int(ext_list_fmt[:4])
        ext_years_listed = date.today().year - ext_list_year
        ext_list_tag = (
            "✅ 上市已满3年（长线安全标的）"
            if ext_years_listed >= 3
            else "⚠️ 上市未满3年（次新股，警惕业绩变脸）"
        )
        L(f"  上市日期: {ext_list_fmt}（已上市 {ext_years_listed} 年）{ext_list_tag}")
    else:
        L(f"  上市日期: {ext_list_fmt}")

    # zhb数据展示（阶段涨幅、52周区间、YTD、员工人数——zhb独有，直接展示）
    # V11.5: 优先从 data_provider 综合数据获取重叠字段，zhb独有字段保留原路径
    _dp_change_ytd = _dp_composite.get("change_ytd", 0) if _dp_composite else 0
    _dp_high_52w = _dp_composite.get("high_52w", 0) if _dp_composite else 0
    _dp_low_52w = _dp_composite.get("low_52w", 0) if _dp_composite else 0

    _zhb_change_ytd = _zhb_data.get("change_ytd", 0) if (_zhb_data and _zhb_fresh) else 0
    _zhb_change_5d = _zhb_data.get("change_5d", 0) if (_zhb_data and _zhb_fresh) else 0
    _zhb_change_10d = _zhb_data.get("change_10d", 0) if (_zhb_data and _zhb_fresh) else 0
    _zhb_change_20d = _zhb_data.get("change_20d", 0) if (_zhb_data and _zhb_fresh) else 0
    _zhb_change_60d = _zhb_data.get("change_60d", 0) if (_zhb_data and _zhb_fresh) else 0
    # change_ytd: data_provider优先
    _show_change_ytd = _dp_change_ytd if _dp_change_ytd and _dp_change_ytd != 0 else _zhb_change_ytd
    if _show_change_ytd:
        L(f"  [年初至今(YTD)] {_show_change_ytd:+.2f}%")
    if _zhb_change_5d or _zhb_change_10d or _zhb_change_20d or _zhb_change_60d:
        L(
            f"  [阶段涨幅] 近5日: {_zhb_change_5d:+.2f}% | 近10日: {_zhb_change_10d:+.2f}% | 近20日: {_zhb_change_20d:+.2f}% | 近60日: {_zhb_change_60d:+.2f}%"
        )

    # 52周区间：data_provider优先
    _show_high_52w = (
        _dp_high_52w if _dp_high_52w > 0 else (_zhb_data.get("high_52w", 0) if _zhb_data else 0)
    )
    _show_low_52w = (
        _dp_low_52w if _dp_low_52w > 0 else (_zhb_data.get("low_52w", 0) if _zhb_data else 0)
    )
    if _show_high_52w > 0 and _show_low_52w > 0 and price_today > 0:
        _52w_pos = (
            (price_today - _show_low_52w) / (_show_high_52w - _show_low_52w) * 100
            if _show_high_52w != _show_low_52w
            else 50
        )
        L(
            f"  [52周区间] 最高: {_show_high_52w:.2f}元 | 最低: {_show_low_52w:.2f}元 | 当前位置: {_52w_pos:.0f}%"
        )

    _zhb_employee_count = _zhb_data.get("employee_count", 0) if _zhb_data else 0
    if _zhb_employee_count > 0:
        L(f"  [员工人数] {_zhb_employee_count:,}人")
        # V10.3: 人效比分析（人均创造市值）
        _mcap_yi = q.get("mcap_yi", 0)
        if _mcap_yi > 0:
            _per_capita_mcap = _mcap_yi * 10000 / _zhb_employee_count
            # V16.4.1: 单位修正——_mcap_yi 为亿元×10000=万元, 除以人数得"万元/人"
            # (原标"元/人"误导: 177 亿/1202 人 = 1473 万, 非 1473 元)
            L(f"  [人效比] 人均创造市值: {_per_capita_mcap:,.0f}万元/人")

    # V10.3: 从tipinfo获取EPS（zhb独有数据）
    _tip_info = get_zhb_tip_info(code)
    if _tip_info:
        _tip_eps = _tip_info.get("eps", 0)
        if _tip_eps and _tip_eps > 0:
            # V16.2.4 修正: tipinfo eps 为单季口径（如 Q1），直接算"对应PE"会与 TTM PE 矛盾误导
            # （实测 0.0692 → 68.9x vs TTM 21.64x），改为标注口径、不再展示误导性 PE
            L(
                f"  [ZHB单季EPS] 最新报告期单季EPS: {_tip_eps:.4f}元（非TTM口径，估值请以上方 PE（TTM） 为准）"
            )

    # 历史最高价——V17.0.7 修复渲染回归: V17.0.5 P2 只改了 qfq 函数, 本处仍
    # high_52w 优先导致前复权修复从未生效(茅台实测显示52周高1539.98/-15.25%,
    # 真 qfq 高1806.54/-27.8%, 黄金坑信号被掩盖)。恢复 qfq 主路径, 52周高仅兜底。
    ext_high_price = get_historical_high(code)
    _hist_src = "qfq"
    if not ext_high_price:
        _dp_high_52w_for_hist = _dp_composite.get("high_52w", 0) if _dp_composite else 0
        _zhb_high_52w_for_hist = _zhb_data.get("high_52w", 0) if _zhb_data else 0
        ext_high_price = (
            _dp_high_52w_for_hist
            if _dp_high_52w_for_hist > 0
            else (_zhb_high_52w_for_hist if _zhb_high_52w_for_hist > 0 else 0)
        )
        _hist_src = "不复权兜底"
    if ext_high_price and price_today > 0:
        ext_deviation = (price_today / ext_high_price - 1) * 100
        L(f"  历史最高价({_hist_src}): {ext_high_price:.2f}元 | 当前偏离度: {ext_deviation:+.2f}%")
        # 口径注: qfq 主路径=腾讯 ifzq 前复权(~640根≈2.6年窗口); 兜底为不复权价
        if _hist_src == "qfq":
            L("    ℹ️ 口径注: 前复权价(含分红送转回溯), 跨除权比较有效; 窗口≈近2.6年")
        else:
            _exd = (_zhb_data or {}).get("ex_date", "") if _zhb_data else ""
            _divd = (_zhb_data or {}).get("div_date", "") if _zhb_data else ""
            if _exd or _divd:
                L(
                    "    ⚠️ 口径注: 兜底为不复权价(该股有除权记录), 跨除权比较偏保守, 请以前复权口径复核"
                )
        # V17.0.7: 回调分级从原嵌套结构拉平(原 elif 挂在不复权口径注分支下,
        # qfq 主路径时黄金坑/显著回调两级信号全部静默丢失)
        if ext_deviation <= -40:
            L(
                f"  🔔 深度回调：距历史最高点已下跌 {abs(ext_deviation):.0f}%，若基本面未恶化，或为长线黄金坑。"
            )
        elif ext_deviation <= -20:
            L(f"  📉 显著回调：距历史最高点已下跌 {abs(ext_deviation):.0f}%，处于阶段性低位区域。")

    # V16.2.3 修正: info.total_shares 单位实为**万股**(实测 == cdata.total_shares_wan, 如 000938=286008 万股),
    # 经 /1e4 转亿股(与 canonical 兜底 f402 同源同单位)。原注释"单位=股"为误判。
    # V17.2.20 修复(B): get_stock_info 对部分标的(实测 002015/301511 等)不返回 total_shares(取默认0),
    # 致"总股本: 0.00亿股"与有值总市值矛盾、且污染策略25规模因子; 回退 canonical 权威层 _cdata.total_shares_wan。
    # V17.3 修正(本报告 3.2 复盘): 原误按 股 /1e8 —— 实测 info.total_shares 实为 万股, /1e8 得 0.00286亿股
    # → 界面显示 0.00亿股, 且正数值绕过 f399 的 <=0 守卫与 f403 的"数据暂缺"。更正为 /1e4 与 canonical 兜底一致。
    # 该误判曾于前期审计被误判为"V17.2.26 已修复的陈旧产物", 实为活体单位 Bug(000938 重跑仍复现)。
    _total_shares_yi = _safe_float(info.get('total_shares', 0)) / 1e4  # 万股→亿股
    if _total_shares_yi <= 0 and _cdata is not None:
        _tsw = _safe_float(getattr(_cdata, 'total_shares_wan', 0))
        if _tsw > 0:
            _total_shares_yi = _tsw / 1e4  # 万股→亿股
    # V17.2.26 修复(报告 3.2): 总股本取空(含 canonical 兜底后仍为空)时渲染"数据暂缺",
    # 不再显示误导性的 0.00亿股(此前与有值总市值自相矛盾, 且曾污染规模因子)。
    _ts_disp = f"{_total_shares_yi:.2f}亿股" if _total_shares_yi > 0 else "数据暂缺"
    L(f"  总股本:   {_ts_disp} | 总市值: {q.get('mcap_yi', 0):.2f}亿元")
    L(f"  当前股价: {price_today:.2f}元")

    L("\n  ➤ 长线估值安全边际指标:")
    # PE估值：data_provider优先，其次zhb，最后fallback到腾讯行情
    _zhb_pe_ttm = _zhb_data.get("pe_ttm", 0) if _zhb_data else 0
    _zhb_pe_dynamic = _zhb_data.get("pe_dynamic", 0) if _zhb_data else 0
    _zhb_pb = _zhb_data.get("pb", 0) if _zhb_data else 0
    _dp_pe = _dp_composite.get("pe_ttm", 0) if _dp_composite else 0
    _dp_pb = _dp_composite.get("pb", 0) if _dp_composite else 0
    _dp_div = _dp_composite.get("dividend_yield", 0) if _dp_composite else 0
    if _dp_pe and _dp_pe > 0:
        _pe = _dp_pe
        # V17.0.17(2026-09-01) 据主字典定案修正: 动态PE=canonical pe_dynamic(f162);
        # 静态PE（LYR）=canonical pe_lyr(f163, 本次新增透传)。原 _pe_static 误用 pe_dynamic(动态) 当静态, 已纠正。
        _pe_dyn = float(getattr(_cdata, "pe_dynamic", 0) or 0) if _cdata else 0
        _pe_lyr = float(getattr(_cdata, "pe_lyr", 0) or 0) if _cdata else 0
    elif _zhb_pe_ttm and _zhb_pe_ttm > 0:
        _pe = _zhb_pe_ttm
        _pe_dyn = _zhb_pe_dynamic
        _pe_lyr = 0  # ZHB 无静态PE字段(只有动态[3]/TTM[9]), 静态缺失不伪造
    else:
        _pe = q.get('pe_ttm', 0)
        # V16.4.1: q 无 pe_dynamic 键 → else 分支 PE(动态) 可能 N/A; 用 ZHB 动态口径兜底
        _pe_dyn = _zhb_pe_dynamic or q.get('pe_dynamic', 0)
        _pe_lyr = float(getattr(_cdata, "pe_lyr", 0) or 0) if _cdata else 0
    if _pe > 0:
        _ey = f"{100/_pe:.2f}%"
        # V16.4.1: 标注 PE 来源口径(ZHB pe_ttm 基于最近年报/季报净利, 可能与
        # 报告期最新财务表有滞后——2026-08-12 实测 000506: ZHB=110.47(2025年报 1.59亿)
        # vs 财务表 TTM 4.73 亿(含 2026Q1) 应 ~37x, 口径差 3 倍)
        _pe_src = (
            "data_provider"
            if (_dp_pe and _dp_pe > 0)
            else ("ZHB" if (_zhb_pe_ttm and _zhb_pe_ttm > 0) else "腾讯")
        )
    else:
        _ey = "N/A"
        # V17.0.9: 亏损股(_pe<=0)补 _pe_src 初始化——原 else 分支未赋值,
        # 688802 等亏损股 444 行访问 _pe_src 报 UnboundLocalError(2026-08-27 批量实测)
        _pe_src = "亏损(无正PE)"
        # V16.0: 改用统一层 _cdata（get_canonical_stock_data）的财务字段计算 EPS，
        # 替代直接 _get_tdx_client().get_finance_info() 协议直连（统一数据来源）
        try:
            if _cdata is not None:
                _profit = _safe_float(_cdata.net_profit)  # 元
                _shares_wan = _safe_float(_cdata.total_shares_wan)  # 万股
                if _profit > 0 and _shares_wan > 0 and price_today > 0:
                    _eps = _profit / (_shares_wan * 1e4)
                    _ey = f"{_eps / price_today * 100:.2f}%"
        except Exception as _e:
            _debug_log(f"lng finance_info error: {_e}")
    # V17.0.1e: 撤销 V17.0.1b 表格化——估值为"字段: 值"竖排, 不适用表格
    # V17.0.27(2026-09-04) A6「缺失≠0」（9/3 报告核查 #1 的 lng 侧）:
    #   亏损股 _pe=0 时原渲染 "0.00x"，虽有 "(亏损(无正PE)口径)" 注脚，但 0.00x 仍是
    #   一个**可被下游/读者当作数值消费的假数**（0 是极值不是中性值）。改为显式 N/A。
    L(
        f"    市盈率 PE（TTM）: {_pe:.2f}x ({_pe_src}口径; 盈利收益率粗估: {_ey})"
        if _pe > 0
        else f"    市盈率 PE（TTM）: N/A（{_pe_src}口径; 盈利收益率粗估: {_ey}）"
    )
    # V17.0.17(2026-09-01) 据主字典定案修正: 动态PE=pe_dynamic(f162) / 静态PE（LYR）=pe_lyr(f163) 分开展示, 口径不再混淆
    L(
        f"    动态市盈率 PE（动）: {_pe_dyn:.2f}x"
        if _pe > 0 and _pe_dyn > 0
        else "    动态市盈率 PE（动）: N/A"
    )
    L(
        f"    静态市盈率 PE（LYR）: {_pe_lyr:.2f}x"
        if _pe > 0 and _pe_lyr > 0
        else "    静态市盈率 PE（LYR）: N/A（无静态口径）"
    )
    # V17.0.26(2026-09-03) DEBT-008: 删除假的 PE(MorePE) 交叉验证展示行（与 med 报告同源问题）。
    #   原注释称"pe_more 与 pe_ttm 口径略有差异，偏差大→提示异常"，但二者同源 f164，
    #   该展示永不触发却向读者谎称存在两个独立口径 —— 违反公理 A2 / A7。
    # V17.0.31(2026-09-04) DEBT-003: 下沉的 debug 自检一并删除。
    #   它同样**永不触发**（f164 已统一映射为 pe_ttm，无任何源产出 pe_more 键
    #   → _pe_more 恒 0 → `and _pe_more > 0` 恒假）。一个永不告警的"自检"不是自检，
    #   是自我安慰（A7）。若将来需要 TTM 口径漂移监测，正确做法是**跨源**对比
    #   （腾讯 vs 东财 vs ZHB 的 TTM 互校），走字典季度核验流程，而非同源别名比对。
    # PB：data_provider优先，其次zhb，最后fallback到腾讯行情
    if _dp_pb and _dp_pb > 0:
        _pb_val = _dp_pb
    elif _zhb_pb and _zhb_pb > 0:
        _pb_val = _zhb_pb
    else:
        _pb_val = q.get('pb', 0)
    L(f"    市净率 PB:      {_pb_val:.2f}x")
    # 股息率：data_provider优先，其次zhb
    _zhb_div_yield = _zhb_data.get("dividend_yield", 0) if _zhb_data else 0
    _show_div_yield = _dp_div if _dp_div and _dp_div > 0 else _zhb_div_yield
    if _show_div_yield > 0:
        L(f"    股息率:        {_show_div_yield:.2f}%")

    if peer_data_lng.get("my_rank", 0) > 0 and peer_data_lng.get("industry_count", 0) > 0:
        L(
            f"  板块排名: 按总市值排序, 该股排名第 {peer_data_lng['my_rank']}/{peer_data_lng['industry_count']} 位"
        )

    try:
        _ic_data = _ic_d  # V16.4.1: 已 try 前初始化, 不再依赖 dir() 防御
        if _ic_data and isinstance(_ic_data, list):
            _our_ind = info.get("industry", "")
            for _ind in _ic_data:
                if _ind.get("name") == _our_ind or _our_ind in _ind.get("name", ""):
                    _lng_pe_lyr = getattr(_cdata, "pe_lyr", 0) or 0
                    _lng_pe_lyr_s = f"{_lng_pe_lyr:.1f}x" if _lng_pe_lyr > 0 else "N/A"
                    L(
                        f"  📊 板块横向对比: 本股PE（TTM）={q.get('pe_ttm',0):.1f}x | 本股PE（静）={_lng_pe_lyr_s} | 板块涨跌{_ind.get('change_pct',0):+.2f}%"
                    )
                    break
    except Exception as _e:
        _debug_log(f"lng industry_compare error: {_e}")

    L("\n## 【二、跨期财务纵深与长效业绩验证 (近8个报告期)】")
    L("---")
    financials = await get_sina_financial_report_async(session, code, num_periods=8)
    if not financials:  # B: 新浪缺失 → fuyao 利润表兜底
        financials = get_financial_report_with_fallback(code, num_periods=8)
    if financials:
        L(f"  {'报告期':<12} {'营业总收入(亿)':>10} {'净利润(亿)':>13}")
        L(f"  {'-'*45}")
        for item in financials:
            date_val = item.get("报告日", "")
            rev = item.get("营业总收入", "0")
            profit = item.get("净利润", "0")
            try:
                rev_yi = f"{float(rev)/1e8:.2f}" if rev and rev != "0" else "N/A"
                profit_yi = f"{float(profit)/1e8:.2f}" if profit and profit != "0" else "N/A"
            except (ValueError, TypeError):
                rev_yi, profit_yi = "N/A", "N/A"
            L(f"  {date_val:<12} {rev_yi:>14} {profit_yi:>14}")
        L("\n  💡 长线逻辑：观察其是否具备持续、平稳的造血能力，警惕大起大落的强周期股。")
    else:
        L("  (新浪财报数据获取失败)")

    bs_data = await get_sina_balance_sheet_async(session, code)
    L("\n  ➤ 核心复利引擎（ROE净资产收益率追踪）:")
    # V17.3 修正(审查): info.total_shares 单位=万股(== cdata.total_shares_wan);
    # get_roe_trend_series 新浪兜底 eps=profit/total_shares 期望"股", 原传万股→EPS/BPS 错 1e4 倍。
    # 改用统一层 cdata.total_shares_wan(万股)*1e4=股, 与 F10 加权口径同源。
    ext_roe_data = get_roe_trend(
        code,
        8,
        financials=financials,
        bs_data=bs_data,
        total_shares=(cdata.total_shares_wan * 1e4) if cdata.total_shares_wan > 0 else 0,
    )
    if ext_roe_data:
        # V17.0.7: 按报告期日期降序排列(修复 FY 优先导致 Q 数据排错位置)
        ext_roe_data = sorted(ext_roe_data, key=lambda r: str(r.get('date', '')), reverse=True)
        # V17.0.2i: 直接 md 表格 5 列(原空格表数据行粘连)
        L("| 报告期 | ROE% | 扣非ROE% | EPS | BPS |")
        L("|---|---|---|---|---|")
        for r in ext_roe_data:
            ext_roe_str = f"{r['roe']:.2f}" if r['roe'] is not None else "N/A"
            ext_roe_kc_str = f"{r['roe_kc']:.2f}" if r['roe_kc'] is not None else "N/A"
            # V17.3.5 修正(报告审查): get_roe_trend 的 F10 路径返回 基本每股收益(元)/每股净资产(元)
            # （已是元单位），新浪兜底路径亦为 profit/total_shares（元/股）——两者均**非** 0.0001 元单位；
            # 旧代码 /10000 致 EPS/BPS 缩水 1e4 倍（如 2.8元→0.0002元）。此处直接以元显示。
            ext_eps_val = r['eps']
            ext_bps_val = r['bps']
            ext_eps_str = f"{ext_eps_val:.4f}" if ext_eps_val is not None else "N/A"
            ext_bps_str = f"{ext_bps_val:.4f}" if ext_bps_val is not None else "N/A"
            L(f"| {r['date']} | {ext_roe_str} | {ext_roe_kc_str} | {ext_eps_str} | {ext_bps_str} |")
        ext_last_roe = ext_roe_data[0].get("roe")
        if ext_last_roe is not None:
            if ext_last_roe >= 20:
                L(
                    f"\n  ✅ 结论：最新 ROE = {ext_last_roe:.2f}% ≥ 20%，属于极其罕见的优质复利机器！"
                )
            elif ext_last_roe >= 15:
                L(f"  ✅ 结论：最新 ROE = {ext_last_roe:.2f}% ≥ 15%，具备长期复利能力。")
            elif ext_last_roe >= 10:
                L(f"  📊 结论：最新 ROE = {ext_last_roe:.2f}%，处于中等水平，需关注趋势。")
            else:
                L(
                    f"  ⚠️ 结论：最新 ROE = {ext_last_roe:.2f}% < 10%，资本回报效率偏低，长线需谨慎。"
                )
    else:
        L("  (ROE数据获取失败)")

    # V17.0.5 P0: ROE 双口径对照——报告期加权(F10) vs TTM扣非(腾讯 tx65/fuyao 官方同族)
    # 背离信号: 报告期 ROE 高但扣非 TTM 低 → 利润含一次性损益(卖资产/政府补助), 盈利质量水分
    try:
        from core.data_provider import get_canonical_stock_data as _gcd

        _cd = await asyncio.to_thread(_gcd, code)
        _rdt = float(getattr(_cd, "roe_deduct_ttm", 0) or 0)
    except Exception:
        _rdt = 0.0
    if _rdt > 0 and ext_roe_data:
        _rep_roe = ext_roe_data[0].get("roe")
        if _rep_roe is not None:
            _gap = _rep_roe - _rdt
            L(
                f"\n  ⚖️ ROE 双口径对照: 报告期加权 {_rep_roe:.2f}% vs 扣非TTM {_rdt:.2f}%（差 {_gap:+.2f}pp）"
            )
            if _gap > 5:
                L("  ⚠️ 报告期 ROE 显著高于扣非 TTM——利润或含大额非经常性损益，核查扣非明细")
            elif _gap < -5:
                L("  ✅ 扣非 TTM 高于报告期——常态化盈利强于表观，质量偏好")
            else:
                L("  ✅ 双口径基本一致，盈利质量扎实")

    if financials and len(financials) >= 2:
        gm_rows = []
        for item in financials:
            try:
                rev = float(item.get("营业总收入", 0))
                cost = float(item.get("营业成本", 0))
                profit = float(item.get("净利润", 0))
                if rev > 0:
                    xsmll = item.get("XSMLL")
                    if xsmll is not None and str(xsmll) not in ("", "0"):
                        gm = float(xsmll)
                    else:
                        gm = (rev - cost) / rev * 100
                    npm = profit / rev * 100
                    gm_rows.append({"date": item.get("报告日", ""), "gm": gm, "npm": npm})
            except (ValueError, TypeError, ZeroDivisionError):
                pass
        if gm_rows:
            L("\n  ➤ 盈利能力与护城河追踪:")
            L(f"  {'报告期':<12} {'毛利率%':>10} {'净利率%':>10}")
            L(f"  {'-'*35}")
            for g in gm_rows:
                L(f"  {g['date']:<12} {g['gm']:>9.2f}% {g['npm']:>9.2f}%")
            # V16.4.1: 净利率>100% 口径提示(2026-08-12 实测 000506 招金黄金 2026Q1
            # 净利 1.87 亿 > 营收 1.79 亿——东财 f183-f188 与 TDX F10 双源一致,
            # 系大额投资收益/非经营收益主导的季度, 非数据错误)
            if any(g["npm"] > 100 for g in gm_rows):
                L("  ⚠️ 注: 净利率>100% 为净利含大额投资收益等非经营项(双源核验一致), 非计算错误")
            latest_gm = gm_rows[0]["gm"]
            if latest_gm >= 40:
                L(f"  ✅ 毛利率 {latest_gm:.1f}% ≥ 40%，具备较强定价权与护城河。")
            elif latest_gm >= 25:
                L(f"  📊 毛利率 {latest_gm:.1f}%，处于中等水平，关注行业格局变化。")
            else:
                L(f"  ⚠️ 毛利率 {latest_gm:.1f}% < 25%，盈利能力偏薄，长线需警惕同质化竞争。")

    if financials and len(financials) >= 4:
        try:
            # V17.3.5 修正(报告审查 #365): 仅用年报(报告日含 12-31/12/31/1231/12月31日)计算复合增速,
            # 避免混入 H1/Q1 季报导致虚假负增长; 且要求 >=3 个年报点方可称 CAGR,
            # 仅 2 点时降级为"近1年同比"并附数据质量提示(单年极端值多为年报数据缺口)。
            def _is_year_end(rd):
                s = str(rd or "")
                return (
                    s.endswith("12-31") or s.endswith("12/31") or "1231" in s or ("12月31日" in s)
                )

            _fy_rows = [f for f in financials if _is_year_end(f.get("报告日", ""))]
            _rev3 = [_safe_float(f.get("营业总收入", "0")) for f in _fy_rows]
            _prf3 = [_safe_float(f.get("净利润", "0")) for f in _fy_rows]
            if len(_rev3) >= 2 and _rev3[0] > 0 and _rev3[-1] > 0:
                if len(_rev3) >= 3:
                    _years = len(_rev3) - 1
                    _rev_cagr = (pow(_rev3[0] / _rev3[-1], 1 / _years) - 1) * 100
                    if _prf3[0] > 0 and _prf3[-1] > 0:
                        _prf_cagr = (pow(_prf3[0] / _prf3[-1], 1 / _years) - 1) * 100
                        _prf_cagr_str = f"{_prf_cagr:.1f}%"
                    else:
                        _prf_cagr_str = "N/A (亏损)"
                    L(f"  📊 近{_years}年营收CAGR: {_rev_cagr:.1f}% | 净利润CAGR: {_prf_cagr_str}")
                else:
                    _rev_yoy = (_rev3[0] / _rev3[-1] - 1) * 100
                    _prf_yoy = (
                        (_prf3[0] / _prf3[-1] - 1) * 100
                        if (_prf3[0] > 0 and _prf3[-1] > 0)
                        else None
                    )
                    _prf_yoy_str = f"{_prf_yoy:.1f}%" if _prf_yoy is not None else "N/A (亏损)"
                    L(f"  📊 近1年营收同比: {_rev_yoy:+.1f}% | 净利润同比: {_prf_yoy_str}")
                    if abs(_rev_yoy) > 50 or (_prf_yoy is not None and abs(_prf_yoy) > 50):
                        L(
                            "    ⚠️ 单年同比变动超 50%, 提示: 可能含年报数据缺口或口径切换, 数值仅供参考"
                        )
        except Exception as _e:
            _debug_log(f"lng cagr_calc error: {_e}")

    L("\n## 【三、财务健康度排雷（现金流验证与商誉预警）】")
    L("---")
    # C: 经营现金流(单报告期)/有息负债等 OCF 维度 canonical 不覆盖(仅 ocf_ttm=f103 为 TTM)，
    #    故单期 OCF/NPL 必须取自 TDX 0x0010 快照(jingyingxianjinliu / 净利润字段)，不可删除。
    _tdx_ocf = 0.0
    _tdx_np = 0.0
    # V16.1: 0x0010 财务快照存局部变量，供下方"核心财务指标"复用（避免重复 TCP 请求）
    _tdx_fi_snapshot = None
    try:
        from core.tdx_client import tdx_get_finance_info

        fi = tdx_get_finance_info(code)
        if fi is not None:
            _tdx_fi_snapshot = fi
            # V15.1: 修正 0x0010 协议 key（参考 docs/field_dict.md 第 7 章）
            # 正确 key: jingyingxianjinliu / jinglirun（无下划线）
            # V16.3 O19: 0x0010 金额字段单位=角（field_dict §零 O 实测）——/10 得元
            # （此前直接 /1e8 显示亿 → 现金流/净利偏大 10 倍）
            # V17.0.26(2026-09-03): 改用 tdx_client 适配器 tdx_get_finance_info（返回归一化 dict, nan→None），
            #   不再直连裸 _get_tdx_client().get_finance_info()，符合"统一层收口"规范（见 AGENTS.md §8.3）。
            _tdx_ocf = _safe_float(fi.get('jingyingxianjinliu', 0)) / 10.0
            _tdx_np = _safe_float(fi.get('jinglirun', 0)) / 10.0
    except Exception as _e:
        _debug_log(f"lng tdx_ocf error: {_e}")

    if bs_data:
        latest_bs = bs_data[0]
        gw = float(latest_bs.get("商誉", 0))
        equity = float(latest_bs.get("归属于母公司股东权益合计", 0))
        total_assets = float(latest_bs.get("资产总计", 0))
        gw_yi = gw / 1e8
        equity_yi = equity / 1e8
        asset_yi = total_assets / 1e8
        if equity_yi > 0:
            gw_ratio = gw / equity * 100
            L(
                f"  商誉: {gw_yi:.2f}亿元 | 净资产: {equity_yi:.2f}亿元 | 商誉/净资产: {gw_ratio:.1f}%"
            )
            if gw_ratio > 20:
                L(
                    f"  ⚠️ 爆雷预警：商誉占净资产 {gw_ratio:.1f}% > 20%，注意行业周期下行时的商誉减值黑天鹅！"
                )
            else:
                L("  ✅ 商誉占比在安全范围内 (< 20%)。")
        _liab = float(latest_bs.get("负债合计", 0))
        # V17.2.26 修复(报告 3.3): 资产负债率须直接用负债合计/资产总计, 原用 100-归母权益/资产
        # 忽略少数股东权益, 对含少数股东的公司系统性高估约5pp(如 002015: 68.7% vs med 63.6%)。
        L(
            f"  资产负债率: {_liab/total_assets*100:.1f}%（截至 {bs_data[0].get('报告日','')}）"
            if (asset_yi > 0 and _liab > 0)
            else ""
        )
        _st_loan = _safe_float(bs_data[0].get("短期借款", "0")) / 1e8
        _lt_loan = _safe_float(bs_data[0].get("长期借款", "0")) / 1e8
        _bd = _safe_float(bs_data[0].get("应付债券", "0")) / 1e8
        _int_debt = _st_loan + _lt_loan + _bd
        _int_ratio = _int_debt / asset_yi * 100 if asset_yi > 0 else 0
        L(
            f"  有息负债率: {_int_ratio:.1f}%（短期借款{_st_loan:.2f}亿+长期借款{_lt_loan:.2f}亿+债券{_bd:.2f}亿）"
        )
        if _int_debt > 0 and _tdx_ocf > 0:
            _ocf_liab = _tdx_ocf / 1e8
            _cov = _ocf_liab / _int_debt
            if _cov > 2:
                L(f"    经营现金流/有息负债: {_cov:.2f}倍 ✅ 偿债能力充裕")
            elif _cov > 0.5:
                L(f"    经营现金流/有息负债: {_cov:.2f}倍 ⚠️ 偿债压力适中")
            else:
                L(f"    经营现金流/有息负债: {_cov:.2f}倍 ⚠️ 偿债压力较大")
    else:
        L("  (资产负债表数据获取失败)")
    if _tdx_ocf != 0 and _tdx_np != 0:
        ocf_yi = _tdx_ocf / 1e8
        np_yi = _tdx_np / 1e8
        if _tdx_np > 0:
            cash_ratio = _tdx_ocf / _tdx_np * 100
            L(
                f"\n  经营现金流: {ocf_yi:.2f}亿元 | 净利润: {np_yi:.2f}亿元 | 现金/利润比: {cash_ratio:.1f}%"
            )
            if cash_ratio < 80:
                L(
                    f"  ⚠️ 警惕：经营现金流仅为净利润的 {cash_ratio:.1f}%，存在利润造假或严重压货风险，现金含量不足！"
                )
            else:
                L("  ✅ 经营现金流覆盖净利润充足 (> 80%)，利润含金量高。")
        elif _tdx_np < 0 and _tdx_ocf < 0:
            L(
                f"\n  经营现金流: {ocf_yi:.2f}亿元 | 净利润: {np_yi:.2f}亿元 (均为负值，持续失血状态)"
            )
        else:
            L(f"\n  经营现金流: {ocf_yi:.2f}亿元 | 净利润: {np_yi:.2f}亿元")
    elif _tdx_ocf != 0:
        L(f"  经营现金流: {_tdx_ocf/1e8:.2f}亿元 (财务数据不足，无法计算现金/利润比)")
    else:
        L("  (经营现金流数据获取失败)")
    parts = []
    # LOW(审查 2026-08-16): 清理空块+冗余 locals 防御——gm_rows 直接可用
    if gm_rows:
        parts.append(f"毛利率 {gm_rows[0]['gm']:.2f}%")
        parts.append(f"净利率 {gm_rows[0]['npm']:.2f}%")
    if ext_roe_data and ext_roe_data[0].get("roe") is not None:
        parts.append(f"ROE {ext_roe_data[0]['roe']:.2f}%")
    # V17.3.5 修正(报告审查): eps 已是元单位（F10 基本每股收益(元)），不再 /10000
    if ext_roe_data and ext_roe_data[0].get("eps") is not None:
        parts.append(f"EPS {ext_roe_data[0]['eps']:.4f}")
    try:
        # V16.1: 复用"三"章节的 0x0010 快照（避免重复 TCP 请求）
        if _tdx_fi_snapshot is not None:
            tdx_fi = _tdx_fi_snapshot
        else:
            # V17.0.26(2026-09-03) DEBT-001: 改用 tdx_client 适配器（公理 A1 数据访问收口），
            #   不再直连裸 _get_tdx_client().get_finance_info()。
            from core.tdx_client import tdx_get_finance_info

            tdx_fi = tdx_get_finance_info(code)
        # 适配器返回 None 或非空 dict（nan→None），故用真值判断即可
        if tdx_fi:
            # V15.1: 修正 0x0010 协议 key（参考 docs/field_dict.md）
            # V16.3 O19: 角→元（/10）后再 /1e8 显示亿——否则偏大 10 倍
            # V17.0.26: 适配器返回归一化 dict, 取值从 .iloc[0].get() 改为 .get()
            ocf = _safe_float(tdx_fi.get('jingyingxianjinliu', 0)) / 10.0 / 1e8
            if ocf != 0:
                parts.append(f"经营现金流 {ocf:.2f}亿")
    except Exception as _e:
        _debug_log(f"lng tdx_fi_ocf error: {_e}")
    if parts:
        L("\n  ➤ 当期核心财务指标一览:")
        for p in parts:
            L(f"    {p}")
    # V17.0.5 P0: 现金流官方指标交叉核验(fuyao 五类指标 cash-flow 族)
    try:
        from stock_common import get_fuyao_fin_indicators, is_fuyao_enabled

        if is_fuyao_enabled():
            _yy = date.today().year
            for _rp in (f"{_yy}-1", f"{_yy - 1}-4"):
                _fi = await asyncio.to_thread(get_fuyao_fin_indicators, code, _rp)
                if _fi:
                    _cf = _fi.get("cash-flow") or {}
                    _npc = _cf.get("net_profit_cash_content")
                    _coi = _cf.get("cash_operating_index")
                    if _npc is not None or _coi is not None:
                        L(f"\n  🔬 现金流官方指标交叉(fuyao, 报告期 {_rp.replace('-', 'Q')}):")
                        if _npc is not None:
                            _v = float(_npc)
                            _tag = (
                                "✅ 含金量充足"
                                if _v >= 100
                                else ("⚠️ 偏低" if _v >= 60 else "🚨 严重不足")
                            )
                            L(f"    净利润现金含量: {_v:.1f}% {_tag}(报告期口径)")
                        if _coi is not None:
                            _v2 = float(_coi)
                            _tag2 = (
                                "✅" if _v2 >= 1.0 else ("⚠️" if _v2 >= 0.9 else "🚨 利润粉饰嫌疑")
                            )
                            L(f"    现金营运指数: {_v2:.2f} {_tag2}")
                        # V17.0.7: 加口径注——fuyao 指标为报告期累计(非TTM)，
                        # 茅台等下半年回款型企业的 H1 现金含量天然偏低，与下方 TTM 对照不矛盾
                        L("    ℹ️ 口径注: 以上为报告期(H1/Q1)单期数据; TTM 口径见下方双源对照")
                        break
    except Exception as _e:
        _debug_log(f"lng fuyao cashflow cross: {_e}")
    # V17.0.7: 现金流双源对照——push2 f103(TTM 口径, 随 push2delay 补取零额外请求)
    # vs 上方 0x0010(最新报告期)。两口径互补非等值; 滚动现金含量跨两财年为粗算参考。
    try:
        _ocf_ttm_v7 = float(getattr(cdata, "ocf_ttm", 0) or 0)
        _rev_ttm_v7 = float(getattr(cdata, "revenue_ttm", 0) or 0)
        _np_annual_v7 = float(getattr(cdata, "net_profit_annual", 0) or 0)
        if _ocf_ttm_v7:
            L("\n  🔬 现金流双源对照(push2delay f103 族, V17.0.7 字典终破口径):")
            _base = f"    经营现金流净额(TTM): {_ocf_ttm_v7/1e8:.2f}亿元"
            if _tdx_ocf:
                _base += f" | 0x0010 最新报告期: {_tdx_ocf/1e8:.2f}亿元"
            L(_base)
            if _rev_ttm_v7:
                L(
                    f"    营业总收入(TTM): {_rev_ttm_v7/1e8:.2f}亿元 → 经营现金流/收入比 {_ocf_ttm_v7/_rev_ttm_v7*100:.1f}%"
                )
            if _np_annual_v7 > 0:
                _cr_v7 = _ocf_ttm_v7 / _np_annual_v7 * 100
                _tag_v7 = (
                    "✅ 含金量充足"
                    if _cr_v7 >= 80
                    else ("⚠️ 偏低" if _cr_v7 >= 60 else "🚨 严重不足")
                )
                L(
                    f"    滚动现金含量(TTM OCF/上年归母净利): {_cr_v7:.1f}% {_tag_v7}(跨两财年粗算, 参考)"
                )
    except Exception as _e:
        _debug_log(f"lng ocf_ttm dual-source: {_e}")
    L(
        "\n  💡 长线排雷：持续的经营现金净流入是检验账面利润真实性的最佳标准，高商誉+低现金含量=高危组合。"
    )

    L("\n## 【四、机构一致预期与 PEG 均值回归模型】")
    L("---")
    # H4 修复(2026-08-15 二审): 本地 ProfitForecast O(1) 优先(零网络), 未命中走网络兜底——与一章重复块合并
    df_eps = await resolve_eps_forecast(session, code)
    eps_cur = eps_next = None
    eps_has_data = False
    if not df_eps.empty and len(df_eps.columns) >= 4:
        L("| 年度 | 覆盖机构数 | 预测EPS均值 |")
        L("|---|---|---|")
        _this_year = date.today().year
        _eps_by_year = {}
        for i, row in df_eps.iterrows():
            try:
                year = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
                cnt = int(row.iloc[1]) if pd.notna(row.iloc[1]) else 0
                mean_v = float(row.iloc[3]) if pd.notna(row.iloc[3]) else 0
                L(f"| {year} | {cnt} | {mean_v:.3f} |")
                _yd = ''.join(ch for ch in year if ch.isdigit())
                if _yd:
                    _eps_by_year[int(_yd)] = mean_v
                if i == 0:
                    eps_cur = mean_v
                    eps_has_data = True
                elif i == 1:
                    eps_next = mean_v
            except (ValueError, TypeError, IndexError):
                pass
        # V17.2.26 修复(报告 3.4/3.5): 前向PE/增速须取【本年度/明年】预测EPS, 不可按行位置取首行
        # (首行常为上年实际, 致 pe_fwd 实为静态PE、增速=上年实际→本年预测, 与 med 口径错配)。
        if _this_year in _eps_by_year:
            eps_cur = _eps_by_year[_this_year]
        if (_this_year + 1) in _eps_by_year:
            eps_next = _eps_by_year[_this_year + 1]
    if not eps_has_data:
        em_eps = await _get_eps_from_em_reports_async(session, code)
        if em_eps:
            eps_cur = em_eps["eps_cur"]
            eps_next = em_eps["eps_next"]
            eps_has_data = True
            this_year = date.today().year
            L("  东财研报一致预期EPS (同花顺兜底):")
            L("| 年度 | 预测EPS |")
            L("|---|---|")
            if eps_cur:
                L(f"| {this_year} | {eps_cur:.3f} |")
            if eps_next:
                L(f"| {this_year + 1} | {eps_next:.3f} |")
    if eps_has_data and price_today and eps_cur and eps_cur > 0:
        pe_fwd = price_today / eps_cur
        L("\n  ➤ 基于机构预期的远期估值消化推演:")
        L(f"    前向市盈率 (本年度): {pe_fwd:.2f}x")
        if eps_next and eps_cur > 0:
            cagr = (eps_next / eps_cur) - 1
            L(f"    未来一年预期净利增速: {cagr*100:.1f}%")
            peg = (
                pe_fwd / (cagr * 100) if cagr > 0 else float("inf")
            )  # V16.4.1: 原 "in" 拼写错误→ValueError
            if peg > 5:
                L("    PEG: >5.0（增速过低或PE过高导致极端值，不具参考意义）")
            else:
                # V16.4.1: 跨期口径标注——pe_fwd 用本年 EPS, 增速用明年 EPS(向前 PEG)
                L(
                    f"    PEG (市盈率相对盈利增长比率): {peg:.2f} (长线买入参考: <1低估, 1-1.5合理) [PE本年/增速明年,跨期口径]"
                )
            if cagr > 0:
                digest_25 = math.log(pe_fwd / 25) / math.log(1 + cagr) if pe_fwd > 25 else 0
                try:
                    _sk_p, _sr_p = await asyncio.to_thread(baidu_kline_full, code)
                    _ci_p = next(
                        (i for i, k in enumerate(_sk_p) if k in ("close", "close_price")), -1
                    )
                    if _ci_p >= 0 and eps_cur > 0:
                        _hp = [_safe_float(rr[_ci_p]) for rr in _sr_p if len(rr) > _ci_p]
                        if len(_hp) > 20:
                            _hpe = [p / eps_cur for p in _hp if p > 0]
                            if _hpe:
                                _pc = sum(1 for p in _hpe if p < pe_fwd) / len(_hpe) * 100
                                L(
                                    f"  PE历史分位: {_pc:.0f}%（当前PE高于{_pc:.0f}%的历史时间，数值越高越贵）"
                                )
                except Exception as _e:
                    _debug_log(f"lng pe_percentile error: {_e}")
                if digest_25 > 0:
                    L(f"    模型测算：当前估值消化至 25 倍合理市盈率约需 {digest_25:.1f} 年")
                else:
                    L("    模型测算：当前估值已低于/等于 25 倍合理水位线，具备长线配置的安全垫。")
    else:
        L("  无足够机构覆盖（冷门标的，长线投研需完全依赖自主财务尽调）。")

    L("\n## 【五、长效股东回报属性 (分红与股息历史)】")
    L("---")
    # 股息率：data_provider优先，其次zhb展示
    _zhb_div_yield_5 = _zhb_data.get("dividend_yield", 0) if _zhb_data else 0
    _dp_div_yield_5 = _dp_composite.get("dividend_yield", 0) if _dp_composite else 0
    _show_div_5 = _dp_div_yield_5 if _dp_div_yield_5 and _dp_div_yield_5 > 0 else _zhb_div_yield_5
    if _show_div_5 > 0:
        L(f"  当前股息率: {_show_div_5:.2f}%（zhb数据）")
    # V17.0.7: 每股未分配利润——分红能力池子(push2 f190, ≡ulist f48, 随行情补取零额外请求)
    try:
        _upp_v7 = float(getattr(cdata, "undist_profit_ps", 0) or 0)
        if _upp_v7:
            if _upp_v7 < 0:
                _upp_tag = "🚨 为负(弥补亏损期, 短期无分红能力)"
            elif _upp_v7 >= 5:
                _upp_tag = "✅ 分红池厚"
            else:
                _upp_tag = "ℹ️ 分红池偏薄"
            L(f"  每股未分配利润: {_upp_v7:.2f}元（分红能力池子）{_upp_tag}")
    except Exception as _e:
        _debug_log(f"lng undist_profit_ps: {_e}")
    div = await asyncio.to_thread(get_dividend_history, code)
    if div:
        L("  近5次分红除息记录:")
        L(f"  {'除权除息日':<14} {'每股派息(元)':>8} {'折算对应股价股息率参考'}")
        L(f"  {'-'*55}")
        total_div_12m = 0.0
        one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        for d in div[:5]:
            yield_str = f"{(d['bonus_rmb'] / price_today) * 100:.2f}%" if price_today > 0 else "N/A"
            L(f"  {d['date']:<14} {d['bonus_rmb']:>12.4f}  约 {yield_str} (按现价计)")
            if d['date'] >= one_year_ago:
                total_div_12m += d['bonus_rmb']

        if price_today > 0 and total_div_12m > 0:
            L(f"\n  ➤ 核心防御指标：近 12 个月累计派息 {total_div_12m:.4f} 元/股")
            L(f"  ➤ 动态股息率 (TTM): {(total_div_12m / price_today) * 100:.2f}%")

        # V16.1: 分红连续性（从分红历史推导连续分红年数）
        try:
            _div_years = set()
            for _d in div:
                _yr = str(_d.get("date", ""))[:4]
                if _yr.isdigit():
                    _div_years.add(int(_yr))
            if _div_years:
                _sorted_years = sorted(_div_years)
                # 从最近一年往前数连续年数
                _consec = 0
                for _y in range(_sorted_years[-1], _sorted_years[-1] - len(_sorted_years) - 1, -1):
                    if _y in _div_years:
                        _consec += 1
                    else:
                        break
                if _consec >= 5:
                    L(f"  🏆 分红连续性: 连续分红 {_consec} 年（含当年），长线股东回报稳定")
                elif _consec >= 3:
                    L(f"  ✅ 分红连续性: 连续分红 {_consec} 年")
                elif _consec >= 1:
                    # V16.4.1: 补"最近分红年份距今"——2026-08-12 实测 000506 最近分红
                    # 在 2014 年, 原"近 2 年有分红"表述误导(应为"近 2 个分红年度, 距今 12 年")
                    _last_div_year = _sorted_years[-1]
                    _gap = date.today().year - _last_div_year
                    if _gap >= 2:
                        L(
                            f"  ℹ️ 分红连续性: 最近分红 {_consec} 个年度（最近一次 {_last_div_year} 年, 距今 {_gap} 年, 长期未分红）"
                        )
                    else:
                        L(f"  ℹ️ 分红连续性: 近 {_consec} 年有分红（连续性待观察）")
        except Exception as _de:
            _debug_log(f"lng dividend continuity: {_de}")
    else:
        # V17.3.5 修正(报告审查 #363): 若股息率>0 已证实有分红, 绝不输出"一毛不拔"——
        # get_dividend_history 返回空只代表明细接口失败/空窗, 与股息率矛盾时以股息率为准。
        if _show_div_yield and _show_div_yield > 0:
            L(
                "  分红明细获取为空，但股息率显示该股有分红，明细数据可能存在缺口。"
                if div is None
                else "  分红历史明细为空，但股息率显示该股有分红，建议以股息率为准。"
            )
        else:
            # V16.2.3: 区分"接口失败"与"真无分红"（tdx_get_dividend_history 失败返回 None）
            L(
                "  分红数据获取失败（TDX 接口暂不可用），未能确认分红历史。"
                if div is None
                else "  暂无任何分红派息记录 (一毛不拔，纯博弈型或极早期成长型企业，长线防御力弱)。"
            )

    L("\n## 【六、长线筹码沉淀与机构持股倾向】")
    L("---")
    st = await asyncio.to_thread(get_holder_structure, code)
    # V17.0.14: 筹码分布 CYQ —— 提前获取(东财 kline f61 → calculate_cyq), 供章节+评分复用
    _cyq_dict = {}
    try:
        from stock_common.sc_datasource import get_cyq_distribution

        _cyq_dict = await asyncio.to_thread(get_cyq_distribution, code) or {}
    except Exception as _e:
        _debug_log(f"lng cyq ({code}): {_e}")
    if st:
        L(f"  数据来源: 十大流通股东季报（最近 {len(st)} 期）")
        L("")
        _header = (
            f"  {'截止':<12} {'北向':>6}  {'外资':>8}  {'境内机构':>8}  {'个人':>6}  {'Top10':>6}"
        )
        L(_header)
        L(f"  {'-'*60}")
        for p in st:
            _cols = f"  {p['date']:<12} {p['northbound']:>5.1f}%"
            _cols += f"  {p['foreign']:>5.1f}%"
            _cols += f"  {p['domestic']:>5.1f}%"
            _cols += f"  {p['individual']:>5.1f}%"
            _cols += f"  {p['total']:>5.1f}%"
            L(_cols)
        L("")
        _dd = st[0].get("dm_detail", {})
        if _dd:
            _parts = [f"{k} {v:.1f}%" for k, v in _dd.items()]
            L(f"  境内机构细分: {' | '.join(_parts)}")
            _lock = sum(v for v in _dd.values()) + st[0].get("northbound", 0)
            if _lock >= 60:
                L(
                    f"  🔒 筹码锁定度: {_lock:.1f}%（含北向），流通盘高度锁定，稍有题材风口即易拉长阳"
                )
        L("")

        latest = st[0]
        if latest['total'] >= 60:
            L(f"  持股集中度: {latest['total']:.1f}% → 筹码高度集中，机构控盘")
        elif latest['total'] >= 40:
            L(f"  持股集中度: {latest['total']:.1f}% → 筹码适中")
        else:
            L(f"  持股集中度: {latest['total']:.1f}% → 筹码分散，散户化程度高")

        if latest['foreign'] > 30:
            L(
                f"  🔍 外资机构合计持股 {latest['foreign']:.1f}%，话语权极强，关注国际资本动向及汇率风险。"
            )
        if latest['northbound'] > 10:
            L(
                f"  🔍 北向资金持股 {latest['northbound']:.1f}% > 10%，外资通过陆股通深度介入，为重要边际定价力量。"
            )
        if latest['individual'] > 10:
            L(
                f"  🔍 个人大股东合计持股 {latest['individual']:.1f}%，创始人/高管利益深度绑定，与中小股东利益一致。"
            )

        if len(st) >= 2:
            prv = st[-1]
            chg = latest['total'] - prv['total']
            if abs(chg) >= 1:
                _dir = "↑" if chg > 0 else "↓"
                L(
                    f"\n  持股集中度变化: {prv['total']:.1f}% → {latest['total']:.1f}% ({_dir}{abs(chg):.1f}个百分点)"
                )
                if chg > 1:
                    L("    ✅ 筹码趋于集中，主力资金持续吸筹")
                elif chg < -1:
                    L("    ⚠️ 筹码趋于分散，主力可能在出货")
    else:
        L("  机构持股数据获取失败。")

    # V17.0.14: 筹码分布 CYQ 章节(东财 kline f61 → calculate_cyq)
    if _cyq_dict:
        L("\n  ➤ 筹码分布（成本集中度）:")
        _ben = _cyq_dict.get("benefit_pct", 0.0) or 0.0
        _c90 = _cyq_dict.get("concentration_90", 0.0) or 0.0
        _c70 = _cyq_dict.get("concentration_70", 0.0) or 0.0
        _avg = _cyq_dict.get("avg_cost", 0.0) or 0.0
        L(f"    - 获利盘比例: {_ben*100:.1f}%（现价下持仓盈利占比）")
        L(f"    - 平均成本: {_avg:.2f} 元")
        L(
            f"    - 90% 筹码集中度: {_c90:.3f}（成本区间 {_cyq_dict.get('cost_90_low',0):.2f}~{_cyq_dict.get('cost_90_high',0):.2f}）"
        )
        L(
            f"    - 70% 筹码集中度: {_c70:.3f}（成本区间 {_cyq_dict.get('cost_70_low',0):.2f}~{_cyq_dict.get('cost_70_high',0):.2f}）"
        )
        _cflag = (
            "高度集中"
            if _c90 < 0.12
            else ("较集中" if _c90 < 0.2 else ("分散" if _c90 > 0.35 else "中性"))
        )
        _pflag = (
            "获利盘丰厚，长线持有者浮盈较大"
            if _ben > 0.85
            else ("套牢盘较重，长线建仓成本区偏上方" if _ben < 0.25 else "成本结构均衡")
        )
        L(f"    ➤ 研判: 筹码{_cflag}；{_pflag}")

    # ─── V17.0.5: 基金持仓侧证(自选基金清单门控——credentials/fund_watch.json, 缺失零请求) ───
    try:
        from stock_common.sc_fuyao import get_fund_watch_evidence

        _fw = await asyncio.to_thread(get_fund_watch_evidence, code)
    except Exception:
        _fw = None
    if _fw and _fw.get("checked"):
        L("\n  ➤ 自选基金重仓侧证 (fuyao 官方定期披露):")
        if _fw["held"]:
            for _f in _fw["held"]:
                _line = f"    {_f['alias']}: 持仓占比 {_f['hold_ratio']:.2f}%"
                if _f.get("investment_rank"):
                    _line += f" / 第{_f['investment_rank']}大重仓"
                _inc = _f.get("period_increase_rate_pct")
                if _inc is not None:
                    _line += f" / 报告期增减 {_inc:+.2f}%"
                L(_line)
            _f0 = _fw["held"][0]
            L(
                f"    （基金股票仓位 {(_f0.get('fund_stock_pct') or 0):.1f}%"
                + (f"，重仓行业 {_f0['main_industry']}" if _f0.get("main_industry") else "")
                + f"，前十集中度 {(_f0.get('concentration_ratio') or 0):.1f}%）"
            )
        else:
            L("    所列自选基金最新报告期均未重仓本股")
        L("    （持仓来自定期披露非实时；清单维护见 credentials/fund_watch.example.json）")

    L("\n## 【七、达摩克利斯之剑：长周期限售股解禁压力】")
    L("---")
    lockup = await get_lockup_expiry_async(session, code, days=730)
    if lockup:
        total_upcoming = sum(h["shares"] for h in lockup)
        L(f"  ⚠️ 未来 2 年内待解禁总计: {total_upcoming/1e4:.1f} 万股")
        _price = q.get("price", 0) if q else 0
        _fmc = q.get("float_mcap_yi", 1) if q else 1
        for h in lockup:
            # V16.2.3: shares 单位=股；解禁市值(亿) = 股 × 价格 / 1e8
            _jiejin_mc = (h['shares'] * _price / 1e8) if _price > 0 else 0
            _jiejin_pct = _jiejin_mc / _fmc * 100 if _fmc > 0 else 0
            _jiejin_tag = "🔴" if _jiejin_pct > 5 else ("🟡" if _jiejin_pct > 1 else "🟢")
            # V17.0.8: 明细保留一位小数(原 .0f 四舍五入致 1.4万股显示 1 → 明细合计≠总计)
            L(
                f"    - {h['date']}: {h['type']} ({h['shares']/1e4:.1f}万股, 解禁市值{_jiejin_mc:.1f}亿 占流通{_jiejin_pct:.1f}% {_jiejin_tag})"
            )
        L("\n  💡 长线避雷：警惕首发原股东或巨额定向增发的集中解禁潮。")
    else:
        L("  ✅ 未来 2 年内无解禁压力，全流通或结构稳定。")

    L("\n## 【八、战略级别重大公告 (回购/增持/员工持股/年报)】")
    L("---")
    anns = await get_strategic_announcements_async(session, code)
    if anns:
        for i, a in enumerate(anns[:12], 1):
            flag = " ⚠️" if "减持" in a["title"] else ""
            L(f"  {i}. [{a['date']}] {a['title']}{flag}")
        reduce_count = sum(1 for a in anns if "减持" in a["title"])
        if reduce_count > 0:
            L(
                f"\n  ⚠️ 减持预警：近期有 {reduce_count} 条减持相关公告，请仔细甄别是否为实控人/大额减持。"
            )
        L("\n  💡 长线催化：密集的回购、高管真金白银增持，通常是长线底部的明确信号。")
    else:
        L("  近期无过滤后的战略级别重大公告。")

    L("\n## 【九、机构长效共识度与投研透明度】")
    L("---")
    reports = await get_reports_async(session, code, max_pages=5)
    if not reports:
        # V17.0.7: 单次瞬断无重试导致九章整段空转(实测 600519 一次运行
        # "暂无任何研报覆盖数据", 复测同函数返回 200 条)——加一轮轻量重试
        await asyncio.sleep(1.0)
        reports = await get_reports_async(session, code, max_pages=3)
    if reports:
        buy_count, add_count = 0, 0
        org_set = set()
        for r in reports:
            rating = str(r.get("emRatingName", ""))
            org = r.get("orgSName", "")
            if org:
                org_set.add(org)
            if "买入" in rating:
                buy_count += 1
            elif "增持" in rating:
                add_count += 1

        L(f"  统计样本: 近 {len(reports)} 篇研报 | 参与覆盖的独立券商/机构: {len(org_set)} 家")
        L(
            f"  ➤ 研报评级分布: **买入** {buy_count} 篇 / **增持** {add_count} 篇(共 {len(reports)} 篇)"
        )

        _rp = [
            r
            for r in reports
            if str(r.get("publishDate", ""))[:10]
            >= (date.today() - timedelta(days=730)).strftime("%Y-%m-%d")
        ]
        L("\n  最新 10 篇核心研报观点:")
        if not _rp:
            L("  （近2年暂无研报覆盖，机构共识度数据缺失）")
        else:
            L(f"  {'日期':<12} {'机构':<16} {'评级':<10} {'标题'}")
            L(f"  {'-'*70}")
            for r in _rp[:10]:
                pub_date = str(r.get("publishDate", r.get("reportDate", "")))[:10]
                org = r.get("orgSName", r.get("orgName", "")) or "—"
                rating = r.get("emRatingName", r.get("rating", "")) or "—"
                title = r.get("title", r.get("reportTitle", r.get("infoContent", "")))[:50]
                if not title:
                    title = r.get("summary", "")[:50] if r.get("summary") else "无标题"
                L(f"  {pub_date:<12} {org:<16} {str(rating):<10} {title}")
        if len(org_set) > 10:
            L("\n  ✅ 结论：该股受到主流外脑机构的广泛覆盖，基本面透明度高，财务造假阻力大。")
        elif len(org_set) == 0:
            L("  ⚠️ 结论：机构荒漠，散户主导的冷门股，长线重仓需谨慎。")
    else:
        L("  暂无任何研报覆盖数据。")

    # V16.1: 风险引擎（sc_risk）— 事件类风险（解禁/减持/质押）
    try:
        from stock_common.sc_risk import scan_event_risk, combine_risk

        # 解禁（未来 2 年，取最近一批；ratio 用解禁市值/流通市值近似）
        _lk = None
        if lockup:
            _lk0 = lockup[0]
            _lk_price = q.get("price", 0) if q else 0
            _lk_fmc = q.get("float_mcap_yi", 0) if q else 0
            _lk_ratio = 0.0
            if _lk_price > 0 and _lk_fmc > 0:
                # V16.2.3: shares 单位=股；解禁市值(亿) = 股×价格/1e8；占比%
                _lk_ratio = (_lk0.get("shares", 0) * _lk_price / 1e8) / _lk_fmc * 100
            _lk = {"date": str(_lk0.get("date", ""))[:10], "ratio": round(_lk_ratio, 2)}
        # 公告标题（减持/增持关键词）
        _ann_titles = [a.get("title", "") for a in anns] if anns else []
        # 质押资讯命中（东财快讯，最多 1 次请求）
        _pledge_hits = 0
        try:
            from stock_common import get_eastmoney_global_news

            _gn = await asyncio.to_thread(get_eastmoney_global_news, 20)
            for _n in _gn or []:
                _txt = str(_n.get("title", "")) + str(_n.get("summary", ""))
                if "质押" in _txt and code in _txt:
                    _pledge_hits += 1
        except Exception as _pe:
            _debug_log(f"lng pledge scan: {_pe}")

        _event_items = scan_event_risk(
            lockup=_lk, announcement_titles=_ann_titles, pledge_hits=_pledge_hits
        )
        _risk = combine_risk([], _event_items)
        L("\n## 【九之二、风险扫描（解禁/减持/质押）】")
        L("---")
        for _it in _risk["items"]:
            _lv_icon = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(_it["level"], "🟢")
            L(f"  {_lv_icon} {_it['name']}: {_it['text']}")
        for _sig in _risk["signals"]:
            L(f"  {_sig}")
    except Exception as _re:
        _debug_log(f"lng risk engine: {_re}")

    # ── V17.0.27(2026-09-04) DEBT-007: Beta 风险档（契约孤儿字段消费，公理 A5）──
    #   源: 腾讯 qt.gtimg [56]，置信度 **高** —— 887 只 800 日K线自构等权市场代理，
    #   自算 Beta 与 [56] Pearson=0.908。口径声明: 腾讯基准/窗口与自算有偏移，
    #   此为**腾讯口径 Beta 估计值**，非本系统重算（A7 文档代码同真，不可写作"本系统 Beta"）。
    #   为什么放长线报告: Beta 衡量个股相对大盘的系统性波动暴露，是**持仓周期越长越显著**
    #   的风险属性；短线它被日内噪声淹没，长线它决定组合波动与回撤预算 → lng 最合适。
    try:
        _beta = _safe_float(getattr(_cdata, "beta", 0) or 0) if _cdata is not None else 0.0
        if _beta > 0:
            if _beta < 0.8:
                _b_lv, _b_txt = "🟢 低波动防御型", "涨跌幅小于大盘，适合作为压舱底仓"
            elif _beta < 1.0:
                _b_lv, _b_txt = "🟢 偏低波动", "略弱于大盘波动，回撤压力较小"
            elif _beta < 1.2:
                _b_lv, _b_txt = "🟡 与大盘同步", "波动与大盘基本同步，无额外系统性风险"
            elif _beta < 1.5:
                _b_lv, _b_txt = "🟠 高波动进攻型", "放大大盘波动，需相应下调仓位预算"
            else:
                _b_lv, _b_txt = "🔴 极高波动", "显著放大大盘波动（题材/高弹性），回撤风险高"
            L(f"  📐 [Beta风险档] {_beta:.2f} — {_b_lv}；{_b_txt}")
            L("     （腾讯口径 Beta 估计值，非本系统重算；用于仓位与回撤预算参考）")
        else:
            L("  📐 [Beta风险档] N/A（未取到）")
    except Exception as _be:
        _debug_log(f"lng beta risk tier: {_be}")

    # V17.0.7: FTShare 结构化排雷（字典 §12.20——董监高变动/商誉对照，零关键词弱口径）
    try:
        from stock_common import get_ft_ggmx_changes, get_ft_goodwill_stock_detail

        _ggmx_v7 = await asyncio.to_thread(get_ft_ggmx_changes, code) or []
        if _ggmx_v7:
            _cut180 = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
            _recent = [g for g in _ggmx_v7 if str(g.get("change_date", "")) >= _cut180]
            if _recent:
                _dec_n = sum(1 for g in _recent if g.get("change_direction") == "减持")
                _add_n = sum(1 for g in _recent if g.get("change_direction") == "增持")
                L(
                    f"\n  🧾 董监高变动(FTShare 结构化, 近180日): 增持 {_add_n} 笔 / 减持 {_dec_n} 笔"
                )
                for g in sorted(_recent, key=lambda x: str(x.get("change_date", "")), reverse=True)[
                    :3
                ]:
                    try:
                        _shares = float(g.get("change_shares") or 0) / 1e4
                        _avgp = float(g.get("avg_price") or 0)
                        L(
                            f"    - [{g.get('change_date')}] {g.get('changer')}"
                            f"({g.get('relation', '')}/{g.get('position', '')}) "
                            f"{g.get('change_direction')} {_shares:.1f}万股"
                            f" @均价{_avgp:.2f}({g.get('change_reason', '')})"
                        )
                    except (ValueError, TypeError):
                        continue
        _gw_v7 = await asyncio.to_thread(get_ft_goodwill_stock_detail, code) or []
        if _gw_v7:
            g0 = _gw_v7[0]
            _ratio = float(g0.get("goodwill_to_net_assets_ratio") or 0) * 100
            _gw_scale = float(g0.get("goodwill_scale") or 0) / 1e8
            _lv = "🔴" if _ratio > 30 else ("🟡" if _ratio > 10 else "🟢")
            L(
                f"\n  🔬 商誉交叉核验(FTShare): 商誉 {_gw_scale:.2f}亿 | "
                f"商誉/净资产 {_ratio:.1f}% {_lv}"
                f"(公告日 {str(g0.get('notice_date'))[:10]})"
            )
    except Exception as _e:
        _debug_log(f"lng ftshare risk cross: {_e}")

    # ─── 十、舆情与互动 ───
    L("\n## **十、舆情与互动**")

    # 财联社快讯（近2天）
    try:
        cls_news = await asyncio.to_thread(cls_telegraph, 50)
        _cls_shown = 0
        _cls_cutoff = datetime.now() - timedelta(days=2)
        for item in cls_news:
            t_str = str(item.get("time", ""))
            if t_str:
                try:
                    pub_dt = datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S")
                    if pub_dt < _cls_cutoff:
                        continue
                except (ValueError, TypeError):
                    pass
            title = str(item.get("title", "")).strip()
            # V16.2.3: 快讯必须与个股相关（代码/名称/简称），否则跳过
            if title and news_matches_stock(title, code, info.get("name", "")):
                L(f"  · [{t_str[:16]}] {title[:80]}")
                _cls_shown += 1
                if _cls_shown >= 10:
                    break
        if _cls_shown == 0:
            L("  近2天无个股相关财联社快讯")
    except Exception as _e:
        _debug_log(f"lng cls_telegraph: {_e}")

    # 互动易问答（近30天）— V16.2.14: 显示答案 + 标注截取条数（30 天窗口内最新 10 条）
    try:
        irm = await asyncio.to_thread(get_irm_qa, code, 30)
        L("  近30天互动易问答:")
        _irm_shown = 0
        _irm_cutoff = datetime.now() - timedelta(days=30)
        for item in irm:
            t_str = str(item.get("ask_time", ""))
            if t_str:
                try:
                    pub_dt = datetime.strptime(t_str, "%Y-%m-%d %H:%M")
                    if pub_dt < _irm_cutoff:
                        continue
                except (ValueError, TypeError):
                    pass
            q = str(item.get("question", "")).strip()[:120]
            if q:
                # V16.4.1: answer 可能为 None(接口返回 null)——str(None)="None" 曾直接展示
                a = str(item.get("answer") or "").strip()
                _ans = f"答案: {a[:120]}" if a else "答案: （公司待回复）"
                L(f"  · [{t_str[:16]}] 提问: {q}")
                L(f"      {_ans}")
                _irm_shown += 1
                if _irm_shown >= 10:
                    L(f"  （近30天共 {len(irm)} 条中最新 10 条）")
                    break
        if _irm_shown == 0:
            L("  近30天暂无互动易问答")
    except Exception as _e:
        _debug_log(f"lng cninfo_irm: {_e}")

    # V17.3.9: 独立「回购预案与股东权益动作」章节（不再挂在战略公告下）。
    # 数据来自 ZHB tipinfo Col[19]/[20]（field_dict §3 ✅ 定案，TdxW 串池 `回购预案:上限%.2f亿元` 实锤；
    # dict §3.1 标准契约表已登记 tipinfo.hg_date / tipinfo.hg_amount_yi 并标 verified）。
    L("\n## 【十一、回购预案与股东权益动作 (ZHB tipinfo 结构化数据)】")
    L("---")
    _hg_date = (_tip_info or {}).get("hg_date", "")
    _hg_amount = (_tip_info or {}).get("hg_amount_yi", 0) or 0
    if _hg_date or _hg_amount:
        L("  📌 ZHB tipinfo 回购预案 (财报日历结构化数据):")
        if _hg_date:
            L(f"    回购预案公告日: {_hg_date}")
        if _hg_amount:
            L(f"    回购金额上限: {_hg_amount:.2f} 亿元")
        L("  💡 回购预案本质是公司对自身价值的信心票；配合真金白银回购注销可提升每股收益，")
        L("     属长线正向信号。需持续跟踪预案是否落地执行及实际回购进度（部分仅规划未实施）。")
    else:
        L("  ZHB tipinfo 暂无本股回购预案结构化记录（Col[19]/[20] 为空）。")

    L("\n" + "---")
    L("## **仓位管理建议**")
    L("---")

    # V8.2: 使用统一评分接口
    from stock_common import ScoreData, calculate_score

    # 构建评分数据
    score_data = ScoreData(
        code=code,
        name=info.get('name', ''),
        price=price_today,
    )

    # ROE数据
    if ext_roe_data:
        score_data.roe = ext_roe_data[0].get("roe", 0) or 0

    # 前向PE
    if eps_has_data and eps_cur and eps_cur > 0 and price_today > 0:
        score_data.forward_pe = price_today / eps_cur

    # 回撤幅度
    if ext_high_price and price_today > 0 and ext_high_price > 0:
        score_data.drawdown_from_high = (price_today / ext_high_price - 1) * 100

    # 分红数据
    if div and len(div) > 0:
        _bonus = div[0].get("bonus_rmb", 0)
        if price_today > 0:
            score_data.dividend_yield = _bonus / price_today * 100
        score_data.consecutive_dividend_years = len([d for d in div if d.get("bonus_rmb", 0) > 0])

    # 现金流和负债
    if _tdx_ocf != 0 and financials:
        # MEDIUM(审查 2026-08-16): float(None) TypeError——新浪缺键时崩溃, 改 _safe_float
        _np = _safe_float(financials[0].get("净利润", 1)) if financials else 1
        if _np > 0:
            score_data.ocf_ratio = _tdx_ocf / _np
        if bs_data:
            _st = _safe_float(bs_data[0].get("短期借款", "0")) / 1e8
            _lt = _safe_float(bs_data[0].get("长期借款", "0")) / 1e8
            _ta = _safe_float(bs_data[0].get("资产总计", "1")) / 1e8
            if _ta > 0:
                score_data.asset_liability_ratio = (_st + _lt) / _ta

    # M3 修复：复用前文【六、长线筹码沉淀与机构持股倾向】已拉取的股东结构，避免重复网络调用
    _inst = st
    if _inst:
        score_data.institution_holding_pct = _inst[0].get("domestic", 0) + _inst[0].get(
            "northbound", 0
        )

    # V17.0.14: 筹码分布 CYQ(复用前文已拉取的 _cyq_dict, 避免重复网络调用)
    if _cyq_dict:
        score_data.cyq_benefit_pct = _cyq_dict.get("benefit_pct", 0.0) or 0.0
        score_data.cyq_avg_cost = _cyq_dict.get("avg_cost", 0.0) or 0.0
        score_data.cyq_concentration_90 = _cyq_dict.get("concentration_90", 0.0) or 0.0
        score_data.cyq_concentration_70 = _cyq_dict.get("concentration_70", 0.0) or 0.0

    # 计算评分
    # V16.1: 传入 strategy_config.yaml 的 scoring_lng 权重（此前未传 cfg → 用硬编码默认）
    _score_cfg = _load_strategy_config() or {}
    _lng_cfg = {"weights_lng": (_score_cfg.get("scoring_lng") or {}).get("weights_lng", {})}
    result = calculate_score("lng", score_data, _lng_cfg)
    _ps = result.total_score
    _details = result.details

    L(f"  评分明细: {' | '.join(_details[:6])}" if _details else None)
    if _ps >= 70:
        L(f"  长线评分: {_ps:.0f}/100 → 优质长线标的，仓位50%")
    elif _ps >= 45:
        L(f"  长线评分: {_ps:.0f}/100 → 可配置，仓位30%")
    elif _ps >= 20:
        L(f"  长线评分: {_ps:.0f}/100 → 观察仓，仓位15%")
    else:
        L(f"  长线评分: {_ps:.0f}/100 → 暂不建议，等待更好的安全边际")

    # V17.0 R5: 多评委评审团评分渲染统一走 sc_render(原 12 行逐字重复已收敛)
    from stock_common.sc_render import render_multi_school_scores

    multi_scores = render_multi_school_scores(L, score_data)

    # 综合投资建议
    try:
        _consensus = multi_scores['consensus'].total_score
        if _consensus >= 60:
            _rating = "**中性偏乐观** 整体表现良好，建议持续跟踪后分批配置"
        elif _consensus >= 40:
            _rating = "**中性观望** 各项指标均衡，等待更明确信号后再决策"
        else:
            _rating = "**中性偏谨慎** 多项评分偏低，需注意风险控制"
        L(f"  综合投资建议: {_rating}")
    except Exception as _e:
        _debug_log(f"lng multi_school_score error: {_e}")

    L("\n" + "=" * 72)
    L("  长线理想基石（个股未必全具）: 强劲自由现金流 / 持续高 ROE / 合理估值 / 高股息防御")
    L("=" * 72)

    # 累积快照数据（批量结束后统一写入）
    _SNAPSHOT_DATA[code] = {
        "name": info.get('name', ''),
        "total_score": _ps,
        "price": price_today,
        "report_source": "lng",
    }

    # [ENRICH] 数据维度充实（统一层 canonical 字段，零新增取数；异常仅记录不阻断报告）
    try:
        from stock_common.enrich_helpers import (
            long_term_return_lines,
            earnings_quality_lines,
            cash_content_lines,
            quality_gate_lines,
        )

        _enrich = []
        _enrich += long_term_return_lines(cdata)
        _enrich += earnings_quality_lines(cdata)
        _enrich += cash_content_lines(cdata)
        _enrich += quality_gate_lines(cdata)
        if _enrich:
            L("")
            L("## 【补充·数据维度充实（基于统一层字段）】")
            L("---")
            for _ln in _enrich:
                L(_ln)
    except Exception as _e:
        _debug_log(f"lng enrich error: {_e}")

    # V17.0(2026-08-15 C 方案): 全量 md 化——渲染层确定性转换(标题/分隔线/F10 边框表/对齐空格表→md)
    # V17.4.1 吸收层个股信号附录: 新浪研报 + 上证e互动(个股级)
    try:
        from stock_common.sc_market_signals import (
            render_stock_research_section,
            render_stock_einteraction_section,
        )

        for _ms in render_stock_research_section(code):
            L(_ms)
        for _ms in render_stock_einteraction_section(code):
            L(_ms)
    except Exception:
        pass  # 吸收层信号任一源失败不应影响主报告生成
    from stock_common.md_render import render_md_report

    output = render_md_report(output_path, lines)
    return output


# ═══════════════════════════════════════════════════════════════
# V12.4: LngReportRunner — 统一运行框架
# ═══════════════════════════════════════════════════════════════


class LngReportRunner(BaseReportRunner):
    """A股长线价投专属深度体检报告 Runner (V12.4)"""

    def __init__(self):
        super().__init__("get_lng_report", "lng", "A股长线价投专属深度体检报告")

    def execute_pipeline(self) -> dict:
        # V17.0 R4: 批量骨架收敛到基类 execute_batch_pipeline(原 90 行本地实现删除)
        _cached_ind_comp = industry_comparison(20)

        # V17.3.10: 批量预取(与 med/sht 对齐) —— 行情(push2delay ulist) + eltdx 连板天梯,
        # 避免长线报告盘中逐股回退 push2/TDX 取数; 预取走 push2delay 安全域(1rps), 限流安全
        def _prefetch(codes):
            _ret = {}
            try:
                from core.data_provider import prefetch_quote_batch

                _ret = prefetch_quote_batch(list(codes)) or {}
            except Exception:
                pass
            try:
                from core.eltdx_adapter import get_eltdx_shortline_bundle

                get_eltdx_shortline_bundle(list(codes))
            except Exception:
                pass
            return _ret

        return self.execute_batch_pipeline(
            "lng",
            generate_report_async,
            gen_kwargs={"ind_comp": _cached_ind_comp},
            prefetch_fn=_prefetch,
            snapshot_data=_SNAPSHOT_DATA,
        )

    def upload_reports(self, drive, folder_id: str, results) -> None:
        self.upload_multi_reports(drive, folder_id, results)


if __name__ == "__main__":
    runner = LngReportRunner()
    runner.run()
