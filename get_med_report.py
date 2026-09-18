#!/usr/bin/env python3
"""
get_med_report.py — A股中线深度投研报告

版本信息:
    V15.2  2026-07-28 - V15.2 P0 崩溃修复：修复 board UnboundLocalError；缓存 valid_if 强化
    V15.1  2026-07-26 - V15.1 全局 ZHB 旁路普及：休市日及盘前，财务与股东结构数据 100% 走 ZHB 静态层提取，生成速度提升 80%
    V15.0  2026-07-26 - 接入 CanonicalStockData 强类型数据合约，实施基于真实周期的 ZHB-First 离线优先路由
    V14.0  2026-07-22 - 文档同步：docstring 版本信息更新到 V14.0；is_workday() Bug 修复由 stock_common 上游提供
    V13.x  2026-07-22 - 受益于 stock_cache.py dataclass 透明序列化（脚本无改动）
    V12.6  2026-07-22 - 受益于字段路由简化（移除估值字段 HTTP fallback）
    V12.4  2026-07-22 - 抽象 BaseReportRunner 基类
    V9.5   2026-07-11 - 东财资金流120天fallback静默异常添加 _debug_log 日志
    V9.3.3 2026-07-11 - 两融数据添加融券余额列；流通股东显示统一为0%；休市提示文案丰富统一
    V9.3.2 2026-07-09 - 基础设施修复：TDX K线假数据防护、SQLite WAL死锁修复、代理环境兼容（脚本本身无改动，受益于底层修复）
    V9.3 2026-07-07 - 盘前行情模式：9:30前使用上一交易日日K线数据；财务数据限制近5季度；盘前提示文本；删除报告标题硬编码版本号
    V9.2 2026-07-05 - 异常处理规范化；缓存交叉验证机制启用
    V9.1 2026-07-04 - F10 全覆盖：新增【财务深度/股东行为/主营构成】3章节+数据质量附录
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

import math, pandas as pd  # V16.4.1: 删 argparse 未使用
import asyncio
from datetime import date, datetime, timedelta
import os

# V15.3 修复: 4 个报告模块同名 _SNAPSHOT_DATA 全局变量冲突
# 抽出到 stock_common.sc_snapshot 统一管理
# V15.3.1: 直接 import 共享的 SnapshotProxy 类，删除 20 行重复定义
from stock_common.sc_snapshot import SnapshotProxy as _SnapshotProxy  # noqa: E402

_SNAPSHOT_DATA = _SnapshotProxy()

from core.tdx_client import (  # V16.4.1: 删 tdx_get_quote_full/cleanup_tdx 未使用
    tdx_get_belong_boards,
    tdx_get_board_members,
    tdx_get_board_by_name,
)

from stock_common import (
    _safe_float,
    _debug_log,
    BaseReportRunner,
    get_holder_structure,
    _load_strategy_config,
    get_dragon_tiger_board_async,
    holder_change_async,
    get_strategic_announcements_async,
    baidu_kline_full,  # V16.4.1: 删 parse_args/get_tencent_quote 等未使用
    get_dividend_history,
    get_industry_comparison,
    get_stock_info,
    get_eps_forecast_async,
    get_reports_async,
    get_northbound_hold_async,
    get_margin_trading_async,
    get_block_trade_async,
    get_lockup_expiry_async,
    get_gross_margin_and_roe_async,
    get_industry_peers,
    get_sina_financial_report_async, get_financial_report_with_fallback,
    get_sina_balance_sheet_async,
    get_hsgt_macro_flow_async,
    get_market_status,
    cls_telegraph,
    news_matches_stock,
    cninfo_irm,
    sec_type_market_label,  # V17.0.32(2026-09-06): DEBT-016 报告露出 sec_type
)  # V10.3

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 模块级策略配置（加载一次，全局共享）
_sc = _load_strategy_config()
_mkt_cfg = _sc.get("market", {})
_peers_low = _mkt_cfg.get("peers_mcap_low", 0.3)
_peers_high = _mkt_cfg.get("peers_mcap_high", 3.0)


# ==================== 核心数据抓取模块 ====================


def get_fund_flow_120d(code):
    """V17.2.x(2026-09-10) 统一口径：sht 已对齐至本 `prefer="em"`（东财直连）。

    原注释称"保留仅东财口径（中线业绩视角）"以区别于 sht 的 TDX 优先——该区分已不成立：
    `tdx_get_history_fund_flow` 自 V12.0 起即委托东财 HTTP，两路径数据同源同值。
    现 med 与 sht 完全一致（同一函数、同一参数），跨报告资金流结论可直接横向比较。
    """
    from stock_common import get_history_fund_flow_120d
    return get_history_fund_flow_120d(code, 60, prefer="em")


# V7.5: get_dragon_tiger_board 由 stock_common 统一提供


async def get_holder_change_async(session, code):
    """async 版: 股东户数变化"""
    return await holder_change_async(session, code)


async def get_stock_sector_rank_async(code, info=None):
    """V4: 板块内排名 — TDX 优先，不可用时回退 board_by_name
    V11.5: 涨跌幅数据优先使用 data_provider
    HIGH(审查 2026-08-16): 原 `await data_provider.get_change_pct_async` 无模块级
    data_provider 名称 → 每次 NameError 被吞 → 板块内排名永久静默失效; 改函数内局部导入
    """
    from core.data_provider import get_change_pct_async as _dp_get_change_pct_async
    boards = tdx_get_belong_boards(code)
    industry_boards = boards.get("industry", []) if boards else []
    if industry_boards:
        primary = industry_boards[0]
        members = tdx_get_board_members(primary["code"])
        if members:
            members_by_chg = sorted(members, key=lambda x: x.get("change_pct", 0), reverse=True)
            for i, m in enumerate(members_by_chg, 1):
                if m["code"] == code:
                    my_chg = m["change_pct"]
                    try:
                        _dp_chg = await _dp_get_change_pct_async(code)
                        if _dp_chg is not None:
                            my_chg = _dp_chg
                    except Exception as _e:
                        _debug_log(f"med sector_rank get_change_pct_async error: {_e}")
                    return {"rank": i, "total": len(members), "change_pct": my_chg}
    ind_name = (industry_boards[0].get("name", "") if industry_boards else "") or (
        info.get("industry", "") if info else ""
    )
    if ind_name:
        st = tdx_get_board_by_name(ind_name, board_type=0)
        if st:
            st_sorted = sorted(st, key=lambda x: x["change_pct"], reverse=True)
            for i, s in enumerate(st_sorted, 1):
                if s["code"] == code:
                    my_chg = s["change_pct"]
                    try:
                        _dp_chg = await _dp_get_change_pct_async(code)
                        if _dp_chg is not None:
                            my_chg = _dp_chg
                    except Exception as _e:
                        _debug_log(f"med sector_rank get_change_pct_async error: {_e}")
                    return {"rank": i, "total": len(st), "change_pct": my_chg}
    return None


# ==================== 报告生成引擎 ====================


async def generate_report_async(session, code, output_path, ind_comp=None, hsgt=None):
    """async 版: 支持 ind_comp/hsgt 外部缓存，批量模式下避免重复查询"""
    today_str = date.today().strftime("%Y-%m-%d")
    lines = []

    def L(s=""):
        lines.append(s)

    L("=" * 72)
    # V17.0.2i: 头部拆分(参照 mak 规则)
    L(f"  **{code} 中线深度投研报告**")
    L(f"  ⏱ {today_str} {datetime.now().strftime('%H.%M.%S')}")
    L("=" * 72)
    L("")
    _sc = _load_strategy_config()
    _val = _sc.get("valuation", {})
    _fund = _sc.get("fundamental", {})
    _pe_mid = _val.get("pe_mid", 30.0)
    _peg_good = _val.get("peg_good", 0.8)
    _peg_rational = _val.get("peg_rational", 1.5)
    _debt_ratio_warn = _fund.get("debt_ratio_warn", 60.0)
    _ar_ratio_warn = _fund.get("ar_ratio_warn", 20.0)
    _gw_ratio = _fund.get("gw_ratio_warn", 30.0)

    _now = datetime.now()
    _mkt_status, _mkt_note = get_market_status(_now)

    # 生成详细提示
    if _mkt_status == "closed":
        note = "⚠️ 休市日：数据为最近交易日快照，龙虎榜/融资融券为最近一期已发布"
    elif _mkt_status == "pre_market":
        note = "⚠️ 盘前时段：行情数据/北向资金为上交易日值，龙虎榜/融资融券为最近一期已发布数据"
    elif _mkt_status in ("morning", "afternoon"):
        note = "⚠️ 盘中时段：行情数据实时跳动，龙虎榜/融资融券/大宗交易需收盘后更新，基本面数据（财报/ROE/股东/分红等）为最新报告期数据不受影响"
    elif _mkt_status == "lunch":
        note = "⚠️ 午休时段（11:30-13:00）：行情暂停但基本面数据正常"
    elif _mkt_status == "post_market":
        note = "⚠️ 盘后结算时段：部分数据（龙虎榜约16:30后）尚在更新中"
    elif _mkt_status == "post_close":
        note = "ℹ️ 盘后收盘：数据为今日收盘快照，龙虎榜/融资融券为今日已发布数据"
    else:
        note = ""
    if note:
        # MEDIUM(审查 2026-08-16): 移除 print(双打印)——报告内 L 已输出, 与其余脚本一致
        L(f"  {note}")
        L("")

    # ─── 0. 宏观资金风向标 ───
    L("\n## **一、宏观资金面背景**")
    L("---")
    if hsgt is None:
        hsgt = await get_hsgt_macro_flow_async(session)
    if hsgt:
        # V17.0.4(2026-08-19): invalid → 同花顺 hgt/sgt 序列错位, 末值恒陈旧(冻结 379.75)——不展示错误数字
        if hsgt.get("data_quality") == "invalid":
            L("  ⚠️ 今日北向资金: 数据源异常(hgt/sgt 序列错位), 净流入暂缺")
        elif hsgt.get("data_quality") == "partial_hgt_only":
            # V17.0.28: hgt=当日分时(可用), sgt=历史序列(不可用) → 只展示沪股通并声明单口径
            signal = "偏多" if hsgt['hgt'] > 0 else "偏空"
            L(f"  今日北向资金: 沪股通 {hsgt['hgt']:+.2f} 亿元"
              f"（深股通序列为历史值暂缺，本项为沪股通单口径，非北向合计）")
            L(f"  大盘外资情绪: {signal} （中线仓位参考点）")
        else:
            signal = "偏多" if hsgt['total'] > 0 else "偏空"
            L(
                f"  今日北向资金总净流入: {hsgt['total']:.2f} 亿元 (沪股通 {hsgt['hgt']:.2f}亿 | 深股通 {hsgt['sgt']:.2f}亿)"
            )
            L(f"  大盘外资情绪: {signal} （中线仓位参考点）")
            # V16.4.1: 数据层降级标记展示(2026-08-12 深股通 379.75 亿异常)
            if hsgt.get("data_quality") == "degraded":
                L("  ⚠️ 北向资金数据源存疑(异常波动), 仅供参考")
    else:
        L("  (北向宏观资金流向获取失败)")

    # ─── 1. 基本信息与实时估值 ───
    L("\n## 【二、个股基本信息与估值锚点】")
    L("---")
    # V15 统一数据中心：通过 get_canonical_stock_data 获取强类型标准化数据
    # V15.2 修正: async 上下文必须包 to_thread，否则阻塞主事件循环
    from core.data_provider import get_canonical_stock_data

    cdata = await asyncio.to_thread(get_canonical_stock_data, code)
    price_today = cdata.price
    q = cdata.to_dict()

    info = await asyncio.to_thread(get_stock_info, code)  # V16.2: 同步网络调用包 to_thread（防阻塞事件循环）
    stock_name = cdata.name or info.get('name', 'N/A')
    stock_industry = cdata.industry or info.get('industry', 'N/A')

    L(f"  股票名称: {stock_name} ({cdata.code})")
    # V16.3.3 (2026-08-10 字典 12.15.8): ST/次新风险信号（结构化名称——ST 不剔除仅标注，涨跌幅已统一 10%）
    if getattr(cdata, "is_st", False):
        L("  ⚠️ 风险标记: **ST/*ST**（退市风险——基本面/财务审核需加强关注）")
    if getattr(cdata, "is_new", False):
        L("  🆕 次新标记: 上市 ≤5 日（财务数据不完整，中线谨慎）")
    L(f"  所属板块: {stock_industry}")
    # V17.2.24: eltdx 连板状态（统一层 cdata.eltdx_*，源自 TDX 7709/7615 实时）
    if getattr(cdata, "eltdx_has_shortline", False):
        _ll = cdata.eltdx_ladder_level or 0
        if _ll >= 2:
            L(f"  🪜 连板状态: **{_ll}连板**（封流比{cdata.eltdx_seal_to_float_ratio:.2f}%）——短线强势，注意连续涨停风险")
    # V17.0.32(2026-09-06) DEBT-016: 露出 sec_type（与 board 地域字段正交）→ 市场板块 + 涨跌幅限制
    L(f"  市场板块: {sec_type_market_label(getattr(cdata, 'sec_type', 0), cdata.code, cdata.name)}")

    # V17.2.21 修复: 优先 cdata.list_date（push2delay+10年缓存, 实测可用）, info 兜底（主域 push2 被风控拦截恒空）
    list_date_raw = cdata.list_date or info.get("list_date", "")
    if list_date_raw and len(list_date_raw) >= 8:
        list_date_fmt = f"{list_date_raw[:4]}-{list_date_raw[4:6]}-{list_date_raw[6:8]}"
    else:
        list_date_fmt = list_date_raw
    L(f"  上市日期: {list_date_fmt}")

    if cdata.change_5d or cdata.change_10d or cdata.change_20d or cdata.change_60d:
        L(
            f"  [阶段涨幅] 近5日: {cdata.change_5d:+.2f}% | 近10日: {cdata.change_10d:+.2f}% | 近20日: {cdata.change_20d:+.2f}% | 近60日: {cdata.change_60d:+.2f}%"
        )
    # V17.0.5 P0: 本月至今涨跌幅(tdxstat2 Col[11] change_mtd, 基准=上月末收盘)——
    # med 持有期 1-3 月的动量锚点, 与 20/60 日正交
    if getattr(cdata, "change_mtd", 0):
        _mtd = cdata.change_mtd
        _mtd_tag = "月内强势" if _mtd >= 10 else ("月内偏强" if _mtd >= 3 else ("月内走弱" if _mtd <= -10 else "月内平缓"))
        L(f"  [本月至今] {_mtd:+.2f}%（{_mtd_tag}）——持有期动量参考")

    # 52周区间与 IPO 破发度分析 (cdata 统一提供)
    if cdata.high_52w > 0 and cdata.low_52w > 0 and cdata.price > 0:
        _52w_pos = (
            (cdata.price - cdata.low_52w) / (cdata.high_52w - cdata.low_52w) * 100
            if cdata.high_52w != cdata.low_52w
            else 50
        )
        L(
            f"  [52周区间] 最高: {cdata.high_52w:.2f}元 | 最低: {cdata.low_52w:.2f}元 | 当前位置: {_52w_pos:.0f}%"
        )

    # ── V17.0.27(2026-09-04) DEBT-007: Beta 中线波动风险档（契约孤儿字段消费，公理 A5）──
    #   源: 腾讯 qt.gtimg [56]，置信度 **高**（887 只 800 日K线自构等权市场代理，
    #   自算 Beta 与 [56] Pearson=0.908）。口径声明: 腾讯基准/窗口与自算有偏移，
    #   此为**腾讯口径 Beta 估计值**，非本系统重算（A7——不可写成"本系统 Beta"）。
    #   与 lng 同名章节的分工: lng 看「长线回撤预算」，med 看「1-3 月持有期的仓位容忍度」——
    #   同一指标在不同持有期的含义不同，故两处文案不同而非简单复制。
    _beta = _safe_float(getattr(cdata, "beta", 0) or 0)
    if _beta > 0:
        if _beta < 0.8:
            _b_tag = "低波动防御型——中线持有回撤压力小"
        elif _beta < 1.0:
            _b_tag = "偏低波动——仓位可适度上调"
        elif _beta < 1.2:
            _b_tag = "与大盘同步——按标准仓位执行"
        elif _beta < 1.5:
            _b_tag = "高波动进攻型——持有期需预留回撤空间，建议仓位打 8 折"
        else:
            _b_tag = "极高波动——1-3 月持有期内大幅回撤概率高，建议仓位打 5 折"
        L(f"  [Beta波动档] {_beta:.2f}（腾讯口径估计值）— {_b_tag}")
    else:
        L("  [Beta波动档] N/A（未取到）")

    if cdata.ipo_price > 0 and cdata.price > 0:
        _ipo_pct = (cdata.price - cdata.ipo_price) / cdata.ipo_price * 100
        if _ipo_pct < 0:
            L(
                f"  [IPO破发度] 发行价: {cdata.ipo_price:.2f}元 | 现价: {cdata.price:.2f}元 | 破发幅度: {_ipo_pct:.2f}%"
            )
            if _ipo_pct < -30:
                L("  📉 深度破发: 破发幅度超30%，安全边际较高")
            elif _ipo_pct < -10:
                L("  ⚠️ 轻度破发: 破发幅度10-30%，关注基本面支撑")

        # V10.3: 中线动能对比（20日 vs 60日）
        if cdata.change_20d and cdata.change_60d:
            _momentum_diff = cdata.change_20d - cdata.change_60d
            L(
                f"  [中线动能] 20日涨幅: {cdata.change_20d:+.2f}% | 60日涨幅: {cdata.change_60d:+.2f}% | 差值: {_momentum_diff:+.2f}%"
            )
            if cdata.change_20d > 0 and _momentum_diff > 5:
                L("  🚀 加速上涨: 短期涨幅显著高于中期，动能增强")
            elif cdata.change_20d < 0 and _momentum_diff < -5:
                L("  🛑 减速下跌: 短期跌幅大于中期，动能衰竭")

    if ind_comp is None:
        # V15.4.2: 同步行业对比包 to_thread
        ind_comp = await asyncio.to_thread(get_industry_comparison)
    stock_ind = info.get('industry', '')
    peer_data = {"industry": "", "my_mcap": 0, "my_rank": 0, "industry_count": 0, "peers": []}
    fin_metrics = {}
    if stock_ind and ind_comp:
        _ind_all = ind_comp.get("all", ind_comp)
        for row in _ind_all:
            if stock_ind in row["name"] or row["name"] in stock_ind:
                L(f"  板块排名: 当日全市场第 {row['rank']} 名 (涨跌幅 {row['change_pct']}%)")
                try:
                    _rank_info = await get_stock_sector_rank_async(code, info=info)
                    if _rank_info:
                        L(
                            f"  本股今日{_rank_info['change_pct']:+.2f}%，板块内排名第{_rank_info['rank']}/{_rank_info['total']}名"
                        )
                except Exception as _e:
                    _debug_log(f"med sector_rank error: {_e}")
                if row['rank'] <= 10:
                    L("  🔥 板块共振: 该板块处于全市场 TOP 10 热门赛道，板块共振溢价效应显著")
                if row.get("leader"):
                    leader_code = row["leader"]
                    leader_name = ""
                    try:
                        li = await asyncio.to_thread(get_stock_info, leader_code)  # V16.2: to_thread
                        leader_name = li.get("name", "")
                    except Exception as _e:
                        _debug_log(f"med leader_info error: {_e}")
                    if leader_name:
                        L(f"  板块龙头: {leader_code} {leader_name}")
                    else:
                        L(f"  板块龙头: {leader_code}")
                break

    await asyncio.sleep(0.5)
    # V15.4.2: 同步同业对比包 to_thread
    peer_data = await asyncio.to_thread(get_industry_peers, code, 3, info=info)
    if peer_data.get("my_rank", 0) > 0 and peer_data.get("industry_count", 0) > 0:
        L(
            f"  板块内排名: 按总市值排序, 该股排名第 {peer_data['my_rank']}/{peer_data['industry_count']} 位"
        )

    L(f"  总市值:   {cdata.mcap_yi:.2f}亿元 (流通股本 {cdata.float_shares_wan/1e4:.2f}亿股)")
    if cdata.time_anchor == "t-1":
        L("  ⚠️ 盘前模式（9:30前），以下行情数据基于上一交易日收盘数据")
    L(f"  现价:   {cdata.price:.2f}元  (今日涨跌: {cdata.change_pct:.2f}%)")
    _pe_s = f"{cdata.pe_dynamic:.2f}x" if cdata.pe_dynamic > 0 else "N/A（亏损）"
    _pe_ttm_str = f"{cdata.pe_ttm:.2f}x" if cdata.pe_ttm > 0 else "N/A"
    _pe_lyr_str = f"{cdata.pe_lyr:.2f}x" if cdata.pe_lyr > 0 else "N/A"
    _div_str = f"  股息率: {cdata.dividend_yield:.2f}%" if cdata.dividend_yield > 0 else ""
    # V17.0.17(2026-09-01) 据主字典定案修正: 三口径清晰化——
    # PE（TTM）=f164 / 动态PE=pe_dynamic(f162) / 静态PE（LYR）=pe_lyr(f163)。
    # 原"动态市盈率 PE（TTM）"标签把 TTM 误标"动态"，已拆分；新增静态PE露出。
    # V17.2.20 修复(C): _pe_ttm_str 在 L385 已带 "x" 后缀, 此处误再拼 "x" 导致 "64.31xx" 双后缀。
    # 与 _pe_s/_pe_lyr_str (L384/386 已带 x, L391 不另拼) 保持一致——去掉此处多余 "x"。
    L(f"  PE（TTM）: {_pe_ttm_str} | 动态PE: {_pe_s} | 静态PE（LYR）: {_pe_lyr_str} | 市净率 PB: {cdata.pb:.2f}")
    if _div_str:
        L(_div_str)

    # ─── 2. 财务业绩兑现追踪 ───
    L("\n## 【三、历史财务业绩兑现追踪 (近5季度)】")
    L("---")

    # V17.0.5 P1: 财务兑现双源核验(fuyao 五类指标 growth 族——营收/净利同比官方口径)
    try:
        from stock_common import get_fuyao_fin_indicators as _f_fi, is_fuyao_enabled as _f_en

        if _f_en():
            _yy = date.today().year
            _fi = None
            _used_rp = ""
            for _rp in (f"{_yy}-1", f"{_yy - 1}-4"):
                _fi = await asyncio.to_thread(_f_fi, code, _rp)
                if _fi:
                    _used_rp = _rp
                    break
            if _fi:
                _gw = _fi.get("growth") or {}
                _pairs = [
                    ("营业收入同比", "calculate_operating_income_yoy_growth_ratio",
                     "operating_income_yoy_growth_ratio"),
                    ("净利润同比", "calculate_parent_holder_net_profit_yoy_growth_ratio",
                     "net_profit_yoy_growth_ratio"),
                    ("营业利润同比", "calculate_operating_profit_yoy_growth_ratio",
                     "operating_profit_yoy_growth_ratio"),
                ]
                _rows = []
                for _label, _id1, _id2 in _pairs:
                    _v = _gw.get(_id1, _gw.get(_id2))
                    if _v is not None:
                        _rows.append((_label, float(_v)))
                if _rows:
                    L(f"\n  [双源核验] fuyao 官方口径(报告期 {_used_rp}, 同花顺 Arsenal):")
                    for _label, _v in _rows:
                        L(f"    {_label}: {_v:+.2f}%")
                    L("    （与上表 F10 口径互为独立源——偏差>2pp 时以财报原文为准）")
    except Exception as _e:
        _debug_log(f"med fuyao growth cross: {_e}")

    financials = await get_sina_financial_report_async(session, code)
    if not financials:  # B: 新浪缺失 → fuyao 利润表兜底
        financials = get_financial_report_with_fallback(code)
    if financials:
        L(f"  {'报告期':<12} {'营业总收入':>11} {'净利润':>13} {'净利率':>8}")
        L(f"  {'-'*60}")
        for item in financials[:5]:
            date_val = item.get("报告日", "")
            rev = item.get("营业总收入", "0")
            profit = item.get("净利润", "0")
            try:
                rv = float(rev) if rev and rev != "0" else 0
                pf = float(profit) if profit and profit != "0" else 0
                rev_yi = f"{rv/1e8:.2f} 亿" if rv else "N/A"
                profit_yi = f"{pf/1e8:.2f} 亿" if pf else "N/A"
                npm = f"{pf/rv*100:.2f}%" if rv > 0 else "N/A"
            except (ValueError, TypeError, ZeroDivisionError):
                rev_yi, profit_yi, npm = "N/A", "N/A", "N/A"
            L(f"  {date_val:<12} {rev_yi:>15} {profit_yi:>15} {npm:>8}")
        L("\n  💡 中线逻辑核实：观察收入与净利润是否保持同步增长。")
    else:
        # V16.0: CanonicalStockData 无 net_profit_yi 字段（只有 net_profit，单位元）→ /1e8 转亿元
        net_profit_yi = (cdata.net_profit or 0) / 1e8
        if net_profit_yi > 0 or (cdata.roe is not None and cdata.roe > 0):
            # V16.3 O22: roe=0 视为缺失（canonical 缺失时 0.0 伪装成 0% 无信息量）
            roe_str = f"{cdata.roe:.2f}%" if cdata.roe and cdata.roe > 0 else "N/A"
            # V16.4.0: F10 数据=最新报告期（非 T 日）——展示标注报告期防误读为"当前 ROE"
            _rp = str(cdata.report_period or "")
            _rp_label = f"（{_rp[:4]}Q{((int(_rp[4:6]) - 1) // 3 + 1)}）" if len(_rp) >= 6 and _rp.isdigit() else ""
            L(
                f"  [ZHB 离线兜底] 归母净利润: {net_profit_yi:.2f} 亿元 | ROE: {roe_str}{_rp_label} | PE（TTM）: {cdata.pe_ttm:.1f}x | PB: {cdata.pb:.2f}x"
            )
        else:
            L("  (新浪财报数据获取失败或该股暂无相关数据)")

    # V17.0.7: push2 财务族对照——f105 归母净利(最新报告期)双源核验 + f190 每股未分配
    # (随 push2delay 补取入 canonical, 零额外请求; 口径经 fuyao 官方报表终判)
    try:
        _np_period_v7 = float(getattr(cdata, "net_profit_period", 0) or 0)
        _upp_v7 = float(getattr(cdata, "undist_profit_ps", 0) or 0)
        if _np_period_v7:
            L("\n  [归母净利润双源核验] (push2delay f105, 最新报告期):")
            _line_v7 = f"    push2 口径: {_np_period_v7/1e8:.2f} 亿元"
            if financials:
                _sina_np_v7 = _safe_float(financials[0].get("净利润", "0"))
                if _sina_np_v7:
                    _dev_v7 = abs(_np_period_v7 - _sina_np_v7) / abs(_sina_np_v7) * 100
                    _tag_v7 = "✅ 双源一致" if _dev_v7 <= 2 else "⚠️ 偏差较大(少数股东损益或口径差异, 以财报原文为准)"
                    _line_v7 += f" | 新浪财报: {_sina_np_v7/1e8:.2f} 亿元 → 偏差 {_dev_v7:.1f}% {_tag_v7}"
            L(_line_v7)
        if _upp_v7:
            _upp_tag_v7 = ("🚨 为负(弥补亏损期)" if _upp_v7 < 0
                           else ("✅ 分红池厚" if _upp_v7 >= 5 else "ℹ️ 分红池偏薄"))
            L(f"  [每股未分配利润] {_upp_v7:.2f} 元（分红能力池子, push2 f190≡ulist f48）{_upp_tag_v7}")
    except Exception as _e:
        _debug_log(f"med push2 fin family cross: {_e}")

    # ─── 4. 资产负债表财务健康度 ───
    L("\n## 【四、资产负债表财务健康度（排雷）】")
    L("---")
    bs_data = await get_sina_balance_sheet_async(session, code)
    if bs_data:
        latest = bs_data[0]
        prev = bs_data[1] if len(bs_data) > 1 else None
        L(f"  📊 最新报告期: {latest.get('报告日', 'N/A')}")
        ar = latest.get("应收账款", "0")
        inv = latest.get("存货", "0")
        gw = latest.get("商誉", "0")
        cash = latest.get("货币资金", "0")
        st_debt = latest.get("短期借款", "0")
        due_debt = latest.get("一年内到期的非流动负债", "0")
        equity = latest.get("归属于母公司股东权益合计", "0")
        total_assets = latest.get("资产总计", "0")
        total_liab = latest.get("负债合计", "0")

        def to_yi(v):
            try:
                return float(v) / 1e8
            except (ValueError, TypeError):
                return 0.0

        ar_yi = to_yi(ar)
        inv_yi = to_yi(inv)
        gw_yi = to_yi(gw)
        cash_yi = to_yi(cash)
        st_debt_yi = to_yi(st_debt)
        due_debt_yi = to_yi(due_debt)
        equity_yi = to_yi(equity)
        asset_yi = to_yi(total_assets)
        liab_yi = to_yi(total_liab)

        L(f"  {'科目':<26} {'金额(亿元)':>12} {'占总资产%':>10}")
        L(f"  {'-'*55}")
        L(f"  {'资产总计':<26} {asset_yi:>12.2f} {100.0:>9.1f}%")
        if asset_yi > 0:
            L(f"  {'负债合计':<26} {liab_yi:>12.2f} {liab_yi/asset_yi*100:>9.1f}%")
            L(f"  {'归属于母公司股东权益':<26} {equity_yi:>12.2f} {equity_yi/asset_yi*100:>9.1f}%")
            L(f"  {'应收账款':<26} {ar_yi:>12.2f} {ar_yi/asset_yi*100:>9.1f}%")
            L(f"  {'存货':<26} {inv_yi:>12.2f} {inv_yi/asset_yi*100:>9.1f}%")
            L(f"  {'货币资金':<26} {cash_yi:>12.2f} {cash_yi/asset_yi*100:>9.1f}%")
            L(f"  {'短期借款':<26} {st_debt_yi:>12.2f} {st_debt_yi/asset_yi*100:>9.1f}%")
            L(f"  {'一年内到期负债':<26} {due_debt_yi:>12.2f} {due_debt_yi/asset_yi*100:>9.1f}%")
            L(f"  {'商誉':<26} {gw_yi:>12.2f} {gw_yi/asset_yi*100:>9.1f}%")
        else:
            L("  ⚠️ 资产总计为0，跳过占比计算")

        if prev:
            ar_prev = to_yi(prev.get("应收账款", "0"))
            inv_prev = to_yi(prev.get("存货", "0"))
            gw_prev = to_yi(prev.get("商誉", "0"))

            def pct_chg(cur, prv):
                if prv > 0:
                    return (cur - prv) / prv * 100
                return 0

            L("\n  📈 环比变动（本期 vs 上期）:")
            L(f"    - 应收账款: {ar_yi:.2f}亿 (环比 {pct_chg(ar_yi, ar_prev):+.1f}%)")
            L(f"    - 存货: {inv_yi:.2f}亿 (环比 {pct_chg(inv_yi, inv_prev):+.1f}%)")
            L(f"    - 商誉: {gw_yi:.2f}亿 (环比 {pct_chg(gw_yi, gw_prev):+.1f}%)")

        flags = []
        if asset_yi > 0 and ar_yi / asset_yi > _ar_ratio_warn / 100:
            flags.append(
                f"⚠️ 应收账款占比{ar_yi/asset_yi*100:.0f}% > {_ar_ratio_warn:.0f}%，回款风险预警"
            )
        _total_debt = st_debt_yi + due_debt_yi
        if cash_yi > 0 and _total_debt > 0 and cash_yi / _total_debt < 1.5:
            flags.append(
                f"⚠️ 货币资金{cash_yi:.1f}亿仅覆盖短期债务{_total_debt:.1f}亿的{cash_yi/_total_debt*100:.0f}%，偿债压力较大"
            )
        # 商誉风险预警：需同时满足净资产>0和商誉占比超阈值
        if equity_yi > 0 and gw_yi > equity_yi * _gw_ratio / 100:
            flags.append(
                f"⚠️ 商誉占净资产{gw_yi/equity_yi*100:.0f}% > {_gw_ratio:.0f}%，减值风险预警"
            )
        elif gw_yi > 0 and equity_yi == 0:
            flags.append(f"⚠️ 商誉{gw_yi:.1f}亿，但净资产数据缺失，无法计算占比")
        if asset_yi > 0 and liab_yi / asset_yi > _debt_ratio_warn / 100:
            flags.append(
                f"⚠️ 资产负债率{liab_yi/asset_yi*100:.0f}% > {_debt_ratio_warn:.0f}%，杠杆偏高"
            )
        if prev and financials:
            try:
                _rev_latest = _safe_float(financials[0].get("营业总收入", "0"))
                _rev_prev = (
                    _safe_float(financials[1].get("营业总收入", "0")) if len(financials) > 1 else 0
                )
                _ar_incr = ar_yi - ar_prev
                _rev_decr = (
                    (_rev_latest - _rev_prev) / 1e8
                    if _rev_latest > 1e5
                    else _rev_latest - _rev_prev
                )
                if _rev_decr < 0 and _ar_incr > 0:
                    flags.append(f"⚠️ 营收下滑但应收账款逆势增长{_ar_incr:.2f}亿，回款风险加剧")
                elif _ar_incr / max(_rev_decr, 1) > 0.3:
                    flags.append(
                        f"⚠️ 应收账款增量占营收增量{_ar_incr/max(_rev_decr,1)*100:.0f}%，营收含金量偏低"
                    )
            except (ValueError, TypeError, ZeroDivisionError, IndexError) as _e:
                _debug_log(f"med bs_flag_calc: {_e}")
        if flags:
            L("")
            for flag in flags:
                L(f"  {flag}")
        else:
            L("\n  ✅ 资产负债表整体健康，未触发预警阈值。")
    else:
        L("  (资产负债表数据获取失败)")

    # ─── 5. 一致预期与PEG成长估值 ───
    L("\n## 【五、机构一致预期与前向 PEG】")
    L("---")
    reports = None  # V16.1: 研报懒加载，EPS fallback 与评级章节共享
    df_eps = await get_eps_forecast_async(session, code)
    eps_cur = eps_next = None
    eps_has_data = False
    if not df_eps.empty and len(df_eps.columns) >= 4:
        L(f"  {'年度':<10} {'覆盖机构数':<10} {'预测EPS均值':<12}")
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
            except (ValueError, TypeError, IndexError) as _e:
                _debug_log(f"med eps_row_parse: {_e}")
    if not eps_has_data:
        # V16.1: 复用研报正文请求（避免 max_pages=1 与 max_pages=3 两次重复请求）
        # 仅当研报尚未在"六"章节获取时独立请求
        try:
            if reports is None:
                reports = await get_reports_async(session, code, max_pages=3)
        except Exception:
            reports = None
        em_eps = None
        if reports:
            for r in reports:
                ty = r.get("predictThisYearEps")
                ny = r.get("predictNextYearEps")
                if ty is not None and str(ty).strip():
                    em_eps = {
                        "eps_cur": float(ty),
                        "eps_next": float(ny) if ny is not None and str(ny).strip() else None,
                    }
                if em_eps:
                    break
        if em_eps:
            eps_cur = em_eps["eps_cur"]
            eps_next = em_eps.get("eps_next")
            eps_has_data = True
            this_year = date.today().year
            this_month = date.today().month
            label_cur = f"预测{this_year}年" if this_month > 4 else f"{this_year}年"
            label_next = f"预测{this_year + 1}年" if this_month > 4 else f"预测{this_year}年"
            L("  东财研报一致预期EPS (同花顺兜底):")
            L(f"  {'年度':<14} {'预测EPS'}")
            L(f"  {'-'*30}")
            if eps_cur:
                L(f"  {label_cur:<14} {eps_cur:.3f}")
            if eps_next:
                L(f"  {label_next:<14} {eps_next:.3f}")
    if eps_has_data and price_today and eps_cur and eps_cur > 0:
        pe_fwd = price_today / eps_cur
        L(f"\n  ➤ 前向市盈率 (预测今年): {pe_fwd:.2f}x")
        if eps_next and eps_cur > 0:
            cagr = (eps_next / eps_cur) - 1
            L(f"  ➤ 预期净利增速: {cagr*100:.1f}%")
            peg = pe_fwd / (cagr * 100) if cagr > 0 else float("inf")
            if peg == float("inf"):
                eval_str = "无法计算"
            elif peg < _peg_good:
                eval_str = "偏低估 (合理区间之下)"
            elif peg <= _peg_rational:
                eval_str = "估值合理"
            else:
                eval_str = "偏高估 (存在透支预期风险)"
            L(f"  ➤ 核心 PEG 指标: {peg:.2f} → {eval_str}")
        _sk_m, _sr_m = await asyncio.to_thread(baidu_kline_full, code)
        if len(_sr_m) >= 26:
            _ci_m = next((i for i, k in enumerate(_sk_m) if k in ("close", "close_price")), -1)
            if _ci_m >= 0:
                # V16.1: 取更多 K 线（120 根）接入共享技术引擎（MACD/RSI/BOLL/KDJ/均线）
                # V17.0.15 修复: TDX 日K 本就返回 open/close/high/low/volume/amount
                #   （见 core/tdx_client.tdx_get_security_bars 的 keys），原实现却把
                #   highs/lows 用 close 近似、volumes 传空列表，造成两处实质失真：
                #   ① KDJ 的 RSV=(C−L9)/(H9−L9) 分母退化成「9 日*收盘价*极差」——系统性小于
                #      真实 9 日振幅 → RSV 被放大 → 金叉/超买信号过度敏感（一字板时 H9==L9
                #      还会被强制钉成 RSV=50）；
                #   ② analyze_technical 在 volumes 为空时**根本不产出 volume 键** → 量价
                #      配合判断全程缺失。改为按列名取真实值，仅在列缺失时回退 close 近似。
                _hi_i = next((i for i, k in enumerate(_sk_m) if k in ("high", "high_price")), -1)
                _lo_i = next((i for i, k in enumerate(_sk_m) if k in ("low", "low_price")), -1)
                _vol_i = next((i for i, k in enumerate(_sk_m) if k in ("volume", "vol")), -1)
                _need_i = max(i for i in (_ci_m, _hi_i, _lo_i, _vol_i) if i >= 0)
                # 统一行过滤条件：确保 closes/highs/lows/volumes 四序列严格等长对齐
                _rows_m = [rr for rr in _sr_m[-120:] if len(rr) > _need_i]
                _cls_m = [_safe_float(rr[_ci_m]) for rr in _rows_m]
                if len(_cls_m) >= 26:
                    from stock_common.sc_technical import analyze_technical

                    _hi_m = ([_safe_float(rr[_hi_i]) for rr in _rows_m]
                             if _hi_i >= 0 else _cls_m[:])
                    _lo_m = ([_safe_float(rr[_lo_i]) for rr in _rows_m]
                             if _lo_i >= 0 else _cls_m[:])
                    _vol_m = ([_safe_float(rr[_vol_i]) for rr in _rows_m]
                              if _vol_i >= 0 else [])
                    _tech = analyze_technical(_cls_m, _hi_m, _lo_m, _vol_m)
                    _macd = _tech.get("macd", {})
                    if _macd:
                        _dif = _macd.get("dif", 0)
                        _dea = _macd.get("dea", 0)
                        _macd_sig = "金叉" if _dif > _dea else "死叉" if _dif < _dea else "粘合"
                        L(f"  [MACD] DIF={_dif:.3f} DEA={_dea:.3f}（{_macd_sig}）")
                    _ma20 = _tech.get("ma", {}).get("ma20", 0)
                    _ma60 = _tech.get("ma", {}).get("ma60", 0)
                    _ma_st = (
                        "多头排列"
                        if _cls_m[-1] > _ma20 > _ma60
                        else ("空头排列" if _cls_m[-1] < _ma20 else "震荡")
                    )
                    L(f"  [均线] MA20={_ma20:.2f} MA60={_ma60:.2f} | {_ma_st}")
                    _rsi = _tech.get("rsi", {})
                    if _rsi:
                        L(f"  [RSI] RSI14={_rsi.get('rsi14', 0):.1f}{'（超买）' if _rsi.get('rsi14', 0) > 70 else '（超卖）' if _rsi.get('rsi14', 0) < 30 else ''}")
                    _boll = _tech.get("boll", {})
                    if _boll:
                        L(f"  [BOLL] 位置={_boll.get('pos_pct', 50):.0f}% 带宽={_boll.get('width_pct', 0):.1f}%")
                    # V17.0.15: KDJ 现基于真实 high/low（此前用 close 近似 → RSV 分母退化失真）
                    _kdj = _tech.get("kdj", {})
                    if _kdj:
                        _k, _d = _kdj.get("k", 50.0), _kdj.get("d", 50.0)
                        _kp, _dp = _kdj.get("k_prev", _k), _kdj.get("d_prev", _d)
                        if _k > _d and _kp <= _dp:
                            _kdj_sig = "✅金叉"
                        elif _k < _d and _kp >= _dp:
                            _kdj_sig = "⚠️死叉"
                        else:
                            _kdj_sig = ""
                        _kdj_zone = "（超买）" if _k > 80 else ("（超卖）" if _k < 20 else "")
                        L(f"  [KDJ] K={_k:.1f} D={_d:.1f} J={_kdj.get('j', 0):.1f}{_kdj_zone} {_kdj_sig}".rstrip())
                    # V17.0.15: 量能分析（此前 volumes 恒传空列表 → analyze_technical 不产出该键）
                    _vol = _tech.get("volume", {})
                    if _vol:
                        _vr = _vol.get("ratio", 1.0)
                        _vt = _vol.get("trend_pct", 0.0)
                        _vt_s = "放量" if _vt > 20 else ("缩量" if _vt < -20 else "量能平稳")
                        L(
                            f"  [量能] 今日 {_vol.get('today_wan', 0):.1f}万手 "
                            f"(5日均 {_vol.get('ma5_wan', 0):.1f}万) 量比={_vr:.2f} "
                            f"近5日较前5日 {_vt:+.1f}% → {_vt_s}"
                        )
            if pe_fwd > _pe_mid and cagr > 0:
                digest = math.log(pe_fwd / _pe_mid) / math.log(1 + cagr)
                L(f"  ➤ 估值消化到30x需: {digest:.1f} 年")
            try:
                _sk_p, _sr_p = await asyncio.to_thread(baidu_kline_full, code)
                _ci_p = next((i for i, k in enumerate(_sk_p) if k in ("close", "close_price")), -1)
                if _ci_p >= 0 and eps_cur > 0:
                    _hp = [_safe_float(rr[_ci_p]) for rr in _sr_p if len(rr) > _ci_p]
                    if len(_hp) > 20:
                        _hpe = [p / eps_cur for p in _hp if p > 0]
                        if _hpe:
                            _pc = sum(1 for p in _hpe if p < pe_fwd) / len(_hpe) * 100
                            L(f"  PE历史分位: {_pc:.0f}%（低于{_pc:.0f}%的历史时间）")
            except Exception as _e:
                _debug_log(f"med pe_percentile error: {_e}")
    else:
        has_black_horse = False
        _st_name = info.get("name", "")
        if "ST" in _st_name or "*ST" in _st_name or "退" in _st_name:
            L("  ⚠️ 该股为ST/风险警示股，不具备黑马潜质，中线严禁左侧建仓！")
        elif financials and len(financials) >= 2:
            try:
                p1, p2 = _safe_float(financials[-1]["净利润"]), _safe_float(
                    financials[-2]["净利润"]
                )
                r1, r2 = _safe_float(financials[-1]["营业总收入"]), _safe_float(
                    financials[-2]["营业总收入"]
                )
                if p1 > p2 and r1 > r2:
                    has_black_horse = True
            except (IndexError, KeyError, TypeError) as _e:
                _debug_log(f"med black_horse_check: {_e}")
        if has_black_horse:
            L("  ⚡ 无机构覆盖，但近两季度净利润+营收连续环比改善，具备黑马潜质预警！")
        elif reports:
            L("  暂无机构EPS一致预期（已有研报覆盖，详见【六】章节评级统计）")
        else:
            L("  无机构覆盖数据（中线建议规避无主流机构覆盖的冷门股）")

    # ─── 4. 研报评级风向标 ───
    L("\n## 【六、研报评级统计与风向变动 (近3个月)】")
    L("---")
    # V16.1: 复用 EPS fallback 已拉取的研报（避免两次请求）
    if reports is None:
        reports = await get_reports_async(session, code, max_pages=3)
    if reports:
        buy_count, add_count = 0, 0
        rating_up, rating_down = 0, 0
        for r in reports:
            rating = str(r.get("emRatingName", ""))
            if "买入" in rating:
                buy_count += 1
            elif "增持" in rating:
                add_count += 1
            # V16.1: 评级变化统计（ratingChange: 3=上调 1=下调 参考）
            _rc = r.get("ratingChange")
            if _rc is not None:
                try:
                    rc_int = int(_rc)
                    if rc_int >= 3:
                        rating_up += 1
                    elif rc_int == 1:
                        rating_down += 1
                except (TypeError, ValueError):
                    pass
        L(f"  统计样本：近 {len(reports)} 篇研报")
        L(f"  买入评级: {buy_count} 篇 | 增持评级: {add_count} 篇")
        # V16.1: 评级风向（评级上调/下调）
        if rating_up or rating_down:
            L(f"  评级变化: 上调 {rating_up} 篇 | 下调 {rating_down} 篇"
              + (" → 机构态度偏积极" if rating_up > rating_down else " → 机构态度偏谨慎" if rating_down > rating_up else ""))
        _rep_sorted = sorted(
            reports,
            key=lambda r: str(r.get("publishDate", r.get("reportDate", "")))[:10],
            reverse=True,
        )
        _rep_shown = _rep_sorted[:5]
        L(f"\n  最新 {len(_rep_shown)} 篇核心研报观点:")
        for r in _rep_shown:
            pub_date = str(r.get("publishDate", ""))[:10]
            org = r.get("orgSName", "")
            title = r.get("title", "")[:45]
            rating = r.get("emRatingName", "无")
            L(f"    - [{pub_date}] {org} ({rating}): {title}")
    else:
        L("  暂无相关研报评级数据。")

    # ─── 5. 重大公告追踪 ───
    L("\n## 【七、重大实质性公告追踪 (避雷与催化)】")
    L("---")
    anns = await get_strategic_announcements_async(session, code, days=30)
    if anns:
        for i, a in enumerate(anns[:10], 1):
            L(f"  {i}. [{a['date']}] {a['title']}")
        rc = sum(1 for a in anns if "减持" in a["title"])
        if rc > 0:
            L(f"\n  ⚠️ 减持预警：近期有 {rc} 条减持相关公告，请仔细甄别。")
        L("\n  💡 中线提醒：重点关注定增、股权激励、减持计划及大额中标公告。")
    else:
        L("  近期无过滤后的重大公告。")

    # ─── 6. 筹码稳定性分析 ───
    L("\n## **八、筹码稳定性与抛压评估**")
    L("---")
    holders = await get_holder_change_async(session, code)
    # V17.0.14: 筹码分布 CYQ —— 提前获取(东财 kline f61 → calculate_cyq), 供章节+评分复用
    _cyq_dict = {}
    try:
        from stock_common.sc_datasource import get_cyq_distribution
        _cyq_dict = await asyncio.to_thread(get_cyq_distribution, code) or {}
    except Exception as _e:
        _debug_log(f"med cyq ({code}): {_e}")
    if holders:
        L("  ➤ 股东户数变化趋势:")
        # V17.0.2m: md 表格(用户: 股东户数趋势用表格)
        L("| 截止日期 | 股东户数 | 环比变化 |")
        L("|---|---|---|")
        for h in holders[:5]:
            _cr = h['change_ratio']
            # 边界检查：变化率超过±500%视为异常数据，不显示
            _cr_disp = _cr if abs(_cr) <= 500 else (999.99 if _cr > 500 else -999.99)
            _cr_flag = " ⚠️" if abs(_cr) > 500 else ""
            L(
                f"| {h['date']} | {h['holder_num']:,} | {_cr_disp:+.2f}%{_cr_flag} |"
            )
        latest = holders[0]
        if latest["change_ratio"] <= -3:
            L("    ✅ 结论: 筹码正在集中，利好中线。")
        elif latest["change_ratio"] >= 3:
            L("    ⚠️ 结论: 筹码趋于分散，散户增多，注意风险。")

    # V17.0.14: 筹码分布 CYQ 章节(东财 kline f61 → calculate_cyq)
    if _cyq_dict:
        L("\n  ➤ 筹码分布（成本集中度）:")
        _ben = _cyq_dict.get("benefit_pct", 0.0) or 0.0
        _c90 = _cyq_dict.get("concentration_90", 0.0) or 0.0
        _c70 = _cyq_dict.get("concentration_70", 0.0) or 0.0
        _avg = _cyq_dict.get("avg_cost", 0.0) or 0.0
        L(f"    - 获利盘比例: {_ben*100:.1f}%（现价下持仓盈利占比）")
        L(f"    - 平均成本: {_avg:.2f} 元")
        L(f"    - 90% 筹码集中度: {_c90:.3f}（成本区间 {_cyq_dict.get('cost_90_low',0):.2f}~{_cyq_dict.get('cost_90_high',0):.2f}）")
        L(f"    - 70% 筹码集中度: {_c70:.3f}（成本区间 {_cyq_dict.get('cost_70_low',0):.2f}~{_cyq_dict.get('cost_70_high',0):.2f}）")
        _cflag = "高度集中" if _c90 < 0.12 else ("较集中" if _c90 < 0.2 else ("分散" if _c90 > 0.35 else "中性"))
        _pflag = ("获利盘丰厚，上方解套抛压需关注" if _ben > 0.85
                  else ("套牢盘较重，反弹承压" if _ben < 0.25 else "成本结构均衡"))
        L(f"    ➤ 研判: 筹码{_cflag}；{_pflag}")

    lockup = await get_lockup_expiry_async(session, code, days=180)
    if lockup:
        _cal_evts = [
            f"{_h['date']} 解禁{_h['ratio']:.1f}%" for _h in lockup if _h.get('ratio', 0) > 0
        ]
        L("\n  ➤ 未来可预期事件:")
        if _cal_evts:
            for _ev in _cal_evts[:5]:
                L(f"    📅 {_ev}")
        else:
            L("    (暂无已披露近期事件)")
    if lockup:
        total_upcoming = sum(h["shares"] for h in lockup)
        L("\n  ➤ 解禁抛压预警 (未来180天):")
        L(f"    ⚠️ 待解禁总计: {total_upcoming/1e4:.1f}万股")
        for h in lockup:
            L(f"    - {h['date']}: {h['type']} ({h['shares']/1e4:.1f}万股, 占 {h['ratio']:.2f}%)")
    else:
        L("\n  ➤ 解禁抛压预警: 未来半年内无解禁压力 ✅")

    # ─── 北向资金持仓动态 ───
    L("\n## **九、北向资金持仓动态**")
    L("---")
    nb = await get_northbound_hold_async(session, code, 90)
    if nb:
        _label = "期" if len(nb) <= 12 else "个交易日"
        L(f"  近 {len(nb)} {_label}北向持仓数据:")
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
                # M12 修复(2026-08-15 二审): fallback 占比为小数(股数/总股本), 主路径为百分数
                # (东财 FREE_SHARES_RATIO)——统一 ×100 百分数口径, 原差 100 倍
                _ratio = (
                    # V17.3 修正(审查): info.total_shares 单位万股(== cdata.total_shares_wan), _shares(北向持股)为股;
                    # 原 _shares/info.total_shares 股÷万股错配(差1e4)。改统一层 cdata.total_shares_wan*1e4=股, ×100 百分数。
                    _shares / (cdata.total_shares_wan * 1e4) * 100
                    if cdata.total_shares_wan > 0 else 0
                )
            L(
                f"  {d['date']:<12} {_shares/1e4:>12.0f} {_mcap/1e4:>12.0f} {_ratio:>9.4f}% {d['change_shares']/1e4:>+12.0f}"
            )
        if len(nb) >= 2:
            ratio_change = nb[0]["hold_ratio"] - nb[-1]["hold_ratio"]
            if ratio_change > 0:
                L(f"  ➤ 信号: 近{len(nb)}{_label}北向持股比例 +{ratio_change:.4f}%，外资增持")
            elif ratio_change < 0:
                L(f"  ➤ 信号: 近{len(nb)}{_label}北向持股比例 {ratio_change:.4f}%，外资减持")
    else:
        L("  该股暂无北向资金持仓数据（可能非陆股通标的或数据延迟）")

    # ─── 同业龙头横向对比 ───
    L("\n## 【十、同业龙头横向对比（赛道身位监测）】")
    L("---")
    if peer_data["peers"]:
        if "note" in peer_data["peers"][0]:
            L(f"  ⚠️ {peer_data['peers'][0]['note']}")
        else:
            L(f"  所属板块: {peer_data['industry']}")
            L(f"  本股市值: {peer_data['my_mcap']:.1f}亿元")
            if peer_data.get("my_rank", 0) > 0:
                L(
                    f"  业内排名: 第 {peer_data['my_rank']}/{peer_data['industry_count']} 位（按总市值）"
                )
            # V17.0.27(2026-09-04) 与 sht 同业表同步的三项修复（9/3 报告核查 #1/#2/#3）：
            #   #1 本股/同业 PE 原为裸 `{x:.1f}`，亏损股输出 "0.0" —— 读者误读为「零估值」，
            #      违反 A6（缺失≠0）。sht 同位置早有 `if >0 else "亏损"` 判断，med 漏做 →
            #      同一消费点两个脚本实现不一致。此处补齐。
            #   #2 列标题原写 "PE（TTM）"，但同业行 `p['pe']` 实为 pe_dynamic → 标题与口径不符
            #      且与本股行(pe_ttm)不同口径、同列不可比。统一为「PE（动）」+ 本股行取 pe_dynamic。
            #   #3 同业 change_pct 取不到时为 0，直接渲染 "0.00%" 被误读为「平盘」（实证 300442），
            #      改为显式 N/A。
            L(
                f"  {'代码':<8} {'名称':<12} {'股价':>8} {'涨跌幅%':>8} {'市值(亿)':>10} {'PE（动）':>9} {'PE（静）':>8} {'换手率%':>8}"
            )
            L(f"  {'-'*80}")
            _my_pe_lyr_s = f"{cdata.pe_lyr:.1f}" if cdata.pe_lyr > 0 else "N/A"
            _my_pe_dyn = cdata.pe_dynamic or 0
            _my_pe_dyn_s = f"{_my_pe_dyn:.1f}" if _my_pe_dyn > 0 else "亏损"
            L(
                f"  {code:<8} {stock_name:<12} {price_today:>8.2f} {cdata.change_pct:>7.2f}% {peer_data['my_mcap']:>9.1f} {_my_pe_dyn_s:>9} {_my_pe_lyr_s:>8} {cdata.turnover_pct:>7.2f}% ← 本股"
            )
            for p in peer_data["peers"]:
                _ppe_lyr_s = f"{p.get('pe_lyr', 0):.1f}" if p.get('pe_lyr', 0) > 0 else "N/A"
                _ppe = p.get('pe', 0) or 0
                _ppe_s = f"{_ppe:.1f}" if _ppe > 0 else "亏损"
                _pchg = p.get('change_pct', 0) or 0
                _pchg_s = f"{_pchg:>7.2f}%" if _pchg != 0 else "    N/A "
                L(
                    f"  {p['code']:<8} {p['name']:<12} {p['price']:>8.2f} {_pchg_s} {p['mcap_yi']:>9.1f} {_ppe_s:>9} {_ppe_lyr_s:>8} {p['turnover']:>7.2f}%"
                )
            fin_metrics = await get_gross_margin_and_roe_async(
                session, code, fin_report=financials, bs_data=bs_data
            )
            if fin_metrics:
                _med_rp = str(cdata.report_period or "")
                _med_rp_label = (
                    f"（{_med_rp[:4]}Q{((int(_med_rp[4:6]) - 1) // 3 + 1)}）"
                    if len(_med_rp) >= 6 and _med_rp.isdigit() else "")
                gm = fin_metrics.get("gross_margin")
                roe = fin_metrics.get("roe")
                parts = []
                if gm is not None:
                    parts.append(f"毛利率 {gm:.1f}%")
                if roe is not None:
                    parts.append(f"ROE {roe:.1f}%")
                if parts:
                    L(f"\n  📊 本股财务质量: {' | '.join(parts)}{_med_rp_label}")
    else:
        L(f"  无法获取同业数据（板块: {peer_data.get('industry', '未知')}）")

    # ─── 中线主力资金底仓流向 ───
    L("\n## 【十一、中线主力资金流向 (60日基准)】")
    L("---")
    # V15.4.2: 同步资金流包 to_thread
    fund_flow = await asyncio.to_thread(get_fund_flow_120d, code)
    if fund_flow["data"]:
        # V16.1: get_em_history_fund_flow "最新在前"，[:20]/[:60] 取最近（原 [-20:]/[-60:] 取最旧）
        fund_data = fund_flow["data"]
        recent_20 = fund_data[:20]
        total_main_20 = sum(d["main_net"] for d in recent_20)
        days_bullish_20 = sum(1 for d in recent_20 if d["main_net"] > 0)
        recent_60 = fund_data[:60]
        total_main_60 = sum(d["main_net"] for d in recent_60)
        # V16.2.4: 延时镜像域可能只有当日数据 → 按实际条数标注，避免"1天/20天"误导
        L("  ➤ 近 20 个交易日：")
        L(f"    主力净流入天数: {days_bullish_20} 天 / {len(recent_20)} 天（实有数据）")
        L(f"    累计主力净流入: {total_main_20/1e8:.2f} 亿元")
        L("  ➤ 近 60 个交易日（中期视角）：")
        L(f"    累计主力净流入: {total_main_60/1e8:.2f} 亿元")
        # V16.4.1: 历史数据不足(<5 天)时不下中线结论——
        # 2026-08-12 实测仅 1 天数据却输出"吸筹/护盘"误导性结论
        _n_days = len(recent_60)
        if _n_days < 5:
            L(f"    ⚠️ 数据不足: 历史资金流仅 {_n_days} 天(源限制), 暂不下中线结论")
        elif total_main_60 > 0:
            L("    ✅ 资金面结论: 中线资金呈吸筹/护盘状态。")
        else:
            L("    ⚠️ 资金面结论: 中线资金呈流出状态，需结合估值谨慎判断。")
    elif fund_flow["error"]:
        L(f"  {fund_flow['error']}")
    else:
        L("  中线资金流数据获取失败。")

    if fund_flow.get("data") and len(fund_flow["data"]) >= 20:
        _p20 = [d["main_net"] for d in fund_flow["data"][:20]]
        _pc_chg = cdata.change_pct
        _cum_f = sum(_p20)
        if _cum_f < 0 and _pc_chg > 3:
            L(f"  ⚠️ 量价背离：近20日主力净流出{abs(_cum_f)/1e8:.2f}亿，股价涨{_pc_chg:.1f}%缺支撑")
        elif _cum_f > 0 and _pc_chg < -3:
            L(f"  💎 资金背离：股价下跌但主力净流入{_cum_f/1e8:.2f}亿，资金暗中介入")

    L("\n## 【十二、融资融券（两融数据，近15日）】")
    L("---")
    margin = await get_margin_trading_async(session, code)
    if margin:
        L(
            f"  {'日期':<12} {'融资余额(万)':>10} {'融资买入(万)':>10} {'融资偿还(万)':>10} {'融券余额(万)':>10}"
        )
        L(f"  {'-'*70}")
        for d in margin[:10]:
            L(
                f"  {d['date']:<12} {d['rzye']/1e4:>14.0f} {d['rzmre']/1e4:>14.0f} {d['rzche']/1e4:>14.0f} {d['rqye']/1e4:>14.0f}"
            )
        # V16.1: 两融净买入 + 3/5/10日维度（中线资金确认）
        latest = margin[0]
        if latest.get("rzjme") is not None:
            L(f"  最新融资净买入: {latest['rzjme']/1e4:+.0f}万元"
              + (f" | 融券净卖出: {latest.get('rqjmg', 0)/1e4:+.0f}万元" if latest.get("rqjmg") is not None else ""))
        _d5 = next((d for d in margin if d.get("rzmre_5d") is not None), None)
        _d10 = next((d for d in margin if d.get("rzmre_10d") is not None), None)
        if _d5:
            L(f"  5日融资买入: {_d5['rzmre_5d']/1e4:.0f}万元 | 5日偿还: {_d5.get('rzche_5d',0)/1e4:.0f}万元 | 5日涨幅: {_d5.get('chg_5d',0):+.2f}%")
        if _d10:
            L(f"  10日融资买入: {_d10['rzmre_10d']/1e4:.0f}万元 | 10日偿还: {_d10.get('rzche_10d',0)/1e4:.0f}万元 | 10日涨幅: {_d10.get('chg_10d',0):+.2f}%")
        if latest.get("balance_gr") is not None:
            L(f"  融资余额环比: {latest['balance_gr']:+.2f}%")  # V16.2.3: balance_gr 已是百分数（东财原值），去掉 *100
    else:
        L("  该股无融资融券数据（可能不是两融标的）。")

    L("\n## 【十三、大宗交易（机构建仓痕迹）】")
    L("---")
    bt = await get_block_trade_async(session, code)
    _one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    bt_filtered = [d for d in bt if d.get("date", "") >= _one_year_ago] if bt else []
    if bt_filtered:
        L(f"  近1年共 {len(bt_filtered)} 笔大宗交易（历史共 {len(bt)} 笔）:")
        # V17.0.2m: md 表格(原空格表"成交量万+买方"1 空格粘连)
        L("| 日期 | 成交价 | 溢价% | 成交量(万股) | 买方 |")
        L("|---|---|---|---|---|")
        for d in bt_filtered:
            L(f"| {d['date']} | {d['price']:.2f} | {d['premium_pct']:+.2f}% | {d['vol']/1e4:.0f} | {d['buyer']} |")
    else:
        L("  无大宗交易记录。")

    L("\n## **十四、龙虎榜机构动向**")
    L("---")
    dtb = await get_dragon_tiger_board_async(session, code, days=180)
    if dtb and dtb.get("records"):
        L(f"  近180日上榜 {len(dtb['records'])} 次:")
        # V17.0.6: 直出 md 表格(同 sht)
        L("| 日期 | 上榜原因 | 净买入(万) | 换手率 |")
        L("|---|---|---|---|")
        for r in dtb["records"]:
            L(f"| {r['date']} | {r.get('reason', '')} | {r['net_buy']:.1f} | {r['turnover']:.2f}% |")

        seats = dtb["seats"]
        if seats["buy"]:
            L("\n  最近买入席位 TOP5:")
            # V17.0.2i: md 表格(原空格表无表头行识别 → 未转)
            L("| 营业部名称 | 买入(万) | 卖出(万) | 净额(万) |")
            L("|---|---|---|---|")
            for s in seats["buy"]:
                L(f"| {s['name']} | {s['buy_amt']:.1f} | {s['sell_amt']:.1f} | {s['net']:.1f} |")
        if seats["sell"]:
            L("\n  最近卖出席位 TOP5:")
            L("| 营业部名称 | 买入(万) | 卖出(万) | 净额(万) |")
            L("|---|---|---|---|")
            for s in seats["sell"]:
                L(f"| {s['name']} | {s['buy_amt']:.1f} | {s['sell_amt']:.1f} | {s['net']:.1f} |")
        inst = dtb["institution"]
        if inst and (inst.get("buy_amt", 0) > 0 or inst.get("sell_amt", 0) > 0):
            L("\n  机构买卖统计:")
            L(f"    机构买入金额: {inst['buy_amt']}万元")
            L(f"    机构卖出金额: {inst['sell_amt']}万元")
            L(f"    机构净买入: {inst['net_amt']}万元")
    else:
        L("  近180日无龙虎榜记录（白马蓝筹或近期未触发异动标准的个股，无龙虎榜属正常现象）。")

    # ─── 9. 高股息防御属性 (分红历史) ───
    L("\n## 【十五、高股息防御属性 (近十次分红)】")
    L("---")
    # 股息率：cdata 统一提供
    _zhb_div_yield = cdata.dividend_yield
    if _zhb_div_yield > 0:
        L(f"  当前股息率: {_zhb_div_yield:.2f}%")
    div = await asyncio.to_thread(get_dividend_history, code)
    if div and len(div) >= 3:
        _dy = len(set(d["date"][:4] for d in div if d.get("bonus_rmb", 0) > 0))
        L(f"  📊 分红持续性: 连续{_dy}年分红")
        if _dy >= 5:
            L("    💎 连续5年以上分红，具备稳定防御属性")
    if div:
        L("  近5次分红除息记录:")
        # V17.0.2i: md 表格(原空格表无分隔线行 → 未转)
        L("| 除权除息日 | 每股派息(元) | 折算对应股价股息率参考 |")
        L("|---|---|---|")
        for d in div[:5]:
            yield_str = f"{(d['bonus_rmb'] / price_today) * 100:.2f}%" if price_today > 0 else "N/A"
            L(f"| {d['date']} | {d['bonus_rmb']:.4f} | 约 {yield_str} (按现价计) |")
    else:
        # V16.2.3: 区分"接口失败"与"真无分红"
        L("  分红数据获取失败（TDX 接口暂不可用）。" if div is None else
          "  暂无分红记录（非防御型收息标的）。")

    # ─── 16. 十大流通股东机构动向 ───
    L("\n## 【十六、十大流通股东机构动向】")
    L("---")
    st = await asyncio.to_thread(get_holder_structure, code)
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
        _dd = st[0].get("dm_detail", {})
        if _dd:
            _parts = [f"{k} {v:.1f}%" for k, v in _dd.items()]
            L(f"\n  境内机构细分: {' | '.join(_parts)}")
        latest = st[0]
        if latest['foreign'] > 30:
            L(f"  🔍 外资机构合计持股 {latest['foreign']:.1f}%，话语权极强")
        if latest['northbound'] > 10:
            L(f"  🔍 北向资金持股 {latest['northbound']:.1f}% > 10%，重要边际定价力量")
        if latest['individual'] > 10:
            L(f"  🔍 个人大股东合计持股 {latest['individual']:.1f}%，利益深度绑定")
    else:
        L("  十大流通股东数据获取失败。")

    # ─── V17.0.5: 基金持仓侧证(自选基金清单门控——credentials/fund_watch.json, 缺失零请求) ───
    try:
        from stock_common.sc_fuyao import get_fund_watch_evidence

        _fw = await asyncio.to_thread(get_fund_watch_evidence, code)
    except Exception:
        _fw = None
    if _fw and _fw.get("checked"):
        L("\n## 【十六之二、自选基金重仓侧证 (fuyao)】")
        L("---")
        if _fw["held"]:
            for _f in _fw["held"]:
                _line = f"  {_f['alias']}: 持仓占比 {_f['hold_ratio']:.2f}%"
                if _f.get("investment_rank"):
                    _line += f" / 第{_f['investment_rank']}大重仓"
                _inc = _f.get("period_increase_rate_pct")
                if _inc is not None:
                    _line += f" / 报告期增减 {_inc:+.2f}%"
                L(_line)
            _f0 = _fw["held"][0]
            L(f"  （基金股票仓位 {(_f0.get('fund_stock_pct') or 0):.1f}%，前十集中度 {(_f0.get('concentration_ratio') or 0):.1f}%）")
        else:
            L("  所列自选基金最新报告期均未重仓本股")
        L("  （定期披露非实时；清单见 credentials/fund_watch.example.json）")

    L("\n" + "=" * 72)
    _bt_items = []
    if holders and len(holders) >= 2:
        _hd_chg = holders[0].get("change_ratio", 0)
        if _hd_chg < -3:
            _bt_items.append(f"股东户数减少{abs(_hd_chg):.1f}%（历史类似信号后中线偏多）")
    if nb and len(nb) >= 5:
        _nb_s = _safe_float(nb[-1].get("hold_shares", 0))
        _nb_e = _safe_float(nb[0].get("hold_shares", 0))
        if _nb_s > 0:
            _nb_chg = (_nb_e - _nb_s) / _nb_s * 100
            _bt_items.append(f"北向近{len(nb)}日持仓{_nb_chg:+.1f}%")
    if _bt_items:
        L("## **回测参考**")
        for _bi in _bt_items:
            L(f"  📊 {_bi}")

    # ─── 十七、舆情与互动 ───
    L("\n## **十七、舆情与互动**")

    # 财联社快讯（近3天）
    try:
        cls_news = await asyncio.to_thread(cls_telegraph, 50)
        _cls_shown = 0
        _cls_cutoff = datetime.now() - timedelta(hours=48)  # V16.2.14: 3天→48h
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
            if title and news_matches_stock(title, code, cdata.name):
                L(f"  · [{t_str[:16]}] {title[:80]}")
                _cls_shown += 1
                if _cls_shown >= 10:
                    break
        if _cls_shown == 0:
            L("  近48小时无个股相关财联社快讯")
    except Exception as _e:
        _debug_log(f"med cls_telegraph: {_e}")

    # 互动易问答（近48小时）— V16.2.14: 48h+标题+答案+合理条数
    try:
        irm = await asyncio.to_thread(cninfo_irm, code, 30)
        L("  近48小时互动易问答:")
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
            q = str(item.get("question", "")).strip()[:120]
            if q:
                a = str(item.get("answer", "")).strip()
                # V17.3 修复: cninfo_irm 对未回复问题偶发返回字面字符串 "None"/"nan",
                # 需归一为"待回复", 否则泄漏 None 到报告(与 sht 的"(公司待回复)"口径对齐)
                if a.lower() in ("none", "nan", "n/a", "null"):
                    a = ""
                _ans = f"答案: {a[:120]}" if a else "答案: （公司待回复）"
                L(f"  · [{t_str[:16]}] 提问: {q}")
                L(f"      {_ans}")
                _irm_shown += 1
                if _irm_shown >= 10:
                    L(f"  （近48小时共 {len(irm)} 条中最新 10 条）")
                    break
        if _irm_shown == 0:
            L("  近48小时暂无互动易问答")
    except Exception as _e:
        _debug_log(f"med cninfo_irm: {_e}")

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

    # 基本面数据
    if fin_metrics:
        score_data.roe = fin_metrics.get("roe", 0) or 0
        score_data.gross_margin = fin_metrics.get("gross_margin", 0) or 0

    # 净利率
    if financials and len(financials) > 0:
        _rev = _safe_float(financials[0].get("营业总收入", 0))
        _np = _safe_float(financials[0].get("净利润", 0))
        if _rev > 0:
            score_data.net_profit_margin = _np / _rev * 100

    # 资产负债率
    if bs_data and len(bs_data) > 0:
        _eq = _safe_float(bs_data[0].get("归属于母公司股东权益合计", 0))
        _ta = _safe_float(bs_data[0].get("资产总计", 1))
        if _ta > 0:
            score_data.asset_liability_ratio = 1 - (_eq / _ta)

    # 估值数据
    score_data.pe_ttm = cdata.pe_ttm
    if peer_data and peer_data.get("peers"):
        score_data.industry_pe = sum(p.get("pe", 0) for p in peer_data["peers"]) / max(
            len(peer_data["peers"]), 1
        )

    # 北向数据
    if nb and len(nb) >= 2:
        score_data.northbound_change = nb[0]["hold_shares"] - nb[-1]["hold_shares"]

    # M3 修复：复用前文【十六、十大流通股东机构动向】已拉取的股东结构，避免重复网络调用
    _st = st
    if _st:
        score_data.institution_holding_pct = _st[0].get("domestic", 0)

    # 筹码数据
    if holders and len(holders) >= 2:
        score_data.holder_change_ratio = holders[0]["change_ratio"]

    # V17.0.14: 筹码分布 CYQ(复用前文已拉取的 _cyq_dict, 避免重复网络调用)
    if _cyq_dict:
        score_data.cyq_benefit_pct = _cyq_dict.get("benefit_pct", 0.0) or 0.0
        score_data.cyq_avg_cost = _cyq_dict.get("avg_cost", 0.0) or 0.0
        score_data.cyq_concentration_90 = _cyq_dict.get("concentration_90", 0.0) or 0.0
        score_data.cyq_concentration_70 = _cyq_dict.get("concentration_70", 0.0) or 0.0

    # 计算评分
    # V16.1: 传入 strategy_config.yaml 的 scoring_med 权重（此前未传 cfg → 用硬编码默认）
    _score_cfg = _load_strategy_config() or {}
    _med_cfg = {"weights_med": (_score_cfg.get("scoring_med") or {}).get("weights_med", {})}
    result = calculate_score("med", score_data, _med_cfg)
    _ps = result.total_score
    _details = result.details

    L(f"  评分明细: {' | '.join(_details[:6])}" if _details else None)
    if _ps >= 70:
        L(f"  中线评分: {_ps:.0f}/100 → 强烈推荐，仓位40%")
    elif _ps >= 45:
        L(f"  中线评分: {_ps:.0f}/100 → 建议配置，仓位25%")
    elif _ps >= 20:
        L(f"  中线评分: {_ps:.0f}/100 → 观察仓，仓位10%")
    else:
        L(f"  中线评分: {_ps:.0f}/100 → 暂不建议，等待基本面拐点")
    L("  核心驱动: 基本面拐点 / 估值 PEG / 筹码结构 / 重大事件")

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
        _debug_log(f"med multi_school_score error: {_e}")

    L("=" * 72)

    # 累积快照数据（批量结束后统一写入）
    _SNAPSHOT_DATA[code] = {
        "name": info.get('name', ''),
        "total_score": _ps,
        "price": price_today,
        "report_source": "med",
    }

    # [ENRICH] 数据维度充实（统一层 canonical 字段，零新增取数；异常仅记录不阻断报告）
    try:
        from stock_common.enrich_helpers import (
            earnings_quality_lines, cash_content_lines, quality_gate_lines,
        )
        _enrich = []
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
        _debug_log(f"med enrich error: {_e}")

    # V17.0(2026-08-15 C 方案): 全量 md 化——渲染层确定性转换(标题/分隔线/F10 边框表/对齐空格表→md)
    from stock_common.md_render import render_md_report
    output = render_md_report(output_path, lines)
    return output


# ═══════════════════════════════════════════════════════════════
# V12.4: MedReportRunner — 统一运行框架
# ═══════════════════════════════════════════════════════════════


class MedReportRunner(BaseReportRunner):
    """A股中线深度投研报告 Runner (V12.4)"""

    def __init__(self):
        super().__init__("get_med_report", "med", "A股中线深度投研报告")

    def execute_pipeline(self) -> dict:
        # V17.0 R4: 批量骨架收敛到基类 execute_batch_pipeline(原 90 行本地实现删除)
        # V17.0 审查: 删 gen_kwargs["hsgt"]=None 误导参数——generate 内部默认拉取(有 trading_day 缓存)
        _cached_ind_comp = get_industry_comparison()

        def _prefetch(codes):
            # V17.2.24: eltdx 连板/封单/开盘抢筹批量预热(一次 TCP, 300s TTL 缓存;
            # 统一层 cdata.eltdx_* 仅读此缓存, 禁止 per-stock 触发取数打爆 TDX TCP)
            try:
                from core.eltdx_adapter import get_eltdx_shortline_bundle
                get_eltdx_shortline_bundle(list(codes))
            except Exception:
                pass

        return self.execute_batch_pipeline(
            "med", generate_report_async,
            gen_kwargs={"ind_comp": _cached_ind_comp},
            prefetch_fn=_prefetch,
            snapshot_data=_SNAPSHOT_DATA,
        )

    def upload_reports(self, drive, folder_id: str, results) -> None:
        self.upload_multi_reports(drive, folder_id, results)


if __name__ == "__main__":
    runner = MedReportRunner()
    runner.run()