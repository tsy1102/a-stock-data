#!/usr/bin/env python3

"""get_sht_report.py — A股短线个股深度数据报告

版本信息:
    V15.2  2026-07-28 - V15.2 P0 崩溃修复：修复 get_canonical_stock_data 中 board 变量 UnboundLocalError；GD 上传 stdout 缓冲修复
    V15.1  2026-07-26 - V15.1 全局 ZHB 旁路普及：阶段涨跌幅与概念板块优先走 ZHB 本地内存解析，大幅提升运行速度
    V15.0  2026-07-26 - 接入 CanonicalStockData 强类型数据合约，实施基于真实周期的 ZHB-First 离线优先路由
    V14.0  2026-07-22 - 文档同步：docstring 版本信息更新到 V14.0；is_workday() Bug 修复由 stock_common 上游提供
    V13.x  2026-07-22 - 受益于 stock_cache.py dataclass 透明序列化（脚本无改动）
    V12.6  2026-07-22 - 受益于字段路由简化（移除估值字段 HTTP fallback）
    V12.4  2026-07-22 - 抽象 BaseReportRunner 基类
    V9.5   2026-07-11 - 基础设施修复：aiohttp原生异步迁移、静默异常日志化（脚本本身无改动，受益于底层修复）
    V9.3.3 2026-07-11 - 资金流函数复用 ff_120d 参数避免重复调用；休市提示文案统一
    V9.3.2 2026-07-09 - 基础设施修复：TDX K线假数据防护、SQLite WAL死锁修复、代理环境兼容（脚本本身无改动，受益于底层修复）
    V9.3   2026-07-07 - 盘前行情模式：9:30前使用上一交易日日K线数据；盘前提示文本；删除报告标题硬编码版本号
    V9.2   2026-07-05 - 异常处理规范化；缓存交叉验证机制启用
    V9.1   2026-07-04 - F10 全覆盖：新增**异动与风险提示**章节+数据质量附录；修复资金流渲染 float/dict 兼容
    V9.0   2026-07-02 - 舆情互动层（Layer 10）；上市日期 push2 fallback；valid_if 校验；_has_zero_price 拦截
    V8.8   2026-06-25 - GD上传逻辑统一化 & 快照格式升级（TXT+自动上传）
    V8.7   2026-06-25 - 死代码清理：同步版替换为薄包装
    V8.5   2026-06-22 - 新增多档分析深度(--depth lite/medium/deep)、席位增强分析
    V8.4   2026-06-22 - 统一缓存层+异步函数族
    V8.3   2026-06-18 - 细节修复
    V8.2   2026-06-18 - 席位参数优化
    V8.1   2026-06-18 - 统一评分接口+快照功能
    V8.0   2026-06-17 - 初始版本
"""

# V16.4.1: 强制 UTF-8 输出（下沉到代码自身——任何 agent/机器/直接运行均 UTF-8，
# 不再依赖 main.py 注入的 PYTHONIOENCODING 环境变量）
from stock_common.env_setup import ensure_utf8_stdio

ensure_utf8_stdio()


import asyncio

from datetime import date, datetime, timedelta

# V15.3 修复: 4 个报告模块同名 _SNAPSHOT_DATA 全局变量冲突
# 抽出到 stock_common.sc_snapshot 统一管理（sc_report_runner 也用此模块）
# V15.3.1: 直接 import 共享的 SnapshotProxy 类，删除 20 行重复定义
from stock_common.sc_snapshot import SnapshotProxy as _SnapshotProxy  # noqa: E402

# 保留 _SNAPSHOT_DATA 名字以便兼容历史引用（实际写入走 sc_snapshot.register）
_SNAPSHOT_DATA = _SnapshotProxy()

from core.tdx_client import (
    tdx_get_latest_bar_with_ma,
    tdx_get_index_quote,
)  # V16.4.1: 删 3 个未使用导入

from stock_common import (
    _safe_float,
    _debug_log,
    get_fuyao_seal_info,
    get_fuyao_auction_snapshot,
    get_fuyao_auction_benchmark,
    _load_settings,
    _load_strategy_config,
    BaseReportRunner,
    get_dragon_tiger_board_async,
    holder_change_async,
    get_strategic_announcements_async,
    baidu_kline_full,
    get_reports,
    get_dividend_history,
    get_industry_comparison,
    get_concept_blocks,
    get_ths_hot_reason_async,
    get_industry_peers,
    get_stock_sector_rank,
    get_stock_info,
    get_hsgt_macro_flow,
    get_hsgt_macro_flow_async,
    get_eps_forecast_async,
    get_margin_trading_async,
    get_block_trade_async,
    get_northbound_hold_async,
    get_lockup_expiry_async,
    get_market_status,
    ScoreData,  # V17.0 审查: 删 clean_codes/create_async_session/calculate_multi_school_scores(基类/渲染收敛)
    ths_hot_list,
    em_hot_concept,
    get_eastmoney_stock_news,
    cls_telegraph,
    news_matches_stock,
    get_irm_qa,
    get_zhb_data_date,
    get_zhb_streak_days,
    get_zhb_tip_info,
    is_limit_up,  # V16.2: 统一涨停/跌停判断（含北交所 30%）
    sec_type_market_label,
    limit_pct_for,
)  # V10.3, V16.2: 统一涨跌停阈值
from stock_common.sc_report_runner import format_52w_reference, format_quote_provenance

from core.data_provider import get_main_net_buy_async  # V16.4.1: 删 9 个未使用 async 包装

# ═══════════════════════════════════════════
# 数据获取层
# ═══════════════════════════════════════════


def _unique_trading_flow_rows(rows):
    """保留有明确交易日、且日历确认开市的资金流记录，按日期从新到旧排序。"""
    from stock_common.stock_calendar import is_trading_day

    dated_rows = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        raw_date = str(row.get("date") or row.get("trade_date") or "")[:10]
        try:
            trade_date = date.fromisoformat(raw_date)
            if not is_trading_day(trade_date):
                continue
        except (TypeError, ValueError, NotImplementedError):
            continue
        previous = dated_rows.get(trade_date)
        if previous is None or (
            previous.get("main_net") is None and row.get("main_net") is not None
        ):
            dated_rows[trade_date] = row
    return [dated_rows[day] for day in sorted(dated_rows, reverse=True)]


def _get_index_quote(idx_code):
    """V4: 指数行情 → tdx_client 适配器（TDX指数K线，自动fallback腾讯）"""

    return tdx_get_index_quote(idx_code)


def get_fund_flow_realtime(code, ff_120d=None):
    """V7.5: 今日主力净流入 → 统一层 get_main_net_buy（V17.0 矩阵定案: f137 无条件优先，f137 本身=超大单f140+大单f143，V17.0.16 重定案禁止再+f140 重复计数），失败则尝试历史数据回退

    V16.0: 改用 data_provider.get_main_net_buy（统一优先级），替代原直连 tdx_get_fund_flow。
    V17.0(2026-08-14): 主力净=f137（本身=超大单f140+大单f143，V17.0.16 重定案：旧 f137+f140 重复计数虚高约40%已废）——ZHB 资金流键为竞价族不可作主力。

    Args:
        code: 股票代码
        ff_120d: 可选的历史资金流数据（避免重复调用 get_fund_flow_120d）

    Returns:
        dict or None
    """
    try:
        from core.data_provider import get_main_net_buy

        mnb = get_main_net_buy(code)
        if mnb and mnb.get("main_net_buy_amount") is not None:
            return {
                "data": [_safe_float(mnb["main_net_buy_amount"])],
                "detail": mnb,
                "source": mnb.get("source") or "unified",
            }
    except Exception as _e:
        _debug_log(f"sht get_main_net_buy error: {_e}")

    # V9.3.3: 使用传入的 ff_120d 避免重复调用
    if ff_120d is None:
        ff_120d = get_fund_flow_120d(code)

    if ff_120d and ff_120d.get("data") and len(ff_120d["data"]) > 0:
        # V16.1: 数据"最新在前"，[:5] 取最近 5 日（原 [-5:] 取最旧）
        recent_data = _unique_trading_flow_rows(ff_120d["data"])[:5]
        flow_values = []
        valid_rows = []
        for row in recent_data:
            raw_value = row.get("main_net") if isinstance(row, dict) else row
            if raw_value is not None:
                flow_values.append(_safe_float(raw_value))
                valid_rows.append(row)
        if flow_values:
            # 历史接口 main_net 单位为元；报告展示单位为万元。
            avg_flow_wan = sum(flow_values) / len(flow_values) / 1e4
            dates = [
                str(row.get("date") or row.get("trade_date") or "")[:10]
                for row in valid_rows
                if isinstance(row, dict) and (row.get("date") or row.get("trade_date"))
            ]
            return {
                "data": [avg_flow_wan],
                "detail": {},
                "source": "history_avg",
                "sample_count": len(flow_values),
                "note": f"使用近{len(flow_values)}个有效交易日平均",
                "date_start": dates[-1] if dates else "",
                "date_end": dates[0] if dates else "",
            }
    return None


def get_fund_flow_120d(code):
    """V17.2.x(2026-09-10) 统一口径：与 med 对齐为 `prefer="em"`（东财直连）。

    ⚠️ 变更依据（非行为变更，数据完全等价）：
      - 原 sht 用 `prefer="tdx"`、med 用 `prefer="em"`，看似两口径；
      - 实测 `tdx_get_history_fund_flow`(`core/tdx_client.py:1694`) **已完全委托东财 HTTP**
        （"V12.0: 委托到东财 HTTP 接口（原 TDX get_history_fund_flow 已废弃）"），
        且 V17.0.13 口径规定主力净额统一走东财 push2 f137（本身含超大单+大单，V17.0.16 重定案禁止再+f140）—— **两路径数据同源同值**；
      - `prefer="tdx"` 仅多一次对同一函数的冗余二次调用，且会把 `source` 误标为 "tdx"。
      故统一为 "em" 直连：数据不变、source 标注正确、少一层间接调用。
    """
    from stock_common import get_history_fund_flow_120d

    return get_history_fund_flow_120d(code, 60, prefer="em")


def get_baidu_kline_with_ma(code):
    """V4: K线+MA → tdx_client 适配器（TDX日K线+本地MA5/10/20计算）"""

    return tdx_get_latest_bar_with_ma(code)


# ═══════════════════════════════════════════

# 报告生成

# ═══════════════════════════════════════════


# V17.0.15: TA-Lib 61 种 K 线形态的中文名表（与 sc_technical.get_kline_patterns 的
# _cdl_map 键一一对应；用于 sht 报告【十七、K线形态识别】章节的可读化输出）。
# 未在表中的形态回退显示英文原名，不影响信号判读。
_CDL_CN = {
    "two_crows": "两只乌鸦",
    "three_black_crows": "三只乌鸦",
    "three_inside_up_down": "三内升/降",
    "three_line_strike": "三线打击",
    "three_outside_up_down": "三外升/降",
    "three_stars_in_the_south": "南方三星",
    "three_white_soldiers": "红三兵",
    "abandoned_baby": "弃婴形态",
    "advance_block": "大敌当前",
    "belt_hold": "捉腰带线",
    "breakaway": "脱离形态",
    "closing_marubozu": "收盘缺影线",
    "concealing_baby_swallow": "藏婴吞没",
    "counterattack": "反击线",
    "dark_cloud_cover": "乌云盖顶",
    "doji": "十字星",
    "doji_star": "十字星线",
    "dragonfly_doji": "蜻蜓十字",
    "gravestone_doji": "墓碑十字",
    "engulfing_pattern": "吞没形态",
    "evening_doji_star": "黄昏十字星",
    "evening_star": "黄昏之星",
    "up_down_gap": "跳空并列阴阳",
    "hammer": "锤子线",
    "hanging_man": "上吊线",
    "harami_pattern": "孕线",
    "harami_cross_pattern": "十字孕线",
    "high_wave_candle": "风高浪大线",
    "hikkake_pattern": "陷阱",
    "modified_hikkake_pattern": "修正陷阱",
    "homing_pigeon": "家鸽",
    "identical_three_crows": "三胞胎乌鸦",
    "in_neck_pattern": "颈内线",
    "inverted_hammer": "倒锤头",
    "kicking": "反冲形态",
    "kicking_bull_bear": "缺影反冲",
    "ladder_bottom": "梯底",
    "long_legged_doji": "长腿十字",
    "long_line_candle": "长蜡烛",
    "marubozu": "光头光脚",
    "matching_low": "相同低价",
    "mat_hold": "铺垫",
    "morning_doji_star": "早晨十字星",
    "morning_star": "早晨之星",
    "on_neck_pattern": "颈上线",
    "piercing_pattern": "刺透形态",
    "rickshaw_man": "黄包车夫",
    "rising_falling_three": "上升/下降三法",
    "separating_lines": "分离线",
    "shooting_star": "射击之星",
    "short_line_candle": "短蜡烛",
    "spinning_top": "陀螺",
    "stalled_pattern": "停顿形态",
    "stick_sandwich": "条形三明治",
    "takuri": "探水竿",
    "tasuki_gap": "跳空并列",
    "thrusting_pattern": "切入形态",
    "tristar_pattern": "三星",
    "unique_3_river": "独特三河",
    "upside_gap_two_crows": "向上跳空两乌鸦",
    "up_downside_gap_three": "跳空三法",
}


async def generate_report_async(
    session, code, output_path, ind_comp=None, idx_q=None, hsgt=None, depth="deep"
):
    """V7.5 async 版: 支持 ind_comp/idx_q/hsgt 外部缓存，批量模式下避免重复查询
    V8.5: 新增 depth 参数，支持 lite/medium/deep 三档分析深度
    """
    # 分析深度说明
    DEPTH_CONFIG = {
        "lite": {
            "skip_fund_flow_120d": True,
            "skip_lhb_detail": True,
            "skip_holder_history": True,
            "skip_margin_detail": True,
            "skip_block_trade_detail": True,
            "skip_announcement_detail": True,
            "skip_industry_peers": True,
            "desc": "快速模式",
        },
        "medium": {
            "skip_fund_flow_120d": True,
            "skip_lhb_detail": False,
            "skip_holder_history": True,
            "skip_margin_detail": False,
            "skip_block_trade_detail": True,
            "skip_announcement_detail": False,
            "skip_industry_peers": False,
            "desc": "标准模式",
        },
        "deep": {
            "skip_fund_flow_120d": False,
            "skip_lhb_detail": False,
            "skip_holder_history": False,
            "skip_margin_detail": False,
            "skip_block_trade_detail": False,
            "skip_announcement_detail": False,
            "skip_industry_peers": False,
            "desc": "深度模式",
        },
    }
    _dc = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["deep"])

    today_str = date.today().strftime("%Y-%m-%d")

    lines = []

    def L(s=""):
        lines.append(s)

    # V17.0.2i: 头部拆分(报告名/时间+模式分行, 参照 mak 规则)
    L("=" * 72)
    L(f"  **{code} 个股深度数据报告**")
    L(f"  ⏱ {today_str} {datetime.now().strftime('%H.%M.%S')} | 模式: {_dc['desc']}")
    L("=" * 72)
    L("")

    _60d_str = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
    from stock_common.stock_calendar import trading_day_window

    _30_trade_start_str = trading_day_window(30)[0].isoformat()

    _sc = _load_strategy_config()

    _mkt = _sc.get("market", {})

    _trd = _sc.get("trader", {})

    _hld = _sc.get("holder", {})

    _lo_strong = _mkt.get("limit_order_strong", 5.0)

    _lo_mid = _mkt.get("limit_order_mid", 2.0)

    try:
        _recent_days = max(1, int(_trd.get("recent_days", 90)))
    except (TypeError, ValueError):
        _recent_days = 90

    _unlock_warn = _hld.get("unlock_warn_days", 90)

    _unlock_ratio_warn = _hld.get("unlock_ratio_warn", 5.0)

    _limit_chg = _mkt.get("limit_chg_pct", 9.5)

    _near_limit = _mkt.get("near_limit_pct", 7.0)

    _seal_ratio_warn = _mkt.get("seal_amount_ratio_warn", 0.1)

    _mkt_status, _mkt_note = get_market_status()

    L(f"  报告生成时段：{_mkt_note}；实际行情日期以统一层元数据为准。")
    L("\n" + "---")
    L("## **一、个股基本信息**")
    L("---")

    # V15 统一数据中心：通过 get_canonical_stock_data 获取强类型标准化数据
    # V15.2 修正: async 上下文必须包 to_thread，否则阻塞主事件循环（val 死锁根因）
    from core.data_provider import get_canonical_stock_data

    cdata = await asyncio.to_thread(get_canonical_stock_data, code)
    price_today = cdata.price
    q = cdata.to_dict()

    # V17.0.5 P0: fuyao 官方封单(涨停池 seal_money/max_seal_money——替代买一估算;
    # trading_day 缓存, 全市场一次请求)。非涨停/无 Key → None, 回落原估算逻辑
    _seal_info = await asyncio.to_thread(get_fuyao_seal_info, code)

    # V15.4.2: get_stock_info 内部调腾讯，包 to_thread
    info = await asyncio.to_thread(get_stock_info, code)
    stock_name = cdata.name or info.get('name', 'N/A')
    stock_industry = cdata.industry or info.get('industry', 'N/A')

    # V17.0.1e(2026-08-16): 撤销 V17.0.1b 表格化——基本信息/行情为"字段: 值"竖排,
    # 原展示方式更佳; 表格仅用于同业横向对比/资金走向/龙虎榜等数字列对齐章节
    L(f"  股票名称: {stock_name}")
    L(f"  股票代码: {cdata.code}")
    # V16.3.3 (2026-08-10 字典 12.15.8): ST/次新风险信号（canonical is_st/is_new——结构化名称）
    if getattr(cdata, "is_st", False):
        L("  ⚠️ 风险标记: **ST/*ST**（退市风险——涨跌停按板块阈值，短线注意连续跌停风险）")
    if getattr(cdata, "is_new", False):
        L(
            f"  🆕 次新标记: 上市 {getattr(cdata, 'listing_days', '?')} 日（临时前缀已忽略——涨跌停规则可能不同）"
        )
    L(f"  所属板块: {stock_industry}")
    # V17.0.32(2026-09-06) DEBT-016: 露出 sec_type（与 board 地域字段正交）→ 市场板块 + 涨跌幅限制
    L(f"  市场板块: {sec_type_market_label(getattr(cdata, 'sec_type', 0), cdata.code, cdata.name)}")
    L(f"  总股本:   {cdata.total_shares_wan/1e4:.2f}亿股")
    L(f"  流通股本: {cdata.float_shares_wan/1e4:.2f}亿股")

    # V17.0.1e: 上市日期唯一来源 list_date（原 listing_date/list_date 双键并存导致重复,
    # listing_date 恒 N/A）
    # V17.2.21 修复: 优先用 canonical cdata.list_date（走 push2delay+10年缓存, 实测可用）,
    # info.get 兜底（get_stock_info 走主域 push2 被风控拦截恒空）——修复 39 份个股报告上市日期全空
    # V17.3.5 修正(报告审查 #362): 改用 normalize_list_date 归一化（避免切片对残缺值生成乱码）
    from core._accessors import normalize_list_date

    ld = cdata.list_date or info.get("list_date", "") or info.get("listing_date", "")
    ldf = normalize_list_date(ld)
    L(f"  上市日期: {ldf}")

    if cdata.change_5d or cdata.change_10d or cdata.change_20d:
        L(
            f"\n  [阶段涨幅] 近5日: {cdata.change_5d:+.2f}% | 近10日: {cdata.change_10d:+.2f}% | 近20日: {cdata.change_20d:+.2f}%"
        )
        # V17.0.5 P0: 本月至今涨跌幅(change_mtd)——短线周内动量与月内趋势衔接参考
        if getattr(cdata, "change_mtd", 0):
            L(f"  [本月至今] {cdata.change_mtd:+.2f}%（基准=上月末收盘）")

    L("\n" + "---")
    L("## 【二、实时行情、估值与短线趋势】")
    L("---")

    # 52周区间位置仅在价格和区间数据可比时展示；区间外价格显示与边界的距离。
    _52w_dates = getattr(cdata, "field_as_of_dates", {}) or {}
    _52w_line = format_52w_reference(
        cdata.price,
        cdata.low_52w,
        cdata.high_52w,
        low_date=_52w_dates.get("low_52w", ""),
        high_date=_52w_dates.get("high_52w", ""),
    )
    if _52w_line:
        L(f"  [{_52w_line}]")

    L(f"  {format_quote_provenance(cdata)}")
    if cdata.price > 0 or cdata.change_pct != 0:
        # V17.0.1e: 撤销 V17.0.1b 表格化, 恢复原"字段: 值"竖排(基本信息/行情不适用表格)
        L(f"  现价:   {cdata.price:.2f} 元")
        L(f"  涨跌幅:   {cdata.change_pct:.2f}%")
        L(f"  今开:     {cdata.open:.2f} 元  昨收: {cdata.prev_close:.2f} 元")
        L(f"  最高:     {cdata.high:.2f} 元  最低: {cdata.low:.2f} 元")
        L(f"  成交额:   {cdata.amount_wan/10000:.2f} 亿元  换手率: {cdata.turnover_pct:.2f}%")
        # V16.2.3 恢复: 振幅/涨停价/跌停价（V16.1 重构时丢失，对照 v9.6 模板；vol_ratio 未入 canonical 跳过）
        if cdata.high > 0 and cdata.low > 0 and cdata.prev_close > 0:
            _amp = (cdata.high - cdata.low) / cdata.prev_close * 100
            L(f"  振幅:     {_amp:.2f}%")
        _limit_up = getattr(cdata, 'limit_up', 0) or 0
        _limit_dn = getattr(cdata, 'limit_down', 0) or 0
        if _limit_up > 0 or _limit_dn > 0:
            L(f"  涨停价:   {_limit_up:.2f} 元  跌停价: {_limit_dn:.2f} 元")
        elif cdata.prev_close > 0:
            # V16.2.14: push2 f51/f52 盘中可能为 0（v9.6 用腾讯有值）→ 按板块阈值计算兜底
            _th = limit_pct_for(code, stock_name)
            L(
                f"  涨停价:   {cdata.prev_close * (1 + _th / 100):.2f} 元  跌停价: {cdata.prev_close * (1 - _th / 100):.2f} 元"
            )
        # V17.3 修复: 流通市值恒由 流通股本(亿股) × 现价 推导, 与总市值/现价同源同价基,
        # 避免 cdata.float_mcap_yi 偶发 stale 价格(实测 002360: 报 16.44 亿 vs 3.26亿股×5.33=17.38 亿)导致不自洽
        _float_mv_yi = (
            (cdata.float_shares_wan / 1e4) * price_today
            if cdata.float_shares_wan
            else cdata.float_mcap_yi
        )
        L(f"  总市值:   {cdata.mcap_yi:.2f} 亿元  流通市值: {_float_mv_yi:.2f} 亿元")
        _pe_str = f"{cdata.pe_ttm:.2f}" if cdata.pe_ttm > 0 else "N/A（亏损）"
        _pe_dyn_str = f"{cdata.pe_dynamic:.2f}" if cdata.pe_dynamic > 0 else "N/A"
        _pe_lyr_str = f"{cdata.pe_lyr:.2f}" if cdata.pe_lyr > 0 else "N/A"
        L(
            f"  PE（TTM）:  {_pe_str}  PE（动）: {_pe_dyn_str}  PE（静/LYR）: {_pe_lyr_str}  PB: {cdata.pb:.2f}"
        )

    else:
        L("  行情数据获取失败")

    ma_data = await asyncio.to_thread(get_baidu_kline_with_ma, code)

    if ma_data and 'ma5avgprice' in ma_data:

        ma5 = _safe_float(ma_data.get('ma5avgprice', 0))
        ma10 = _safe_float(ma_data.get('ma10avgprice', 0))

        L(f"\n  [技术支撑] MA5={ma5:.2f}元 | MA10={ma10:.2f}元")

        if price_today > 0 and ma5 > 0:

            bias = (price_today - ma5) / ma5 * 100

            L(
                f"  [短线趋势] 现价相对 MA5 乖离率: {bias:+.2f}% ({'站上 MA5, 趋势偏强' if price_today>=ma5 else '跌破 MA5, 短线走弱'})"
            )

    L("")

    all_idx = [
        ("sh000001", "上证指数"),
        ("sz399106", "深证综指"),
        ("sz399102", "创业综指"),
        ("sh000680", "科创综指"),
    ]

    if code.startswith("688"):
        bi = "sh000680"

    elif code.startswith(("300", "301")):
        bi = "sz399102"

    elif code.startswith("6"):
        bi = "sh000001"

    elif code.startswith(("0")):
        bi = "sz399106"

    else:
        bi = ""

    if idx_q is None:

        idx_q = {}

        # V15.4.2: 4 个指数并行获取，避免早盘前 TDX 限流时串行 60s × 4 卡死
        async def _idx_async(idx_code: str) -> tuple:
            _q = await asyncio.to_thread(_get_index_quote, idx_code)
            return idx_code, _q

        _idx_results = await asyncio.gather(
            *[_idx_async(ic) for ic, _ in all_idx], return_exceptions=True
        )
        for _r in _idx_results:
            if isinstance(_r, Exception):
                continue
            _ic, _iq = _r
            if _iq:
                idx_q[_ic] = _iq

    for ic, inm in all_idx:

        _iq_val = idx_q.get(ic, {})

        if _iq_val:

            L(
                f"  [{inm}] 开盘 {_iq_val.get('open',0):.2f} | 当前 {_iq_val.get('price',0):.2f} | 涨跌幅 {_iq_val.get('change_pct',0):+.2f}%{' ← 本股' if ic==bi else ''}"
            )

    miq = idx_q.get("sh000001", {})
    biq = idx_q.get(bi, {}) if bi else {}

    if hsgt is None:

        hsgt = await get_hsgt_macro_flow_async(session)

    if hsgt:
        # V17.0.4(2026-08-19): data_quality=invalid → 数据源序列错位(同花顺 hgt/sgt 长度不同步,
        # 末值恒为陈旧值——8/12-8/19 冻结 379.75)——不再展示错误数字
        if hsgt.get("data_quality") == "invalid":
            L("  ⚠️ 今日北向资金: 数据源异常(hgt/sgt 序列错位), 净流入暂缺")
        elif hsgt.get("data_quality") == "partial_hgt_only":
            # V17.0.28: hgt=当日分时(可用), sgt=历史序列(不可用) → 只展示沪股通并声明单口径
            _sig = "偏多" if hsgt["hgt"] > 0 else "偏空"
            L(
                f"  💰 今日北向资金: 沪股通 {hsgt['hgt']:+.2f}亿（{_sig}）"
                f" | 深股通序列为历史值暂缺，本项为沪股通单口径，非北向合计"
            )
        else:
            _sig = "偏多" if hsgt["total"] > 0 else "偏空"

            L(
                f"  💰 今日北向资金: 沪股通 {hsgt['hgt']:+.2f}亿 | 深股通 {hsgt['sgt']:+.2f}亿 | 合计 {hsgt['total']:+.2f}亿（{_sig}）"
            )
            # V16.4.1: 数据层降级标记展示——2026-08-12 实测深股通 379.75 亿(sgt/hgt 比例 40.9 异常,
            # 远超历史单日记录), 源数据存疑时显式警告, 避免误导
            # V17.0.2: 内部字段名(warning 原文)下沉为统一话术
            if hsgt.get("data_quality") == "degraded":
                L("  ⚠️ 北向资金数据源存疑(异常波动), 仅供参考")

    # V15.4.2: 资金流同步调用包 to_thread，避免阻塞事件循环
    ff = dict(await asyncio.to_thread(get_fund_flow_120d, code) or {})
    _raw_flow_rows = ff.get("data") or []
    ff["data"] = _unique_trading_flow_rows(_raw_flow_rows)
    ff["unverified_date_count"] = max(0, len(_raw_flow_rows) - len(ff["data"]))
    rf = await asyncio.to_thread(
        get_fund_flow_realtime, code, ff_120d=ff
    )  # V9.3.3: 复用 ff_120d 避免重复调用

    if rf and rf.get("data"):
        _main_wan = _safe_float(rf["data"][0])
        _main_txt = f"{_main_wan/1e4:.2f}亿" if abs(_main_wan) >= 1e4 else f"{_main_wan:.0f}万"
        if rf.get("source") == "history_avg":
            _period = ""
            if rf.get("date_start") and rf.get("date_end"):
                _period = f"（{rf['date_start']} 至 {rf['date_end']}）"
            _sample_count = max(1, int(rf.get("sample_count", 1) or 1))
            if _sample_count == 1:
                L(f"  💰 最近有效交易日主力净流入{_period}: {_main_txt}")
            else:
                L(f"  💰 近{_sample_count}个有效交易日平均主力净流入{_period}: {_main_txt}")
        else:
            L(f"  💰 最新有效交易日主力净流入: {_main_txt}")
    elif ff and ff.get("data"):
        # 历史资金流为“最新在前”，报告按来源有效交易日标记，不用自然日“昨日”。
        _d0 = ff["data"][0]
        _raw_flow = _d0.get("main_net") if isinstance(_d0, dict) else None
        if _raw_flow is not None:
            _latest_wan = _safe_float(_raw_flow) / 1e4
            _latest_txt = (
                f"{_latest_wan/1e4:.2f}亿" if abs(_latest_wan) >= 1e4 else f"{_latest_wan:.0f}万"
            )
            _latest_date = str(_d0.get("date") or _d0.get("trade_date") or "")[:10]
            _date_label = f"（{_latest_date}）" if _latest_date else "（日期未提供）"
            L(f"  ▲ 最近交易日{_date_label}主力净流入: {_latest_txt}")
        else:
            L("  ⚠️ 资金流历史记录未包含有效主力净额，本项暂缺，不按 0 处理")
    elif ff.get("unverified_date_count"):
        L(
            f"  ⚠️ 资金流返回 {ff['unverified_date_count']} 条记录，但日期缺失、重复或非交易日；"
            "不能计入有效交易日窗口，也不据此推断资金方向"
        )
    else:
        L("  ⚠️ 主力资金流未取得有效数据；本项暂缺，不按 0 推断资金方向")

    # V17.2.24: eltdx 连板梯队与封单强度（统一层 cdata.eltdx_*，源自 TDX 7709/7615 实时）
    if getattr(cdata, "eltdx_has_shortline", False):
        _ll = cdata.eltdx_ladder_level or 0
        _streak = cdata.eltdx_limit_up_streak_days or 0
        _seal = cdata.eltdx_seal_to_float_ratio or 0.0
        _ov = cdata.eltdx_open_volume_ratio or 0.0
        _bt = cdata.eltdx_limit_board_text or ""
        L("\n" + "---")
        L("## 【二·附、连板梯队与封单强度（通达信 eltdx 实时）】")
        L("---")
        if _ll >= 2:
            L(
                f"  🪜 连板梯队: **{_ll}连板**{('（' + _bt + '）') if _bt else ''}（连续涨停 {_streak} 日）"
            )
            L(f"  🔒 封单占流通比: {_seal:.2f}%（封板坚决度；封流比越高越难开板）")
        else:
            L(f"  🪜 连板高度: {_ll}板（未达连板梯队）")
            if _seal >= 0.5:
                L(f"  🔒 首板强封: 封单占流通比 {_seal:.2f}%（封板坚决）")
        if _ov:
            L(f"  📊 开盘量比: {_ov:.2f}（集合竞价活跃度）")
        L("  📡 数据来源: 通达信 eltdx（TDX 公网主站 7709/7615 实时）")
    else:
        # V17.4.x (#442): eltdx 不可用时显式占位, 不静默缺章; 连板梯队/封单强度为 eltdx 专属实时能力,
        # easy-tdx/mootdx 无对应接口, 故无等价后备通道.
        L("\n" + "---")
        L("## 【二·附、连板梯队与封单强度（通达信 eltdx 实时）】")
        L("---")
        L("  ⚠️ 本次未取得 eltdx 连板梯队与封单强度的有效数据。")
        L(
            "     盘后/非竞价时段可能没有实时样本，也可能是后端未返回；仅凭空结果无法区分。"
            "该专属维度无等价后备通道，本节暂缺，不能据此判断当日没有连板或封单。"
        )

    L("\n" + "---")
    L("## **三、机构一致预期与估值**")
    L("---")

    df_eps = await get_eps_forecast_async(session, code)

    # MEDIUM(审查 2026-08-16): 守卫需 >=4 列(循环访问 iloc[_,3..5]), 原 >=2 列数不足时 IndexError
    if not df_eps.empty and len(df_eps.columns) >= 4:

        _this_year = str(date.today().year)

        eps_cur = None
        eps_next = None

        eps_min = None
        eps_max = None
        eps_ind = None
        _n_analysts = 0

        for _ri in range(min(len(df_eps), 5)):

            _row_label = str(df_eps.iloc[_ri, 0])

            if (
                _this_year in _row_label
                or f"{_this_year}预测" in _row_label
                or f"{_this_year}E" in _row_label
            ):

                eps_cur = _safe_float(df_eps.iloc[_ri, 3])

                eps_min = _safe_float(df_eps.iloc[_ri, 2])

                eps_max = _safe_float(df_eps.iloc[_ri, 4])

                eps_ind = _safe_float(df_eps.iloc[_ri, 5])

                _n_analysts = int(_safe_float(df_eps.iloc[_ri, 1]))

            elif str(date.today().year + 1) in _row_label:

                eps_next = _safe_float(df_eps.iloc[_ri, 3])

        if not eps_cur:

            eps_cur = _safe_float(df_eps.iloc[0, 3]) if len(df_eps) > 0 else None

            eps_next = _safe_float(df_eps.iloc[1, 3]) if len(df_eps) > 1 else None

        if eps_cur and eps_cur > 0:

            pe_fwd = price_today / eps_cur

            L(f"  {_n_analysts} 家机构覆盖" if _n_analysts else "  有机构覆盖")

            _range_str = f"，区间 {eps_min:.2f}~{eps_max:.2f}" if eps_min and eps_max else ""

            _ind_str = f"，行业中值 {eps_ind:.2f}" if eps_ind and eps_ind > 0 else ""

            L(f"  {_this_year}E EPS 均值: {eps_cur:.2f} 元{_range_str}{_ind_str}")

            if eps_next and eps_next > 0:

                L(f"  {int(_this_year)+1}E EPS 均值: {eps_next:.2f} 元")

                cagr = (eps_next / eps_cur - 1) * 100

                L(
                    f"  预期增速: {cagr:+.1f}% | PEG: {pe_fwd/cagr:.2f}"
                    if cagr > 0
                    else f"  预期增速: {cagr:+.1f}%"
                )

            L(f"  前向PE ({_this_year}E): {pe_fwd:.2f}x")

        else:
            L("  (当前亏损或无数据，前向PE无意义)")

    else:
        L("  无机构覆盖数据")

    # V17.0.5 P0: 官方封单口径优先(fuyao 涨停池 seal_money/max_seal_money), 买一估算兜底
    if _seal_info:
        fa = (_seal_info['seal_money'] or 0) / 1e8
        fr = fa / (q.get('mcap_yi', 0) or 1) * 100
        t = f"  封单额 {fa:.2f}亿元（fuyao 官方），占流通市值 {fr:.1f}%"
        _dec = _seal_info.get('seal_decay_ratio')
        if _dec is not None:
            _pct = _dec * 100
            if _pct < 30:
                t += f"\n  ⚠️ 封单衰减率 {_pct:.0f}%（峰值 {(_seal_info['max_seal_money'] or 0)/1e8:.1f}亿→现 {fa:.1f}亿）——烂板特征，警惕炸板"
            elif _pct < 60:
                t += f"\n  📊 封单衰减率 {_pct:.0f}%——盘中有所开板回封"
            else:
                t += f"\n  🔥 封单衰减率 {_pct:.0f}%——全日封死，封板质量极高"
        if _seal_info.get('limit_up_reason'):
            t += f"\n  涨停原因: {_seal_info['limit_up_reason']}"
        L(t)
    else:
        lu = q.get("limit_up", 0) if q else 0
        b1v = q.get("bid1_vol", 0) if q else 0
        np2 = q.get("price", 0) if q else 0
        is_lu = lu > 0 and abs(np2 - lu) / lu < 0.005
        if is_lu and b1v > 0:
            fa = b1v * lu / 1e8
            fr = fa / (q.get("mcap_yi", 0) or 1) * 100
            if fa >= 0.1 or fr > 0.5:
                t = f"  封单额 {fa:.2f}亿元，占流通市值 {fr:.1f}%"
                if fr > 5:
                    t += "\n  🔥 封单实力强劲，次日大概率高开"
                elif fr > 2:
                    t += "\n  ✅ 封单质量良好"
                else:
                    t += "\n  ⚠️ 封单偏弱"
                L(t)

    L("\n" + "---")
    L("## **四、个股研报（东财）**")
    L("---")

    # V15.4.2: 同步研报拉取包 to_thread
    reports = await asyncio.to_thread(
        get_reports, code, 3
    )  # V17.0.7: 5→3(四章仅60天计数+前10篇, 3页足够)

    rr = [r for r in reports if str(r.get("publishDate", ""))[:10] >= _60d_str]

    if rr:

        L(f"  最近60天共 {len(rr)} 篇研报，显示前10篇:")

        L(f"  {'日期':<12} {'机构':<16} {'评级':<10} {'标题'}")
        L(f"  {'-'*70}")

        for r in rr[:10]:

            L(
                f"  {str(r.get('publishDate',''))[:10]:<12} {str(r.get('orgSName','') or '—'):<16} {str(r.get('emRatingName','') or '—'):<10} {str(r.get('title','') or '')[:50]}"
            )

    elif reports:
        L(f"  近60天内无新研报（共 {len(reports)} 篇历史研报，已省略）")

    else:
        L("  无研报数据（该股可能无机构覆盖）")

    L("\n" + "---")
    L("## 【五、概念板块、热点归因与板块共振】")
    L("---")

    # V15.4.2: 同步概念+行业对比包 to_thread
    blocks = await asyncio.to_thread(get_concept_blocks, code)

    if blocks["industry"]:
        L(f"  所属板块: {', '.join(b['name'] for b in blocks['industry'])}")

    if ind_comp is None:

        ind_comp = await asyncio.to_thread(get_industry_comparison)

    stock_ind = info.get('industry', '')

    if blocks and blocks.get("industry"):

        stock_ind = blocks["industry"][0].get("name", stock_ind)

    industry_rank = 0
    industry_change_pct = 0
    industry_match_name = ""

    if stock_ind and ind_comp.get("all"):

        rank_str = "未进入前100"
        is_top = False

        _ind_clean = (
            stock_ind.replace("行业", "").replace("服务", "").replace("Ⅱ", "").replace("Ⅲ", "")
        )

        for row in ind_comp["all"]:

            _row_clean = (
                row["name"]
                .replace("行业", "")
                .replace("服务", "")
                .replace("Ⅱ", "")
                .replace("Ⅲ", "")
            )

            if (
                stock_ind in row["name"]
                or row["name"] in stock_ind
                or _ind_clean in _row_clean
                or _row_clean in _ind_clean
            ):

                industry_rank = row['rank']
                industry_change_pct = row['change_pct']
                industry_match_name = row['name']

                rank_str = f"第 {industry_rank} 名（板块快照涨跌幅 {industry_change_pct}%，有效日期未核实）"

                if industry_rank <= 10:
                    is_top = True

                break

        L("  ➤ 板块共振监测")
        L(f"  该板块行情快照全市场排名（有效日期未核实）: {rank_str}")

        if is_top:
            L(
                "     🔥 提醒: 所在板块在该行情快照中处于全市场 TOP10；快照日期未核实，不据此认定当前板块共振。"
            )

    # V16.1: time.sleep 阻塞事件循环 → await asyncio.sleep
    await asyncio.sleep(0.5)

    # V16.1: lite 模式跳过同业对比（省一次 TDX 板块成员查询）
    # V16.4.1: lite 分支补 peers/my_mcap 键——下游 L654/L1422 裸索引 peer_data["peers"],
    # 缺键时 --depth lite 必抛 KeyError 整份报告失败
    if _dc.get("skip_industry_peers"):
        peer_data = {
            "my_rank": 0,
            "industry_count": 0,
            "industry": stock_ind,
            "peers": [],
            "my_mcap": 0,
        }
    else:
        # V15.4.2: 同步同业对比包 to_thread (TDX 限流时易卡)
        peer_data = await asyncio.to_thread(get_industry_peers, code, 3, info=info)

    if peer_data.get("my_rank", 0) > 0 and peer_data.get("industry_count", 0) > 0:

        L("  ➤ 市值排名")
        L(
            f"  {peer_data.get('industry', stock_ind)}: 该股排名第 {peer_data['my_rank']}/{peer_data['industry_count']} 位 (按总市值)"
        )

    _has_peer = peer_data.get("my_rank", 0) > 0 and peer_data.get("industry_count", 0) > 0

    if (industry_rank > 0 and industry_match_name) or _has_peer:

        _rank_parts = []

        if industry_rank > 0 and industry_match_name:

            _up = 0
            _down = 0

            _all_members = peer_data.get('all_members', [])

            if _all_members:

                _up = sum(1 for m in _all_members if m.get('change_pct', 0) > 0)

                _down = sum(1 for m in _all_members if m.get('change_pct', 0) < 0)

            _rank_parts.append(
                f"[板块快照涨跌排名/日期未核实] 上涨 {int(_up)} 家 / 下跌 {int(_down)} 家"
            )

        try:

            # V16.1: 同步阻塞包 to_thread
            _sr = await asyncio.to_thread(get_stock_sector_rank, code, info=info, q=q)

            if _sr:
                _rank_parts.append(
                    f"本股行情涨跌幅{_sr['change_pct']:+.2f}%（有效日期未核实），板块内排名第{_sr['rank']}/{_sr['total']}名"
                )

        except Exception as _e:
            _debug_log(f"sector_rank error: {_e}")

        if _rank_parts:
            L(f"     {'  '.join(_rank_parts)}")

    # 股息率：zhb优先，无zhb时fallback到get_dividend_history
    _zhb_div_yield = cdata.dividend_yield if cdata and cdata.dividend_yield else 0
    if _zhb_div_yield and _zhb_div_yield > 0:
        L(f"  股息率: {_zhb_div_yield:.2f}%")
    # V16.2.3: zhb 有股息率时也补最近分红（对齐 v9.6 模板）；接口失败（None）不显示
    div = await asyncio.to_thread(get_dividend_history, code)
    if div:
        ld2 = div[0]
        ye = f"{(ld2['bonus_rmb']/price_today)*100:.2f}%" if price_today > 0 else "N/A"
        L(f"  最近分红: {ld2['date']} 每股{ld2['bonus_rmb']:.4f}元 (约{ye}股息率)")

    if blocks["concept"]:

        L(f"\n  概念板块(TDX): {', '.join(b['name'] for b in blocks['concept'])}")

    L("\n  ➤ 同花顺热点题材归因 (基于当日强势股/涨停榜):")

    # 优化同花顺热点题材时段显示逻辑
    if _mkt_status in ("pre_market", "morning", "lunch"):
        L("  ⚠️ 同花顺热点池需16:00后更新，当前为盘中时段数据可能为空")
    elif _mkt_status == "afternoon":
        L("  ⚠️ 当前为下午盘，同花顺热点池更新中，数据可能为空或不完整")
    else:
        L("  ⚠️ 同花顺热点池数据为更新周期内的汇总信息")

    ths_hot = await get_ths_hot_reason_async(session, code, today_str)

    if ths_hot:
        L(f"  [强势归因] {ths_hot.get('reason','')}")

    else:
        L("  (该股今日未进入同花顺强势股列表，暂无热点题材归因数据)")

    L("\n" + "---")
    L("## **六、同业龙头横向对比**")
    L("---")

    if peer_data["peers"]:

        if "note" in peer_data["peers"][0]:
            L(f"  ⚠️ {peer_data['peers'][0]['note']}")

        else:

            _my_mcap_show = (
                peer_data['my_mcap'] if peer_data['my_mcap'] > 0 else q.get('mcap_yi', 0)
            )

            L(f"  所属板块: {peer_data['industry']}")
            L(f"  本股市值: {_my_mcap_show:.1f}亿元")

            # V17.0.27(2026-09-04) 口径对齐修复（9/3 报告核查 #2）：
            #   同业行 `p['pe']` 来自 tdx_get_board_members → pe_dynamic（东财兜底路径为 f9=动态PE，
            #   V17.0.15 已定案）；而本股行原取 pe_ttm —— **同一列里两个口径**，横向对比不可比，
            #   且列标题写 "PE（TTM）" 与同业行实际口径不符（语义漂移，A2）。
            #   实测佐证: 300442 报告显示 PE（TTM）=43.9，统一层实测 pe_ttm=20.93 / pe_dynamic=19.68，
            #   43.9 两者皆不匹配（来自 TDX MAC 的 pe_dynamic）。
            #   修复: 本股行改用 pe_dynamic，列标题改为「PE（动）」→ 同列同口径 + 标题如实。
            L("  同业龙头对比:")
            L(
                f"  {'代码':<8} {'名称':<12} {'股价':>8} {'涨跌幅%':>8} {'市值(亿)':>10} {'PE（动）':>9} {'PE（静）':>8} {'换手率%':>8}"
            )
            L(f"  {'-'*80}")

            _my_mcap = peer_data['my_mcap'] if peer_data['my_mcap'] > 0 else q.get('mcap_yi', 0)

            _my_pe = q.get('pe_dynamic', 0) or 0
            _my_pe_s = f"{_my_pe:.1f}" if _my_pe > 0 else "亏损"
            _my_pe_lyr = cdata.pe_lyr or 0
            _my_pe_lyr_s = f"{_my_pe_lyr:.1f}" if _my_pe_lyr > 0 else "N/A"
            L(
                f"  {code:<8} {info.get('name','N/A'):<12} {price_today:>8.2f} {q.get('change_pct',0):>7.2f}% {_my_mcap:>9.1f} {_my_pe_s:>9} {_my_pe_lyr_s:>8} {q.get('turnover_pct',0):>7.2f}% ← 本股"
            )

            for p in peer_data["peers"]:
                _ppe = p.get('pe', 0) or 0
                _ppe_s = f"{_ppe:.1f}" if _ppe > 0 else "亏损"
                _ppe_lyr = p.get('pe_lyr', 0) or 0
                _ppe_lyr_s = f"{_ppe_lyr:.1f}" if _ppe_lyr > 0 else "N/A"
                # V17.0.27(2026-09-04) A6「缺失≠0」（9/3 报告核查 #3）：
                #   peers 的 change_pct 来自 TDX board_members，取不到时返回 0 —— 直接渲染
                #   成 "0.00%" 会被读者误读为「平盘」。实证: 300442 在 300454/301396 两份
                #   报告同业表均显示 0.00%，但统一层对其 change_pct 的 field_source 是
                #   **"missing"**，且该股当日换手率 0.88%（有成交、非停牌）→ 确为缺失非平盘。
                #   平盘（真实 0.00%）在 A 股极罕见，故此处按「0 即缺失」显式渲染 N/A。
                _pchg = p.get('change_pct', 0) or 0
                _pchg_s = f"{_pchg:>7.2f}%" if _pchg != 0 else "    N/A "
                L(
                    f"  {p['code']:<8} {p['name']:<12} {p['price']:>8.2f} {_pchg_s} {p['mcap_yi']:>9.1f} {_ppe_s:>9} {_ppe_lyr_s:>8} {p['turnover']:>7.2f}%"
                )

    else:
        L(f"  无法获取同业数据（板块: {peer_data.get('industry','未知')}）")

    L("\n" + "---")
    L("## **七、资金走向分析**")
    L("---")

    # V15.2 修复: 改名 _composite → q (cdata.to_dict() 的标准变量名)
    # 同时把 cdata 的字段名转换为 zhb_main_net dict 格式（向后兼容下游 print 逻辑）
    zhb_main_net = None
    _q_field_sources = q.get("field_sources") or {} if q else {}
    _q_flow_source = _q_field_sources.get("main_net_buy_wan")
    _q_hands_source = _q_field_sources.get("main_net_buy_hands")
    _has_q_flow = (
        bool(q)
        and bool(_q_flow_source)
        and str(_q_flow_source).lower() != "missing"
        and q.get("main_net_buy_wan") is not None
    )
    _has_q_hands = (
        bool(q)
        and bool(_q_hands_source)
        and str(_q_hands_source).lower() != "missing"
        and q.get("main_net_buy_hands") is not None
    )
    _q_flow_1d_source = _q_field_sources.get("main_net_buy_wan_1d")
    _has_q_flow_1d = (
        bool(q)
        and _has_q_flow
        and bool(_q_flow_1d_source)
        and str(_q_flow_1d_source).lower() != "missing"
        and q.get("main_net_buy_wan_1d") is not None
    )
    if q and (_has_q_flow or _has_q_hands):
        zhb_main_net = {
            "main_net_buy_hands": q.get("main_net_buy_hands") if _has_q_hands else None,
            "main_net_buy_hands_1d": None,
            "main_net_buy_hands_2d": None,
            "main_net_buy_amount": q.get("main_net_buy_wan") if _has_q_flow else None,
            "main_net_buy_amount_1d": q.get("main_net_buy_wan_1d") if _has_q_flow_1d else None,
            "main_net_buy_amount_2d": None,
        }
    if not _has_q_flow:
        try:
            _fallback_main_net = await get_main_net_buy_async(code, session)
            if _fallback_main_net:
                if not zhb_main_net:
                    zhb_main_net = {}
                if _fallback_main_net.get("main_net_buy_amount") is not None:
                    zhb_main_net["main_net_buy_amount"] = _fallback_main_net["main_net_buy_amount"]
                zhb_main_net["source"] = _fallback_main_net.get("source")
        except Exception as _e:
            _debug_log(f"get_main_net_buy_async error ({code}): {_e}")
    if zhb_main_net:
        # 来源以字段元数据/实际适配器为准；get_main_net_buy 不再从 ZHB 同名竞价字段回退。
        _flow_src = (
            _q_flow_source
            if _has_q_flow
            else zhb_main_net.get("source")
            or (_q_hands_source if _has_q_hands else "东财资金流兼容接口")
        )
        L(f"\n  ➤ 主力资金流向 ({_flow_src}):")
        if _has_q_hands and zhb_main_net.get("main_net_buy_hands") is not None:
            L(
                f"    最新有效交易日主力净买入量: {zhb_main_net['main_net_buy_hands']:.0f}手"
            )  # V17.0: 仅 TDX 0x0011 实时有值
        _amount_value = zhb_main_net.get("main_net_buy_amount")
        if _amount_value is not None:
            _amt = _safe_float(_amount_value)
            L(f"    最新有效交易日主力净流入额: {_amt:+.0f}万元")
            if _has_q_flow_1d:
                L(
                    f"    前一有效交易日主力净流入额: "
                    f"{_safe_float(zhb_main_net['main_net_buy_amount_1d']):+.0f}万元"
                )
            _amt_wan = q.get('amount_wan', 0) if q else 0
            # V16.4.1: 占比保留符号(原 abs 把净流出显示成正占比, 222% 即由此+源数据异常);
            # 净额绝对值超成交额 = 源数据存疑, 显式标注
            if _amt_wan > 0:
                flow_ratio = _amt / _amt_wan * 100
                _flow_note = (
                    " ⚠️ 异常:净流入额超成交额(源数据存疑)" if abs(flow_ratio) > 100 else ""
                )
                L(f"    主力资金占比: {flow_ratio:+.2f}%{_flow_note}")
            else:
                L("    主力资金占比: N/A（成交额缺失）")
            if _amt > 0:
                _flow_signal = "🟢 主力资金净流入"
            elif _amt < 0:
                _flow_signal = "🔴 主力资金净流出"
            else:
                _flow_signal = "⚪ 主力资金净额为零"
            L(f"    信号: {_flow_signal}")
        else:
            L("    主力净流入额: N/A（来源未提供，不能按 0 推断）")
    else:
        L("\n  ⚠️ 主力资金流数据未返回有效字段；本项不按 0 或 ZHB 竞价额推断方向")

    # V15.2 修复: 改名 _composite → q
    streak = None
    if q and q.get("streak_days"):
        streak = q["streak_days"]
    if not streak:
        try:
            streak = get_zhb_streak_days(code)
        except Exception as _e:
            _debug_log(f"get_zhb_streak_days error ({code}): {_e}")
            streak = 0
    if streak:
        if streak > 0:
            L(
                f"\n  ➤ 连涨天数: {streak}天 {'⚠️ 连涨时间较长，注意波动风险' if streak >= 5 else ''}"
            )
        elif streak < 0:
            L(
                f"\n  ➤ 连跌天数: {abs(streak)}天 {'⚠️ 连跌时间较长；连跌不等同于超卖' if abs(streak) >= 5 else ''}"
            )

    if ff["data"]:

        # V16.1 修复: get_em_history_fund_flow 返回"最新在前"（sort reverse=True），
        # 原 [-10:] 取到最旧 10 条 → 改 [:10] 取最新 10 条；显示按时间正序（reversed）
        # V16.1: lite 模式跳过资金流历史明细（_dc["skip_fund_flow_120d"]）
        if _dc.get("skip_fund_flow_120d"):
            L("\n  ➤ 资金流监控: (lite 模式跳过历史明细，仅显示当日)")
            L(f"    主力净流入(最新): {ff['data'][0].get('main_net', 0)/1e4:+.0f}万元")
        else:
            # V17.0.7: 标题按实际数据量自适应(2026-08-24 全批实测 push2his 连接封锁+
            # push2delay daykline 返回空 klines, 上游退化后仅剩 TDX 单日——
            # 原固定"最近 10 日"标题配 1 行数据误导)
            _n_avail = len(ff["data"])
            if _n_avail >= 10:
                L("\n  ➤ 60日资金流监控 (最近 10 日):")
            elif _n_avail > 1:
                L(f"\n  ➤ 60日资金流监控 (仅 {_n_avail} 日可用):")
            else:
                L("\n  ➤ 60日资金流监控 (仅当日 1 日可用——历史窗口源暂缺, 单日数据不代表趋势):")

            _recent = ff["data"][:10]

            L(
                f"  {'日期':<12} {'主力净流入(万)':>12} {'超大单(万)':>10} {'大单(万)':>10} {'中单(万)':>10} {'小单(万)':>10}"
            )
            L(f"  {'-'*70}")
            for d in reversed(_recent):
                L(
                    f"  {d['date']:<12} {d['main_net']/1e4:>+12.0f} {d['super_net']/1e4:>+10.0f} {d['large_net']/1e4:>+10.0f} {d['mid_net']/1e4:>+10.0f} {d['small_net']/1e4:>+10.0f}"
                )

            r20 = ff["data"][:20]
            # V17.0.7: 数据不足 5 日时跳过误导性统计(原"近20日统计: 0/1天"无信息量),
            # 仅提示数据受限
            if len(r20) < 5:
                L(
                    "\n  ⚠️ 历史资金流窗口数据受限(<5 日), 趋势统计已跳过; 请以上方单日值结合龙虎榜/两融综合判断"
                )
            else:
                tmain = sum(d["main_net"] for d in r20)
                tdays = sum(1 for d in r20 if d["main_net"] > 0)
                # V16.2.4: 延时镜像域可能只有当日 → 按实际条数标注
                L(
                    f"\n  近20日统计:\n    主力累计净流入: {tmain/1e4:.0f}万元\n    主力净流入天数: {tdays}/{len(r20)}天（实有数据）"
                )
            if len(r20) >= 5:
                if tmain > 0:
                    L("  信号: 主力资金近期净流入 → 偏多")
                elif tmain < 0:
                    L("  信号: 主力资金近期净流出 → 偏空")
                else:
                    L("  信号: 近20日主力资金累计净额为零 → 中性")

    else:
        if ff.get("unverified_date_count"):
            L("  ⚠️ 返回的历史资金流记录未通过日期或交易日校验，历史窗口不展示")
        else:
            L("  (资金流数据获取失败)")

    L("\n" + "---")
    L("## **八、北向资金持仓动态**")
    L("---")

    # V17.0.7: datacenter 五类预取流水线消费端(批量启动时已后台拉取)
    from stock_common.sc_datasource import resolve_datacenter

    nb = await resolve_datacenter(
        'northbound', code, direct_fn=lambda: get_northbound_hold_async(session, code, 20)
    )

    if nb:

        # 北向持股披露为季度频；数据年龄仍按 A 股交易日计数，不把周末和休市日计入。
        _nb_latest = str(nb[0].get("date", "")) if isinstance(nb[0], dict) else ""
        try:
            from stock_common.stock_calendar import trading_day_age

            _nb_age = trading_day_age(datetime.strptime(_nb_latest, "%Y-%m-%d").date())
        except (ValueError, TypeError, NotImplementedError):
            _nb_age = None
        if _nb_age is not None and _nb_age > 10:
            L(
                f"  北向持仓共 {len(nb)} 期（季度频披露, 最新一期 {_nb_latest},"
                f"距今 {_nb_age} 个交易日）:"
            )
        else:
            L(f"  北向持仓近 {len(nb)} 期:")

        L(
            f"  {'日期':<12} {'持股数量(万)':>12} {'持股市值(万)':>12} {'持股占比%':>10} {'变动股数(万)':>12}"
        )
        L(f"  {'-'*65}")

        for d in nb:

            _mcap = d.get('market_cap', 0) or 0

            _ratio = d.get('hold_ratio', 0) or 0

            _shares = d.get('hold_shares', 0) or 0

            if _mcap == 0 and _shares > 0 and price_today > 0:

                _mcap = _shares * price_today

                # V17.3 修正(审查): info.total_shares 单位=万股(== cdata.total_shares_wan), 而 _shares(北向持股)为股;
                # 原 _shares/info.total_shares 股÷万股单位错配(差1e4), 且缺×100百分数口径(与 med 不一致)。
                # 改统一层 cdata.total_shares_wan(万股)*1e4=股, ×100 得百分数, 与 med 同源同口径。
                _ratio = (
                    _shares / (cdata.total_shares_wan * 1e4) * 100
                    if cdata.total_shares_wan > 0
                    else 0
                )

            L(
                f"  {d['date']:<12} {_shares/1e4:>12.0f} {_mcap/1e4:>12.0f} {_ratio:>9.4f}% {d['change_shares']/1e4:>+12.0f}"
            )

    else:
        L("  该股暂无北向资金持仓数据（可能非陆股通标的或数据延迟）")

    L("\n" + "---")
    L("## **九、龙虎榜席位**")
    L("---")

    # 优化时段显示：根据不同市场状态提供更精准的提示
    if _mkt_status == "pre_market":
        L("  ⚠️ 当前为盘前时段，龙虎榜数据为最近一期已发布数据（约16:30后更新）")
    elif _mkt_status in ("morning", "lunch"):
        L("  ⚠️ 当前为盘中时段，龙虎榜数据需收盘后更新，显示的是最近一期已发布数据")
    elif _mkt_status == "afternoon":
        L("  ⚠️ 当前为下午盘，龙虎榜数据约16:30后更新，当前显示的是最近一期已发布数据")
    elif _mkt_status == "post_market":
        L("  ⚠️ 当前为盘后结算时段，龙虎榜数据正在更新中，部分信息可能延迟")
    elif _mkt_status == "post_close":
        L("  ℹ️ 当前为盘后收盘时段，龙虎榜数据为今日已发布数据")
    else:  # closed
        L("  ⚠️ 休市日：数据为最近交易日快照，龙虎榜数据为最近一期已发布")

    # V8.5: lite模式跳过席位详情（V16.1: include_seats 一并关闭，省 2 次 API）
    # V17.0.7: 走 datacenter 预取流水线(批量启动时已后台拉取)
    dtb = await resolve_datacenter(
        'dragon_tiger',
        code,
        direct_fn=lambda: get_dragon_tiger_board_async(
            session,
            code,
            days=_recent_days,
            include_seats=not _dc.get("skip_lhb_detail", False),
            enhance_seats=not _dc.get("skip_lhb_detail", False),
        ),
    )

    if dtb["records"]:

        L(f"  近{_recent_days}个交易日上榜 {len(dtb['records'])} 次:")
        # V17.0.6: 直出 md 表格(原 CJK 对齐空格表依赖脆弱的间隙推断, 常态未转换)
        L("| 日期 | 上榜原因 | 净买入(万) | 换手率 |")
        L("|---|---|---|---|")
        for r in dtb["records"]:
            L(
                f"| {r['date']} | {r.get('reason', '')} | {r['net_buy']:.1f} | {r['turnover']:.2f}% |"
            )

        _cfg = _load_settings()

        _trader_tags = [(k, v) for k, v in _cfg.get("trader_tags", {}).items()]

        def _tag(name):

            for kw, t in _trader_tags:

                if kw in name:
                    return t

            return ""

        seats = dtb["seats"]

        if seats["buy"]:
            # V17.0.2o: 直接 md 表格 4 列(原空格表被旧渲染器破坏)
            L("\n  最近买入席位 TOP5:")
            L("| 营业部名称 | 买入(万) | 卖出(万) | 净额(万) |")
            L("|---|---|---|---|")
            for s in seats["buy"]:
                L(
                    f"| {_tag(s['name'])} {s['name']} | {s['buy_amt']:.1f} | {s['sell_amt']:.1f} | {s['net']:.1f} |"
                )

        if seats["sell"]:
            L("\n  最近卖出席位 TOP5:")
            L("| 营业部名称 | 买入(万) | 卖出(万) | 净额(万) |")
            L("|---|---|---|---|")
            for s in seats["sell"]:
                L(
                    f"| {_tag(s['name'])} {s['name']} | {s['buy_amt']:.1f} | {s['sell_amt']:.1f} | {s['net']:.1f} |"
                )

        inst = dtb["institution"]

        if inst and (inst.get("buy_amt", 0) > 0 or inst.get("sell_amt", 0) > 0):

            L(
                f"\n  机构买卖统计:\n    机构买入金额: {inst['buy_amt']}万元\n    机构卖出金额: {inst['sell_amt']}万元\n    机构净买入: {inst['net_amt']}万元"
            )

        _dt_cfg = _load_settings()

        _dt_trader_tags = _dt_cfg.get("trader_tags", {}) if _dt_cfg else {}

        _all_depts = []

        for _side in ["buy", "sell"]:

            for _s in seats.get(_side, []):

                _sname = str(_s.get("name", ""))

                for _kw, _tg in _dt_trader_tags.items():

                    if _kw in _sname:

                        _all_depts.append((_tg, _sname, _side, _s.get("net", 0)))

                        break

        _lhasa_count = sum(
            1 for _s in seats.get("buy", []) if "东方财富证券拉萨" in str(_s.get("name", ""))
        )

        _lhasa_sell = sum(
            1 for _s in seats.get("sell", []) if "东方财富证券拉萨" in str(_s.get("name", ""))
        )

        L("  ── 游资活跃度诊断 ──")

        if _all_depts:

            # V16.3 J: trader_tags 是席位分类标签（机构/北向/量化/游资/散户），
            # 只有 [游资] 类才叫"著名游资"；机构/北向等单独归类显示
            _buy_tags = [x[0] for x in _all_depts if x[2] == "buy"]

            _sell_tags = [x[0] for x in _all_depts if x[2] == "sell"]

            _youzi_buy = list(dict.fromkeys(t for t in _buy_tags if t == "[游资]"))

            _youzi_sell = list(dict.fromkeys(t for t in _sell_tags if t == "[游资]"))

            _other_buy = [t for t in _buy_tags if t != "[游资]"]

            _other_sell = [t for t in _sell_tags if t != "[游资]"]

            if _youzi_buy:

                L(f"  🟢 著名游资买入: {'、'.join(_youzi_buy)}")

            if _youzi_sell:

                L(f"  🔴 著名游资卖出: {'、'.join(_youzi_sell)}")

            if _other_buy or _other_sell:

                _ob = {t: _buy_tags.count(t) for t in dict.fromkeys(_other_buy)}

                _os = {t: _sell_tags.count(t) for t in dict.fromkeys(_other_sell)}

                L(
                    f"  🏦 其他席位分类: 买入{'、'.join(f'{k}×{v}' for k, v in _ob.items()) if _ob else '无'} | 卖出{'、'.join(f'{k}×{v}' for k, v in _os.items()) if _os else '无'}"
                )

            L("  📊 席位明细:")

            # V17.0.7: 排名标签修复——原硬编码"买五/卖五"(9 报告全批 5 行皆"买五"),
            # 改按买卖方向分别计数(买一~买N / 卖一~卖M)
            _rank_buy = 0
            _rank_sell = 0
            for _tg, _nm, _sd, _nt in _all_depts[:5]:
                if _sd == "buy":
                    _rank_buy += 1
                    _rank_txt = f"买{_rank_buy}"
                else:
                    _rank_sell += 1
                    _rank_txt = f"卖{_rank_sell}"
                L(f"     {_rank_txt} {_tg} {_nm[:20]} 净{_nt:+.1f}万")

        else:

            L("  ℹ️  无著名游资/机构专用席位上榜")

        if _lhasa_count + _lhasa_sell > 0:

            L(
                f"  龙虎榜席位名称匹配“东方财富证券拉萨”：买{_lhasa_count}家 / 卖{_lhasa_sell}家；"
                "此名称标签不能确认账户身份或交易动机。"
            )

        _inst_net = inst.get("net_amt", 0) if inst else 0

        if _all_depts and _inst_net > 0:

            L("  ✅ 综合判断: 机构资金+游资同步关注，资金面积极")

        elif _inst_net > 0:

            L("  ✅ 综合判断: 机构净买入，机构资金关注")

        elif _all_depts and _inst_net < -1000:

            # V17.0.25(2026-09-02) P1-5 修复: 原结论「机构大额卖出 + 游资炒作」仅凭 _all_depts(含北向/机构席位)
            # 即输出, 与审计发现的4份「仅[北向]/[机构]仍称游资炒作」矛盾。须校验确有游资席位(_youzi_buy/_youzi_sell)。
            if _youzi_buy or _youzi_sell:
                L("  ⚠️ 综合判断: 机构大额卖出 + 游资炒作，需谨慎")
            else:
                L("  ⚠️ 综合判断: 机构大额卖出，需谨慎（未见知名游资席位）")

        elif _lhasa_count + _lhasa_sell > 3:

            L(
                f"  龙虎榜出现 {_lhasa_count + _lhasa_sell} 个拉萨名称标签；"
                "仅为席位名称分类，不能据此判断散户占主导或短期波动。"
            )

        # V8.5新增：席位增强分析
        if dtb.get("seat_analysis"):
            sa = dtb["seat_analysis"]
            L("\n  ── 席位增强分析 ──")
            # V17.0.25(2026-09-02) P1-6 配套: 席位全部未匹配到已知游资库时,
            # seat_quality_score=None / premium_signal="unknown" → 显式标注「无法评级」, 不输出伪精确 50 分。
            if sa.get("seat_quality_score") is not None:
                L(f"  席位质量评分: {sa['seat_quality_score']}分")
            else:
                L("  席位质量评分: N/A（龙虎榜席位未匹配到已知游资库，无法评级）")
            if sa.get("premium_signal"):
                _signal_map = {
                    "buy_high": "✅ 强势买入信号，游资抢筹意愿强烈，短线关注",
                    "sell_high": "⚠️ 强势卖出信号，游资集中出货，注意回调风险",
                    "sell_caution": "⚠️ 卖出警示，卖方力量占优，建议观望",
                    "neutral": "➖ 中性评级，价格已透支，此时追涨性价比低",
                    "unknown": "⚪ 数据不足（无已知游资席位，暂不评级）",
                }
                _signal_text = _signal_map.get(sa['premium_signal'], sa['premium_signal'])
                L(f"  溢价信号: {_signal_text}")
            if sa.get("legend_count"):
                L(f"  顶级游资席位: {sa['legend_count']}家")
            if sa.get("buy_seats_analysis"):
                notable_buyers = [s for s in sa["buy_seats_analysis"] if s.get("short_name")]
                if notable_buyers:
                    L(f"  买方知名席位: {'、'.join([s['short_name'] for s in notable_buyers])}")
            if sa.get("sell_seats_analysis"):
                notable_sellers = [s for s in sa["sell_seats_analysis"] if s.get("short_name")]
                if notable_sellers:
                    L(f"  卖方知名席位: {'、'.join([s['short_name'] for s in notable_sellers])}")

    else:
        L(
            f"  近{_recent_days}个交易日无龙虎榜记录（白马蓝筹或近期未触发异动标准的个股，无龙虎榜属正常现象）"
        )

    L("\n" + "---")
    L("## **十、限售解禁日历**")
    L("---")

    lockup = await resolve_datacenter(
        'lockup',
        code,
        direct_fn=lambda: get_lockup_expiry_async(session, code, days=90, include_history=True),
    )

    rh = [h for h in lockup["history"] if _30_trade_start_str <= h["date"] <= today_str]

    if rh:

        L(f"  近30个交易日解禁 {len(rh)} 批:")
        L(f"  {'日期':<12} {'类型':<30} {'数量类型及数量':>22} {'来源占比%':>9}")
        L(f"  {'-'*65}")

        for h in rh:
            amount_label = "实际可流通" if h.get("shares_is_actual") is True else "公告解禁量"
            L(
                f"  {h['date']:<12} {str(h['type'])[:30]:<30} {amount_label} {h['shares']/1e4:>8.0f}万股"
                f" {h['ratio']:>8.2f}% {'🔴' if h['ratio']>_unlock_ratio_warn else ('🟡' if h['ratio']>1 else '🟢')}"
            )

    elif lockup["history"]:
        L(f"  近30个交易日内无解禁（共 {len(lockup['history'])} 批历史记录，已省略）")

    else:
        L("  当前查询未返回历史解禁记录；不能据此确认近期不存在解禁。")

    if lockup["upcoming"]:

        L(f"\n  未来{_unlock_warn}天待解禁 {len(lockup['upcoming'])} 批: ⚠️")

        for h in lockup["upcoming"]:
            amount_label = "实际可流通" if h.get("shares_is_actual") is True else "公告解禁量"
            L(
                f"    {h['date']}: {str(h['type'])} {amount_label}={h['shares']/1e4:.0f}万股"
                f" 来源占比={h['ratio']:.2f}% 压力:{'🔴高' if h['ratio']>_unlock_ratio_warn else ('🟡中' if h['ratio']>1 else '🟢低')}"
            )

    else:
        L(f"\n  当前查询未返回未来{_unlock_warn}天解禁记录；空结果不等于确认没有解禁压力。")

    L("\n" + "---")
    L("## 【十一、融资融券（两融数据）】")
    L("---")

    if _dc.get("skip_margin_detail"):
        L("  [lite模式] 跳过详细数据")
        margin = []
    else:
        margin = await resolve_datacenter(
            'margin', code, direct_fn=lambda: get_margin_trading_async(session, code)
        )

    if margin and isinstance(margin, list):
        # V17.0.9: isinstance 防御——批量预取偶发返回 dict(非 list)时跳过
        # (300475 2026-08-27 批量实测 TypeError: string indices must be integers)

        _latest_margin = margin[0] if isinstance(margin[0], dict) else {}
        _latest_margin_date = str(_latest_margin.get("date") or "").strip()[:10]
        _margin_age_note = "有效日期未确认"
        if _latest_margin_date:
            try:
                from stock_common.stock_calendar import trading_day_age

                _margin_age = trading_day_age(date.fromisoformat(_latest_margin_date))
                if _margin_age == 0:
                    _margin_age_note = "与当前行情基准日一致"
                elif _margin_age > 0:
                    _margin_age_note = f"滞后 {_margin_age} 个交易日"
                else:
                    _margin_age_note = "晚于当前行情基准日，需复核"
            except (TypeError, ValueError, NotImplementedError) as _e:
                _debug_log(f"sht margin date age ({code}): {_e}")
        L(
            f"  最近 {len(margin)} 条两融记录（最新日期 {_latest_margin_date or '未提供'}；{_margin_age_note}）:"
        )
        L(
            f"  {'日期':<12} {'融资余额(万)':>10} {'融资买入(万)':>10} {'融资偿还(万)':>10} {'融券余额(万)':>10}"
        )
        L(f"  {'-'*70}")

        # V17.0.7: 修复标签与行数不一致——原循环 [:10] 截断但标题写 len(margin)(=15)
        for d in margin:
            L(
                f"  {d['date']:<12} {d['rzye']/1e4:>14.0f} {d['rzmre']/1e4:>14.0f} {d['rzche']/1e4:>14.0f} {d['rqye']/1e4:>14.0f}"
            )

        _amt = _safe_float(q.get("amount_wan")) * 1e4 if q else 0
        _latest_rzmre = _safe_float(_latest_margin.get("rzmre"))
        _quote_date = str(
            (q.get("quote_date") if q else "") or getattr(cdata, "quote_date", "") or ""
        ).strip()[:10]
        _quote_date_key = _quote_date.replace("-", "")[:8]
        _margin_date_key = _latest_margin_date.replace("-", "")[:8]

        if _amt > 0 and _latest_rzmre > 0:
            if _quote_date_key and _quote_date_key == _margin_date_key:
                _rz_ratio = _latest_rzmre / _amt * 100
                if _rz_ratio > 20:
                    L(
                        f"  融资买入额占同日成交额 {_rz_ratio:.1f}%（仅作成交额占比观察，"
                        "不代表资金主体或价格方向）"
                    )
            else:
                L(
                    "  未计算融资买入额/成交额：两融样本日期 "
                    f"{_latest_margin_date or '未提供'} 与行情有效日期 {_quote_date or '未确认'} 未匹配。"
                )

        if len(margin) >= 3:
            _rq_comparisons = min(3, len(margin) - 1)
            _rq_up = sum(
                1
                for i in range(_rq_comparisons)
                if _safe_float(margin[i].get("rqye")) > _safe_float(margin[i + 1].get("rqye"))
            )
            if _rq_up >= 2:
                L(
                    f"  融券余额在最近 {_rq_comparisons} 次相邻样本比较中上升 {_rq_up} 次；"
                    "余额变化不能单独证明新增做空或未来抛压。"
                )

    else:
        L("  本次未取得有效两融样本；无法据此判断该股是否为两融标的。")

    L("\n" + "---")
    L("## **十二、大宗交易**")
    L("---")

    if _dc.get("skip_block_trade_detail"):
        L("  [lite模式] 跳过详细数据")
        bt = []
        rbt = []
    else:
        bt = await resolve_datacenter(
            'block_trade', code, direct_fn=lambda: get_block_trade_async(session, code)
        )
        rbt = [d for d in bt if d["date"] >= _30_trade_start_str]

    if rbt:

        L(f"  近30个交易日共 {len(rbt)} 笔大宗交易:")
        # V17.0.2m: md 表格 7 列(原空格表"成交量万+买方"1 空格粘连合并列)
        L("| 日期 | 成交价 | 收盘价 | 溢价% | 成交量(万股) | 买方 | 卖方 |")
        L("|---|---|---|---|---|---|---|")
        for d in rbt:
            L(
                f"| {d['date']} | {d['price']:.2f} | {d['close']:.2f} | {d['premium_pct']:+.2f}% | {d['vol']/1e4 if d['vol'] else 0:.0f} | {d['buyer']} | {d['seller']} |"
            )

    elif bt:
        L(f"  近30个交易日内无大宗交易（共 {len(bt)} 笔历史记录，已省略）")

    else:
        L("  无大宗交易记录")

    L("\n" + "---")
    L("## **十三、股东户数变化**")
    L("---")

    if _dc.get("skip_holder_history"):
        L("  [lite/medium模式] 跳过详细历史")
        holders = []
    else:
        holders = await holder_change_async(session, code)

    # V17.0.14: 筹码分布 CYQ —— 提前获取(东财 kline f61 → calculate_cyq), 供章节+评分复用
    _cyq_dict = {}
    try:
        from stock_common.sc_datasource import get_cyq_distribution

        _cyq_dict = await asyncio.to_thread(get_cyq_distribution, code) or {}
    except Exception as _e:
        _debug_log(f"sht cyq ({code}): {_e}")

    if holders:

        ld3 = holders[0]["date"]

        try:
            from stock_common.stock_calendar import trading_day_age

            _holder_age = trading_day_age(datetime.strptime(ld3, "%Y-%m-%d").date())
        except (ValueError, NotImplementedError):
            _holder_age = None
        if _holder_age is not None and _holder_age > 90:
            L(f"  ⚠️ 数据距今已 {_holder_age} 个交易日，尚未更新至最新报告期")

        L(f"  {'截止日期':<14} {'股东户数':>7} {'环比变化':>10} {'环比%':>8}")
        L(f"  {'-'*50}")

        for h in holders[:5]:
            _cr = h.get('change_ratio', 0)
            # 边界检查：变化率超过±500%视为异常数据，不显示
            _cr_disp = _cr if abs(_cr) <= 500 else (999.99 if _cr > 500 else -999.99)
            _cr_flag = " ⚠️" if abs(_cr) > 500 else ""
            L(
                f"  {h['date']:<14} {h['holder_num']:>10,} {h['change_num']:>+14,} {_cr_disp:>+9.2f}%{_cr_flag}"
            )

        if len(holders) >= 2:

            lh = holders[0]
            ph = holders[1]

            if lh["change_ratio"] < 0 and ph["change_ratio"] < 0:
                sig = "股东户数连续下降；持股分布可能趋于集中，但无法识别买方主体，不代表主力吸筹"

            elif lh["change_ratio"] < 0:
                sig = "股东户数下降；仅说明持有人数量减少，不据此判断资金主体"

            else:
                sig = "股东户数上升；仅说明持有人数量增加，不据此判断散户化或卖压"

            L(f"\n  ➤ 信号: {sig}")

    else:
        L("  股东户数数据获取失败")

    # V17.0.14: 筹码分布 CYQ 章节(东财 kline f61 → calculate_cyq)
    # V17.0.17 修复: 源空时渲染可见告警占位, 不再整章静默跳过(重演 V17.0 已修的 M1/M4 假空白章节反模式)
    L("\n" + "---")
    L("## **十四、筹码分布（成本集中度）**")
    L("---")
    if _cyq_dict:
        _ben = _cyq_dict.get("benefit_pct", 0.0) or 0.0
        _c90 = _cyq_dict.get("concentration_90", 0.0) or 0.0
        _c70 = _cyq_dict.get("concentration_70", 0.0) or 0.0
        _avg = _cyq_dict.get("avg_cost", 0.0) or 0.0
        L(f"  - 获利盘比例: {_ben*100:.1f}%（现价下持仓盈利占比）")
        L(f"  - 平均成本: {_avg:.2f} 元")
        L(
            f"  - 90% 筹码集中度: {_c90:.3f}（成本区间 {_cyq_dict.get('cost_90_low',0):.2f}~{_cyq_dict.get('cost_90_high',0):.2f}）"
        )
        L(
            f"  - 70% 筹码集中度: {_c70:.3f}（成本区间 {_cyq_dict.get('cost_70_low',0):.2f}~{_cyq_dict.get('cost_70_high',0):.2f}）"
        )
        _cflag = (
            "高度集中"
            if _c90 < 0.12
            else ("较集中" if _c90 < 0.2 else ("分散" if _c90 > 0.35 else "中性"))
        )
        _pflag = (
            "获利盘丰厚，上方解套抛压需关注"
            if _ben > 0.85
            else ("套牢盘较重，反弹承压" if _ben < 0.25 else "成本结构均衡")
        )
        L(f"  ➤ 研判: 筹码{_cflag}；{_pflag}")
    else:
        # 返回空也可能由样本不足等原因导致；不将其直接归因为源故障。
        L("  ⚠️ 未取得可计算的K线/CYQ数据，成本集中度维度暂缺；不能据此判断筹码分布。")

    L("\n" + "---")
    L("## **十五、短线情绪与事件催化**")
    L("---")

    # 东财个股新闻（近7日）
    try:
        stock_news = await asyncio.to_thread(get_eastmoney_stock_news, code, page_size=10)
        _news_shown = 0
        for item in stock_news:
            title = str(item.get("title", "")).strip()
            pub_time = str(item.get("publish_time", ""))[:10]
            if title and pub_time:
                try:
                    from datetime import datetime as _dt

                    pub_date = _dt.strptime(pub_time, "%Y-%m-%d")
                    if (_dt.now() - pub_date).days > 7:
                        continue
                except (ValueError, TypeError):
                    pass
                L(f"    · [{pub_time}] {title[:80]}")
                _news_shown += 1
                if _news_shown >= 7:
                    break
        if _news_shown == 0:
            L("    近7日暂无相关个股新闻")
    except Exception as _e:
        _debug_log(f"sht news_fetch: {_e}")
        L("    (新闻获取失败)")

    # 财联社快讯（近420分钟=7小时）— V16.1: 同步包 to_thread
    try:
        cls_news = await asyncio.to_thread(cls_telegraph, page_size=50)
        _cls_shown = 0
        _cutoff = datetime.now() - timedelta(hours=48)  # V16.2.14: 7h→48h
        for item in cls_news:
            t_str = str(item.get("time", ""))
            if t_str:
                try:
                    pub_dt = datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S")
                    if pub_dt < _cutoff:
                        continue
                except (ValueError, TypeError):
                    pass
            title = str(item.get("title", "")).strip()
            # V16.2.3: 快讯必须与个股相关（代码/名称/简称），否则跳过（原直接展示全市场快讯）
            if title and news_matches_stock(title, code, stock_name):
                L(f"    · [{t_str[:16]}] {title[:80]}")
                _cls_shown += 1
                if _cls_shown >= 10:
                    break
        if _cls_shown == 0:
            L("    近48小时无个股相关快讯")
    except Exception as _e:
        _debug_log(f"sht cls_telegraph: {_e}")

    # 同花顺热榜 — V16.1: 同步包 to_thread
    try:
        hot_all = await asyncio.to_thread(ths_hot_list, "hour")
        in_hot = next((h for h in hot_all if h.get("code") == code), None)
        if in_hot:
            L(f"    🔥 同花顺热榜 #{in_hot['rank']}  热度值 {in_hot['heat']:,.0f}")
    except Exception as _e:
        _debug_log(f"ths_hot_list error: {_e}")

    # 互动易问答（近48小时）— V16.1: 同步包 to_thread；V16.2.14: 48h+标题+答案+合理条数
    try:
        irm = await asyncio.to_thread(get_irm_qa, code, 30)
        L("\n    近48小时互动易问答:")
        _irm_shown = 0
        _irm_cutoff = datetime.now() - timedelta(hours=48)
        for item in irm:
            t_str = str(item.get("ask_time", ""))
            if t_str:
                try:
                    pub_dt = datetime.strptime(t_str, "%Y-%m-%d %H:%M")
                    if pub_dt < _irm_cutoff:
                        continue
                except (ValueError, TypeError):
                    pass
            irm_q = str(item.get("question", "")).strip()[:120]
            if irm_q:
                # V17.0.7: answer=None 时 str(None)="None" 被当有效文本展示(实测
                # 300059/002156 报告出现"答案: None")——None/空/"none"统一视为待回复
                _irm_raw = item.get("answer")
                irm_a = "" if _irm_raw is None else str(_irm_raw).strip()
                if irm_a.lower() == "none":
                    irm_a = ""
                _ans_part = f"答案: {irm_a[:120]}" if irm_a else "答案: （公司待回复）"
                L(f"    · [{t_str[:16]}] 提问: {irm_q}")
                L(f"        {_ans_part}")
                _irm_shown += 1
                if _irm_shown >= 10:
                    L(f"    （近48小时共 {len(irm)} 条中最新 10 条）")
                    break
        if _irm_shown == 0:
            L("    近48小时暂无互动易问答")
    except Exception as _e:
        _debug_log(f"sht cninfo_irm: {_e}")

    L("\n  ➤ 近7日巨潮实质性重大公告:")

    if _dc.get("skip_announcement_detail"):
        L("  [lite模式] 跳过详细公告")
        anns = []
    else:
        anns = await get_strategic_announcements_async(session, code, days=7)

    if anns:

        for i, a in enumerate(anns, 1):

            fl = " ⚠️" if any(k in a["title"] for k in ["减持", "立案", "严重异动"]) else ""

            tt = f" [{a['type']}]" if a['type'] else ""

            L(f"  {i}. [{a['date']}]{tt} {a['title']}{fl}")

        rc = sum(1 for a in anns if "减持" in a["title"])

        if rc > 0:
            L(f"    ⚠️ 减持预警：近7日有 {rc} 条减持相关公告，请注意风险。")

    else:
        L("  近7日暂无触及关键词的重大公告")

    # ── 打板分析 ── V16.1: 同步包 to_thread
    L("\n  ➤ 打板与涨停分析:")
    try:
        from stock_common import get_limit_pool_summary

        pool = await asyncio.to_thread(get_limit_pool_summary)
        zt_count = pool.get("limit_up_count", 0)
        zb_count = pool.get("limit_broken_count", 0)
        # V17.3 修复: 跌停池接口(pool.limit_down_count)偶发返回 stale T-1 数据(实测 33 篇 sht 报 3 只,
        # 而 mak A 段用全市场实时涨跌幅口径(is_limit_down)得 0 只)。为与 mak 同源同口径,
        # 优先采用实时涨跌幅口径, 仅在实时源不可用时回退 pool。
        _dt_count_pool = pool.get("limit_down_count", 0)
        try:
            from core.tdx_client import tdx_get_market_abnormal_data
            from stock_common import is_limit_down

            _abn = tdx_get_market_abnormal_data()
            if _abn:
                dt_count = sum(
                    1
                    for s in _abn
                    if is_limit_down(
                        str(s.get("code", "")),
                        str(s.get("name", "") or ""),
                        _safe_float(s.get("change_pct", 0)),
                    )
                )  # 实时口径优先(与 mak A 段 _dt_count 同源)
            else:
                dt_count = _dt_count_pool
        except Exception as _e:
            _debug_log(f"sht dt realtime: {_e}")
            dt_count = _dt_count_pool
        success_rate = pool.get("success_rate", 0)
        L(
            f"    今日涨停 {zt_count} 只 | 炸板 {zb_count} 只 | 跌停 {dt_count} 只 | 封板率 {success_rate:.0f}%"
        )

        # V17.2.0: 全市场广度(通达信统计指数)交叉校验打板池口径
        try:
            from core.tdx_client import tdx_get_market_stat

            _ms = await asyncio.to_thread(tdx_get_market_stat)
            if _ms:
                L(
                    f"    全市场(通达信): 涨停{_ms['limit_up_count']}/跌停{_ms['limit_down_count']}"
                    f" | 上涨{_ms['up_count']}/下跌{_ms['down_count']}"
                    f" | 停牌{_ms['suspended_count']} | 总市值{_ms['total_market_cap']/1e12:.2f}万亿"
                )
        except Exception as _e:
            _debug_log(f"sht market stat: {_e}")

        # 检查当前股票是否在涨停池/炸板池中
        # V17.0.1g/h: 叠加同花顺增强字段(涨停原因/板型/封板率/炸板次数/换手/流通市值/市场类型/回封)
        for item in pool.get("limit_up_list", []):
            if item.get("code") == code:
                _extra = ""
                if item.get("reason"):
                    _extra += f" 原因:{item['reason']}"
                if item.get("board_type"):
                    _extra += f" 板型:{item['board_type']}"
                if item.get("seal_rate"):
                    _extra += f" 封板率:{_safe_float(item['seal_rate'])*100:.0f}%"
                if item.get("break_times"):
                    _extra += f" 炸板{item['break_times']}次"
                if item.get("first_time"):
                    _extra += f" 首封{item['first_time']}"
                if item.get("last_time"):
                    _extra += f" 末封{item['last_time']}"
                if item.get("is_again"):
                    _extra += " 回封板"
                _mt = item.get("market_type", "")
                if _mt in ("GEM", "USTM", "KCB"):
                    _extra += f" {_mt}(20/30cm 高波动)"
                if item.get("turnover_rate"):
                    _extra += f" 换手{_safe_float(item['turnover_rate']):.1f}%"
                if item.get("currency_value"):
                    _cv = _safe_float(item['currency_value']) / 1e8
                    _extra += f" 流通{_cv:.0f}亿"
                if item.get("order_volume"):
                    _extra += f" 封单量{_safe_float(item['order_volume'])/1e4:.0f}万股"
                _lf = item.get('limit_fund', 0) or 0
                if _lf >= 1e8:
                    _lf_txt = f"{_lf/1e8:.2f}亿"
                elif _lf >= 1e4:
                    _lf_txt = f"{_lf/1e4:.0f}万"
                else:
                    _lf_txt = f"{_lf:.0f}"
                _sector_name = item.get("sector") or "板块信息未提供"
                L(
                    f"    📌 当前股票在涨停池中！连板{item.get('limit_count',0)} 板块:{_sector_name} 封单额:{_lf_txt}元{_extra}"
                )
                break
        for item in pool.get("limit_broken_list", []):
            if item.get("code") == code:
                _sector_name = item.get("sector") or "板块信息未提供"
                L(f"    ⚠️ 当前股票炸板！炸板次数:{item.get('broken_count',0)} 板块:{_sector_name}")
                break

        # 涨停板块分布（前5）
        sector_stats = pool.get("sector_stats", {})
        if sector_stats:
            _missing_sector_count = sector_stats.get("板块信息未提供", sector_stats.get("其他", 0))
            top_sectors = [
                (name, count)
                for name, count in sector_stats.items()
                if name not in ("板块信息未提供", "其他")
            ][:5]
            if top_sectors:
                L(f"    涨停板块分布: {' | '.join(f'{k}({v})' for k,v in top_sectors)}")
            if _missing_sector_count:
                if top_sectors:
                    L(f"    行业分类未取得: {_missing_sector_count} 只（不计入板块分布）")
                else:
                    L(f"    涨停板块分布暂缺: {_missing_sector_count} 只涨停股的上游行业字段未提供")

        # V16.1: 昨日涨停池晋级率/赚钱效应（push2ex getYesterdayZTPool）
        # MEDIUM(审查 2026-08-16): 同步 HTTP 包 to_thread
        try:
            from stock_common import get_yesterday_limit_pool

            yzt = await asyncio.to_thread(get_yesterday_limit_pool)
            if yzt:
                yzt_total = len(yzt)
                # 晋级 = 今日仍涨停（统一 is_limit_up 判断，含北交所 30%）
                yzt_promoted = [
                    s
                    for s in yzt
                    if is_limit_up(
                        str(s.get("code", "")), s.get("name", ""), s.get("change_pct", 0)
                    )
                ]
                yzt_avg_pct = sum(s.get("change_pct", 0) for s in yzt) / yzt_total
                promotion_rate = len(yzt_promoted) / yzt_total * 100 if yzt_total else 0
                L(
                    f"    昨日涨停 {yzt_total} 只 → 今日晋级(仍涨停) {len(yzt_promoted)} 只，晋级率 {promotion_rate:.0f}%，平均涨幅 {yzt_avg_pct:+.1f}%"
                )
                # 当前股票是否在昨日涨停池（看今日承接）
                for item in yzt:
                    if item.get("code") == code:
                        L(
                            f"    📌 当前股票为昨日涨停股（昨连板{item.get('y_limit_count',0)}板），今日涨幅 {item.get('change_pct',0):+.2f}% 振幅{item.get('amplitude_pct',0):.1f}%"
                        )
                        break
        except Exception as _e2:
            _debug_log(f"sht yzt_pool: {_e2}")
    except Exception as _e:
        _debug_log(f"sht limit_pool: {_e}")
        L("    (打板数据获取失败)")

    # V16.1.7: AxData 短线指标（字典 §12.12.1，消费项目 zhb.zip）
    # V17.0.1f(2026-08-16): 移除盘口异动 4 类扫描——push2ex 接口必要性不成立,
    # 用户原则: 5 大脚本不扩张东财 push 接口; 该数据无增量价值, 不再采集
    try:
        from stock_common import get_shortline_indicators

        # AxData 短线指标 34 字段（消费项目 zhb.zip，零下载）
        try:
            _sl = await asyncio.to_thread(get_shortline_indicators, code)
            if _sl:
                _parts = []
                if _sl.get("open_volume_ratio"):
                    _parts.append(f"开盘量比{_sl['open_volume_ratio']:.2f}")
                if _sl.get("auction_prev_volume_ratio"):
                    # V17.0.30(2026-09-02) 标签订正: 原标为「竞价昨比」, 但实测 32 份报告中
                    # 该值 == fuyao「竞价量比」31/32(唯一不等的 688305 为 0.44 vs 0.43 舍入差),
                    # 而与 fuyao「竞价昨比」归一化后 0/32 相同(如 000657: 本值5.20 / fuyao昨比149%)
                    # → 本字段实为**竞价量比**(字段名 auction_prev_volume_ratio 的 prev 系误导)。
                    # 原标签导致同一份报告 ZHB 段与 fuyao 段出现两个「竞价昨比」且数值矛盾。
                    _parts.append(f"竞价量比{_sl['auction_prev_volume_ratio']:.2f}")
                if (
                    _sl.get("seal_to_float_ratio") is not None
                    and _sl.get("seal_to_float_ratio", 0) > 0
                ):
                    # V17.0.2: 极小封流比(0.002%)无展示意义——过滤 <0.01%
                    if _sl["seal_to_float_ratio"] * 100 >= 0.01:
                        _parts.append(f"封流比{_sl['seal_to_float_ratio']*100:.2f}%")
                if _sl.get("limit_board_text"):
                    _parts.append(f"几天几板:{_sl['limit_board_text']}")
                if _sl.get("limit_up_streak_days"):
                    _parts.append(f"连板{_sl['limit_up_streak_days']}")
                if _sl.get("year_limit_up_days"):
                    _parts.append(f"年涨停{_sl['year_limit_up_days']}次")
                if _parts:
                    L(f"    📐 短线指标(ZHB同源): {' | '.join(_parts)}")
                # V17.0.5 P0: fuyao 竞价实时族(live)——与 ZHB T-1 同源互锁(19/19), 盘中时效升级
                try:
                    _auc = await asyncio.to_thread(get_fuyao_auction_snapshot, [code], "live") or []
                    if _auc:
                        _a = _auc[0]
                        _aparts = []
                        if _a.get("auction_unmatched") is not None:
                            _um = _a["auction_unmatched"]
                            _dir = "买盘未成交完(承接强)" if _um > 0 else "卖压未消化"
                            _aparts.append(f"未匹配量{_um:+.0f}手({_dir})")
                        if _a.get("auction_yesterday_ratio_pct") is not None:
                            # V17.0.24(2026-09-02) 修正: 实测该字段返回**比值**而非百分数——
                            # 000657=1.4875 / 600410=2.6442 / 300059=0.5931(与同族 auction_volume_ratio
                            # 同为量比口径, 键名 _pct 系上游误导命名)。原代码直接按百分数比较
                            # (<50 / >120) 并以 .0f% 渲染 → 全部样本恒落 <50 分支,
                            # 2026-09-01 32/32 份报告误报「缩量高开诱多风险」, 且 >120 放量分支为死代码。
                            # 修正: ×100 归一成百分数后再判阈值(保留原 50%/120% 语义)。
                            _yr = _a["auction_yesterday_ratio_pct"] * 100.0
                            if _yr < 50:
                                _aparts.append(f"竞价昨比{_yr:.0f}%⚠️缩量高开诱多风险")
                            elif _yr > 120:
                                _aparts.append(f"竞价昨比{_yr:.0f}%放量")
                            else:
                                _aparts.append(f"竞价昨比{_yr:.0f}%")
                        if _a.get("auction_volume_ratio") is not None:
                            _aparts.append(f"竞价量比{_a['auction_volume_ratio']:.2f}")
                        if _aparts:
                            L(f"    ⚡ 竞价实时(fuyao): {' | '.join(_aparts)}")
                except Exception as _e3:
                    _debug_log(f"sht fuyao auction: {_e3}")

                # V17.0.5 P1: 官方风向标标签直采(高开/放量等——免自建阈值)
                try:
                    _bl = await asyncio.to_thread(get_fuyao_auction_benchmark)
                    _be = next((b for b in (_bl or []) if str(b.get("ticker")) == code), None)
                    if _be and _be.get("tags"):
                        L(
                            f"    🏷️ 官方风向标标签: {'/'.join(str(x) for x in _be['tags'])}"
                            f"（竞价 {_be.get('auction_pct', 0):+.2f}%）"
                        )
                except Exception as _e4:
                    _debug_log(f"sht fuyao benchmark: {_e4}")

        except Exception as _e:
            _debug_log(f"sht shortline_indicators: {_e}")
    except Exception as _e:
        _debug_log(f"sht changes/shortline: {_e}")

    # V17.0.5 P1: 异动解读(fuyao AI 分析文本——替代 V17.0.2 移除的盘口异动扫描语义层)
    try:
        from stock_common import get_fuyao_anomaly as _f_ano, is_fuyao_enabled

        if is_fuyao_enabled():
            _ano = await asyncio.to_thread(_f_ano, code)
            if _ano:
                _a0 = _ano[0]
                _raw_content = " ".join(str(_a0.get("analysis_content", "")).split())
                _body_end = len(_raw_content)
                for _marker in (
                    "免责声明",
                    "以上内容仅供参考",
                    "仅供参考，不构成投资建议",
                    "仅供参考",
                ):
                    _marker_pos = _raw_content.find(_marker)
                    if _marker_pos >= 0:
                        _body_end = min(_body_end, _marker_pos)
                _content = _raw_content[:_body_end].strip()
                if len(_content) > 300:
                    _content = _content[:300].rstrip() + "…"
                L(f"\n  🔍 异动解读(fuyao AI, 标签:{_a0.get('tag_name', '')}):")
                if _content:
                    L(f"    {_content}")
                else:
                    L("    （上游未提供可展示的解读正文）")
                L("    ℹ️ AI 整理内容仅供参考，不构成投资建议；事实以公司公告为准。")
                if _a0.get("keyword_list"):
                    L(f"    关键词: {'、'.join(str(k) for k in _a0['keyword_list'][:6])}")
    except Exception as _e:
        _debug_log(f"sht fuyao anomaly: {_e}")

    L("\n" + "---")
    L("## **十六、综合信号汇总**")
    L("---")

    signals = []

    lu2 = q.get("limit_up", 0) if q else 0
    b1v2 = q.get("bid1_vol", 0) if q else 0
    np3 = q.get("price", 0) if q else 0

    is_lu2 = lu2 > 0 and abs(np3 - lu2) / lu2 < 0.005

    _lu = q.get("limit_up", 0) if q else 0
    _ld = q.get("limit_down", 0) if q else 0

    _hi = q.get("high", 0) if q else 0
    _lo = q.get("low", 0) if q else 0
    _chg = q.get("change_pct", 0) if q else 0

    if _lu > 0 and _hi >= _lu * 0.98 and _chg < -15:

        signals.append(
            f"⚠️ 天地板预警：今日最高触及涨停({_hi:.2f})后暴跌至{price_today:.2f}，单日振幅{(_hi-_lo)/_hi*100:.1f}%，极端风险！"
        )

    elif _ld > 0 and _lo <= _ld * 1.02 and _chg > 10:

        signals.append(
            f"⚠️ 地天板预警：今日最低触及跌停({_lo:.2f})后拉升至{price_today:.2f}，分歧巨大！"
        )

    if is_lu2 and b1v2 > 0:

        fa2 = b1v2 * lu2 / 1e8
        fr2 = fa2 / (q.get("mcap_yi", 0) or 1) * 100

        if fa2 >= 0.1 or fr2 > 0.5:

            if fr2 > _lo_strong:
                signals.append(f"🔥 封单占比流通市值 {fr2:.1f}% (>{_lo_strong}%)，主力封板力度极强")

            elif fr2 > _lo_mid:
                signals.append(f"✅ 封单质量良好，封单占比流通市值 {fr2:.1f}%")

    if q and price_today > 0:

        if q.get("change_pct", 0) > _limit_chg and price_today >= q.get("limit_up", 0) * 0.995:
            signals.append("🚀 强势涨停，封单密实，短线溢价预期强烈")

        elif q.get("change_pct", 0) > _near_limit:
            signals.append(f"📈 今日涨幅 {q.get('change_pct',0):.1f}%，逼近涨停，短线动能充沛")

    if q and is_lu2 and b1v2 > 0:

        _tamt = q.get("amount_wan", 0) * 1e4

        if _tamt > 0:

            _cr = (b1v2 * lu2) / _tamt

            if _cr < _seal_ratio_warn:
                signals.append(
                    f"⚠️ 封单预警：封单额仅占今日成交额 {_cr*100:.1f}%，弱势烂板，极易炸板悶杀"
                )
    # V17.0.5 P0: 封单衰减率信号(fuyao 官方口径——峰值→现值)
    if _seal_info and _seal_info.get("seal_decay_ratio") is not None:
        _dec_pct = _seal_info["seal_decay_ratio"] * 100
        if _dec_pct < 30:
            signals.append(
                f"⚠️ 封单衰减率 {_dec_pct:.0f}%（峰值 {(_seal_info['max_seal_money'] or 0)/1e8:.1f}亿）——烂板，次日溢价预期转弱"
            )
        elif _dec_pct >= 90:
            signals.append(
                f"🔥 封单全日封死（衰减率 {_dec_pct:.0f}%）——封板质量极高，动能延续概率大"
            )

    if nb and len(nb) >= 2:

        chg = nb[0]["hold_shares"] - nb[-1]["hold_shares"]

        if chg > 0:
            signals.append(f"北向资金近{len(nb)}日净增持，外资看多信号")

    if ff["data"] and len(ff["data"]) >= 20:
        # V16.4.1: ff 数据最新在前(实测 [0]=今日)——原 [-20:] 取最旧 20 日, 近20日统计全错
        _ff_data = ff["data"][:20]
        if _ff_data and isinstance(_ff_data[0], dict):
            tmain2 = sum(d.get("main_net", 0) for d in _ff_data)
        else:
            tmain2 = sum(_ff_data) if _ff_data else 0
        if tmain2 > 0:
            signals.append(f"近20日主力累计净流入 {tmain2/1e8:.2f}亿，中线资金面偏多")
        else:
            signals.append(f"近20日主力净流出 {abs(tmain2)/1e8:.2f}亿，中线资金面偏空")

    if margin and len(margin) >= 5:

        _rzye_trend = sum(1 for i in range(4) if margin[i]["rzye"] > margin[i + 1]["rzye"])

        _rqye_trend = sum(1 for i in range(4) if margin[i]["rqye"] > margin[i + 1]["rqye"])

        if _rzye_trend >= 3 and _rqye_trend <= 1:
            signals.append(
                "两融余额观察：近5条样本中融资余额环比上升 "
                f"{_rzye_trend}/4 次、融券余额环比上升 {_rqye_trend}/4 次；"
                "仅描述余额变化，不据此推断逼空、参与者身份或后续走势。"
            )

    if rr and len(rr) >= 3 and q and abs(q.get("change_pct", 0)) > 5:

        _buy_ratings = sum(
            1
            for r in rr
            if "买入" in str(r.get("emRatingName", "")) or "推荐" in str(r.get("emRatingName", ""))
        )

        if _buy_ratings >= 3:

            signals.append(
                f"💡 交易员笔记：短线高位突发{_buy_ratings}篇券商买入/推荐评级，卖方在摇旗呐喊，谨防游资借利好兑现见顶闷杀"
            )

    if dtb["records"]:

        tn = sum(r["net_buy"] for r in dtb["records"])

        _rd_label = f"近{_recent_days}个交易日"
        signals.append(
            f"{_rd_label}龙虎榜净买入合计 {tn:.0f}万元，上榜 {len(dtb['records'])} 次，股性活跃"
        )

        inst2 = dtb["institution"]

        _lhasa = sum(1 for s in dtb["seats"]["buy"] if "东方财富证券拉萨" in s["name"])

        if _lhasa >= 3:

            signals.append(
                f"龙虎榜买方有 {_lhasa} 个席位名称匹配“东方财富证券拉萨”；"
                "该名称分类不能证明纯散户交易、对倒或筹码松动。"
            )

        if inst2 and inst2.get("net_amt", 0) > 0:
            signals.append(f"龙虎榜机构净买入 {inst2['net_amt']}万元，机构资金关注")

    if holders and len(holders) >= 2 and holders[0]["change_ratio"] < 0:

        signals.append(
            f"股东户数环比减少 {abs(holders[0]['change_ratio']):.1f}%；"
            "仅为披露户数变化，不能单独判定筹码集中或买方主体。"
        )

    if nb and len(nb) >= 2:

        rc2 = nb[0]["hold_ratio"] - nb[-1]["hold_ratio"]

        if rc2 > 0.01:
            signals.append(f"北向披露持股比例近{len(nb)}条样本变化 +{rc2:.3f}%")

        elif rc2 < -0.01:
            signals.append(f"北向披露持股比例近{len(nb)}条样本变化 {rc2:.3f}%")

    if peer_data and peer_data["peers"] and "note" not in peer_data["peers"][0]:

        my_m = peer_data.get("my_mcap", 0)
        ptm = peer_data["peers"][0]["mcap_yi"] if peer_data["peers"] else 0

        if ptm > 0 and my_m > 0 and my_m / ptm < 0.1:
            signals.append(
                f"本股市值仅为板块龙头 {peer_data['peers'][0]['name']} 的 {my_m/ptm*100:.1f}%，属板块小市值标的"
            )

    if rbt:

        for d in rbt[:3]:

            _premium_pct = _safe_float(d.get("premium_pct"))
            if round(_premium_pct, 2) > 0:

                signals.append(
                    f"场外溢价成交：{d['date']}大宗交易溢价{_premium_pct:+.2f}%；"
                    "该价格差异不能单独证明买方身份或主力抢筹意图"
                )

                break

        for d in rbt[:3]:

            _premium_pct = _safe_float(d.get("premium_pct"))
            if round(_premium_pct, 2) < -8:

                signals.append(
                    f"大宗交易折价：{d['date']}折价{abs(_premium_pct):.2f}%；"
                    "折价幅度反映成交价格差异，后续影响仍需结合成交双方与市场情况判断"
                )

                break

    mc = miq.get("change_pct") if miq else None
    # V16.4.1: biq 为空时 bc2 应为 None(原 {} 会骗过下方 all(... is not None) 判断)
    bc2 = biq.get("change_pct") if biq else None

    sc2 = q.get("change_pct", 0) if q else None
    ic2 = industry_change_pct if industry_rank > 0 else None

    if all(v is not None for v in [mc, bc2, sc2, ic2]):

        cd = sc2 - ic2

        if cd > 2.0 and sc2 > 0:
            signals.append(
                f"🔥 鹤立鸡群模型：个股 {sc2:+.2f}% >> 板块 {ic2:+.2f}% (领先 {cd:.1f}%)，属板块领涨龙头"
            )

        elif abs(sc2 - ic2) < 1.0 and abs(sc2) > 0.5:
            signals.append(
                f"📊 随波逐流模型：个股 {sc2:+.2f}% ≈ 板块 {ic2:+.2f}%，属板块普涨型跟风"
            )

    try:
        from core.data_provider import _should_use_zhb_for_realtime

        if _should_use_zhb_for_realtime() and cdata.change_5d:
            stk3 = cdata.change_5d * 0.6  # ZHB 5日涨幅做3日偏离估算
            tl = limit_pct_for(code, stock_name)
            if stk3 >= tl:
                signals.append(
                    f"异动雷达(ZHB离线)：近5日涨幅{cdata.change_5d:+.2f}%，估算3日偏离{stk3:+.2f}%>={tl}%，触发异动"
                )
        else:
            # V17.0.15: count 5→60 —— 与下文【十七、K线形态识别】共用同一 cache_key
            # ("D:{code}:60")，第二次命中进程内/磁盘缓存，**净增网络请求为 0**；
            # 60 根同时满足 TA-Lib CDL 族的 lookback 需求（形态识别需 ≥3 根且历史越长越稳）。
            _sk_r, _sr_r = await asyncio.to_thread(baidu_kline_full, code, 60)
            if len(_sr_r) >= 4 and len(_sk_r) > 0:
                _ci_r = next((i for i, k in enumerate(_sk_r) if k in ("close", "close_price")), -1)
                if _ci_r >= 0:
                    s_c = [_safe_float(rr[_ci_r]) for rr in _sr_r[-4:] if len(rr) > _ci_r]
                    if len(s_c) == 4 and s_c[0] > 0:
                        stk3 = (s_c[-1] / s_c[0] - 1) * 100
                        ic_r = bi if bi else "sh000001"
                        pi_r = ic_r[2:] if ic_r.startswith(("sh", "sz")) else ic_r
                        _ik_r, _ir_r = baidu_kline_full(pi_r, is_index=True)
                        if len(_ir_r) >= 4:
                            _ci2_r = next(
                                (i for i, k in enumerate(_ik_r) if k in ("close", "close_price")),
                                -1,
                            )
                            if _ci2_r >= 0:
                                i_c = [
                                    _safe_float(rr[_ci2_r]) for rr in _ir_r[-4:] if len(rr) > _ci2_r
                                ]
                                idx3 = (
                                    (i_c[-1] / i_c[0] - 1) * 100
                                    if len(i_c) == 4 and i_c[0] > 0
                                    else 0
                                )
                                dv = round(stk3 - idx3, 2)
                                tl = limit_pct_for(code, stock_name)
                                if dv >= tl:
                                    signals.append(
                                        f"异动雷达：3日偏离值{dv:+.2f}%>={tl}%，触发短期异动"
                                    )
                                elif dv >= tl * 0.9:
                                    signals.append(
                                        f"异动雷达：3日偏离值{dv:+.2f}%，距红线仅差{tl-dv:.2f}%，卡异动"
                                    )
    except Exception as _e:
        _debug_log(f"sht deviation radar error: {_e}")

    L("  综合分析条目:")

    if signals:

        for i, s in enumerate(signals, 1):
            L(f"  {i}. {s}")

    else:
        L("  (数据不足，暂无法生成综合信号)")

    # V17.0.17: 预初始化 _sk/_sr, 供【十七、K线形态识别】复用。
    # 此前 _sk/_sr 仅在涨停块(L1836)内赋值, 非涨停股触发 NameError 被下方 except 吞掉 → 整章静默消失
    # (重演 V17.0 已修的 M1/M4 假空白章节反模式)。现预置空, 涨停块会覆盖, K线形态块按需自取。
    _sk, _sr = [], []

    if q and price_today > 0 and is_limit_up(code, stock_name, q.get("change_pct", 0)):

        # V17.0(2026-08-15): 连板追踪增强——ZHB [33] 连板数(2026-08-27 天梯20/20 定案)优先, fallback 3日涨幅估算
        _zt_lb = 0
        _zt_ty = -1  # L1 修复: 先行初始化, 异常时结构安全
        _zt_seal = 0
        try:
            from stock_common.sc_datasource import get_zhb_single_stock_data

            _zdata = get_zhb_single_stock_data(code) or {}
            _zt_lb = int(_zdata.get("zt_lianban", 0) or 0)
            _zt_v = _zdata.get("zt_type")
            # H6 修复: 0 是合法值(盘中涨停档), 不能用 `or -1` 吞掉
            _zt_ty = int(_zt_v) if _zt_v is not None else -1
            _zt_seal = _zdata.get("zt_seal_amount", 0) or 0
        except Exception as _e:  # H5 修复: 显式日志, 不静默吞
            _debug_log(f"sht zt zhb data ({code}): {_e}")
        if _zt_lb > 0:
            # 封板类型(zt_type)原取自 Col[33]; V17.0.10 证伪 Col[33]=涨停类型、实为连板数, ZHB 不再提供(=_zt_ty=-1)
            _ty_txt = "一字/竞价封板" if _zt_ty >= 2 else ("盘中封板" if _zt_ty >= 0 else "")
            _seal_txt = f" 封单额(官方ZHB): {_zt_seal:.0f}万" if _zt_seal > 0 else ""
            L(
                f"  📊 连板追踪: 今日涨停，真连板数 **{_zt_lb}板**(ZHB[33] 连板数铁证){' ['+_ty_txt+']' if _ty_txt else ''}{_seal_txt}"
            )

        try:

            # V17.0.15: count 5→60（与上文异动雷达共用 cache_key "D:{code}:60"，命中缓存零额外请求）
            _sk, _sr = await asyncio.to_thread(baidu_kline_full, code, 60)

            _ci = next((i for i, k in enumerate(_sk) if k in ("close", "close_price")), -1)

            if _ci >= 0:

                _c3 = [_safe_float(rr[_ci]) for rr in _sr[-4:] if len(rr) > _ci]

                if len(_c3) == 4 and _c3[0] > 0:

                    _3d = (_c3[-1] / _c3[0] - 1) * 100

                    _lb_pct = limit_pct_for(code, stock_name)  # V16.2: 统一阈值（北交所 30 等）

                    _lb2 = _lb_pct * 1.9

                    _lb3 = _lb_pct * 2.85

                    _lb_t = (
                        "3连板"
                        if _lb3 <= _3d < _lb3 + _lb_pct
                        else (
                            "2连板"
                            if _lb2 <= _3d < _lb3
                            else (
                                "首板"
                                if _lb_pct * 0.95 <= _3d < _lb2
                                else f"高标{int(_3d/_lb_pct)}板" if _3d >= _lb3 + _lb_pct else ""
                            )
                        )
                    )

                    if _lb_t and _zt_lb <= 0:
                        L(f"  📊 连板追踪: 今日涨停，判定为{_lb_t}(3日累计{_3d:.1f}%)")

        except Exception as _e:
            _debug_log(f"sht lb estimate ({code}): {_e}")  # M11 修复(2026-08-15 二审): 吞异常补日志

    # ─── V17.0.15: K线形态识别（TA-Lib 61 形态，短线择时高价值维度）───
    # V17.0.17 修复: ① 此前 _sk/_sr 仅在涨停块(L1836)内赋值, 非涨停股触发 NameError 被 except 吞掉
    #       → 整章静默消失(重演 V17.0 已修的 M1/M4 假空白章节反模式); 现统一在此自取(TDX 磁盘缓存
    #       命中零额外请求), 涨停块已取则复用。② 源空/数据不足时渲染可见告警占位, 不再静默跳过。
    #       ③ 有数据但无形态时显式标注"无显著形态", 使该维度章节稳定存在。
    try:
        # 确保 K 线数据可用: 涨停块(L1836)已取则复用, 否则自取
        if not _sr:
            _sk, _sr = await asyncio.to_thread(baidu_kline_full, code, 60)
        _oi = next((i for i, k in enumerate(_sk) if k in ("open", "open_price")), -1)
        _hi2 = next((i for i, k in enumerate(_sk) if k in ("high", "high_price")), -1)
        _li2 = next((i for i, k in enumerate(_sk) if k in ("low", "low_price")), -1)
        _ci2 = next((i for i, k in enumerate(_sk) if k in ("close", "close_price")), -1)
        L("\n" + "---")
        L("## **十七、K线形态识别（TA-Lib 61 形态）**")
        L("---")
        if not _sr or min(_oi, _hi2, _li2, _ci2) < 0:
            # 源抓取失败(远端 TDX 截断/不可达) → 可见告警, 不再静默消失
            L("  ⚠️ K线数据源暂不可用（TDX 远端行情抓取失败或返回空），本章形态识别数据暂缺")
        else:
            _need2 = max(_oi, _hi2, _li2, _ci2)
            _rows_p = [rr for rr in _sr if len(rr) > _need2]
            if len(_rows_p) < 3:
                L("  ⚠️ K线数据不足（有效日K < 3 根），无法识别形态，暂缺")
            else:
                from stock_common.sc_technical import get_kline_patterns

                _pat = get_kline_patterns(
                    [_safe_float(rr[_oi]) for rr in _rows_p],
                    [_safe_float(rr[_hi2]) for rr in _rows_p],
                    [_safe_float(rr[_li2]) for rr in _rows_p],
                    [_safe_float(rr[_ci2]) for rr in _rows_p],
                )
                _bull = [k for k, v in _pat.items() if v > 0]
                _bear = [k for k, v in _pat.items() if v < 0]
                if _bull or _bear:
                    if _bull:
                        L(
                            f"  ➤ 看涨信号({len(_bull)}): "
                            + "、".join(f"{_CDL_CN.get(k, k)}" for k in _bull[:6])
                        )
                    if _bear:
                        L(
                            f"  ➤ 看跌信号({len(_bear)}): "
                            + "、".join(f"{_CDL_CN.get(k, k)}" for k in _bear[:6])
                        )
                    if _bull and not _bear:
                        _pj = "短线形态**一致偏多**"
                    elif _bear and not _bull:
                        _pj = "短线形态**一致偏空**"
                    else:
                        _pj = "多空形态信号**对冲**，方向待量能确认"
                    L(f"  📌 研判: {_pj}（看涨 {len(_bull)} / 看跌 {len(_bear)}）")
                    L(
                        "  ⚠️ 形态信号须结合**位置与量能**解读——单日形态噪音大，仅作辅助确认，"
                        "不可单独作为买卖依据；且信号基于日K收盘，盘中会变化。"
                    )
                else:
                    L("  (当前无显著看涨/看跌形态信号)")
    except Exception as _e:
        _debug_log(f"sht kline patterns ({code}): {_e}")
        L("  ⚠️ K线形态识别异常，本章暂缺")

    # V17.3.9: 短线报告接入 ZHB tipinfo 回购预案结构化数据（field_dict §3.1 tipinfo.hg_date / tipinfo.hg_amount_yi，verified）
    L("\n## 【十八、回购预案与股东权益动作 (ZHB tipinfo 结构化数据)】")
    L("---")
    _tip_info = get_zhb_tip_info(code)
    _hg_date = (_tip_info or {}).get("hg_date", "")
    _hg_amount = (_tip_info or {}).get("hg_amount_yi", 0) or 0
    if _hg_date or _hg_amount:
        L("  📌 ZHB tipinfo 回购预案 (财报日历结构化数据):")
        if _hg_date:
            L(f"    回购预案公告日: {_hg_date}")
        if _hg_amount:
            L(f"    回购金额上限: {_hg_amount:.2f} 亿元")
        L(
            "  💡 回购预案属短线情绪正向催化（彰显信心+潜在买单），但须区分「预案」与「实际回购进度」；"
        )
        L("     突发大额回购预案常引发短线脉冲，需结合量能判别真伪与持续性。")
    else:
        L("  ZHB tipinfo 暂无本股回购预案结构化记录（Col[19]/[20] 为空）。")

    L("\n" + "---")
    L("## **综合评分与交易风险参考**")
    L("---")
    L(
        "  短线模型分与多评委共识分使用不同指标和权重；两者方向不一致时应视为模型分歧。"
        "评分及下方仓位参数仅供参考，不构成个性化配置。"
    )

    # V8.2: 使用统一评分接口
    from stock_common import calculate_score

    # 构建评分数据
    score_data = ScoreData(
        code=code,
        name=info.get('name', ''),
        price=price_today,
        change_pct=q.get('change_pct', 0) if q else 0,
    )

    # 均线数据
    if ma_data and 'ma5avgprice' in ma_data:
        score_data.ma5 = _safe_float(ma_data.get('ma5avgprice', 0))
        score_data.ma10 = _safe_float(ma_data.get('ma10avgprice', 0))
        score_data.ma20 = _safe_float(ma_data.get('ma20avgprice', 0))

    # 涨停判断
    if q and q.get('change_pct', 0) >= 9.5 and price_today >= q.get("limit_up", 0) * 0.99:
        score_data.is_limit_up = True

    # 资金流向：使用最近 20 个有效交易日；“连续流入天数”按最新日期起连续统计。
    _score_flow_data = ff.get("data") or []
    _score_flow_sample_count = min(len(_score_flow_data), 20)
    if _score_flow_sample_count >= 20:
        _ff_data = _score_flow_data[:20]
        score_data.main_net_inflow = sum(_safe_float(row.get("main_net")) for row in _ff_data)
        for _flow_day in _ff_data:
            if _safe_float(_flow_day.get("main_net")) <= 0:
                break
            score_data.consecutive_inflow_days += 1

    # 筹码数据
    if holders and len(holders) >= 2:
        score_data.holder_change_ratio = holders[0]["change_ratio"]
        if holders[0]["change_ratio"] < 0 and holders[1]["change_ratio"] < 0:
            score_data.holder_consecutive_decrease = True

    # 筹码分布 CYQ(V17.0.14: _cyq_dict 已在上方股东户数段提前获取, 此处仅写入评分)
    if _cyq_dict:
        score_data.cyq_benefit_pct = _cyq_dict.get("benefit_pct", 0.0) or 0.0
        score_data.cyq_avg_cost = _cyq_dict.get("avg_cost", 0.0) or 0.0
        score_data.cyq_concentration_90 = _cyq_dict.get("concentration_90", 0.0) or 0.0
        score_data.cyq_concentration_70 = _cyq_dict.get("concentration_70", 0.0) or 0.0

    # 北向数据
    if nb and len(nb) >= 2:
        score_data.northbound_change = nb[0]["hold_shares"] - nb[-1]["hold_shares"]

    # 机构净买入
    if dtb["institution"].get("net_amt", 0) > 0:
        score_data.institution_net_buy = dtb["institution"].get("net_amt", 0)

    # 融券下降
    if margin and len(margin) >= 3:
        if all(margin[i]["rqye"] <= margin[i + 1]["rqye"] for i in range(2)):
            score_data.margin_short_decline = True

    # 计算评分
    # V16.1: 传入 strategy_config.yaml 的 scoring_sht 权重（此前未传 cfg → 用硬编码默认）
    _score_cfg = _load_strategy_config() or {}
    _sht_cfg = {"weights_sht": (_score_cfg.get("scoring_sht") or {}).get("weights_sht", {})}
    result = calculate_score("sht", score_data, _sht_cfg)
    _ps = result.total_score
    _details = result.details

    # 风险信号扣分
    _warn_cnt = sum(1 for s in signals if "⚠️" in s or "❌" in s)
    _ps -= _warn_cnt * 10
    _ps = max(0, min(100, _ps))

    # 涨停封单预警检测：封单弱时仓位降级
    _seal_warn = any("封单预警" in s or "弱势烂板" in s for s in signals)

    L(f"  评分明细: {' | '.join(_details[:8])}" if _details else None)
    _score_input_gaps = []
    if not ma_data or "ma5avgprice" not in ma_data:
        _score_input_gaps.append("均线数据")
    if score_data.rsi14 is None:
        _score_input_gaps.append("RSI技术指标")
    if _score_flow_sample_count < 20:
        _score_input_gaps.append(f"20个有效交易日的资金流样本（当前{_score_flow_sample_count}日）")
    if not holders or len(holders) < 2:
        _score_input_gaps.append("股东户数变化")
    if not _cyq_dict:
        _score_input_gaps.append("CYQ筹码分布")
    if _score_input_gaps:
        L(
            "  ⚠️ 评分输入不完整："
            + "、".join(_score_input_gaps)
            + "；缺失项按模型默认值处理，评分档位不代表完整信号。"
        )
    L("  仓位与止损百分比是模型参数示例，不是个人化投资指令。")

    if _seal_warn:
        # 封单弱时仓位降级：原仓位建议减半
        # V17.0.25(2026-09-02) P2-9 修复: 显示用 int() 截断(非四舍五入), 与档位判定(_ps>=50/30/15)一致 —
        # 49.6 原 .0f 显示50却落30-49档, 读者误判。int(非负)即 floor。
        if _ps >= 50:
            L(f"  短线模型评分: {int(_ps)}/100 → 封单偏弱，模型仓位参数参考20%，止损参数参考-5% ⚠️")
        elif _ps >= 30:
            L(f"  短线模型评分: {int(_ps)}/100 → 封单偏弱，模型仓位参数参考12%，止损参数参考-5% ⚠️")
        elif _ps >= 15:
            L(f"  短线模型评分: {int(_ps)}/100 → 封单偏弱，模型仓位参数参考5%，止损参数参考-3% ⚠️")
        else:
            L(f"  短线模型评分: {int(_ps)}/100 → 封单偏弱，模型仓位参数参考2%，以观望为主 ⚠️")
    elif _ps >= 50:
        L(f"  短线模型评分: {int(_ps)}/100 → 高分档，模型仓位参数参考40%，止损参数参考-5%")
    elif _ps >= 30:
        L(f"  短线模型评分: {int(_ps)}/100 → 中高分档，模型仓位参数参考25%，止损参数参考-5%")
    elif _ps >= 15:
        L(f"  短线模型评分: {int(_ps)}/100 → 低分档，模型仓位参数参考10%，止损参数参考-3%")
    else:
        L(f"  短线模型评分: {int(_ps)}/100 → 低分档，模型仓位参数参考5%，保持观望")

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
        # V17.2.27(2026-09-18) P2 协调注: 短线评分(封单/资金维度)与综合建议(多评委共识分)维度独立,
        # 前者看盘中博弈强度、后者看多因子共振质量, 二者可并存不冲突, 勿直接对照。
        L(
            "    ℹ️ 综合投资建议基于多评委共识分(基本面/技术/资金等多维共振), 与上文明细「短线评分」(封单强度/资金博弈维度)口径不同, 二者可并存不冲突"
        )
    except Exception as _e:
        _debug_log(f"multi_school_score error: {_e}")

    # 市场热度参考（同花顺热榜 + 概念命中）— V16.1: 同步包 to_thread
    try:
        hot_list = await asyncio.to_thread(ths_hot_list, "hour")
        # 检查该股是否在热榜中
        in_hot = next((h for h in hot_list if h.get("code") == code), None)
        if in_hot:
            L(
                f"\n  📊 市场热度: 该股当前在同花顺热榜 #{in_hot['rank']}，热度值 {in_hot['heat']:,.0f}"
            )
            if in_hot.get("concepts"):
                L(f"     关联概念: {', '.join(in_hot['concepts'][:3])}")
            if in_hot.get("tag"):
                L(f"     标签: {in_hot['tag']}")
        # V14.2: 优先用 ZHB tdxchain.cfg 本地概念匹配（零网络请求）
        try:
            from core.data_provider import get_concept_from_zhb

            zhb_concepts = await asyncio.to_thread(get_concept_from_zhb, code)
            if zhb_concepts:
                L(f"     产业链/概念（ZHB 本地）: {', '.join(zhb_concepts[:5])}")
        except Exception as _e:
            _debug_log(f"get_concept_from_zhb error: {_e}")
        # 东财概念命中（V14.2: 仅当 ZHB 无数据时 fallback）
        concepts = await asyncio.to_thread(em_hot_concept, code)
        if concepts:
            # V17.3.5 修正(报告审查 #367): 标注来源(东财)以区别于上方 TDX 概念板块,
            # 两者口径不同、可存在差异, 避免读者误判为报告自相矛盾。
            L(f"     热门概念(东财): {', '.join([c['concept'] for c in concepts[:3]])}")
    except Exception as _e:
        _debug_log(f"em_hot_concept error: {_e}")

    # 累积快照数据（批量结束后统一写入）
    _SNAPSHOT_DATA[code] = {
        "name": info.get('name', ''),
        "total_score": _ps,
        "price": price_today,
        "report_source": "sht",
    }

    # [ENRICH] 数据维度充实（统一层 canonical 字段，零新增取数；异常仅记录不阻断报告）
    try:
        from stock_common.enrich_helpers import (
            fund_flow_detail_lines,
            order_book_lines,
            quality_gate_lines,
        )

        _enrich = []
        _enrich += fund_flow_detail_lines(cdata)
        _enrich += order_book_lines(cdata)
        _enrich += quality_gate_lines(cdata)
        if _enrich:
            L("")
            L("## 【补充·数据维度充实（基于统一层字段）】")
            L("---")
            for _ln in _enrich:
                L(_ln)
    except Exception as _e:
        _debug_log(f"sht enrich error: {_e}")

    # V17.0(2026-08-15 C 方案): 全量 md 化——渲染层确定性转换(标题/分隔线/F10 边框表/对齐空格表→md)
    from stock_common.md_render import render_md_report

    output = render_md_report(output_path, lines)

    return output


# ═══════════════════════════════════════════

# 入口

# ═══════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
# V12.4: ShtReportRunner — 统一运行框架
# ═══════════════════════════════════════════════════════════════


class ShtReportRunner(BaseReportRunner):
    """短线策略个股分析报告 Runner (V12.4)"""

    def __init__(self):
        super().__init__("get_sht_report", "sht", "短线策略个股分析报告")

    def execute_pipeline(self) -> dict:
        args = self.args
        if args is None:
            raise RuntimeError("report arguments have not been initialized")
        # V17.0 R4: 批量骨架收敛到基类 execute_batch_pipeline——
        # 缓存构建/prefetch 钩子/逐只 GD 上传钩子(pre_gd_init)全部参数化, 原 110 行本地实现删除
        _cached_ind_comp = get_industry_comparison()
        _cached_idx_q = {}
        for ic in ("sh000001", "sz399106", "sz399102", "sh000680"):
            _iq = _get_index_quote(ic)
            if _iq:
                _cached_idx_q[ic] = _iq
        _cached_hsgt = get_hsgt_macro_flow()
        # V16.4.1: 缓存值必须传入——否则每只股票重复拉 HSGT, 与 docstring"批量避免重复查询"相悖

        def _prefetch(codes):
            # V17.4.45: push2delay 基础行情 + 腾讯批量补充；统一层内部按字段记录来源。
            from core.data_provider import prefetch_quote_batch

            _ret = prefetch_quote_batch(codes)
            # V17.2.24: eltdx 连板/封单/开盘抢筹批量预热(一次 TCP, 300s TTL 缓存;
            # 统一层 cdata.eltdx_* 仅读此缓存, 禁止 per-stock 触发取数打爆 TDX TCP)
            try:
                from core.eltdx_adapter import get_eltdx_shortline_bundle

                get_eltdx_shortline_bundle(list(codes))
            except Exception as _e:
                _debug_log(f"sht eltdx prefetch: {_e}")
            return _ret

        # V17.0.7: datacenter 五类(龙虎榜/两融/北向/解禁/大宗)批量预取流水线钩子
        _depth = getattr(args, "depth", "deep") or "deep"
        _seats_on = _depth != "lite"

        async def _prefetch_async(session, codes):
            from stock_common.sc_datasource import start_datacenter_prefetch

            return start_datacenter_prefetch(
                codes,
                session,
                dragon_kwargs={"include_seats": _seats_on, "enhance_seats": _seats_on},
            )

        return self.execute_batch_pipeline(
            "sht",
            generate_report_async,
            gen_kwargs={
                "ind_comp": _cached_ind_comp,
                "idx_q": _cached_idx_q,
                "hsgt": _cached_hsgt,
                "depth": args.depth,
            },
            prefetch_fn=_prefetch,
            prefetch_async_fn=_prefetch_async,
            snapshot_data=_SNAPSHOT_DATA,
            # V17.0: 去除 pre_gd_init(逐只上传)——main.py 已改用输出活性检测(无固定超时),
            # "超时 kill 丢 GD" 场景不再存在 → 上传逻辑与 med/lng 统一(全部完成后统一上传)
        )

    def upload_reports(self, drive, folder_id: str, results) -> None:
        # V16.4.1: execute_pipeline 已逐只上传(_gd_per_stock=True)时 no-op 防重复;
        # 早 init 失败时回退批量上传(原逻辑)
        if getattr(self, "_gd_per_stock", False):
            return
        self.upload_multi_reports(drive, folder_id, results)


if __name__ == "__main__":
    runner = ShtReportRunner()
    runner.run()
