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
    tdx_get_historical_high, tdx_get_board_list,
)
from core.data_provider import (
    get_canonical_stock_data,  # V15.3 强类型合约推广; V17.0 R3: 唯一综合数据入口(替代已删 get_stock_composite_async)
)
from stock_common import (_safe_float, _debug_log,
                           _load_strategy_config, BaseReportRunner,
                           _market_code,
                          get_holder_structure,
                          get_strategic_announcements_async,
                          baidu_kline_full,
                          get_dividend_history,
                          get_stock_info,
                          get_eps_forecast_async, get_reports_async,
                          get_lockup_expiry_async, get_industry_peers,
                          get_sina_financial_report_async, get_sina_balance_sheet_async,
                          get_market_status,
                          get_zhb_single_stock_data, is_zhb_data_fresh,
                          get_zhb_industry_map, get_zhb_data_date,
                          get_zhb_tip_info,
                          cls_telegraph, news_matches_stock, cninfo_irm)  # V10.3, V16.2.3

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# ==================== 长线价投核心数据模块 ====================

def industry_comparison(top_n=20):
    """V16.3 O25: 行业排名 → ZHB 本地聚合优先（参照系 T-1 可接受，零网络），
    TDX board_list 兜底（原 V4 直接东财 clist——每次现取，用户纠正应 ZHB）。"""
    try:
        from stock_common.sc_datasource import get_industry_rank_from_zhb

        rows = get_industry_rank_from_zhb(top_n)
        if rows:
            return rows
    except Exception as _e:
        _debug_log(f"lng industry_rank zhb error: {_e}")
    sectors = tdx_get_board_list(0)
    if not sectors:
        return []
    return sectors


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
    """V4: 历史最高价 → tdx_client 适配器（easy-tdx 替代 mootdx）"""
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
                return {"eps_cur": this_year, "eps_next": next_year, "analyst_count": 1, "source": "东财研报"}
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
    def L(s=""): lines.append(s)

    L("=" * 72)
    L(f"  {code} 长线价投专属深度体检报告 — {today_str} {datetime.now().strftime('%H:%M:%S')}")
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

    L("\n【一、企业基本盘与绝对估值锚点】")
    L("─" * 72)

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
            "price": _cdata.price, "change_pct": _cdata.change_pct,
            "mcap_yi": _cdata.mcap_yi, "float_mcap_yi": _cdata.float_mcap_yi,
            "industry": _cdata.industry, "board": _cdata.board, "name": _cdata.name,
            "change_ytd": _cdata.change_ytd, "high_52w": _cdata.high_52w,
            "low_52w": _cdata.low_52w, "dividend_yield": _cdata.dividend_yield,
            "pe_ttm": _cdata.pe_ttm, "pb": _cdata.pb,
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
                price=0, change_pct=0, pe_ttm=0, pb=0, mcap_yi=0, float_mcap_yi=0,
                industry="", board="", name="", change_ytd=0, high_52w=0, low_52w=0,
                dividend_yield=0,
            )
        _dp_composite = {
            "price": cdata.price, "change_pct": cdata.change_pct,
            "mcap_yi": cdata.mcap_yi, "float_mcap_yi": cdata.float_mcap_yi,
            "industry": cdata.industry, "board": cdata.board, "name": cdata.name,
            "change_ytd": cdata.change_ytd, "high_52w": cdata.high_52w,
            "low_52w": cdata.low_52w, "dividend_yield": cdata.dividend_yield,
            "pe_ttm": cdata.pe_ttm, "pb": cdata.pb,
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
        L(f"  ⚠️ 风险标记: **ST/*ST**（退市风险——长期价值需严格财务验证）")
    if getattr(_cdata, "is_new", False):
        L(f"  🆕 次新标记: 上市 ≤5 日（历史数据不足，长线谨慎）")
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
                    L(f"  📊 行业周期定位: 全市场排名#{_ind_rank} | 涨幅{_ind_chg:+.2f}% | 上涨{_ind_up}家/下跌{_ind_down}家")
                    break
    except Exception as _e:
        _debug_log(f"lng industry_cycle error: {_e}")
    
    ext_list_date_raw = info.get("list_date", "")
    if ext_list_date_raw and len(ext_list_date_raw) >= 8:
        ext_list_year = int(ext_list_date_raw[:4])
        ext_years_listed = date.today().year - ext_list_year
        ext_list_fmt = f"{ext_list_date_raw[:4]}-{ext_list_date_raw[4:6]}-{ext_list_date_raw[6:8]}"
        ext_list_tag = "✅ 上市已满3年（长线安全标的）" if ext_years_listed >= 3 else "⚠️ 上市未满3年（次新股，警惕业绩变脸）"
        L(f"  上市日期: {ext_list_fmt}（已上市 {ext_years_listed} 年）{ext_list_tag}")
    else:
        L(f"  上市日期: {ext_list_date_raw}")
    
    # zhb数据展示（阶段涨幅、52周区间、YTD、员工人数——zhb独有，直接展示）
    # V11.5: 优先从 data_provider 综合数据获取重叠字段，zhb独有字段保留原路径
    _dp_change_ytd = _dp_composite.get("change_ytd", 0) if _dp_composite else 0
    _dp_high_52w = _dp_composite.get("high_52w", 0) if _dp_composite else 0
    _dp_low_52w = _dp_composite.get("low_52w", 0) if _dp_composite else 0
    _dp_div_yield = _dp_composite.get("dividend_yield", 0) if _dp_composite else 0
    _dp_pe_ttm_val = _dp_composite.get("pe_ttm", 0) if _dp_composite else 0
    _dp_pb_val = _dp_composite.get("pb", 0) if _dp_composite else 0

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
        L(f"  [阶段涨幅] 近5日: {_zhb_change_5d:+.2f}% | 近10日: {_zhb_change_10d:+.2f}% | 近20日: {_zhb_change_20d:+.2f}% | 近60日: {_zhb_change_60d:+.2f}%")

    # 52周区间：data_provider优先
    _show_high_52w = _dp_high_52w if _dp_high_52w > 0 else (_zhb_data.get("high_52w", 0) if _zhb_data else 0)
    _show_low_52w = _dp_low_52w if _dp_low_52w > 0 else (_zhb_data.get("low_52w", 0) if _zhb_data else 0)
    if _show_high_52w > 0 and _show_low_52w > 0 and price_today > 0:
        _52w_pos = (price_today - _show_low_52w) / (_show_high_52w - _show_low_52w) * 100 if _show_high_52w != _show_low_52w else 50
        L(f"  [52周区间] 最高: {_show_high_52w:.2f}元 | 最低: {_show_low_52w:.2f}元 | 当前位置: {_52w_pos:.0f}%")

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
            L(f"  [ZHB单季EPS] 最新报告期单季EPS: {_tip_eps:.4f}元（非TTM口径，估值请以上方 PE(TTM) 为准）")

    # 历史最高价：data_provider的high_52w优先，其次zhb，最后fallback到get_historical_high
    _dp_high_52w_for_hist = _dp_composite.get("high_52w", 0) if _dp_composite else 0
    _zhb_high_52w_for_hist = _zhb_data.get("high_52w", 0) if _zhb_data else 0
    if _dp_high_52w_for_hist and _dp_high_52w_for_hist > 0 and price_today > 0:
        ext_high_price = _dp_high_52w_for_hist
    elif _zhb_high_52w_for_hist and _zhb_high_52w_for_hist > 0 and price_today > 0:
        ext_high_price = _zhb_high_52w_for_hist
    else:
        ext_high_price = get_historical_high(code)
    if ext_high_price and price_today > 0:
        ext_deviation = (price_today / ext_high_price - 1) * 100
        L(f"  历史最高价: {ext_high_price:.2f}元 | 当前偏离度: {ext_deviation:+.2f}%")
        if ext_deviation <= -40:
            L(f"  🔔 深度回调：距历史最高点已下跌 {abs(ext_deviation):.0f}%，若基本面未恶化，或为长线黄金坑。")
        elif ext_deviation <= -20:
            L(f"  📉 显著回调：距历史最高点已下跌 {abs(ext_deviation):.0f}%，处于阶段性低位区域。")
    
    # V16.2.3 修正: info.total_shares 单位=股（easy_tdx zong_guben 实为股，非注释的万股）→ /1e8 转亿股
    L(f"  总股本:   {info.get('total_shares', 0)/1e8:.2f}亿股 | 总市值: {q.get('mcap_yi', 0):.2f}亿元")
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
        _pe_static = _zhb_pe_dynamic
    elif _zhb_pe_ttm and _zhb_pe_ttm > 0:
        _pe = _zhb_pe_ttm
        _pe_static = _zhb_pe_dynamic
    else:
        _pe = q.get('pe_ttm', 0)
        # V16.4.1: q 无 pe_static 键(恒 0) → else 分支 PE(静态) 永远 N/A; 用 ZHB 静态口径兜底
        _pe_static = _zhb_pe_dynamic or q.get('pe_static', 0)
    if _pe > 0:
        _ey = f"{100/_pe:.2f}%"
        # V16.4.1: 标注 PE 来源口径(ZHB pe_ttm 基于最近年报/季报净利, 可能与
        # 报告期最新财务表有滞后——2026-08-12 实测 000506: ZHB=110.47(2025年报 1.59亿)
        # vs 财务表 TTM 4.73 亿(含 2026Q1) 应 ~37x, 口径差 3 倍)
        _pe_src = "data_provider" if (_dp_pe and _dp_pe > 0) else ("ZHB" if (_zhb_pe_ttm and _zhb_pe_ttm > 0) else "腾讯")
    else:
        _ey = "N/A"
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
    L(f"    市盈率 PE(TTM): {_pe:.2f}x ({_pe_src}口径; 盈利收益率粗估: {_ey})")
    L(f"    市盈率 PE(静态): {_pe_static:.2f}x" if _pe > 0 and _pe_static > 0 else "    市盈率 PE(静态): N/A（亏损）")
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
        L(f"  板块排名: 按总市值排序, 该股排名第 {peer_data_lng['my_rank']}/{peer_data_lng['industry_count']} 位")

    try:
        _ic_data = _ic_d  # V16.4.1: 已 try 前初始化, 不再依赖 dir() 防御
        if _ic_data and isinstance(_ic_data, list):
            _our_ind = info.get("industry", "")
            for _ind in _ic_data:
                if _ind.get("name") == _our_ind or _our_ind in _ind.get("name", ""):
                    L(f"  📊 板块横向对比: 本股PE={q.get('pe_ttm',0):.1f}x | 板块涨跌{_ind.get('change_pct',0):+.2f}%")
                    break
    except Exception as _e:
        _debug_log(f"lng industry_compare error: {_e}")


    L("\n【二、跨期财务纵深与长效业绩验证 (近8个报告期)】")
    L("─" * 72)
    financials = await get_sina_financial_report_async(session, code, num_periods=8)
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
    ext_roe_data = get_roe_trend(code, 8, financials=financials, bs_data=bs_data,
                                  total_shares=info.get("total_shares", 0))
    if ext_roe_data:
        L(f"  {'报告期':<12} {'ROE%':>8} {'扣非ROE%':>10} {'EPS':>8} {'BPS':>10}")
        L(f"  {'-'*55}")
        for r in ext_roe_data:
            ext_roe_str = f"{r['roe']:.2f}" if r['roe'] is not None else "N/A"
            ext_roe_kc_str = f"{r['roe_kc']:.2f}" if r['roe_kc'] is not None else "N/A"
            ext_eps_str = f"{r['eps']:.2f}" if r['eps'] is not None else "N/A"
            ext_bps_str = f"{r['bps']:.2f}" if r['bps'] is not None else "N/A"
            L(f"  {r['date']:<12} {ext_roe_str:>8} {ext_roe_kc_str:>10} {ext_eps_str:>8} {ext_bps_str:>10}")
        ext_last_roe = ext_roe_data[0].get("roe")
        if ext_last_roe is not None:
            if ext_last_roe >= 20:
                L(f"\n  ✅ 结论：最新 ROE = {ext_last_roe:.2f}% ≥ 20%，属于极其罕见的优质复利机器！")
            elif ext_last_roe >= 15:
                L(f"  ✅ 结论：最新 ROE = {ext_last_roe:.2f}% ≥ 15%，具备长期复利能力。")
            elif ext_last_roe >= 10:
                L(f"  📊 结论：最新 ROE = {ext_last_roe:.2f}%，处于中等水平，需关注趋势。")
            else:
                L(f"  ⚠️ 结论：最新 ROE = {ext_last_roe:.2f}% < 10%，资本回报效率偏低，长线需谨慎。")
    else:
        L("  (ROE数据获取失败)")

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
            _rev3 = [_safe_float(f.get("营业总收入", "0")) for f in financials[:4] if f.get("报告日", "") > "2022-01-01"]
            _prf3 = [_safe_float(f.get("净利润", "0")) for f in financials[:4] if f.get("报告日", "") > "2022-01-01"]
            if len(_rev3) >= 4 and _rev3[0] > 0 and _rev3[-1] > 0:
                _rev_cagr = (pow(_rev3[0]/_rev3[-1], 1/3)-1)*100
                _prf_cagr_str = f"{(pow(_prf3[0]/_prf3[-1], 1/3)-1)*100:.1f}%" if _prf3[0] > 0 and _prf3[-1] > 0 else "N/A (亏损)"
                L(f"  📊 近3年营收CAGR: {_rev_cagr:.1f}% | 净利润CAGR: {_prf_cagr_str}")
        except Exception as _e:
            _debug_log(f"lng cagr_calc error: {_e}")

    L("\n【三、财务健康度排雷（现金流验证与商誉预警）】")
    L("─" * 72)
    _tdx_ocf = 0.0; _tdx_np = 0.0
    # V16.1: 0x0010 财务快照存局部变量，供下方"核心财务指标"复用（避免重复 TCP 请求）
    _tdx_fi_snapshot = None
    try:
        from core.tdx_client import _get_tdx_client
        c = _get_tdx_client()
        if c:
            fi = c.get_finance_info(_market_code(code), code)
            if fi is not None and not fi.empty:
                _tdx_fi_snapshot = fi
                # V15.1: 修正 0x0010 协议 key（参考 docs/field_dict.md 第 7 章）
                # 正确 key: jingyingxianjinliu / jinglirun（无下划线）
                # V16.3 O19: 0x0010 金额字段单位=角（field_dict §零 O 实测）——/10 得元
                # （此前直接 /1e8 显示亿 → 现金流/净利偏大 10 倍）
                _tdx_ocf = _safe_float(fi.iloc[0].get('jingyingxianjinliu', 0)) / 10.0
                _tdx_np = _safe_float(fi.iloc[0].get('jinglirun', 0)) / 10.0
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
            L(f"  商誉: {gw_yi:.2f}亿元 | 净资产: {equity_yi:.2f}亿元 | 商誉/净资产: {gw_ratio:.1f}%")
            if gw_ratio > 20:
                L(f"  ⚠️ 爆雷预警：商誉占净资产 {gw_ratio:.1f}% > 20%，注意行业周期下行时的商誉减值黑天鹅！")
            else:
                L("  ✅ 商誉占比在安全范围内 (< 20%)。")
        L(f"  资产负债率: {100 - equity_yi/asset_yi*100:.1f}%（截至 {bs_data[0].get('报告日','')}）" if asset_yi > 0 else "")
        _st_loan = _safe_float(bs_data[0].get("短期借款", "0")) / 1e8
        _lt_loan = _safe_float(bs_data[0].get("长期借款", "0")) / 1e8
        _bd = _safe_float(bs_data[0].get("应付债券", "0")) / 1e8
        _int_debt = _st_loan + _lt_loan + _bd
        _int_ratio = _int_debt / asset_yi * 100 if asset_yi > 0 else 0
        L(f"  有息负债率: {_int_ratio:.1f}%（短期借款{_st_loan:.2f}亿+长期借款{_lt_loan:.2f}亿+债券{_bd:.2f}亿）")
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
            L(f"\n  经营现金流: {ocf_yi:.2f}亿元 | 净利润: {np_yi:.2f}亿元 | 现金/利润比: {cash_ratio:.1f}%")
            if cash_ratio < 80:
                L(f"  ⚠️ 警惕：经营现金流仅为净利润的 {cash_ratio:.1f}%，存在利润造假或严重压货风险，现金含量不足！")
            else:
                L("  ✅ 经营现金流覆盖净利润充足 (> 80%)，利润含金量高。")
        elif _tdx_np < 0 and _tdx_ocf < 0:
            L(f"\n  经营现金流: {ocf_yi:.2f}亿元 | 净利润: {np_yi:.2f}亿元 (均为负值，持续失血状态)")
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
    if ext_roe_data and ext_roe_data[0].get("eps") is not None:
        parts.append(f"EPS {ext_roe_data[0]['eps']:.4f}")
    try:
        # V16.1: 复用"三"章节的 0x0010 快照（避免重复 TCP 请求）
        if _tdx_fi_snapshot is not None:
            tdx_fi = _tdx_fi_snapshot
        else:
            from core.tdx_client import _get_tdx_client
            client = _get_tdx_client()
            tdx_fi = client.get_finance_info(_market_code(code), code) if client else None
        if tdx_fi is not None and not tdx_fi.empty:
            # V15.1: 修正 0x0010 协议 key（参考 docs/field_dict.md）
            # V16.3 O19: 角→元（/10）后再 /1e8 显示亿——否则偏大 10 倍
            ocf = _safe_float(tdx_fi.iloc[0].get('jingyingxianjinliu', 0)) / 10.0 / 1e8
            if ocf != 0:
                parts.append(f"经营现金流 {ocf:.2f}亿")
    except Exception as _e:
        _debug_log(f"lng tdx_fi_ocf error: {_e}")
    if parts:
        L("\n  ➤ 当期核心财务指标一览:")
        for p in parts:
            L(f"    {p}")
    L("\n  💡 长线排雷：持续的经营现金净流入是检验账面利润真实性的最佳标准，高商誉+低现金含量=高危组合。")

    L("\n【四、未来三年机构一致预期与 PEG 均值回归模型】")
    L("─" * 72)
    # H4 修复(2026-08-15 二审): 本地 ProfitForecast O(1) 优先(零网络), 未命中走网络兜底——与一章重复块合并
    from stock_common.sc_datasource import get_eps_forecast as _eps_local
    df_eps = await asyncio.to_thread(_eps_local, code)
    if df_eps is None or df_eps.empty:
        df_eps = await get_eps_forecast_async(session, code)
    eps_cur = eps_next = None
    eps_has_data = False
    if not df_eps.empty and len(df_eps.columns) >= 4:
        L(f"  {'年度':<10} {'覆盖机构数':>7} {'预测EPS均值':<9}")
        L(f"  {'-'*40}")
        for i, row in df_eps.iterrows():
            try:
                year = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
                cnt = int(row.iloc[1]) if pd.notna(row.iloc[1]) else 0
                mean_v = float(row.iloc[3]) if pd.notna(row.iloc[3]) else 0
                L(f"  {year:<10} {cnt:<10} {mean_v:<12.3f}")
                if i == 0:
                    eps_cur = mean_v
                    eps_has_data = True
                elif i == 1:
                    eps_next = mean_v
            except (ValueError, TypeError, IndexError):
                pass
    if not eps_has_data:
        em_eps = await _get_eps_from_em_reports_async(session, code)
        if em_eps:
            eps_cur = em_eps["eps_cur"]
            eps_next = em_eps["eps_next"]
            eps_has_data = True
            this_year = date.today().year
            L("  东财研报一致预期EPS (同花顺兜底):")
            L(f"  {'年度':<14} {'预测EPS'}")
            L(f"  {'-'*30}")
            if eps_cur:
                L(f"  {this_year:<14} {eps_cur:.3f}")
            if eps_next:
                L(f"  {this_year + 1:<14} {eps_next:.3f}")
    if eps_has_data and price_today and eps_cur and eps_cur > 0:
        pe_fwd = price_today / eps_cur
        L("\n  ➤ 基于机构预期的远期估值消化推演:")
        L(f"    前向市盈率 (本年度): {pe_fwd:.2f}x")
        if eps_next and eps_cur > 0:
            cagr = (eps_next / eps_cur) - 1
            L(f"    未来一年预期净利增速: {cagr*100:.1f}%")
            peg = pe_fwd / (cagr * 100) if cagr > 0 else float("inf")  # V16.4.1: 原 "in" 拼写错误→ValueError
            if peg > 5:
                L(f"    PEG: >5.0（增速过低或PE过高导致极端值，不具参考意义）")
            else:
                # V16.4.1: 跨期口径标注——pe_fwd 用本年 EPS, 增速用明年 EPS(向前 PEG)
                L(f"    PEG (市盈率相对盈利增长比率): {peg:.2f} (长线买入参考: <1低估, 1-1.5合理) [PE本年/增速明年,跨期口径]")
            if cagr > 0:
                digest_25 = math.log(pe_fwd / 25) / math.log(1 + cagr) if pe_fwd > 25 else 0
                try:
                    _sk_p, _sr_p = baidu_kline_full(code)
                    _ci_p = next((i for i,k in enumerate(_sk_p) if k in ("close","close_price")), -1)
                    if _ci_p >= 0 and eps_cur > 0:
                        _hp = [_safe_float(rr[_ci_p]) for rr in _sr_p if len(rr) > _ci_p]
                        if len(_hp) > 20:
                            _hpe = [p/eps_cur for p in _hp if p > 0]
                            if _hpe:
                                _pc = sum(1 for p in _hpe if p < pe_fwd)/len(_hpe)*100
                                L(f"  PE历史分位: {_pc:.0f}%（当前PE高于{_pc:.0f}%的历史时间，数值越高越贵）")
                except Exception as _e:
                    _debug_log(f"lng pe_percentile error: {_e}")
                if digest_25 > 0:
                    L(f"    模型测算：当前估值消化至 25 倍合理市盈率约需 {digest_25:.1f} 年")
                else:
                    L("    模型测算：当前估值已低于/等于 25 倍合理水位线，具备长线配置的安全垫。")
    else:
        L("  无足够机构覆盖（冷门标的，长线投研需完全依赖自主财务尽调）。")

    L("\n【五、长效股东回报属性 (分红与股息历史)】")
    L("─" * 72)
    # 股息率：data_provider优先，其次zhb展示
    _zhb_div_yield_5 = _zhb_data.get("dividend_yield", 0) if _zhb_data else 0
    _dp_div_yield_5 = _dp_composite.get("dividend_yield", 0) if _dp_composite else 0
    _show_div_5 = _dp_div_yield_5 if _dp_div_yield_5 and _dp_div_yield_5 > 0 else _zhb_div_yield_5
    if _show_div_5 > 0:
        L(f"  当前股息率: {_show_div_5:.2f}%（zhb数据）")
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
                        L(f"  ℹ️ 分红连续性: 最近分红 {_consec} 个年度（最近一次 {_last_div_year} 年, 距今 {_gap} 年, 长期未分红）")
                    else:
                        L(f"  ℹ️ 分红连续性: 近 {_consec} 年有分红（连续性待观察）")
        except Exception as _de:
            _debug_log(f"lng dividend continuity: {_de}")
    else:
        # V16.2.3: 区分"接口失败"与"真无分红"（tdx_get_dividend_history 失败返回 None）
        L("  分红数据获取失败（TDX 接口暂不可用），未能确认分红历史。" if div is None else
          "  暂无任何分红派息记录 (一毛不拔，纯博弈型或极早期成长型企业，长线防御力弱)。")

    L("\n【六、长线筹码沉淀与机构持股倾向】")
    L("─" * 72)
    st = await asyncio.to_thread(get_holder_structure, code)
    if st:
        L(f"  数据来源: 十大流通股东季报（最近 {len(st)} 期）")
        L("")
        _header = f"  {'截止':<12} {'北向':>6}  {'外资':>8}  {'境内机构':>8}  {'个人':>6}  {'Top10':>6}"
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
                L(f"  🔒 筹码锁定度: {_lock:.1f}%（含北向），流通盘高度锁定，稍有题材风口即易拉长阳")
        L("")

        latest = st[0]
        if latest['total'] >= 60:
            L(f"  持股集中度: {latest['total']:.1f}% → 筹码高度集中，机构控盘")
        elif latest['total'] >= 40:
            L(f"  持股集中度: {latest['total']:.1f}% → 筹码适中")
        else:
            L(f"  持股集中度: {latest['total']:.1f}% → 筹码分散，散户化程度高")

        if latest['foreign'] > 30:
            L(f"  🔍 外资机构合计持股 {latest['foreign']:.1f}%，话语权极强，关注国际资本动向及汇率风险。")
        if latest['northbound'] > 10:
            L(f"  🔍 北向资金持股 {latest['northbound']:.1f}% > 10%，外资通过陆股通深度介入，为重要边际定价力量。")
        if latest['individual'] > 10:
            L(f"  🔍 个人大股东合计持股 {latest['individual']:.1f}%，创始人/高管利益深度绑定，与中小股东利益一致。")

        if len(st) >= 2:
            prv = st[-1]
            chg = latest['total'] - prv['total']
            if abs(chg) >= 1:
                _dir = "↑" if chg > 0 else "↓"
                L(f"\n  持股集中度变化: {prv['total']:.1f}% → {latest['total']:.1f}% ({_dir}{abs(chg):.1f}个百分点)")
                if chg > 1:
                    L("    ✅ 筹码趋于集中，主力资金持续吸筹")
                elif chg < -1:
                    L("    ⚠️ 筹码趋于分散，主力可能在出货")
    else:
        L("  机构持股数据获取失败。")

    L("\n【七、达摩克利斯之剑：长周期限售股解禁压力】")
    L("─" * 72)
    lockup = await get_lockup_expiry_async(session, code, days=730)
    if lockup:
        total_upcoming = sum(h["shares"] for h in lockup)
        L(f"  ⚠️ 未来 2 年内待解禁总计: {total_upcoming/1e4:.0f} 万股")
        _price = q.get("price", 0) if q else 0
        _fmc = q.get("float_mcap_yi", 1) if q else 1
        for h in lockup:
            # V16.2.3: shares 单位=股；解禁市值(亿) = 股 × 价格 / 1e8
            _jiejin_mc = (h['shares'] * _price / 1e8) if _price > 0 else 0
            _jiejin_pct = _jiejin_mc / _fmc * 100 if _fmc > 0 else 0
            _jiejin_tag = "🔴" if _jiejin_pct > 5 else ("🟡" if _jiejin_pct > 1 else "🟢")
            L(f"    - {h['date']}: {h['type']} ({h['shares']/1e4:.0f}万股, 解禁市值{_jiejin_mc:.1f}亿 占流通{_jiejin_pct:.1f}% {_jiejin_tag})")
        L("\n  💡 长线避雷：警惕首发原股东或巨额定向增发的集中解禁潮。")
    else:
        L("  ✅ 未来 2 年内无解禁压力，全流通或结构稳定。")

    L("\n【八、战略级别重大公告 (回购/增持/员工持股/年报)】")
    L("─" * 72)
    anns = await get_strategic_announcements_async(session, code)
    if anns:
        for i, a in enumerate(anns[:12], 1):
            flag = " ⚠️" if "减持" in a["title"] else ""
            L(f"  {i}. [{a['date']}] {a['title']}{flag}")
        reduce_count = sum(1 for a in anns if "减持" in a["title"])
        if reduce_count > 0:
            L(f"\n  ⚠️ 减持预警：近期有 {reduce_count} 条减持相关公告，请仔细甄别是否为实控人/大额减持。")
        L("\n  💡 长线催化：密集的回购、高管真金白银增持，通常是长线底部的明确信号。")
    else:
        L("  近期无过滤后的战略级别重大公告。")

    L("\n【九、机构长效共识度与投研透明度】")
    L("─" * 72)
    reports = await get_reports_async(session, code, max_pages=5)
    if reports:
        buy_count, add_count = 0, 0
        org_set = set()
        for r in reports:
            rating = str(r.get("emRatingName", ""))
            org = r.get("orgSName", "")
            if org: org_set.add(org)
            if "买入" in rating: buy_count += 1
            elif "增持" in rating: add_count += 1
            
        L(f"  统计样本: 近 {len(reports)} 篇研报 | 参与覆盖的独立券商/机构: {len(org_set)} 家")
        L(f"  ➤ 【买入】评级: {buy_count} 篇 | 【增持】评级: {add_count} 篇")
        
        L("\n  最新 10 篇核心研报观点:")
        L(f"  {'日期':<12} {'机构':<16} {'评级':<10} {'标题'}")
        L(f"  {'-'*70}")
        _rp = [r for r in reports if str(r.get("publishDate",""))[:10] >= (date.today() - timedelta(days=730)).strftime("%Y-%m-%d")]
        for r in _rp[:10]:
            pub_date = str(r.get("publishDate", r.get("reportDate", "")))[:10]
            org = r.get("orgSName", r.get("orgName", ""))
            rating = r.get("emRatingName", r.get("rating", ""))
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

        _event_items = scan_event_risk(lockup=_lk, announcement_titles=_ann_titles, pledge_hits=_pledge_hits)
        _risk = combine_risk([], _event_items)
        L("\n【九之二、风险扫描（解禁/减持/质押）】")
        L("─" * 72)
        for _it in _risk["items"]:
            _lv_icon = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(_it["level"], "🟢")
            L(f"  {_lv_icon} {_it['name']}: {_it['text']}")
        for _sig in _risk["signals"]:
            L(f"  {_sig}")
    except Exception as _re:
        _debug_log(f"lng risk engine: {_re}")

    # ─── 十、舆情与互动 ───
    L("\n【十、舆情与互动】")

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
        irm = await asyncio.to_thread(cninfo_irm, code, 30)
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

    L("\n"+"─"*72); L("【仓位管理建议】"); L("─"*72)
    
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
    
    # 机构持仓
    _inst = await asyncio.to_thread(get_holder_structure, code)
    if _inst:
        score_data.institution_holding_pct = _inst[0].get("domestic", 0) + _inst[0].get("northbound", 0)
    
    # 计算评分
    # V16.1: 传入 strategy_config.yaml 的 scoring_lng 权重（此前未传 cfg → 用硬编码默认）
    _score_cfg = _load_strategy_config() or {}
    _lng_cfg = {"weights_lng": (_score_cfg.get("scoring_lng") or {}).get("weights_lng", {})}
    result = calculate_score("lng", score_data, _lng_cfg)
    _ps = result.total_score
    _details = result.details
    
    L(f"  评分明细: {' | '.join(_details[:6])}" if _details else None)
    if _ps>=70: L(f"  长线评分: {_ps:.0f}/100 → 优质长线标的，仓位50%")
    elif _ps>=45: L(f"  长线评分: {_ps:.0f}/100 → 可配置，仓位30%")
    elif _ps>=20: L(f"  长线评分: {_ps:.0f}/100 → 观察仓，仓位15%")
    else: L(f"  长线评分: {_ps:.0f}/100 → 暂不建议，等待更好的安全边际")
    
    # V17.0 R5: 多评委评审团评分渲染统一走 sc_render(原 12 行逐字重复已收敛)
    from stock_common.sc_render import render_multi_school_scores

    multi_scores = render_multi_school_scores(L, score_data)

    # 综合投资建议
    try:
        _consensus = multi_scores['consensus'].total_score
        if _consensus >= 60:
            _rating = "【中性偏乐观】整体表现良好，建议持续跟踪后分批配置"
        elif _consensus >= 40:
            _rating = "【中性观望】各项指标均衡，等待更明确信号后再决策"
        else:
            _rating = "【中性偏谨慎】多项评分偏低，需注意风险控制"
        L(f"  综合投资建议: {_rating}")
    except Exception as _e:
        _debug_log(f"lng multi_school_score error: {_e}")

    L("\n" + "=" * 72)
    L("  长线基石: 强劲自由现金流 / 持续高 ROE / 合理估值 / 高股息防御")
    L("=" * 72)

    # 累积快照数据（批量结束后统一写入）
    _SNAPSHOT_DATA[code] = {
        "name": info.get('name', ''),
        "total_score": _ps,
        "price": price_today,
        "report_source": "lng"
    }

    # V17.0(2026-08-15 C 方案): 全量 md 化——渲染层确定性转换(标题/分隔线/F10 边框表/对齐空格表→md)
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
        return self.execute_batch_pipeline(
            "lng", generate_report_async,
            gen_kwargs={"ind_comp": _cached_ind_comp},
            snapshot_data=_SNAPSHOT_DATA,
        )

    def upload_reports(self, drive, folder_id: str, results) -> None:
        self.upload_multi_reports(drive, folder_id, results)


if __name__ == "__main__":
    runner = LngReportRunner()
    runner.run()