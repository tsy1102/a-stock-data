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
    V9.1   2026-07-04 - F10 全覆盖：新增【异动与风险提示】章节+数据质量附录；修复资金流渲染 float/dict 兼容
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



import time, os
from typing import List

import asyncio

from datetime import date, datetime, timedelta

from gd_uploader import init_gd, upload_stock_report_by_code, cleanup_gd_proxy

# V15.3 修复: 4 个报告模块同名 _SNAPSHOT_DATA 全局变量冲突
# 抽出到 stock_common.sc_snapshot 统一管理（sc_report_runner 也用此模块）
# V15.3.1: 直接 import 共享的 SnapshotProxy 类，删除 20 行重复定义
from stock_common.sc_snapshot import SnapshotProxy as _SnapshotProxy  # noqa: E402

# 保留 _SNAPSHOT_DATA 名字以便兼容历史引用（实际写入走 sc_snapshot.register）
_SNAPSHOT_DATA = _SnapshotProxy()

from tdx_client import (tdx_get_security_bars, tdx_get_latest_bar_with_ma,
                         tdx_get_quote_full, tdx_get_index_quote,
                         tdx_get_history_fund_flow,  # V16.0: 移除 tdx_get_fund_flow（改用统一层 get_main_net_buy）
                         cleanup_tdx)



from stock_common import (clean_codes, _safe_float, UA, _debug_log,
                           _load_settings, _load_strategy_config, BaseReportRunner,
                           get_dragon_tiger_board,
                           create_async_session, get_dragon_tiger_board_async,
                           holder_change_async, get_strategic_announcements_async,
                           parse_args, get_tencent_quote, baidu_kline_full,
                           get_reports, get_dividend_history, get_industry_comparison,
                           get_concept_blocks, get_ths_hot_reason_async, get_industry_peers,
                           get_stock_sector_rank, get_stock_info, get_hsgt_macro_flow, get_hsgt_macro_flow_async,
                           get_eps_forecast_async, get_margin_trading_async,
                           get_block_trade_async, get_northbound_hold_async,
                           get_lockup_expiry_async, get_market_status,
                           calculate_multi_school_scores, ScoreData,
                           ths_hot_list, em_hot_concept, get_eastmoney_stock_news,
                           cls_telegraph, cninfo_irm,
                           get_zhb_single_stock_data, is_zhb_data_fresh,
                           get_zhb_industry_map, get_zhb_data_date,
                           get_zhb_main_net_buy, get_zhb_streak_days)  # V10.3

from data_provider import (get_stock_composite_async, get_main_net_buy_async,
                            get_stock_price_async, get_change_pct_async,
                            get_amount_wan_async, get_pe_ttm_async,
                            get_pb_async, get_dividend_yield_async,
                            get_52w_range_async, get_change_ytd_async,
                            get_turnover_pct_async)







# ═══════════════════════════════════════════
# 数据获取层
# ═══════════════════════════════════════════


def _get_index_quote(idx_code):

    """V4: 指数行情 → tdx_client 适配器（TDX指数K线，自动fallback腾讯）"""

    return tdx_get_index_quote(idx_code)



def get_fund_flow_realtime(code, ff_120d=None):
    """V7.5: 今日主力净流入 → 统一层 get_main_net_buy（ZHB→HTTP），失败则尝试历史数据回退
    
    V16.0: 改用 data_provider.get_main_net_buy（统一 ZHB→HTTP 优先级），
    替代原直连 tdx_get_fund_flow（函数名误导，实为东财 HTTP）。
    
    Args:
        code: 股票代码
        ff_120d: 可选的历史资金流数据（避免重复调用 get_fund_flow_120d）
    
    Returns:
        dict or None
    """
    try:
        from data_provider import get_main_net_buy
        mnb = get_main_net_buy(code)
        if mnb and mnb.get("main_net_buy_amount"):
            return {"data": [mnb["main_net_buy_amount"]], "detail": mnb, "source": "unified"}
    except Exception as _e:
        _debug_log(f"sht get_main_net_buy error: {_e}")
    
    # V9.3.3: 使用传入的 ff_120d 避免重复调用
    if ff_120d is None:
        ff_120d = get_fund_flow_120d(code)
    
    if ff_120d and ff_120d.get("data") and len(ff_120d["data"]) > 0:
        # V16.1: 数据"最新在前"，[:5] 取最近 5 日（原 [-5:] 取最旧）
        recent_data = ff_120d["data"][:5]
        if recent_data:
            if isinstance(recent_data[0], dict):
                avg_flow = sum(d.get("main_net", 0) for d in recent_data) / len(recent_data)
            else:
                avg_flow = sum(recent_data) / len(recent_data)
        else:
            avg_flow = 0
        if avg_flow != 0:
            return {"data": [avg_flow], "detail": {}, "source": "history_avg", "note": "使用近5日平均"}
    return None



def get_fund_flow_120d(code):
    """V7.5: 60日资金流 → TDX TCP（SKILL.md V3.2 增强：东财push2 fallback）"""
    tdx_data = tdx_get_history_fund_flow(code, 60)
    
    if tdx_data:
        return {"data": tdx_data, "error": "", "source": "tdx"}
    
    # TDX获取失败，尝试东财push2 fallback
    try:
        em_data = _get_eastmoney_fund_flow_120d(code)
        if em_data:
            return {"data": em_data, "error": "", "source": "eastmoney_push2"}
    except Exception as _e:
        _debug_log(f"get_fund_flow_120d eastmoney fallback ({code}): {_e}")
    
    return {"data": [], "error": "资金流数据获取失败"}


def _get_eastmoney_fund_flow_120d(code: str) -> List[float]:
    """获取东财push2资金流120日数据（SKILL.md V3.2 推荐）。
    
    Args:
        code: 股票代码
    
    Returns:
        list: 主力净流入数据列表（单位：万元）
    """
    from stock_common import em_get
    
    try:
        secid = f"1.{code}" if code.startswith("6") else f"0.{code}"
        url = "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
        params = {
            "secid": secid,
            "klt": 101,  # 日K线
            "fields1": "f1,f2,f3,f7",
            "fields2": "f51,f52,f53,f54,f55,f56,f57",
        }
        headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
        
        r = em_get(url, params=params, headers=headers, timeout=15)
        if r is None:
            return []
        
        d = r.json()
        klines = d.get("data", {}).get("klines", [])
        if not klines:
            return []
        
        result = []
        for line in klines[-120:]:  # 取最近120天
            parts = line.split(",")
            if len(parts) >= 6:
                main_net = float(parts[1]) / 10000  # 元转万元
                result.append(main_net)
        
        return result
    except Exception as _e:
        _debug_log(f"sht fund_flow_parse: {_e}")
        return []



# V7.5: get_dragon_tiger_board 由 stock_common 统一提供（import 已导入）























def get_baidu_kline_with_ma(code):

    """V4: K线+MA → tdx_client 适配器（TDX日K线+本地MA5/10/20计算）"""

    return tdx_get_latest_bar_with_ma(code)










# ═══════════════════════════════════════════

# 报告生成

# ═══════════════════════════════════════════



async def generate_report_async(session, code, output_path, ind_comp=None, idx_q=None, hsgt=None, depth="deep"):

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
            "desc": "快速模式"
        },
        "medium": {
            "skip_fund_flow_120d": True,
            "skip_lhb_detail": False,
            "skip_holder_history": True,
            "skip_margin_detail": False,
            "skip_block_trade_detail": True,
            "skip_announcement_detail": False,
            "skip_industry_peers": False,
            "desc": "标准模式"
        },
        "deep": {
            "skip_fund_flow_120d": False,
            "skip_lhb_detail": False,
            "skip_holder_history": False,
            "skip_margin_detail": False,
            "skip_block_trade_detail": False,
            "skip_announcement_detail": False,
            "skip_industry_peers": False,
            "desc": "深度模式"
        }
    }
    _dc = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["deep"])

    today_str = date.today().strftime("%Y-%m-%d")

    lines = []

    def L(s=""): lines.append(s)

    L("="*72); L(f"  {code} 个股深度数据报告 [{_dc['desc']}] — {today_str} {datetime.now().strftime('%H:%M:%S')}"); L("="*72); L("")

    _30d_str = (datetime.now()-timedelta(days=30)).strftime("%Y-%m-%d")

    _60d_str = (datetime.now()-timedelta(days=60)).strftime("%Y-%m-%d")

    _90d_str = (datetime.now()-timedelta(days=90)).strftime("%Y-%m-%d")

    _sc = _load_strategy_config()

    _mkt = _sc.get("market", {})

    _trd = _sc.get("trader", {})

    _hld = _sc.get("holder", {})

    _lo_strong = _mkt.get("limit_order_strong", 5.0)

    _lo_mid   = _mkt.get("limit_order_mid", 2.0)

    _recent_days = _trd.get("recent_days", 90)

    _unlock_warn = _hld.get("unlock_warn_days", 90)

    _unlock_ratio_warn = _hld.get("unlock_ratio_warn", 5.0)

    _limit_chg = _mkt.get("limit_chg_pct", 9.5)

    _near_limit = _mkt.get("near_limit_pct", 7.0)

    _seal_ratio_warn = _mkt.get("seal_amount_ratio_warn", 0.1)

    _mkt_status, _mkt_note = get_market_status()

    if _mkt_status == "closed":
        L("  ⚠️ 休市日：数据为最近交易日快照，短线技术指标已标注")
    elif _mkt_status == "lunch":
        L("  ⚠️ 午休时段（11:30-13:00）：行情暂停，技术指标基于盘中快照")
    elif _mkt_status in ("post_market", "pre_market"):
        L("  ⚠️ 非交易时段：数据为最近交易日快照，短线技术指标已标注")
    elif _mkt_status == "post_close":
        L("  ℹ️ 盘后收盘：数据为今日收盘快照，短线技术指标基于收盘价")
    L("\n"+"─"*72); L("【一、个股基本信息】"); L("─"*36)

    # V15 统一数据中心：通过 get_canonical_stock_data 获取强类型标准化数据
    # V15.2 修正: async 上下文必须包 to_thread，否则阻塞主事件循环（val 死锁根因）
    from data_provider import get_canonical_stock_data
    cdata = await asyncio.to_thread(get_canonical_stock_data, code)
    price_today = cdata.price
    q = cdata.to_dict()

    # V15.4.2: get_stock_info 内部调腾讯，包 to_thread
    info = await asyncio.to_thread(get_stock_info, code)
    stock_name = cdata.name or info.get('name', 'N/A')
    stock_industry = cdata.industry or info.get('industry', 'N/A')

    L(f"  股票名称: {stock_name}")
    L(f"  股票代码: {cdata.code}")
    L(f"  所属板块: {stock_industry}")
    L(f"  总股本:   {cdata.total_shares_wan/1e4:.2f}亿股")
    L(f"  流通股本: {cdata.float_shares_wan/1e4:.2f}亿股")

    ld = info.get("list_date", "")
    if ld and len(ld) >= 8: ldf = f"{ld[:4]}-{ld[4:6]}-{ld[6:8]}"
    else: ldf = ld
    L(f"  上市日期: {ldf}")

    if cdata.change_5d or cdata.change_10d or cdata.change_20d:
        L(f"\n  [阶段涨幅] 近5日: {cdata.change_5d:+.2f}% | 近10日: {cdata.change_10d:+.2f}% | 近20日: {cdata.change_20d:+.2f}%")


    L("\n"+"─"*72); L("【二、实时行情、估值与短线趋势】"); L("─"*36)

    # 52周高低位（cdata 统一提供）
    if cdata.high_52w > 0 and cdata.low_52w > 0 and cdata.price > 0:
        _52w_pos = (cdata.price - cdata.low_52w) / (cdata.high_52w - cdata.low_52w) * 100 if cdata.high_52w != cdata.low_52w else 50
        L(f"  [52周区间] 最高: {cdata.high_52w:.2f}元 | 最低: {cdata.low_52w:.2f}元 | 当前位置: {_52w_pos:.0f}%")

    if cdata.price > 0 or cdata.change_pct != 0:
        if cdata.time_anchor == "t-1":
            L("  ⚠️ 盘前/休市模式，以下行情数据基于上一交易日收盘数据")
        
        L(f"  当前价:   {cdata.price:.2f}元")
        L(f"  涨跌幅:   {cdata.change_pct:.2f}%")
        L(f"  今开:     {cdata.open:.2f}元  昨收: {cdata.prev_close:.2f}元")
        L(f"  最高:     {cdata.high:.2f}元  最低: {cdata.low:.2f}元")
        L(f"  成交额:   {cdata.amount_wan/10000:.2f}亿元  换手率: {cdata.turnover_pct:.2f}%")
        L(f"  总市值:   {cdata.mcap_yi:.2f}亿元  流通市值: {cdata.float_mcap_yi:.2f}亿元")
        _pe_str = f"{cdata.pe_ttm:.2f}" if cdata.pe_ttm > 0 else "N/A（亏损）"
        L(f"  PE(TTM):  {_pe_str}  PE(动): {cdata.pe_dynamic:.2f}  PB: {cdata.pb:.2f}")
    else:
        L("  行情数据获取失败")


    ma_data = await asyncio.to_thread(get_baidu_kline_with_ma, code)

    if ma_data and 'ma5avgprice' in ma_data:

        ma5 = _safe_float(ma_data.get('ma5avgprice',0)); ma10 = _safe_float(ma_data.get('ma10avgprice',0))

        L(f"\n  [技术支撑] MA5={ma5:.2f}元 | MA10={ma10:.2f}元")

        if price_today>0 and ma5>0:

            bias = (price_today-ma5)/ma5*100

            L(f"  [短线趋势] 当前价相对 MA5 乖离率: {bias:+.2f}% ({'站上 MA5, 趋势偏强' if price_today>=ma5 else '跌破 MA5, 短线走弱'})")

    L("")

    all_idx = [("sh000001","上证指数"),("sz399106","深证综指"),("sz399102","创业综指"),("sh000688","科创综指")]

    if code.startswith("688"): bi = "sh000688"

    elif code.startswith(("300","301")): bi = "sz399102"

    elif code.startswith("6"): bi = "sh000001"

    elif code.startswith(("0")): bi = "sz399106"

    else: bi = ""

    if idx_q is None:

        idx_q = {}

        # V15.4.2: 4 个指数并行获取，避免早盘前 TDX 限流时串行 60s × 4 卡死
        async def _idx_async(idx_code: str) -> tuple:
            _q = await asyncio.to_thread(_get_index_quote, idx_code)
            return idx_code, _q

        _idx_results = await asyncio.gather(*[_idx_async(ic) for ic, _ in all_idx], return_exceptions=True)
        for _r in _idx_results:
            if isinstance(_r, Exception):
                continue
            _ic, _iq = _r
            if _iq:
                idx_q[_ic] = _iq

    for ic,inm in all_idx:

        _iq_val = idx_q.get(ic, {})

        if _iq_val:

            L(f"  [{inm}] 开盘 {_iq_val.get('open',0):.2f} | 当前 {_iq_val.get('price',0):.2f} | 涨跌幅 {_iq_val.get('change_pct',0):+.2f}%{' ← 本股' if ic==bi else ''}")

    miq = idx_q.get("sh000001",{}); biq = idx_q.get(bi,{}) if bi else {}

    if hsgt is None:

        hsgt = await get_hsgt_macro_flow_async(session)

    if hsgt:

        _sig = "偏多" if hsgt["total"] > 0 else "偏空"

        L(f"  💰 今日北向资金: 沪股通 {hsgt['hgt']:+.2f}亿 | 深股通 {hsgt['sgt']:+.2f}亿 | 合计 {hsgt['total']:+.2f}亿（{_sig}）")

    # V15.4.2: 资金流同步调用包 to_thread，避免阻塞事件循环
    ff = await asyncio.to_thread(get_fund_flow_120d, code)
    rf = await asyncio.to_thread(get_fund_flow_realtime, code, ff_120d=ff)  # V9.3.3: 复用 ff_120d 避免重复调用

    if rf and rf.get("data") and len(rf["data"]) > 0:
        _fd = rf["data"]
        L(f"  💰 今日主力净流入: {_fd[0]:.0f}万元 ({_fd[0]/1e4:.2f}亿)")
    else:
        if ff and len(ff) > 0:
            last_day_flow = ff.iloc[0].get('net_main', 0) if hasattr(ff, 'iloc') else 0
            if last_day_flow != 0:
                L(f"  💰 昨日主力净流入: {last_day_flow:.0f}万元 ({last_day_flow/1e4:.2f}亿)")
            else:
                L("\n  [资金流向] 今日主力净流入(实时): 暂无数据")
        else:
            L("\n  [资金流向] 今日主力净流入(实时): 暂无数据")

    L("\n"+"─"*72); L("【三、机构一致预期与估值】"); L("─"*36)

    df_eps = await get_eps_forecast_async(session, code)

    if not df_eps.empty and len(df_eps.columns)>=2:

        _this_year = str(date.today().year)

        eps_cur = None; eps_next = None

        eps_min = None; eps_max = None; eps_ind = None; _n_analysts = 0

        for _ri in range(min(len(df_eps),5)):

            _row_label = str(df_eps.iloc[_ri,0])

            if _this_year in _row_label or f"{_this_year}预测" in _row_label or f"{_this_year}E" in _row_label:

                eps_cur = _safe_float(df_eps.iloc[_ri,3])

                eps_min = _safe_float(df_eps.iloc[_ri,2])

                eps_max = _safe_float(df_eps.iloc[_ri,4])

                eps_ind = _safe_float(df_eps.iloc[_ri,5])

                _n_analysts = int(_safe_float(df_eps.iloc[_ri,1]))

            elif str(date.today().year+1) in _row_label:

                eps_next = _safe_float(df_eps.iloc[_ri,3])

        if not eps_cur:

            eps_cur = _safe_float(df_eps.iloc[0,3]) if len(df_eps)>0 else None

            eps_next = _safe_float(df_eps.iloc[1,3]) if len(df_eps)>1 else None

        if eps_cur and eps_cur>0:

            pe_fwd = price_today/eps_cur

            L(f"  {_n_analysts} 家机构覆盖" if _n_analysts else "  有机构覆盖")

            _range_str = f"，区间 {eps_min:.2f}~{eps_max:.2f}" if eps_min and eps_max else ""

            _ind_str = f"，行业中值 {eps_ind:.2f}" if eps_ind and eps_ind > 0 else ""

            L(f"  {_this_year}E EPS 均值: {eps_cur:.2f} 元{_range_str}{_ind_str}")

            if eps_next and eps_next > 0:

                L(f"  {int(_this_year)+1}E EPS 均值: {eps_next:.2f} 元")

                cagr = (eps_next / eps_cur - 1) * 100

                L(f"  预期增速: {cagr:+.1f}% | PEG: {pe_fwd/cagr:.2f}" if cagr > 0 else f"  预期增速: {cagr:+.1f}%")

            L(f"  前向PE ({_this_year}E): {pe_fwd:.2f}x")

        else: L("  (当前亏损或无数据，前向PE无意义)")

    else: L("  无机构覆盖数据")

    lu = q.get("limit_up",0) if q else 0; b1v = q.get("bid1_vol",0) if q else 0; np2 = q.get("price",0) if q else 0

    is_lu = lu>0 and abs(np2-lu)/lu<0.005

    if is_lu and b1v>0:

        fa = b1v*lu/1e8; fr = fa/(q.get("mcap_yi",0) or 1)*100

        if fa>=0.1 or fr>0.5:

            t = f"  封单资金 {fa:.2f}亿元，占流通市值 {fr:.1f}%"

            if fr>5: t += "\n  🔥 封单实力强劲，次日大概率高开"

            elif fr>2: t += "\n  ✅ 封单质量良好"

            else: t += "\n  ⚠️ 封单偏弱"

            L(t)

    L("\n"+"─"*72); L("【四、个股研报（东财）】"); L("─"*36)

    # V15.4.2: 同步研报拉取包 to_thread
    reports = await asyncio.to_thread(get_reports, code, 5)

    rr = [r for r in reports if str(r.get("publishDate",""))[:10]>=_60d_str]

    if rr:

        L(f"  最近60天共 {len(rr)} 篇研报，显示前10篇:")

        L(f"  {'日期':<12} {'机构':<16} {'评级':<10} {'标题'}"); L(f"  {'-'*70}")

        for r in rr[:10]:

            L(f"  {str(r.get('publishDate',''))[:10]:<12} {r.get('orgSName',''):<16} {str(r.get('emRatingName','')):<10} {r.get('title','')[:50]}")

    elif reports: L(f"  近60天内无新研报（共 {len(reports)} 篇历史研报，已省略）")

    else: L("  无研报数据（该股可能无机构覆盖）")

    L("\n"+"─"*72); L("【五、概念板块、热点归因与板块共振】"); L("─"*36)

    # V15.4.2: 同步概念+行业对比包 to_thread
    blocks = await asyncio.to_thread(get_concept_blocks, code)

    if blocks["industry"]: L(f"  所属板块: {', '.join(b['name'] for b in blocks['industry'])}")

    if ind_comp is None:

        ind_comp = await asyncio.to_thread(get_industry_comparison)

    stock_ind = info.get('industry','')

    if blocks and blocks.get("industry"):

        stock_ind = blocks["industry"][0].get("name", stock_ind)

    industry_rank=0; industry_change_pct=0; industry_match_name=""

    if stock_ind and ind_comp.get("all"):

        rank_str = "未进入前100"; is_top=False

        _ind_clean = stock_ind.replace("行业","").replace("服务","").replace("Ⅱ","").replace("Ⅲ","")

        for row in ind_comp["all"]:

            _row_clean = row["name"].replace("行业","").replace("服务","").replace("Ⅱ","").replace("Ⅲ","")

            if stock_ind in row["name"] or row["name"] in stock_ind or _ind_clean in _row_clean or _row_clean in _ind_clean:

                industry_rank=row['rank']; industry_change_pct=row['change_pct']; industry_match_name=row['name']

                rank_str = f"第 {industry_rank} 名 (板块当日涨跌幅 {industry_change_pct}%)"

                if industry_rank<=10: is_top=True

                break

        L(f"  ➤ [板块共振监测] 该板块今日全市场排名: {rank_str}")

        if is_top: L("     🔥 提醒: 所在板块处于全市场 TOP10，具备较强板块共振溢价效应！")

    # V16.1: time.sleep 阻塞事件循环 → await asyncio.sleep
    await asyncio.sleep(0.5)

    # V16.1: lite 模式跳过同业对比（省一次 TDX 板块成员查询）
    if _dc.get("skip_industry_peers"):
        peer_data = {"my_rank": 0, "industry_count": 0, "industry": stock_ind}
    else:
        # V15.4.2: 同步同业对比包 to_thread (TDX 限流时易卡)
        peer_data = await asyncio.to_thread(get_industry_peers, code, 3, info=info)

    if peer_data.get("my_rank",0)>0 and peer_data.get("industry_count",0)>0:

        L(f"  ➤ [市值排名] {peer_data.get('industry',stock_ind)}: 该股排名第 {peer_data['my_rank']}/{peer_data['industry_count']} 位 (按总市值)")

    _has_peer = peer_data.get("my_rank",0)>0 and peer_data.get("industry_count",0)>0

    if (industry_rank>0 and industry_match_name) or _has_peer:

        _rank_parts = []

        if industry_rank>0 and industry_match_name:

            _up = 0; _down = 0

            _all_members = peer_data.get('all_members', [])

            if _all_members:

                _up = sum(1 for m in _all_members if m.get('change_pct', 0) > 0)

                _down = sum(1 for m in _all_members if m.get('change_pct', 0) < 0)

            _rank_parts.append(f"[板块涨跌排名] 上涨 {int(_up)} 家 / 下跌 {int(_down)} 家")

        try:

            # V16.1: 同步阻塞包 to_thread
            _sr = await asyncio.to_thread(get_stock_sector_rank, code, info=info, q=q)

            if _sr: _rank_parts.append(f"本股今日{_sr['change_pct']:+.2f}%，板块内排名第{_sr['rank']}/{_sr['total']}名")

        except Exception as _e:
            _debug_log(f"sector_rank error: {_e}")

        if _rank_parts: L(f"     {'  '.join(_rank_parts)}")

    # 股息率：zhb优先，无zhb时fallback到get_dividend_history
    _zhb_div_yield = cdata.dividend_yield if cdata and cdata.dividend_yield else 0
    if _zhb_div_yield and _zhb_div_yield > 0:
        L(f"  股息率: {_zhb_div_yield:.2f}%")
    else:
        div = await asyncio.to_thread(get_dividend_history, code)
        if div:
            ld2 = div[0]; ye = f"{(ld2['bonus_rmb']/price_today)*100:.2f}%" if price_today>0 else "N/A"
            L(f"  最近分红: {ld2['date']} 每股{ld2['bonus_rmb']:.4f}元 (约{ye}股息率)")

    if blocks["concept"]:

        L(f"\n  概念板块: {', '.join(b['name'] for b in blocks['concept'])}")

    L("\n  ➤ 同花顺热点题材归因 (基于当日强势股/涨停榜):")

    # 优化同花顺热点题材时段显示逻辑
    if _mkt_status in ("pre_market", "morning", "lunch"):
        L("  ⚠️ 同花顺热点池需16:00后更新，当前为盘中时段数据可能为空")
    elif _mkt_status == "afternoon":
        L("  ⚠️ 当前为下午盘，同花顺热点池更新中，数据可能为空或不完整")
    else:
        L("  ⚠️ 同花顺热点池数据为更新周期内的汇总信息")

    ths_hot = await get_ths_hot_reason_async(session, code, today_str)

    if ths_hot: L(f"  [强势归因] {ths_hot.get('reason','')}")

    else: L("  (该股今日未进入同花顺强势股列表，暂无热点题材归因数据)")

    L("\n"+"─"*72); L("【六、同业龙头横向对比】"); L("─"*36)

    if peer_data["peers"]:

        if "note" in peer_data["peers"][0]: L(f"  ⚠️ {peer_data['peers'][0]['note']}")

        else:

            _my_mcap_show = peer_data['my_mcap'] if peer_data['my_mcap'] > 0 else q.get('mcap_yi', 0)

            L(f"  所属板块: {peer_data['industry']}"); L(f"  本股市值: {_my_mcap_show:.1f}亿元")

            L("  同业龙头对比:"); L(f"  {'代码':<8} {'名称':<12} {'股价':>8} {'涨跌幅%':>8} {'市值(亿)':>10} {'PE':>8} {'换手率%':>8}"); L(f"  {'-'*70}")

            _my_mcap = peer_data['my_mcap'] if peer_data['my_mcap'] > 0 else q.get('mcap_yi', 0)

            L(f"  {code:<8} {info.get('name','N/A'):<12} {price_today:>8.2f} {q.get('change_pct',0):>7.2f}% {_my_mcap:>9.1f} {q.get('pe_ttm',0):>7.1f} {q.get('turnover_pct',0):>7.2f}% ← 本股")

            for p in peer_data["peers"]: L(f"  {p['code']:<8} {p['name']:<12} {p['price']:>8.2f} {p['change_pct']:>7.2f}% {p['mcap_yi']:>9.1f} {p['pe']:>7.1f} {p['turnover']:>7.2f}%")

    else: L(f"  无法获取同业数据（板块: {peer_data.get('industry','未知')}）")

    L("\n"+"─"*72); L("【七、资金走向分析】"); L("─"*36)

    # V15.2 修复: 改名 _composite → q (cdata.to_dict() 的标准变量名)
    # 同时把 cdata 的字段名转换为 zhb_main_net dict 格式（向后兼容下游 print 逻辑）
    zhb_main_net = None
    if q and (q.get("main_net_buy_wan") or q.get("main_net_buy_hands")):
        zhb_main_net = {
            "main_net_buy_hands": q.get("main_net_buy_hands", 0),
            "main_net_buy_hands_1d": 0,
            "main_net_buy_hands_2d": 0,
            "main_net_buy_amount": q.get("main_net_buy_wan", 0),
            "main_net_buy_amount_1d": q.get("main_net_buy_wan_1d", 0),
            "main_net_buy_amount_2d": 0,
        }
    if not zhb_main_net:
        try:
            zhb_main_net = await get_main_net_buy_async(code, session)
        except Exception as _e:
            _debug_log(f"get_main_net_buy_async error ({code}): {_e}")
    if zhb_main_net:
        zhb_date = get_zhb_data_date()
        L(f"\n  ➤ ZHB主力资金流向 ({zhb_date}):")
        L(f"    T日主力净买入量: {zhb_main_net['main_net_buy_hands']:.0f}手")
        L(f"    T日主力净流入额: {zhb_main_net['main_net_buy_amount']:+.0f}万元")
        if zhb_main_net['main_net_buy_amount_1d']:
            L(f"    T-1日主力净流入额: {zhb_main_net['main_net_buy_amount_1d']:+.0f}万元")
        flow_ratio = abs(zhb_main_net['main_net_buy_amount']) / q.get('amount_wan', 0) * 100 if q.get('amount_wan', 0) else 0
        L(f"    主力资金占比: {flow_ratio:.2f}%")
        L(f"    信号: {'🟢 主力资金净流入' if zhb_main_net['main_net_buy_amount'] > 0 else '🔴 主力资金净流出'}")

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
            L(f"\n  ➤ 连涨天数: {streak}天 {'🔥 情绪过热预警' if streak >= 5 else ''}")
        elif streak < 0:
            L(f"\n  ➤ 连跌天数: {abs(streak)}天 {'🧊 超卖信号' if abs(streak) >= 5 else ''}")

    if ff["data"]:

        # V16.1 修复: get_em_history_fund_flow 返回"最新在前"（sort reverse=True），
        # 原 [-10:] 取到最旧 10 条 → 改 [:10] 取最新 10 条；显示按时间正序（reversed）
        # V16.1: lite 模式跳过资金流历史明细（_dc["skip_fund_flow_120d"]）
        if _dc.get("skip_fund_flow_120d"):
            L("\n  ➤ 资金流监控: (lite 模式跳过历史明细，仅显示当日)")
            if isinstance(ff["data"][0], dict):
                L(f"    主力净流入(最新): {ff['data'][0].get('main_net', 0)/1e4:+.0f}万元")
            else:
                L(f"    主力净流入(最新): {ff['data'][0]:+.0f}万元")
        else:
            L("\n  ➤ 60日资金流监控 (最近 10 日):")

            _recent = ff["data"][:10]

            # 兼容 float 列表（东财回退，单位万元）和 dict 列表（TDX，单位元）两种格式
            _is_dict = bool(_recent) and isinstance(_recent[0], dict)

            if _is_dict:
                L(f"  {'日期':<12} {'主力净流入(万)':>12} {'超大单(万)':>10} {'大单(万)':>10} {'中单(万)':>10} {'小单(万)':>10}")
                L(f"  {'-'*70}")
                for d in reversed(_recent):
                    L(f"  {d['date']:<12} {d['main_net']/1e4:>+12.0f} {d['super_net']/1e4:>+10.0f} {d['large_net']/1e4:>+10.0f} {d['mid_net']/1e4:>+10.0f} {d['small_net']/1e4:>+10.0f}")
            else:
                L(f"  {'主力净流入(万)':>12}")
                L(f"  {'-'*30}")
                for d in reversed(_recent):
                    L(f"  {d:>+12.0f}")

            r20 = ff["data"][:20]
            if _is_dict:
                tmain = sum(d["main_net"] for d in r20); tdays = sum(1 for d in r20 if d["main_net"]>0)
                L(f"\n  近20日统计:\n    主力累计净流入: {tmain/1e4:.0f}万元\n    主力净流入天数: {tdays}/20天")
            else:
                tmain = sum(r20); tdays = sum(1 for d in r20 if d>0)
                L(f"\n  近20日统计:\n    主力累计净流入: {tmain:.0f}万元\n    主力净流入天数: {tdays}/20天")

            L(f"  信号: {'主力资金近期净流入 → 偏多' if tmain>0 else '主力资金近期净流出 → 偏空'}")

    else: L("  (资金流数据获取失败)")

    L("\n"+"─"*72); L("【八、北向资金持仓动态】"); L("─"*36)

    nb = await get_northbound_hold_async(session, code, 20)

    if nb:

        L(f"  近 {len(nb)} 个交易日北向持仓数据:")

        L(f"  {'日期':<12} {'持股数量(万)':>12} {'持股市值(万)':>12} {'持股占比%':>10} {'变动股数(万)':>12}"); L(f"  {'-'*65}")

        for d in nb:

            _mcap = d.get('market_cap',0) or 0

            _ratio = d.get('hold_ratio',0) or 0

            _shares = d.get('hold_shares',0) or 0

            if _mcap == 0 and _shares > 0 and price_today > 0:

                _mcap = _shares * price_today

                _ratio = _shares / info.get('total_shares',1) if info.get('total_shares',0) > 0 else 0

            L(f"  {d['date']:<12} {_shares/1e4:>12.0f} {_mcap/1e4:>12.0f} {_ratio:>9.4f}% {d['change_shares']/1e4:>+12.0f}")

    else: L("  该股暂无北向资金持仓数据（可能非陆股通标的或数据延迟）")

    L("\n"+"─"*72); L("【九、龙虎榜席位】"); L("─"*36)

    # 优化时段显示：根据不同市场状态提供更精准的提示
    current_time = datetime.now()
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
    dtb = await get_dragon_tiger_board_async(session, code, days=180,
                                             include_seats=not _dc.get("skip_lhb_detail", False),
                                             enhance_seats=not _dc.get("skip_lhb_detail", False))

    if dtb["records"]:

        L(f"  近{_recent_days}日上榜 {len(dtb['records'])} 次:"); L(f"  {'日期':<12} {'上榜原因':<50} {'净买入(万)':>9} {'换手率':>6}"); L(f"  {'-'*85}")

        for r in dtb["records"]: L(f"  {r['date']:<12} {r.get('reason','')[:48]:<50} {r['net_buy']:>12.1f} {r['turnover']:>7.2f}%")

        _cfg = _load_settings()

        _trader_tags = [(k, v) for k, v in _cfg.get("trader_tags", {}).items()]

        def _tag(name):

            for kw, t in _trader_tags:

                if kw in name: return t

            return ""

        seats = dtb["seats"]

        if seats["buy"]:

            L("\n  最近买入席位 TOP5:"); L(f"  {'营业部名称':<30} {'买入(万)':>9} {'卖出(万)':>9} {'净额(万)':>9}"); L(f"  {'-'*70}")

            for s in seats["buy"]: L(f"  {_tag(s['name'])} {s['name']:<28} {s['buy_amt']:>12.1f} {s['sell_amt']:>12.1f} {s['net']:>12.1f}")

        if seats["sell"]:

            L("\n  最近卖出席位 TOP5:"); L(f"  {'营业部名称':<30} {'买入(万)':>9} {'卖出(万)':>9} {'净额(万)':>9}"); L(f"  {'-'*70}")

            for s in seats["sell"]: L(f"  {_tag(s['name'])} {s['name']:<28} {s['buy_amt']:>12.1f} {s['sell_amt']:>12.1f} {s['net']:>12.1f}")

        inst = dtb["institution"]

        if inst and (inst.get("buy_amt",0)>0 or inst.get("sell_amt",0)>0):

            L(f"\n  机构买卖统计:\n    机构买入金额: {inst['buy_amt']}万元\n    机构卖出金额: {inst['sell_amt']}万元\n    机构净买入: {inst['net_amt']}万元")

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

        _lhasa_count = sum(1 for _s in seats.get("buy", []) if "东方财富证券拉萨" in str(_s.get("name", "")))

        _lhasa_sell = sum(1 for _s in seats.get("sell", []) if "东方财富证券拉萨" in str(_s.get("name", "")))

        L("  ── 游资活跃度诊断 ──")

        if _all_depts:

            _buy_tags = [x[0] for x in _all_depts if x[2] == "buy"]

            _sell_tags = [x[0] for x in _all_depts if x[2] == "sell"]

            _unique_buy = list(dict.fromkeys(_buy_tags))

            _unique_sell = list(dict.fromkeys(_sell_tags))

            if _unique_buy:

                L(f"  🟢 著名游资买入: {'、'.join(_unique_buy)}")

            if _unique_sell:

                L(f"  🔴 著名游资卖出: {'、'.join(_unique_sell)}")

            L("  📊 席位明细:")

            for _tg, _nm, _sd, _nt in _all_depts[:5]:

                _sd_txt = "买" if _sd == "buy" else "卖"

                L(f"     {_sd_txt}五 {_tg} {_nm[:20]} 净{_nt:+.1f}万")

        else:

            L("  ℹ️  无著名游资/机构专用席位上榜")

        if _lhasa_count + _lhasa_sell > 0:

            L(f"  ⚠️  拉萨散户席位: 买{_lhasa_count}家 / 卖{_lhasa_sell}家（散户聚集，注意追高风险）")

        _inst_net = inst.get("net_amt", 0) if inst else 0

        if _all_depts and _inst_net > 0:

            L("  ✅ 综合判断: 机构资金+游资同步关注，资金面积极")

        elif _inst_net > 0:

            L("  ✅ 综合判断: 机构净买入，机构资金关注")

        elif _all_depts and _inst_net < -1000:

            L("  ⚠️ 综合判断: 机构大额卖出 + 游资炒作，需谨慎")

        elif _lhasa_count + _lhasa_sell > 3:

            L("  ⚠️ 综合判断: 散户席位占主导，短期波动较大")
        
        # V8.5新增：席位增强分析
        if dtb.get("seat_analysis"):
            sa = dtb["seat_analysis"]
            L("\n  ── 席位增强分析 ──")
            if sa.get("seat_quality_score"):
                L(f"  席位质量评分: {sa['seat_quality_score']}分")
            if sa.get("premium_signal"):
                _signal_map = {
                    "buy_high": "✅ 强势买入信号，游资抢筹意愿强烈，短线关注",
                    "sell_high": "⚠️ 强势卖出信号，游资集中出货，注意回调风险",
                    "sell_caution": "⚠️ 卖出警示，卖方力量占优，建议观望",
                    "neutral": "➖ 中性评级，价格已透支，此时追涨性价比低",
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
                _notable = sa.get('notable_seats', [])
                if _notable:
                    L(f"  知名席位: {'、'.join(_notable)}")

    else: L(f"  近{_recent_days}日无龙虎榜记录（白马蓝筹或近期未触发异动标准的个股，无龙虎榜属正常现象）")

    L("\n"+"─"*72); L("【十、限售解禁日历】"); L("─"*36)

    lockup = await get_lockup_expiry_async(session, code, days=90, include_history=True)

    rh = [h for h in lockup["history"] if _30d_str <= h["date"] <= today_str]

    if rh:

        L(f"  近30天解禁 {len(rh)} 批:"); L(f"  {'日期':<12} {'类型':<30} {'数量':>10} {'占比%':>6}"); L(f"  {'-'*65}")

        for h in rh: L(f"  {h['date']:<12} {str(h['type'])[:30]:<30} {h['shares']/1e4 if h['shares'] else 0:>12.0f}万 {h['ratio']:>7.2f}% {'🔴' if h['ratio']>_unlock_ratio_warn else ('🟡' if h['ratio']>1 else '🟢')}{'高' if h['ratio']>_unlock_ratio_warn else ('中' if h['ratio']>1 else '低')}")

    elif lockup["history"]: L(f"  近30天内无解禁（共 {len(lockup['history'])} 批历史记录，已省略）")

    else: L("  无历史解禁记录")

    if lockup["upcoming"]:

        L(f"\n  未来{_unlock_warn}天待解禁 {len(lockup['upcoming'])} 批: ⚠️")

        for h in lockup["upcoming"]: L(f"    {h['date']}: {str(h['type'])} 数量={h['shares']/1e4 if h['shares'] else 0:.0f}万 占比={h['ratio']:.2f}% 压力:{'🔴高' if h['ratio']>_unlock_ratio_warn else ('🟡中' if h['ratio']>1 else '🟢低')}")

    else: L(f"\n  未来{_unlock_warn}天无待解禁")

    L("\n"+"─"*72); L("【十一、融资融券（两融数据）】"); L("─"*36)

    if _dc.get("skip_margin_detail"):
        L("  [lite模式] 跳过详细数据")
        margin = []
    else:
        margin = await get_margin_trading_async(session, code)

    if margin:

        L(f"  最近 {len(margin)} 个交易日数据:"); L(f"  {'日期':<12} {'融资余额(万)':>10} {'融资买入(万)':>10} {'融资偿还(万)':>10} {'融券余额(万)':>10}"); L(f"  {'-'*70}")

        for d in margin[:10]: L(f"  {d['date']:<12} {d['rzye']/1e4:>14.0f} {d['rzmre']/1e4:>14.0f} {d['rzche']/1e4:>14.0f} {d['rqye']/1e4:>14.0f}")

        _amt = q.get("amount_wan",0)*1e4 if q else 0

        if _amt>0 and margin[0]["rzmre"]>0:

            _rz_ratio = margin[0]["rzmre"]/_amt*100

            if _rz_ratio>20:

                L(f"  🔥 融资买入占当日成交额 {_rz_ratio:.1f}%（>{20}%），杠杆资金疯狂涌入！")

        if len(margin)>=3:

            _rq_up = sum(1 for i in range(3) if i+1<len(margin) and margin[i]["rqye"]>margin[i+1]["rqye"])

            if _rq_up>=2:

                L("  ⚠️ 融券余额连续上升，做空筹码在暗中积累，警惕高位融券砸盘")

    else: L("  该股无融资融券数据（可能不是两融标的）")

    L("\n"+"─"*72); L("【十二、大宗交易】"); L("─"*36)

    if _dc.get("skip_block_trade_detail"):
        L("  [lite模式] 跳过详细数据")
        bt = []; rbt = []
    else:
        bt = await get_block_trade_async(session, code); rbt = [d for d in bt if d["date"]>=_30d_str]

    if rbt:

        L(f"  近30天共 {len(rbt)} 笔大宗交易:"); L(f"  {'日期':<12} {'成交价':>6} {'收盘价':>6} {'溢价%':>6} {'成交量':>10} {'买方':<24} {'卖方'}"); L(f"  {'-'*95}")

        for d in rbt: L(f"  {d['date']:<12} {d['price']:>8.2f} {d['close']:>8.2f} {d['premium_pct']:>7.2f}% {d['vol']/1e4 if d['vol'] else 0:>10.0f}万 {d['buyer']:<24} {d['seller']}")

    elif bt: L(f"  近30天内无大宗交易（共 {len(bt)} 笔历史记录，已省略）")

    else: L("  无大宗交易记录")

    L("\n"+"─"*72); L("【十三、股东户数变化】"); L("─"*36)

    if _dc.get("skip_holder_history"):
        L("  [lite/medium模式] 跳过详细历史")
        holders = []
    else:
        holders = await holder_change_async(session, code)

    if holders:

        ld3 = holders[0]["date"]

        if ld3<_90d_str:

            do = (datetime.now()-datetime.strptime(ld3,"%Y-%m-%d")).days

            L(f"  ⚠️ 数据距今已 {do} 天，尚未更新至最新报告期")

        L(f"  {'截止日期':<14} {'股东户数':>7} {'环比变化':>10} {'环比%':>8}"); L(f"  {'-'*50}")

        for h in holders[:5]:
            _cr = h.get('change_ratio', 0)
            # 边界检查：变化率超过±500%视为异常数据，不显示
            _cr_disp = _cr if abs(_cr) <= 500 else (999.99 if _cr > 500 else -999.99)
            _cr_flag = " ⚠️" if abs(_cr) > 500 else ""
            L(f"  {h['date']:<14} {h['holder_num']:>10,} {h['change_num']:>+14,} {_cr_disp:>+9.2f}%{_cr_flag}")

        if len(holders)>=2:

            lh = holders[0]; ph = holders[1]

            if lh["change_ratio"]<0 and ph["change_ratio"]<0: sig = "连续减少 = 筹码持续集中，主力吸筹信号"

            elif lh["change_ratio"]<0: sig = "筹码趋于集中"

            else: sig = "筹码松动/散户化"

            L(f"\n  ➤ 信号: {sig}")

    else: L("  股东户数数据获取失败")

    L("\n"+"─"*72); L("【十四、短线情绪与事件催化】"); L("─"*36)

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
        _cutoff = datetime.now() - timedelta(minutes=420)
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
            if title:
                L(f"    · [{t_str[:16]}] {title[:80]}")
                _cls_shown += 1
                if _cls_shown >= 10:
                    break
        if _cls_shown == 0:
            L("    近7小时暂无财联社快讯")
    except Exception as _e:
        _debug_log(f"sht cls_telegraph: {_e}")

    # 同花顺热榜 — V16.1: 同步包 to_thread
    try:
        hot_all = await asyncio.to_thread(ths_hot_list, "hour")
        in_hot = next((h for h in hot_all if h.get("code") == code), None)
        if in_hot:
            L(f"    🔥 同花顺热榜 #{in_hot['rank']} 热度{in_hot['heat']}")
    except Exception as _e:
        _debug_log(f"ths_hot_list error: {_e}")

    # 互动易问答（近24小时）— V16.1: 同步包 to_thread
    try:
        irm = await asyncio.to_thread(cninfo_irm, code, 20)
        _irm_shown = 0
        _irm_cutoff = datetime.now() - timedelta(hours=24)
        for item in irm:
            t_str = str(item.get("ask_time", ""))
            if t_str:
                try:
                    pub_dt = datetime.strptime(t_str, "%Y-%m-%d %H:%M")
                    if pub_dt < _irm_cutoff:
                        continue
                except (ValueError, TypeError):
                    pass
            irm_q = str(item.get("question", "")).strip()[:80]
            if irm_q:
                L(f"    · [{t_str[:16]}] 互动: {irm_q}")
                _irm_shown += 1
                if _irm_shown >= 5:
                    break
        if _irm_shown == 0:
            L("    近24小时暂无互动易问答")
    except Exception as _e:
        _debug_log(f"sht cninfo_irm: {_e}")

    L("\n  ➤ 近7日巨潮实质性重大公告:")

    if _dc.get("skip_announcement_detail"):
        L("  [lite模式] 跳过详细公告")
        anns = []
    else:
        anns = await get_strategic_announcements_async(session, code, days=7)

    if anns:

        for i,a in enumerate(anns,1):

            fl = " ⚠️" if any(k in a["title"] for k in ["减持","立案","严重异动"]) else ""

            tt = f" [{a['type']}]" if a['type'] else ""

            L(f"  {i}. [{a['date']}]{tt} {a['title']}{fl}")

        rc = sum(1 for a in anns if "减持" in a["title"])

        if rc>0: L(f"    ⚠️ 减持预警：近7日有 {rc} 条减持相关公告，请注意风险。")

    else: L("  近7日暂无触及关键词的重大公告")

    # ── 打板分析 ── V16.1: 同步包 to_thread
    L("\n  ➤ 打板与涨停分析:")
    try:
        from stock_common import get_limit_pool_summary
        pool = await asyncio.to_thread(get_limit_pool_summary)
        zt_count = pool.get("limit_up_count", 0)
        zb_count = pool.get("limit_broken_count", 0)
        dt_count = pool.get("limit_down_count", 0)
        success_rate = pool.get("success_rate", 0)
        L(f"    今日涨停 {zt_count} 只 | 炸板 {zb_count} 只 | 跌停 {dt_count} 只 | 封板率 {success_rate:.0f}%")

        # 检查当前股票是否在涨停池/炸板池中
        for item in pool.get("limit_up_list", []):
            if item.get("code") == code:
                L(f"    ✅ 当前股票在涨停池中！连板数:{item.get('limit_count',0)} 板块:{item.get('sector','')} 封板资金:{item.get('limit_fund',0)/1e8:.2f}亿")
                break
        for item in pool.get("limit_broken_list", []):
            if item.get("code") == code:
                L(f"    ⚠️ 当前股票炸板！炸板次数:{item.get('broken_count',0)} 板块:{item.get('sector','')}")
                break

        # 涨停板块分布（前5）
        sector_stats = pool.get("sector_stats", {})
        if sector_stats:
            top_sectors = list(sector_stats.items())[:5]
            L(f"    涨停板块分布: {' | '.join(f'{k}({v})' for k,v in top_sectors)}")

        # V16.1: 昨日涨停池晋级率/赚钱效应（push2ex getYesterdayZTPool）
        try:
            from stock_common import get_yesterday_limit_pool
            yzt = get_yesterday_limit_pool()
            if yzt:
                yzt_total = len(yzt)
                # 晋级 = 今日仍涨停（涨幅≥9.5 或 20cm 阈值）
                yzt_promoted = [
                    s for s in yzt
                    if s.get("change_pct", 0) >= (19.5 if str(s.get("code","")).startswith(("300","301","688")) else 9.5)
                ]
                yzt_avg_pct = sum(s.get("change_pct", 0) for s in yzt) / yzt_total
                promotion_rate = len(yzt_promoted) / yzt_total * 100 if yzt_total else 0
                L(f"    昨日涨停 {yzt_total} 只 → 今日晋级(仍涨停) {len(yzt_promoted)} 只，晋级率 {promotion_rate:.0f}%，平均涨幅 {yzt_avg_pct:+.1f}%")
                # 当前股票是否在昨日涨停池（看今日承接）
                for item in yzt:
                    if item.get("code") == code:
                        L(f"    📌 当前股票为昨日涨停股（昨连板{item.get('y_limit_count',0)}板），今日涨幅 {item.get('change_pct',0):+.2f}% 振幅{item.get('amplitude_pct',0):.1f}%")
                        break
        except Exception as _e2:
            _debug_log(f"sht yzt_pool: {_e2}")
    except Exception as _e:
        _debug_log(f"sht limit_pool: {_e}")
        L("    (打板数据获取失败)")

    # V16.1.7: 盘口异动个股检测（字典 §12.10.1 levistock 实测可用）+ AxData 短线指标（§12.12.1）
    try:
        from stock_common import get_stock_changes, get_shortline_indicators

        # 盘口异动（火箭发射/大笔买入/封涨停板/有大买盘 4 类）
        for _ct, _ctn in [("8201", "火箭发射"), ("8193", "大笔买入"), ("8205", "封涨停板"), ("64", "有大买盘")]:
            try:
                _chg_list = get_stock_changes(_ct)
                _hit = next((c for c in _chg_list if c.get("code") == code), None)
                if _hit:
                    L(f"    🚀 盘口异动[{_ctn}]: 时间{_hit.get('time','')} 涨幅{_safe_float(_hit.get('change_pct',0)):+.2f}%")
            except Exception as _e:
                _debug_log(f"sht stock_changes {_ct}: {_e}")

        # AxData 短线指标 34 字段（消费项目 zhb.zip，零下载）
        try:
            _sl = await asyncio.to_thread(get_shortline_indicators, code)
            if _sl:
                _parts = []
                if _sl.get("open_volume_ratio"):
                    _parts.append(f"开盘量比{_sl['open_volume_ratio']:.2f}")
                if _sl.get("auction_prev_volume_ratio"):
                    _parts.append(f"竞价昨比{_sl['auction_prev_volume_ratio']:.2f}")
                if _sl.get("seal_to_float_ratio") is not None and _sl.get("seal_to_float_ratio", 0) > 0:
                    _parts.append(f"封流比{_sl['seal_to_float_ratio']*100:.3f}%")
                if _sl.get("limit_board_text"):
                    _parts.append(f"几天几板:{_sl['limit_board_text']}")
                if _sl.get("limit_up_streak_days"):
                    _parts.append(f"连板{_sl['limit_up_streak_days']}")
                if _sl.get("year_limit_up_days"):
                    _parts.append(f"年涨停{_sl['year_limit_up_days']}次")
                if _parts:
                    L(f"    📐 短线指标(ZHB同源): {' | '.join(_parts)}")
        except Exception as _e:
            _debug_log(f"sht shortline_indicators: {_e}")
    except Exception as _e:
        _debug_log(f"sht changes/shortline: {_e}")

    L("\n"+"─"*72); L("【十五、综合信号汇总】"); L("─"*36)

    signals = []

    lu2 = q.get("limit_up",0) if q else 0; b1v2 = q.get("bid1_vol",0) if q else 0; np3 = q.get("price",0) if q else 0

    is_lu2 = lu2>0 and abs(np3-lu2)/lu2<0.005

    _lu = q.get("limit_up",0) if q else 0; _ld = q.get("limit_down_price",0) if q else 0

    _hi = q.get("high",0) if q else 0; _lo = q.get("low",0) if q else 0; _chg = q.get("change_pct",0) if q else 0

    if _lu > 0 and _hi >= _lu * 0.98 and _chg < -15:

        signals.append(f"⚠️ 天地板预警：今日最高触及涨停({_hi:.2f})后暴跌至{price_today:.2f}，单日振幅{(_hi-_lo)/_hi*100:.1f}%，极端风险！")

    elif _ld > 0 and _lo <= _ld * 1.02 and _chg > 10:

        signals.append(f"⚠️ 地天板预警：今日最低触及跌停({_lo:.2f})后拉升至{price_today:.2f}，分歧巨大！")

    if is_lu2 and b1v2>0:

        fa2 = b1v2*lu2/1e8; fr2 = fa2/(q.get("mcap_yi",0) or 1)*100

        if fa2>=0.1 or fr2>0.5:

            if fr2 > _lo_strong: signals.append(f"🔥 封单占比流通市值 {fr2:.1f}% (>{_lo_strong}%)，主力封板力度极强")

            elif fr2 > _lo_mid: signals.append(f"✅ 封单质量良好，封单占比流通市值 {fr2:.1f}%")

    if q and price_today>0:

        if q.get("change_pct", 0)>_limit_chg and price_today>=q.get("limit_up",0)*0.995: signals.append("🚀 强势涨停，封单密实，短线溢价预期强烈")

        elif q.get("change_pct", 0)>_near_limit: signals.append(f"📈 今日涨幅 {q.get('change_pct',0):.1f}%，逼近涨停，短线动能充沛")

    if q and is_lu2 and b1v2>0:

        _tamt = q.get("amount_wan",0)*1e4

        if _tamt>0:

            _cr = (b1v2*lu2)/_tamt

            if _cr<_seal_ratio_warn: signals.append(f"⚠️ 封单预警：封单资金仅占今日成交额 {_cr*100:.1f}%，弱势烂板，极易炸板悶杀")

    if nb and len(nb)>=2:

        chg = nb[0]["hold_shares"]-nb[-1]["hold_shares"]

        if chg>0: signals.append(f"北向资金近{len(nb)}日净增持，外资看多信号")

    if ff["data"] and len(ff["data"])>=20:
        _ff_data = ff["data"][-20:]
        if _ff_data and isinstance(_ff_data[0], dict):
            tmain2 = sum(d.get("main_net", 0) for d in _ff_data)
        else:
            tmain2 = sum(_ff_data) if _ff_data else 0
        if tmain2>0: signals.append(f"近20日主力累计净流入 {tmain2/1e8:.2f}亿，中线资金面偏多")
        else: signals.append(f"近20日主力净流出 {abs(tmain2)/1e8:.2f}亿，中线资金面偏空")

    if margin and len(margin)>=5:

        _rzye_trend = sum(1 for i in range(4) if margin[i]["rzye"]>margin[i+1]["rzye"])

        _rqye_trend = sum(1 for i in range(4) if margin[i]["rqye"]>margin[i+1]["rqye"])

        if _rzye_trend>=3 and _rqye_trend<=1:

            signals.append("🔥 两融多头共振：融资余额持续飙升而融券受压，杠杆资金锁仓强推，多头逼空动能强劲")

        if q and abs(q.get("change_pct",0))<3 and _rzye_trend>=3:

            signals.append("⚠️ 两融风险预警：股价滞涨而融资余额创新高，散户杠杆接盘筹码松动")

    if rr and len(rr)>=3 and q and abs(q.get("change_pct",0))>5:

        _buy_ratings = sum(1 for r in rr if "买入" in str(r.get("emRatingName","")) or "推荐" in str(r.get("emRatingName","")))

        if _buy_ratings>=3:

            signals.append(f"💡 交易员笔记：短线高位突发{_buy_ratings}篇券商买入/推荐评级，卖方在摇旗呐喊，谨防游资借利好兑现见顶闷杀")

    if dtb["records"]:

        tn = sum(r["net_buy"] for r in dtb["records"])

        _rd_label = '近半年' if _recent_days >= 150 else ('近一季度' if _recent_days >= 80 else f'近{_recent_days}日'); signals.append(f"{_rd_label}龙虎榜净买入合计 {tn:.0f}万元，上榜 {len(dtb['records'])} 次，股性活跃")

        inst2 = dtb["institution"]

        _lhasa = sum(1 for s in dtb["seats"]["buy"] if "东方财富证券拉萨" in s["name"])

        if _lhasa>=3:

            signals.append(f"❌ 筹码散户化：买方出现{_lhasa}席拉萨天团，纯散户跟风对倒，筹码极度松动")

        if inst2 and inst2.get("net_amt",0)>0: signals.append(f"龙虎榜机构净买入 {inst2['net_amt']}万元，机构资金关注")

    if holders and len(holders)>=2 and holders[0]["change_ratio"]<0:

        signals.append(f"股东户数环比减少 {abs(holders[0]['change_ratio']):.1f}%，筹码集中")

    if nb and len(nb)>=2:

        rc2 = nb[0]["hold_ratio"]-nb[-1]["hold_ratio"]

        if rc2>0.01: signals.append(f"北向资金近{len(nb)}日持股比例 +{rc2:.3f}%，外资增持信号")

        elif rc2<-0.01: signals.append(f"北向资金近{len(nb)}日持股比例 {rc2:.3f}%，外资减持信号")

    if peer_data and peer_data["peers"] and "note" not in peer_data["peers"][0]:

        my_m = peer_data.get("my_mcap",0); ptm = peer_data["peers"][0]["mcap_yi"] if peer_data["peers"] else 0

        if ptm>0 and my_m>0 and my_m/ptm<0.1: signals.append(f"本股市值仅为板块龙头 {peer_data['peers'][0]['name']} 的 {my_m/ptm*100:.1f}%，属板块小市值标的")

    if rbt:

        for d in rbt[:3]:

            if d["premium_pct"] >= 0:

                signals.append(f"💎 场外抢筹：{d['date']}发生溢价大宗（溢价{d['premium_pct']:.1f}%），买方溢价接盘，主力抢筹意图明显")

                break

        for d in rbt[:3]:

            if d["premium_pct"] < -8:

                signals.append(f"❌ 折价套现：{d['date']}发生折价{abs(d['premium_pct']):.1f}%大宗交易，场外廉价倒手，对二级市场价格有压制")

                break

    mc = miq.get("change_pct") if miq else None; bc2 = biq.get("change_pct") if biq else {}

    sc2 = q.get("change_pct",0) if q else None; ic2 = industry_change_pct if industry_rank>0 else None

    if all(v is not None for v in [mc,bc2,sc2,ic2]):

        cd = sc2-ic2

        if cd>2.0 and sc2>0: signals.append(f"🔥 鹤立鸡群模型：个股 {sc2:+.2f}% >> 板块 {ic2:+.2f}% (领先 {cd:.1f}%)，属板块领涨龙头")

        elif abs(sc2-ic2)<1.0 and abs(sc2)>0.5: signals.append(f"📊 随波逐流模型：个股 {sc2:+.2f}% ≈ 板块 {ic2:+.2f}%，属板块普涨型跟风")

    try:
        from data_provider import _should_use_zhb_for_realtime
        if _should_use_zhb_for_realtime() and cdata.change_5d:
            stk3 = cdata.change_5d * 0.6  # ZHB 5日涨幅做3日偏离估算
            tl = 30 if code.startswith(("300","301","688")) else 20
            if stk3 >= tl:
                signals.append(f"异动雷达(ZHB离线)：近5日涨幅{cdata.change_5d:+.2f}%，估算3日偏离{stk3:+.2f}%>={tl}%，触发异动")
        else:
            _sk_r, _sr_r = tdx_get_security_bars(code, count=5)
            if len(_sr_r) >= 4 and len(_sk_r) > 0:
                _ci_r = next((i for i,k in enumerate(_sk_r) if k in ("close","close_price")), -1)
                if _ci_r >= 0:
                    s_c = [_safe_float(rr[_ci_r]) for rr in _sr_r[-4:] if len(rr) > _ci_r]
                    if len(s_c) == 4 and s_c[0] > 0:
                        stk3 = (s_c[-1]/s_c[0]-1)*100
                        ic_r = bi if bi else "sh000001"
                        pi_r = ic_r[2:] if ic_r.startswith(("sh","sz")) else ic_r
                        _ik_r, _ir_r = baidu_kline_full(pi_r, is_index=True)
                        if len(_ir_r) >= 4:
                            _ci2_r = next((i for i,k in enumerate(_ik_r) if k in ("close","close_price")), -1)
                            if _ci2_r >= 0:
                                i_c = [_safe_float(rr[_ci2_r]) for rr in _ir_r[-4:] if len(rr) > _ci2_r]
                                idx3 = (i_c[-1]/i_c[0]-1)*100 if len(i_c)==4 and i_c[0]>0 else 0
                                dv = round(stk3-idx3,2)
                                tl = 30 if code.startswith(("300","301","688")) else 20
                                if dv>=tl: signals.append(f"异动雷达：3日偏离值{dv:+.2f}%>={tl}%，触发短期异动")
                                elif dv>=tl*0.9: signals.append(f"异动雷达：3日偏离值{dv:+.2f}%，距红线仅差{tl-dv:.2f}%，卡异动")
    except Exception as _e:
        _debug_log(f"sht deviation radar error: {_e}")

    L("  综合分析条目:")

    if signals:

        for i,s in enumerate(signals,1): L(f"  {i}. {s}")

    else: L("  (数据不足，暂无法生成综合信号)")

    if q and price_today>0 and q.get("change_pct",0)>=(19.5 if code.startswith(("300","301","688")) else 9.5):

        try:

            _sk, _sr = tdx_get_security_bars(code, count=5)

            _ci = next((i for i,k in enumerate(_sk) if k in ("close","close_price")), -1)

            if _ci>=0:

                _c3 = [_safe_float(rr[_ci]) for rr in _sr[-4:] if len(rr)>_ci]

                if len(_c3)==4 and _c3[0]>0:

                    _3d = (_c3[-1]/_c3[0]-1)*100

                    _lb_pct = 20 if code.startswith(("300","301","688")) else 10

                    _lb2 = _lb_pct * 1.9

                    _lb3 = _lb_pct * 2.85

                    _lb_t = "3连板" if _lb3<=_3d<_lb3+_lb_pct else ("2连板" if _lb2<=_3d<_lb3 else ("首板" if _lb_pct*0.95<=_3d<_lb2 else f"高标{int(_3d/_lb_pct)}板" if _3d>=_lb3+_lb_pct else ""))

                    if _lb_t: L(f"  📊 连板追踪: 今日涨停，判定为{_lb_t}(3日累计{_3d:.1f}%)")

        except Exception as _e:

            pass

    L("\n"+"─"*72); L("【仓位管理建议】"); L("─"*36)

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
    
    # 资金流向（V16.1: 数据"最新在前"，[:20] 取最近 20 日）
    if ff["data"] and len(ff["data"]) >= 20:
        _ff_data = ff["data"][:20]
        if _ff_data and isinstance(_ff_data[0], dict):
            score_data.main_net_inflow = sum(d.get("main_net", 0) for d in _ff_data)
            score_data.consecutive_inflow_days = sum(1 for d in _ff_data if d.get("main_net", 0) > 0)
        else:
            score_data.main_net_inflow = sum(_ff_data) if _ff_data else 0
            score_data.consecutive_inflow_days = sum(1 for d in _ff_data if d > 0) if _ff_data else 0
    
    # 筹码数据
    if holders and len(holders) >= 2:
        score_data.holder_change_ratio = holders[0]["change_ratio"]
        if holders[0]["change_ratio"] < 0 and holders[1]["change_ratio"] < 0:
            score_data.holder_consecutive_decrease = True
    
    # 北向数据
    if nb and len(nb) >= 2:
        score_data.northbound_change = nb[0]["hold_shares"] - nb[-1]["hold_shares"]
    
    # 机构净买入
    if dtb["institution"].get("net_amt", 0) > 0:
        score_data.institution_net_buy = dtb["institution"].get("net_amt", 0)
    
    # 融券下降
    if margin and len(margin) >= 3:
        if all(margin[i]["rqye"] <= margin[i+1]["rqye"] for i in range(2)):
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

    if _seal_warn:
        # 封单弱时仓位降级：原仓位建议减半
        if _ps >= 50: L(f"  短线评分: {_ps:.0f}/100 → 封单偏弱，仓位降至20%，止损-5% ⚠️")
        elif _ps >= 30: L(f"  短线评分: {_ps:.0f}/100 → 封单偏弱，仓位降至12%，止损-5% ⚠️")
        elif _ps >= 15: L(f"  短线评分: {_ps:.0f}/100 → 封单偏弱，仓位降至5%，止损-3% ⚠️")
        else: L(f"  短线评分: {_ps:.0f}/100 → 封单偏弱，观望为主，仓位2% ⚠️")
    elif _ps>=50: L(f"  短线评分: {_ps:.0f}/100 → 强烈参与，仓位40%，止损-5%")
    elif _ps>=30: L(f"  短线评分: {_ps:.0f}/100 → 可参与，仓位25%，止损-5%")
    elif _ps>=15: L(f"  短线评分: {_ps:.0f}/100 → 轻仓试探，仓位10%，止损-3%")
    else: L(f"  短线评分: {_ps:.0f}/100 → 观望，仓位5%试水")

    # 多评委评审团评分（V8.9）
    try:
        multi_scores = calculate_multi_school_scores(score_data)
        L("")
        L("  ★ 多评委评审团评分")
        L(f"    价值派评分: {multi_scores['value'].total_score:.1f}分")
        L(f"    成长派评分: {multi_scores['growth'].total_score:.1f}分")
        L(f"    投机派评分: {multi_scores['speculator'].total_score:.1f}分")
        L(f"    综合共识: {multi_scores['consensus'].total_score:.1f}分")
        if multi_scores['dispersion'] > 15:
            L(f"    ⚠️ 派别分歧度较大({multi_scores['dispersion']:.1f})，投资需谨慎")
    except Exception as e:
        L(f"    多评委评分异常: {e}")

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
        _debug_log(f"multi_school_score error: {_e}")

    # 市场热度参考（同花顺热榜 + 概念命中）— V16.1: 同步包 to_thread
    try:
        hot_list = await asyncio.to_thread(ths_hot_list, "hour")
        # 检查该股是否在热榜中
        in_hot = next((h for h in hot_list if h.get("code") == code), None)
        if in_hot:
            L(f"\n  📊 市场热度: 该股当前在同花顺热榜 #{in_hot['rank']}，热度{in_hot['heat']}")
            if in_hot.get("concepts"):
                L(f"     关联概念: {', '.join(in_hot['concepts'][:3])}")
            if in_hot.get("tag"):
                L(f"     标签: {in_hot['tag']}")
        # V14.2: 优先用 ZHB tdxchain.cfg 本地概念匹配（零网络请求）
        try:
            from data_provider import get_concept_from_zhb
            zhb_concepts = await asyncio.to_thread(get_concept_from_zhb, code)
            if zhb_concepts:
                L(f"     产业链/概念（ZHB 本地）: {', '.join(zhb_concepts[:5])}")
        except Exception as _e:
            _debug_log(f"get_concept_from_zhb error: {_e}")
        # 东财概念命中（V14.2: 仅当 ZHB 无数据时 fallback）
        concepts = await asyncio.to_thread(em_hot_concept, code)
        if concepts:
            L(f"     热门概念: {', '.join([c['concept'] for c in concepts[:3]])}")
    except Exception as _e:
        _debug_log(f"em_hot_concept error: {_e}")

    # 累积快照数据（批量结束后统一写入）
    _SNAPSHOT_DATA[code] = {
        "name": info.get('name', ''),
        "total_score": _ps,
        "price": price_today,
        "report_source": "sht"
    }

    output = "\n".join(filter(None, lines))

    with open(output_path,"w",encoding="utf-8") as f: f.write(output)

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
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        report_type = "sht"

        _cached_ind_comp = get_industry_comparison()
        _cached_idx_q = {}
        for ic in ("sh000001", "sz399106", "sz399102", "sh000688"):
            _iq = _get_index_quote(ic)
            if _iq:
                _cached_idx_q[ic] = _iq
        _cached_hsgt = get_hsgt_macro_flow()

        args = self.args

        async def _main_async():
            codes = clean_codes(args.codes, verbose=True)
            if not codes:
                print("  ❌ 没有有效的股票代码")
                return []
            for code in codes:
                try:
                    print(f"  📋 加入队列: {code}", flush=True)
                except UnicodeEncodeError:
                    print(f"  [INFO] 加入队列: {code}", flush=True)

            _session = await create_async_session()
            try:
                sem = asyncio.Semaphore(3)

                async def _limited(code):
                    async with sem:
                        result_path = os.path.join(args.output, f"{code}_{report_type}_{ts}.txt")
                        try:
                            await generate_report_async(
                                _session, code, result_path,
                                ind_comp=_cached_ind_comp, idx_q=_cached_idx_q,
                                hsgt=None, depth=args.depth
                            )
                            print(f"  ✅ 已保存: {result_path}", flush=True)
                            return {"code": code, "status": "成功", "error": "", "path": result_path}
                        except Exception as e:
                            print(f"❌ {code} 数据生成失败: {e}", flush=True)
                            return {"code": code, "status": "数据失败", "error": str(e), "path": ""}

                results = await asyncio.gather(*[_limited(c) for c in codes])
                return results
            finally:
                await _session.close()

        _results = asyncio.run(_main_async())

        if _SNAPSHOT_DATA:
            from stock_common.analyze_history import save_snapshot
            save_snapshot("sht", _SNAPSHOT_DATA)

        ok = [r for r in _results if r["status"] == "成功"]
        fd = [r for r in _results if r["status"] == "数据失败"]
        print(f"\n{'='*60}\n  批量执行完成 — 共处理 {len(_results)} 只股票\n{'='*60}")
        print(f"  ✅ 全部成功: {len(ok)}  |  ❌ 数据失败: {len(fd)}")
        for r in fd:
            print(f"    ❌ {r['code']} — {r['error'][:80]}")

        return {"results": _results, "time_str": ts, "report_type": report_type}

    def upload_reports(self, drive, folder_id: str, results) -> None:
        self.upload_multi_reports(drive, folder_id, results)


if __name__ == "__main__":
    runner = ShtReportRunner()
    runner.run()
