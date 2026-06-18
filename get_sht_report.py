#!/usr/bin/env python3

"""get_sht_report.py — A股短线个股深度数据报告 (V8)"""



import argparse, requests, math, time, pandas as pd, json, os, sys, re as _re

import asyncio

import random

from datetime import date, datetime, timedelta

from gd_uploader import init_gd, upload_stock_report_by_code, cleanup_gd_proxy

from tdx_client import (tdx_get_security_bars, tdx_get_latest_bar_with_ma,

                         tdx_get_quote_full,

                         tdx_get_index_quote, tdx_get_index_bars,

                         tdx_get_fund_flow, tdx_get_history_fund_flow,

                         tdx_get_eps_from_reports, tdx_get_latest_announcements,

                         tdx_get_belong_boards, tdx_get_board_list,

                         tdx_get_board_members, tdx_get_board_by_name,

                         tdx_get_dividend_history, cleanup_tdx)



from stock_common import (clean_codes, _safe_float, _request_with_retry, _quick_request, UA,
                           _market_code, eastmoney_datacenter, _em_filter,
                           _load_settings, _load_strategy_config, holder_change,
                           holder_cache_flush,
                           get_strategic_announcements, get_dragon_tiger_board,
                           create_async_session, eastmoney_datacenter_async,
                           _em_filter_async, _async_request_with_retry,
                           _async_quick_request, get_dragon_tiger_board_async,
                           holder_change_async, get_strategic_announcements_async,
                           parse_args, get_tencent_quote, baidu_kline_full,
                           get_reports, get_eps_forecast, get_northbound_hold,
                           get_margin_trading, get_block_trade,
                           get_dividend_history, get_industry_comparison,
                           print_batch_summary,
                           get_concept_blocks, get_ths_hot_reason,
                           get_ths_hot_reason_async, get_industry_peers,
                           get_stock_sector_rank,
                           get_stock_info, get_hsgt_macro_flow, get_lockup_expiry,
                           get_eps_forecast_async, get_margin_trading_async,
                           get_block_trade_async, get_northbound_hold_async,
                           get_lockup_expiry_async,
                           is_trading_day, get_market_status)



# 脚本所在目录（用于确定默认输出目录）

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))





# ═══════════════════════════════════════════
# 数据获取层
# ═══════════════════════════════════════════


def _get_index_quote(idx_code):

    """V4: 指数行情 → tdx_client 适配器（TDX指数K线，自动fallback腾讯）"""

    return tdx_get_index_quote(idx_code)



def get_fund_flow_realtime(code):

    """V7.5: 今日主力净流入 → TDX TCP（push2 fallback 已删除）"""

    ff = tdx_get_fund_flow(code)

    if ff and ff.get("main_net_wan", 0) != 0:

        return {"data": [ff["main_net_wan"]], "detail": ff, "source": "tdx"}

    return None



def get_fund_flow_120d(code):

    """V7.5: 60日资金流 → TDX TCP（同花顺 fallback 已删除）"""

    tdx_data = tdx_get_history_fund_flow(code, 60)

    if tdx_data:

        return {"data": tdx_data, "error": "", "source": "tdx"}

    return {"data":[],"error":"资金流数据获取失败"}



# V7.5: get_dragon_tiger_board 由 stock_common 统一提供（import 已导入）























def get_baidu_kline_with_ma(code):

    """V4: K线+MA → tdx_client 适配器（TDX日K线+本地MA5/10/20计算）"""

    return tdx_get_latest_bar_with_ma(code)







async def get_hsgt_macro_flow_async(session):

    """async 版: 同花顺北向资金大盘净流入（宏观风向标）"""

    url = "https://data.hexin.cn/market/hsgtApi/method/dayChart/"

    headers = {"User-Agent": UA, "Host": "data.hexin.cn", "Referer": "https://data.hexin.cn/"}

    try:

        r = await _async_quick_request(session, url, headers=headers, timeout=10)

        if r is None: return None

        d = r

        hgt = d.get("hgt", [])

        sgt = d.get("sgt", [])

        if not hgt or not sgt: return None

        hgt_val = float(hgt[-1]) if hgt[-1] else 0

        sgt_val = float(sgt[-1]) if sgt[-1] else 0

        return {"hgt": hgt_val, "sgt": sgt_val, "total": hgt_val + sgt_val}

    except Exception:

        return None





# ═══════════════════════════════════════════

# 报告生成

# ═══════════════════════════════════════════



def generate_report(code, output_path, ind_comp=None, idx_q=None, hsgt=None):

    """V7.5: 支持 ind_comp/idx_q/hsgt 外部缓存，批量模式下避免重复查询"""

    today_str = date.today().strftime("%Y-%m-%d")

    lines = []

    def L(s=""): lines.append(s)

    L("="*72); L(f"  {code} 个股深度数据报告V8 — {today_str} {datetime.now().strftime('%H:%M:%S')}"); L("="*72); L("")

    _30d_str = (datetime.now()-timedelta(days=30)).strftime("%Y-%m-%d")

    _60d_str = (datetime.now()-timedelta(days=60)).strftime("%Y-%m-%d")

    _90d_str = (datetime.now()-timedelta(days=90)).strftime("%Y-%m-%d")

    # 加载策略阈值配置

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



    # ─── 1. 基本信息 ───

    _is_td = is_trading_day()
    _mkt_status, _mkt_note = get_market_status()

    L("\n"+"━"*72); L(f"【一、个股基本信息】（{_mkt_note}）"); L("━"*72)

    info = get_stock_info(code)

    L(f"  股票名称: {info.get('name','N/A')}")

    L(f"  股票代码: {info.get('code',code)}")

    L(f"  所属板块: {info.get('industry','N/A')}")

    L(f"  总股本:   {info.get('total_shares',0)/1e8:.2f}亿股")

    L(f"  流通股本: {info.get('float_shares',0)/1e8:.2f}亿股")

    ld = info.get("list_date","")

    if ld and len(ld)>=8: ldf = f"{ld[:4]}-{ld[4:6]}-{ld[6:8]}"

    else: ldf = ld

    L(f"  上市日期: {ldf}")



    # ─── 2. 实时行情 ───

    L("\n"+"━"*72); L("【二、实时行情、估值与短线趋势】"); L("━"*72)

    q = get_tencent_quote(code); price_today = q.get("price",0) if q else 0

    if q:

        L(f"  当前价:   {price_today:.2f}元")

        L(f"  涨跌额:   {q['change_amt']:.2f}元  涨跌幅: {q['change_pct']:.2f}%")

        L(f"  今开:     {q['open']:.2f}元  昨收: {q['last_close']:.2f}元")

        L(f"  最高:     {q['high']:.2f}元  最低: {q['low']:.2f}元")

        L(f"  成交额:   {q['amount_wan']/10000:.2f}亿元  换手率: {q['turnover_pct']:.2f}%")

        L(f"  量比:     {q['vol_ratio']:.2f}  振幅: {q['amplitude_pct']:.2f}%")

        L(f"  总市值:   {q['mcap_yi']:.2f}亿元  流通市值: {q['float_mcap_yi']:.2f}亿元")

        _pe_t = q.get('pe_ttm',0); _pe_s = q.get('pe_static',0)

        _pe_s_str = f"{_pe_s:.2f}" if _pe_t > 0 and _pe_s > 0 else "N/A（亏损）"

        L(f"  PE(TTM):  {_pe_t:.2f}  PE(静): {_pe_s_str}  PB: {q.get('pb',0):.2f}")

        L(f"  涨停价:   {q['limit_up']:.2f}元  跌停价: {q['limit_down_price']:.2f}元")

    else: L("  实时行情获取失败")

    ma_data = get_baidu_kline_with_ma(code)

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

        for ic,inm in all_idx:

            iq = _get_index_quote(ic)

            if iq:

                idx_q[ic] = iq

    for ic,inm in all_idx:

        iq = idx_q.get(ic, {})

        if iq:

            L(f"  [{inm}] 开盘 {iq.get('open',0):.2f} | 当前 {iq.get('price',0):.2f} | 涨跌幅 {iq.get('change_pct',0):+.2f}%{' ← 本股' if ic==bi else ''}")

    miq = idx_q.get("sh000001",{}); biq = idx_q.get(bi,{}) if bi else {}

    # 北向资金大盘流向

    if hsgt is None:

        hsgt = get_hsgt_macro_flow()

    if hsgt:

        _sig = "偏多" if hsgt["total"] > 0 else "偏空"

        L(f"  💰 今日北向资金: 沪股通 {hsgt['hgt']:+.2f}亿 | 深股通 {hsgt['sgt']:+.2f}亿 | 合计 {hsgt['total']:+.2f}亿（{_sig}）")

    ff = get_fund_flow_120d(code)

    rf = get_fund_flow_realtime(code)

    if rf and rf.get("data") and len(rf["data"]) > 0:

        _fd = rf["data"]

        L(f"  💰 今日主力净流入: {_fd[0]:.0f}万元 ({_fd[0]/1e4:.2f}亿)")

    else:

        L(f"\n  [资金流向] 今日主力净流入(实时): 暂无数据")



    # ─── 3. 机构预期 ───

    L("\n"+"━"*72); L("【三、机构一致预期与估值】"); L("━"*72)

    df_eps = get_eps_forecast(code)

    if not df_eps.empty and len(df_eps.columns)>=2:

        _this_year = str(date.today().year)

        eps_cur = None; eps_next = None

        eps_min = None; eps_max = None; eps_ind = None; _n_analysts = 0

        for _ri in range(min(len(df_eps),5)):

            _row_label = str(df_eps.iloc[_ri,0])

            if _this_year in _row_label or f"{_this_year}预测" in _row_label or f"{_this_year}E" in _row_label:

                eps_cur = _safe_float(df_eps.iloc[_ri,3])      # 均值

                eps_min = _safe_float(df_eps.iloc[_ri,2])      # 最小值

                eps_max = _safe_float(df_eps.iloc[_ri,4])      # 最大值

                eps_ind = _safe_float(df_eps.iloc[_ri,5])      # 行业均值

                _n_analysts = int(_safe_float(df_eps.iloc[_ri,1]))  # 机构数

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



    # ─── 4. 研报 ───

    L("\n"+"━"*72); L("【四、个股研报（东财）】"); L("━"*72)

    reports = get_reports(code, 5)

    rr = [r for r in reports if str(r.get("publishDate",""))[:10]>=_60d_str]

    if rr:

        L(f"  最近60天共 {len(rr)} 篇研报，显示前10篇:")

        L(f"  {'日期':<12} {'机构':<16} {'评级':<10} {'标题'}"); L(f"  {'-'*70}")

        for r in rr[:10]:

            L(f"  {str(r.get('publishDate',''))[:10]:<12} {r.get('orgSName',''):<16} {str(r.get('emRatingName','')):<10} {r.get('title','')[:50]}")

    elif reports: L(f"  近60天内无新研报（共 {len(reports)} 篇历史研报，已省略）")

    else: L("  无研报数据（该股可能无机构覆盖）")



    # ─── 5. 概念板块 ───

    L("\n"+"━"*72); L("【五、概念板块、热点归因与板块共振】"); L("━"*72)

    blocks = get_concept_blocks(code)

    if blocks["industry"]: L(f"  所属板块: {', '.join(b['name'] for b in blocks['industry'])}")

    if ind_comp is None:

        ind_comp = get_industry_comparison()

    # V4.2: 优先使用 TDX 行业名（与 ind_comp 同源 TDX 分类，保证匹配）

    stock_ind = info.get('industry','')

    if blocks and blocks.get("industry"):

        stock_ind = blocks["industry"][0].get("name", stock_ind)

    industry_rank=0; industry_change_pct=0; industry_match_name=""

    if stock_ind and ind_comp.get("all"):

        rank_str = "未进入前100"; is_top=False

        # 精确匹配 + 模糊匹配（去除行业/服务等后缀）

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

    time.sleep(0.5)

    peer_data = get_industry_peers(code, 3, info=info)

    if peer_data.get("my_rank",0)>0 and peer_data.get("industry_count",0)>0:

        L(f"  ➤ [所属板块排名] {peer_data.get('industry',stock_ind)}: 按总市值该股排名第 {peer_data['my_rank']}/{peer_data['industry_count']} 位")

    # 板块涨跌排名（industry_rank>0 精确匹配 或 有 peer_data 兜底）

    _has_peer = peer_data.get("my_rank",0)>0 and peer_data.get("industry_count",0)>0

    if (industry_rank>0 and industry_match_name) or _has_peer:

        _rank_parts = []

        if industry_rank>0 and industry_match_name:

            # V4 fix: TDX BoardInfo 无涨跌家数，从 peer_data.all_members 全量统计

            _up = 0; _down = 0

            _all_members = peer_data.get('all_members', [])

            if _all_members:

                _up = sum(1 for m in _all_members if m.get('change_pct', 0) > 0)

                _down = sum(1 for m in _all_members if m.get('change_pct', 0) < 0)

            _rank_parts.append(f"[板块涨跌排名] 上涨 {int(_up)} 家 / 下跌 {int(_down)} 家")

        try:

            _sr = get_stock_sector_rank(code, info=info, q=q)

            if _sr: _rank_parts.append(f"本股今日{_sr['change_pct']:+.2f}%，板块内排名第{_sr['rank']}/{_sr['total']}名")

        except Exception:

            pass

        if _rank_parts: L(f"     {'  '.join(_rank_parts)}")

    div = get_dividend_history(code)

    if div:

        ld2 = div[0]; ye = f"{(ld2['bonus_rmb']/price_today)*100:.2f}%" if price_today>0 else "N/A"

        L(f"  最近分红: {ld2['date']} 每股{ld2['bonus_rmb']:.4f}元 (约{ye}股息率)")

    if blocks["concept"]:

        L(f"\n  概念板块: {', '.join(b['name'] for b in blocks['concept'])}")

    L(f"\n  ➤ 同花顺热点题材归因 (基于当日强势股/涨停榜):")

    if datetime.now().hour*100+datetime.now().minute<1600:

        L("  ⚠️ 同花顺热点池需16:00后更新，当前为盘中时段数据可能为空")

    ths_hot = get_ths_hot_reason(code, today_str)

    if ths_hot: L(f"  [强势归因] {ths_hot.get('reason','')}")

    else: L("  (该股今日未进入同花顺强势股列表，暂无热点题材归因数据)")



    # ─── 6. 同业对比 ───

    L("\n"+"━"*72); L("【六、同业龙头横向对比】"); L("━"*72)

    if peer_data["peers"]:

        if "note" in peer_data["peers"][0]: L(f"  ⚠️ {peer_data['peers'][0]['note']}")

        else:

            _my_mcap_show = peer_data['my_mcap'] if peer_data['my_mcap'] > 0 else q.get('mcap_yi', 0)

            L(f"  所属板块: {peer_data['industry']}"); L(f"  本股市值: {_my_mcap_show:.1f}亿元")

            L(f"  同业龙头对比:"); L(f"  {'代码':<8} {'名称':<12} {'股价':>8} {'涨跌幅%':>8} {'市值(亿)':>10} {'PE':>8} {'换手率%':>8}"); L(f"  {'-'*70}")

            _my_mcap = peer_data['my_mcap'] if peer_data['my_mcap'] > 0 else q.get('mcap_yi', 0)

            L(f"  {code:<8} {info.get('name','N/A'):<12} {price_today:>8.2f} {q.get('change_pct',0):>7.2f}% {_my_mcap:>9.1f} {q.get('pe_ttm',0):>7.1f} {q.get('turnover_pct',0):>7.2f}% ← 本股")

            for p in peer_data["peers"]: L(f"  {p['code']:<8} {p['name']:<12} {p['price']:>8.2f} {p['change_pct']:>7.2f}% {p['mcap_yi']:>9.1f} {p['pe']:>7.1f} {p['turnover']:>7.2f}%")

    else: L(f"  无法获取同业数据（板块: {peer_data.get('industry','未知')}）")



    # ─── 7. 资金流 ───

    L("\n"+"━"*72); L("【七、资金走向分析】"); L("━"*72)

    if ff["data"]:

        L("\n  ➤ 60日资金流监控 (最近 10 日):")

        _recent = ff["data"][-10:]

        L(f"  {'日期':<12} {'主力净流入(亿)':>12} {'超大单(亿)':>10} {'大单(亿)':>10} {'中单(亿)':>10} {'小单(亿)':>10}")

        L(f"  {'-'*70}")

        for d in reversed(_recent):

            if d['main_net'] == 0 and d['super_net'] == 0 and d['large_net'] == 0:

                continue

            L(f"  {d['date']:<12} {d['main_net']/1e4:>+12.0f} {d['super_net']/1e4:>+10.0f} {d['large_net']/1e4:>+10.0f} {d['mid_net']/1e4:>+10.0f} {d['small_net']/1e4:>+10.0f}")

        r20 = ff["data"][-20:]; tmain = sum(d["main_net"] for d in r20); tdays = sum(1 for d in r20 if d["main_net"]>0)

        L(f"\n  近20日统计:\n    主力累计净流入: {tmain/1e8:.2f}亿元\n    主力净流入天数: {tdays}/20天")

        L(f"  信号: {'主力资金近期净流入 → 偏多' if tmain>0 else '主力资金近期净流出 → 偏空'}")

    else: L(f"  (资金流数据获取失败)")



    # ─── 8. 北向资金 ───

    L("\n"+"━"*72); L("【八、北向资金持仓动态】"); L("━"*72)

    nb = get_northbound_hold(code, 20)

    if nb:

        L(f"  近 {len(nb)} 个交易日北向持仓数据:")

        L(f"  {'日期':<12} {'持股数量(万)':>12} {'持股市值(万)':>12} {'持股占比%':>10} {'变动股数(万)':>12}"); L(f"  {'-'*65}")

        for d in nb:

            # V4.1: 推算缺失的市值/占比（东财有时返回0）

            _mcap = d.get('market_cap',0) or 0

            _ratio = d.get('hold_ratio',0) or 0

            _shares = d.get('hold_shares',0) or 0

            if _mcap == 0 and _shares > 0 and price_today > 0:

                _mcap = _shares * price_today

                _ratio = _shares / info.get('total_shares',1) if info.get('total_shares',0) > 0 else 0

            L(f"  {d['date']:<12} {_shares/1e4:>12.0f} {_mcap/1e4:>12.0f} {_ratio:>9.4f}% {d['change_shares']/1e4:>+12.0f}")

    else: L("  该股暂无北向资金持仓数据（可能非陆股通标的或数据延迟）")



    # ─── 9. 龙虎榜 ───

    L("\n"+"━"*72); L("【九、龙虎榜席位】"); L("━"*72)

    if datetime.now().hour*100+datetime.now().minute<1630:

        L("  ⚠️ 龙虎榜数据约16:30后更新，当前时段显示的是最近一期已发布数据")

    dtb = get_dragon_tiger_board(code, today_str)

    if dtb["records"]:

        L(f"  近{_recent_days}日上榜 {len(dtb['records'])} 次:"); L(f"  {'日期':<12} {'上榜原因':<50} {'净买入(万)':>9} {'换手率':>6}"); L(f"  {'-'*85}")

        for r in dtb["records"]: L(f"  {r['date']:<12} {r.get('reason','')[:48]:<50} {r['net_buy']:>12.1f} {r['turnover']:>7.2f}%")

        # 游资标签库（V7.5: 外置到 strategy_config.yaml）

        _cfg = _load_settings()

        _trader_tags = [(k, v) for k, v in _cfg.get("trader_tags", {}).items()]

        def _tag(name):

            for kw, t in _trader_tags:

                if kw in name: return t

            return ""

        seats = dtb["seats"]

        if seats["buy"]:

            L(f"\n  最近买入席位 TOP5:"); L(f"  {'营业部名称':<30} {'买入(万)':>9} {'卖出(万)':>9} {'净额(万)':>9}"); L(f"  {'-'*70}")

            for s in seats["buy"]: L(f"  {_tag(s['name'])} {s['name']:<28} {s['buy_amt']:>12.1f} {s['sell_amt']:>12.1f} {s['net']:>12.1f}")

        if seats["sell"]:

            L(f"\n  最近卖出席位 TOP5:"); L(f"  {'营业部名称':<30} {'买入(万)':>9} {'卖出(万)':>9} {'净额(万)':>9}"); L(f"  {'-'*70}")

            for s in seats["sell"]: L(f"  {_tag(s['name'])} {s['name']:<28} {s['buy_amt']:>12.1f} {s['sell_amt']:>12.1f} {s['net']:>12.1f}")

        inst = dtb["institution"]

        if inst and (inst.get("buy_amt",0)>0 or inst.get("sell_amt",0)>0):

            L(f"\n  机构买卖统计:\n    机构买入金额: {inst['buy_amt']}万元\n    机构卖出金额: {inst['sell_amt']}万元\n    机构净买入: {inst['net_amt']}万元")

        # V7.5: 游资活跃度诊断
        _dt_cfg = _load_settings()
        _dt_trader_tags = _dt_cfg.get("trader_tags", {}) if _dt_cfg else {}

        # 汇总所有席位中的著名游资
        _all_depts = []
        for _side in ["buy", "sell"]:
            for _s in seats.get(_side, []):
                _sname = str(_s.get("name", ""))
                for _kw, _tg in _dt_trader_tags.items():
                    if _kw in _sname:
                        _all_depts.append((_tg, _sname, _side, _s.get("net", 0)))
                        break

        # 拉萨散户席位数量识别
        _lhasa_count = sum(1 for _s in seats.get("buy", []) if "东方财富证券拉萨" in str(_s.get("name", "")))
        _lhasa_sell = sum(1 for _s in seats.get("sell", []) if "东方财富证券拉萨" in str(_s.get("name", "")))

        # 诊断输出
        L("\n  ━━ 游资活跃度诊断 ━━")
        if _all_depts:
            _buy_tags = [x[0] for x in _all_depts if x[2] == "buy"]
            _sell_tags = [x[0] for x in _all_depts if x[2] == "sell"]
            _unique_buy = list(dict.fromkeys(_buy_tags))
            _unique_sell = list(dict.fromkeys(_sell_tags))
            if _unique_buy:
                L(f"  🟢 著名游资买入: {'、'.join(_unique_buy)}")
            if _unique_sell:
                L(f"  🔴 著名游资卖出: {'、'.join(_unique_sell)}")
            L(f"  📊 席位明细:")
            for _tg, _nm, _sd, _nt in _all_depts[:5]:
                _sd_txt = "买" if _sd == "buy" else "卖"
                L(f"     {_sd_txt}五 {_tg} {_nm[:20]} 净{_nt:+.1f}万")
        else:
            L("  ℹ️  无著名游资/机构专用席位上榜")

        if _lhasa_count + _lhasa_sell > 0:
            L(f"  ⚠️  拉萨散户席位: 买{_lhasa_count}家 / 卖{_lhasa_sell}家（散户聚集，注意追高风险）")

        # 综合判断
        _inst_net = inst.get("net_amt", 0) if inst else 0
        if _all_depts and _inst_net > 0:
            L("  ✅ 综合判断: 机构资金+游资同步关注，资金面积极")
        elif _inst_net > 0:
            L("  ✅ 综合判断: 机构净买入，机构资金关注")
        elif _all_depts and _inst_net < -1000:
            L("  ⚠️ 综合判断: 机构大额卖出 + 游资炒作，需谨慎")
        elif _lhasa_count + _lhasa_sell > 3:
            L("  ⚠️ 综合判断: 散户席位占主导，短期波动较大")

    else: L(f"  近{_recent_days}日无龙虎榜记录（白马蓝筹或近期未触发异动标准的个股，无龙虎榜属正常现象）")



    # ─── 10. 解禁 ───

    L("\n"+"━"*72); L("【十、限售解禁日历】"); L("━"*72)

    lockup = get_lockup_expiry(code, today_str, days=90, include_history=True)

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



    # ─── 11. 融资融券 ───

    L("\n"+"━"*72); L("【十一、融资融券（两融数据）】"); L("━"*72)

    margin = get_margin_trading(code)

    if margin:

        L(f"  最近 {len(margin)} 个交易日数据:"); L(f"  {'日期':<12} {'融资余额(万)':>10} {'融资买入(万)':>10} {'融资偿还(万)':>10} {'融券余额(万)':>10}"); L(f"  {'-'*70}")

        for d in margin[:10]: L(f"  {d['date']:<12} {d['rzye']/1e4:>14.0f} {d['rzmre']/1e4:>14.0f} {d['rzche']/1e4:>14.0f} {d['rqye']/1e4:>14.0f}")

        # 融资买入占比

        _amt = q.get("amount_wan",0)*1e4 if q else 0

        if _amt>0 and margin[0]["rzmre"]>0:

            _rz_ratio = margin[0]["rzmre"]/_amt*100

            if _rz_ratio>20:

                L(f"  🔥 融资买入占当日成交额 {_rz_ratio:.1f}%（>{20}%），杠杆资金疯狂涌入！")

        # 融券余额趋势

        if len(margin)>=3:

            _rq_up = sum(1 for i in range(3) if margin[i]["rqye"]>margin[i+1]["rqye"] if i+1<len(margin))

            if _rq_up>=2:

                L(f"  ⚠️ 融券余额连续上升，做空筹码在暗中积累，警惕高位融券砸盘")

    else: L("  该股无融资融券数据（可能不是两融标的）")



    # ─── 12. 大宗交易 ───

    L("\n"+"━"*72); L("【十二、大宗交易】"); L("━"*72)

    bt = get_block_trade(code); rbt = [d for d in bt if d["date"]>=_30d_str]

    if rbt:

        L(f"  近30天共 {len(rbt)} 笔大宗交易:"); L(f"  {'日期':<12} {'成交价':>6} {'收盘价':>6} {'溢价%':>6} {'成交量':>10} {'买方':<24} {'卖方'}"); L(f"  {'-'*95}")

        for d in rbt: L(f"  {d['date']:<12} {d['price']:>8.2f} {d['close']:>8.2f} {d['premium_pct']:>7.2f}% {d['vol']/1e4 if d['vol'] else 0:>10.0f}万 {d['buyer']:<24} {d['seller']}")

    elif bt: L(f"  近30天内无大宗交易（共 {len(bt)} 笔历史记录，已省略）")

    else: L("  无大宗交易记录")



    # ─── 13. 股东户数 ───

    L("\n"+"━"*72); L("【十三、股东户数变化】"); L("━"*72)

    holders = get_holder_change(code)

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



    # ─── 14. 情绪与催化 ───

    L("\n"+"━"*72); L("【十四、短线情绪与事件催化】"); L("━"*72)

    L("  ➤ 即时新闻: (已关闭全球快讯源，仅依赖巨潮公告)")

    L(f"\n  ➤ 近7日巨潮实质性重大公告:")

    anns = get_strategic_announcements(code, days=7)

    if anns:

        for i,a in enumerate(anns,1):

            fl = " ⚠️" if any(k in a["title"] for k in ["减持","立案","严重异动"]) else ""

            tt = f" [{a['type']}]" if a['type'] else ""

            L(f"  {i}. [{a['date']}]{tt} {a['title']}{fl}")

        rc = sum(1 for a in anns if "减持" in a["title"])

        if rc>0: L(f"    ⚠️ 减持预警：近7日有 {rc} 条减持相关公告，请注意风险。")

    else: L("  近7日暂无触及关键词的重大公告")



    # ─── 15. 综合信号 ───

    L("\n"+"━"*72); L("【十五、综合信号汇总】"); L("━"*72)

    signals = []

    lu2 = q.get("limit_up",0) if q else 0; b1v2 = q.get("bid1_vol",0) if q else 0; np3 = q.get("price",0) if q else 0

    is_lu2 = lu2>0 and abs(np3-lu2)/lu2<0.005

    # 天地板预警

    _lu = q.get("limit_up",0) if q else 0; _ld = q.get("limit_down",0) if q else 0

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

        if q["change_pct"]>_limit_chg and price_today>=q.get("limit_up",0)*0.995: signals.append("🚀 强势涨停，封单密实，短线溢价预期强烈")

        elif q["change_pct"]>_near_limit: signals.append(f"📈 今日涨幅 {q['change_pct']:.1f}%，逼近涨停，短线动能充沛")

    # 封单/成交额比值（弱板预警）

    if q and is_lu2 and b1v2>0:

        _tamt = q.get("amount_wan",0)*1e4

        if _tamt>0:

            _cr = (b1v2*lu2)/_tamt

            if _cr<_seal_ratio_warn: signals.append(f"⚠️ 封单预警：封单资金仅占今日成交额 {_cr*100:.1f}%，弱势烂板，极易炸板悶杀")

    if nb and len(nb)>=2:

        chg = nb[0]["hold_shares"]-nb[-1]["hold_shares"]

        if chg>0: signals.append(f"北向资金近{len(nb)}日净增持，外资看多信号")

    if ff["data"] and len(ff["data"])>=20:

        tmain2 = sum(d["main_net"] for d in ff["data"][-20:])

        if tmain2>0: signals.append(f"近20日主力累计净流入 {tmain2/1e8:.2f}亿，中线资金面偏多")

        else: signals.append(f"近20日主力净流出 {abs(tmain2)/1e8:.2f}亿，中线资金面偏空")

    # 两融两极分化信号

    if margin and len(margin)>=5:

        _rzye_trend = sum(1 for i in range(4) if margin[i]["rzye"]>margin[i+1]["rzye"])

        _rqye_trend = sum(1 for i in range(4) if margin[i]["rqye"]>margin[i+1]["rqye"])

        if _rzye_trend>=3 and _rqye_trend<=1:

            signals.append(f"🔥 两融多头共振：融资余额持续飙升而融券受压，杠杆资金锁仓强推，多头逼空动能强劲")

        if q and abs(q.get("change_pct",0))<3 and _rzye_trend>=3:

            signals.append(f"⚠️ 两融风险预警：股价滞涨而融资余额创新高，散户杠杆接盘筹码松动")

    # 研报过热反向指标

    if rr and len(rr)>=3 and q and abs(q.get("change_pct",0))>5:

        _buy_ratings = sum(1 for r in rr if "买入" in str(r.get("emRatingName","")) or "推荐" in str(r.get("emRatingName","")))

        if _buy_ratings>=3:

            signals.append(f"💡 交易员笔记：短线高位突发{_buy_ratings}篇券商买入/推荐评级，卖方在摇旗呐喊，谨防游资借利好兑现见顶闷杀")

    if dtb["records"]:

        tn = sum(r["net_buy"] for r in dtb["records"])

        _rd_label = '近半年' if _recent_days >= 150 else ('近一季度' if _recent_days >= 80 else f'近{_recent_days}日'); signals.append(f"{_rd_label}龙虎榜净买入合计 {tn:.0f}万元，上榜 {len(dtb['records'])} 次，股性活跃")

        inst2 = dtb["institution"]

        # 拉萨天团散户化提示

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

    # 大宗交易审判

    if rbt:

        for d in rbt[:3]:

            if d["premium_pct"] >= 0:

                signals.append(f"💎 场外抢筹：{d['date']}发生溢价大宗（溢价{d['premium_pct']:.1f}%），买方溢价接盘，主力抢筹意图明显")

                break

        for d in rbt[:3]:

            if d["premium_pct"] < -8:

                signals.append(f"❌ 折价套现：{d['date']}发生折价{abs(d['premium_pct']):.1f}%大宗交易，场外廉价倒手，对二级市场价格有压制")

                break

    mc = miq.get("change_pct") if miq else None; bc2 = biq.get("change_pct") if biq else None

    sc2 = q.get("change_pct",0) if q else None; ic2 = industry_change_pct if industry_rank>0 else None

    if all(v is not None for v in [mc,bc2,sc2,ic2]):

        cd = sc2-ic2

        if cd>2.0 and sc2>0: signals.append(f"🔥 鹤立鸡群模型：个股 {sc2:+.2f}% >> 板块 {ic2:+.2f}% (领先 {cd:.1f}%)，属板块领涨龙头")

        elif abs(sc2-ic2)<1.0 and abs(sc2)>0.5: signals.append(f"📊 随波逐流模型：个股 {sc2:+.2f}% ≈ 板块 {ic2:+.2f}%，属板块普涨型跟风")

    # 异动雷达联动：交易所3日偏离值标准精算

    try:

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

                            tl = 20 if (code.startswith("6") and "ST" not in info.get("name","")) else 30

                            if "ST" in info.get("name",""): tl=12

                            if dv>=tl: signals.append(f"异动雷达：3日偏离值{dv:+.2f}%>={tl}%，触发短期异动")

                            elif dv>=tl*0.9: signals.append(f"异动雷达：3日偏离值{dv:+.2f}%，距红线仅差{tl-dv:.2f}%，卡异动")

    except:

        pass



    L(f"  综合分析条目:")

    if signals:

        for i,s in enumerate(signals,1): L(f"  {i}. {s}")

    else: L("  (数据不足，暂无法生成综合信号)")

    

    # 连板高度追踪

    if q and price_today>0 and q.get("change_pct",0)>=(19.5 if code.startswith(("300","301","688")) else 9.5):

        try:

            _sk, _sr = tdx_get_security_bars(code, count=5)

            _ci = next((i for i,k in enumerate(_sk) if k in ("close","close_price")), -1)

            if _ci>=0:

                _c3 = [_safe_float(rr[_ci]) for rr in _sr[-4:] if len(rr)>_ci]

                if len(_c3)==4 and _c3[0]>0:

                    _3d = (_c3[-1]/_c3[0]-1)*100

                    # 按板块涨停线: 主板10%, 双创20%, ST/ST*5%

                    _lb_pct = 20 if code.startswith(("300","301","688")) else (5 if "ST" in info.get("name","") else 10)

                    _lb2 = _lb_pct * 1.9   # 2连板阈值(含摩擦)

                    _lb3 = _lb_pct * 2.85  # 3连板阈值

                    _lb_t = "3连板" if _lb3<=_3d<_lb3+_lb_pct else ("2连板" if _lb2<=_3d<_lb3 else ("首板" if _lb_pct*0.95<=_3d<_lb2 else f"高标{int(_3d/_lb_pct)}板" if _3d>=_lb3+_lb_pct else ""))

                    if _lb_t: L(f"  📊 连板追踪: 今日涨停，判定为{_lb_t}(3日累计{_3d:.1f}%)")

        except Exception as _e:

            pass  # {_e}

    if q:

        

        L(f"\n  股价: {price_today:.2f}元 | PE(TTM): {q['pe_ttm']:.1f}x  | PB: {q['pb']:.2f}")



        L(f"  市值: {q['mcap_yi']:.1f}亿元")

    else:





        L(f"\n  股价: {price_today:.2f}元")

    # ── V8.2 仓位管理建议（统一评分接口）──

    L("\n"+"━"*72); L("【仓位管理建议】"); L("━"*72)

    from stock_common import ScoreData, calculate_score, save_score_snapshot
    
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
    
    # 资金流向
    if ff["data"] and len(ff["data"]) >= 20:
        score_data.main_net_inflow = sum(d["main_net"] for d in ff["data"][-20:])
        score_data.consecutive_inflow_days = sum(1 for d in ff["data"][-20:] if d["main_net"] > 0)
    
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
    result = calculate_score("sht", score_data)
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

    # 保存评分快照
    try:
        save_score_snapshot("sht", code, info.get('name', ''), _ps, price_today)
    except Exception:
        pass

    output = "\n".join(filter(None, lines))

    with open(output_path,"w",encoding="utf-8") as f: f.write(output)

    return output



async def generate_report_async(session, code, output_path, ind_comp=None, idx_q=None, hsgt=None):

    """V7.5 async 版: 支持 ind_comp/idx_q/hsgt 外部缓存，批量模式下避免重复查询"""

    today_str = date.today().strftime("%Y-%m-%d")

    lines = []

    def L(s=""): lines.append(s)

    L("="*72); L(f"  {code} 个股深度数据报告V8 — {today_str} {datetime.now().strftime('%H:%M:%S')}"); L("="*72); L("")

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

    _is_td = is_trading_day()
    _mkt_status, _mkt_note = get_market_status()

    L("\n"+"━"*72); L(f"【一、个股基本信息】（{_mkt_note}）"); L("━"*72)

    info = get_stock_info(code)

    L(f"  股票名称: {info.get('name','N/A')}")

    L(f"  股票代码: {info.get('code',code)}")

    L(f"  所属板块: {info.get('industry','N/A')}")

    L(f"  总股本:   {info.get('total_shares',0)/1e8:.2f}亿股")

    L(f"  流通股本: {info.get('float_shares',0)/1e8:.2f}亿股")

    ld = info.get("list_date","")

    if ld and len(ld)>=8: ldf = f"{ld[:4]}-{ld[4:6]}-{ld[6:8]}"

    else: ldf = ld

    L(f"  上市日期: {ldf}")

    L("\n"+"━"*72); L("【二、实时行情、估值与短线趋势】"); L("━"*72)

    q = get_tencent_quote(code); price_today = q.get("price",0) if q else 0

    if q:

        L(f"  当前价:   {price_today:.2f}元")

        L(f"  涨跌额:   {q['change_amt']:.2f}元  涨跌幅: {q['change_pct']:.2f}%")

        L(f"  今开:     {q['open']:.2f}元  昨收: {q['last_close']:.2f}元")

        L(f"  最高:     {q['high']:.2f}元  最低: {q['low']:.2f}元")

        L(f"  成交额:   {q['amount_wan']/10000:.2f}亿元  换手率: {q['turnover_pct']:.2f}%")

        L(f"  量比:     {q['vol_ratio']:.2f}  振幅: {q['amplitude_pct']:.2f}%")

        L(f"  总市值:   {q['mcap_yi']:.2f}亿元  流通市值: {q['float_mcap_yi']:.2f}亿元")

        _pe_t = q.get('pe_ttm',0); _pe_s = q.get('pe_static',0)

        _pe_s_str = f"{_pe_s:.2f}" if _pe_t > 0 and _pe_s > 0 else "N/A（亏损）"

        L(f"  PE(TTM):  {_pe_t:.2f}  PE(静): {_pe_s_str}  PB: {q.get('pb',0):.2f}")

        L(f"  涨停价:   {q['limit_up']:.2f}元  跌停价: {q['limit_down_price']:.2f}元")

    else: L("  实时行情获取失败")

    ma_data = get_baidu_kline_with_ma(code)

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

        for ic,inm in all_idx:

            _iq = _get_index_quote(ic)

            if _iq:

                idx_q[ic] = _iq

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

    ff = get_fund_flow_120d(code)

    rf = get_fund_flow_realtime(code)

    if rf and rf.get("data") and len(rf["data"]) > 0:

        _fd = rf["data"]

        L(f"  💰 今日主力净流入: {_fd[0]:.0f}万元 ({_fd[0]/1e4:.2f}亿)")

    else:

        L(f"\n  [资金流向] 今日主力净流入(实时): 暂无数据")

    L("\n"+"━"*72); L("【三、机构一致预期与估值】"); L("━"*72)

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

    L("\n"+"━"*72); L("【四、个股研报（东财）】"); L("━"*72)

    reports = get_reports(code, 5)

    rr = [r for r in reports if str(r.get("publishDate",""))[:10]>=_60d_str]

    if rr:

        L(f"  最近60天共 {len(rr)} 篇研报，显示前10篇:")

        L(f"  {'日期':<12} {'机构':<16} {'评级':<10} {'标题'}"); L(f"  {'-'*70}")

        for r in rr[:10]:

            L(f"  {str(r.get('publishDate',''))[:10]:<12} {r.get('orgSName',''):<16} {str(r.get('emRatingName','')):<10} {r.get('title','')[:50]}")

    elif reports: L(f"  近60天内无新研报（共 {len(reports)} 篇历史研报，已省略）")

    else: L("  无研报数据（该股可能无机构覆盖）")

    L("\n"+"━"*72); L("【五、概念板块、热点归因与板块共振】"); L("━"*72)

    blocks = get_concept_blocks(code)

    if blocks["industry"]: L(f"  所属板块: {', '.join(b['name'] for b in blocks['industry'])}")

    if ind_comp is None:

        ind_comp = get_industry_comparison()

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

    time.sleep(0.5)

    peer_data = get_industry_peers(code, 3, info=info)

    if peer_data.get("my_rank",0)>0 and peer_data.get("industry_count",0)>0:

        L(f"  ➤ [所属板块排名] {peer_data.get('industry',stock_ind)}: 按总市值该股排名第 {peer_data['my_rank']}/{peer_data['industry_count']} 位")

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

            _sr = get_stock_sector_rank(code, info=info, q=q)

            if _sr: _rank_parts.append(f"本股今日{_sr['change_pct']:+.2f}%，板块内排名第{_sr['rank']}/{_sr['total']}名")

        except Exception:

            pass

        if _rank_parts: L(f"     {'  '.join(_rank_parts)}")

    div = get_dividend_history(code)

    if div:

        ld2 = div[0]; ye = f"{(ld2['bonus_rmb']/price_today)*100:.2f}%" if price_today>0 else "N/A"

        L(f"  最近分红: {ld2['date']} 每股{ld2['bonus_rmb']:.4f}元 (约{ye}股息率)")

    if blocks["concept"]:

        L(f"\n  概念板块: {', '.join(b['name'] for b in blocks['concept'])}")

    L(f"\n  ➤ 同花顺热点题材归因 (基于当日强势股/涨停榜):")

    if datetime.now().hour*100+datetime.now().minute<1600:

        L("  ⚠️ 同花顺热点池需16:00后更新，当前为盘中时段数据可能为空")

    ths_hot = await get_ths_hot_reason_async(session, code, today_str)

    if ths_hot: L(f"  [强势归因] {ths_hot.get('reason','')}")

    else: L("  (该股今日未进入同花顺强势股列表，暂无热点题材归因数据)")

    L("\n"+"━"*72); L("【六、同业龙头横向对比】"); L("━"*72)

    if peer_data["peers"]:

        if "note" in peer_data["peers"][0]: L(f"  ⚠️ {peer_data['peers'][0]['note']}")

        else:

            _my_mcap_show = peer_data['my_mcap'] if peer_data['my_mcap'] > 0 else q.get('mcap_yi', 0)

            L(f"  所属板块: {peer_data['industry']}"); L(f"  本股市值: {_my_mcap_show:.1f}亿元")

            L(f"  同业龙头对比:"); L(f"  {'代码':<8} {'名称':<12} {'股价':>8} {'涨跌幅%':>8} {'市值(亿)':>10} {'PE':>8} {'换手率%':>8}"); L(f"  {'-'*70}")

            _my_mcap = peer_data['my_mcap'] if peer_data['my_mcap'] > 0 else q.get('mcap_yi', 0)

            L(f"  {code:<8} {info.get('name','N/A'):<12} {price_today:>8.2f} {q.get('change_pct',0):>7.2f}% {_my_mcap:>9.1f} {q.get('pe_ttm',0):>7.1f} {q.get('turnover_pct',0):>7.2f}% ← 本股")

            for p in peer_data["peers"]: L(f"  {p['code']:<8} {p['name']:<12} {p['price']:>8.2f} {p['change_pct']:>7.2f}% {p['mcap_yi']:>9.1f} {p['pe']:>7.1f} {p['turnover']:>7.2f}%")

    else: L(f"  无法获取同业数据（板块: {peer_data.get('industry','未知')}）")

    L("\n"+"━"*72); L("【七、资金走向分析】"); L("━"*72)

    if ff["data"]:

        L("\n  ➤ 60日资金流监控 (最近 10 日):")

        _recent = ff["data"][-10:]

        L(f"  {'日期':<12} {'主力净流入(亿)':>12} {'超大单(亿)':>10} {'大单(亿)':>10} {'中单(亿)':>10} {'小单(亿)':>10}")

        L(f"  {'-'*70}")

        for d in reversed(_recent):

            if d['main_net'] == 0 and d['super_net'] == 0 and d['large_net'] == 0:

                continue

            L(f"  {d['date']:<12} {d['main_net']/1e4:>+12.0f} {d['super_net']/1e4:>+10.0f} {d['large_net']/1e4:>+10.0f} {d['mid_net']/1e4:>+10.0f} {d['small_net']/1e4:>+10.0f}")

        r20 = ff["data"][-20:]; tmain = sum(d["main_net"] for d in r20); tdays = sum(1 for d in r20 if d["main_net"]>0)

        L(f"\n  近20日统计:\n    主力累计净流入: {tmain/1e8:.2f}亿元\n    主力净流入天数: {tdays}/20天")

        L(f"  信号: {'主力资金近期净流入 → 偏多' if tmain>0 else '主力资金近期净流出 → 偏空'}")

    else: L(f"  (资金流数据获取失败)")

    L("\n"+"━"*72); L("【八、北向资金持仓动态】"); L("━"*72)

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

    L("\n"+"━"*72); L("【九、龙虎榜席位】"); L("━"*72)

    if datetime.now().hour*100+datetime.now().minute<1630:

        L("  ⚠️ 龙虎榜数据约16:30后更新，当前时段显示的是最近一期已发布数据")

    dtb = await get_dragon_tiger_board_async(session, code, today_str)

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

            L(f"\n  最近买入席位 TOP5:"); L(f"  {'营业部名称':<30} {'买入(万)':>9} {'卖出(万)':>9} {'净额(万)':>9}"); L(f"  {'-'*70}")

            for s in seats["buy"]: L(f"  {_tag(s['name'])} {s['name']:<28} {s['buy_amt']:>12.1f} {s['sell_amt']:>12.1f} {s['net']:>12.1f}")

        if seats["sell"]:

            L(f"\n  最近卖出席位 TOP5:"); L(f"  {'营业部名称':<30} {'买入(万)':>9} {'卖出(万)':>9} {'净额(万)':>9}"); L(f"  {'-'*70}")

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

        L("\n  ━━ 游资活跃度诊断 ━━")

        if _all_depts:

            _buy_tags = [x[0] for x in _all_depts if x[2] == "buy"]

            _sell_tags = [x[0] for x in _all_depts if x[2] == "sell"]

            _unique_buy = list(dict.fromkeys(_buy_tags))

            _unique_sell = list(dict.fromkeys(_sell_tags))

            if _unique_buy:

                L(f"  🟢 著名游资买入: {'、'.join(_unique_buy)}")

            if _unique_sell:

                L(f"  🔴 著名游资卖出: {'、'.join(_unique_sell)}")

            L(f"  📊 席位明细:")

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

    else: L(f"  近{_recent_days}日无龙虎榜记录（白马蓝筹或近期未触发异动标准的个股，无龙虎榜属正常现象）")

    L("\n"+"━"*72); L("【十、限售解禁日历】"); L("━"*72)

    lockup = await get_lockup_expiry_async(session, code, today_str, days=90, include_history=True)

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

    L("\n"+"━"*72); L("【十一、融资融券（两融数据）】"); L("━"*72)

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

            _rq_up = sum(1 for i in range(3) if margin[i]["rqye"]>margin[i+1]["rqye"] if i+1<len(margin))

            if _rq_up>=2:

                L(f"  ⚠️ 融券余额连续上升，做空筹码在暗中积累，警惕高位融券砸盘")

    else: L("  该股无融资融券数据（可能不是两融标的）")

    L("\n"+"━"*72); L("【十二、大宗交易】"); L("━"*72)

    bt = await get_block_trade_async(session, code); rbt = [d for d in bt if d["date"]>=_30d_str]

    if rbt:

        L(f"  近30天共 {len(rbt)} 笔大宗交易:"); L(f"  {'日期':<12} {'成交价':>6} {'收盘价':>6} {'溢价%':>6} {'成交量':>10} {'买方':<24} {'卖方'}"); L(f"  {'-'*95}")

        for d in rbt: L(f"  {d['date']:<12} {d['price']:>8.2f} {d['close']:>8.2f} {d['premium_pct']:>7.2f}% {d['vol']/1e4 if d['vol'] else 0:>10.0f}万 {d['buyer']:<24} {d['seller']}")

    elif bt: L(f"  近30天内无大宗交易（共 {len(bt)} 笔历史记录，已省略）")

    else: L("  无大宗交易记录")

    L("\n"+"━"*72); L("【十三、股东户数变化】"); L("━"*72)

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

    L("\n"+"━"*72); L("【十四、短线情绪与事件催化】"); L("━"*72)

    L("  ➤ 即时新闻: (已关闭全球快讯源，仅依赖巨潮公告)")

    L(f"\n  ➤ 近7日巨潮实质性重大公告:")

    anns = await get_strategic_announcements_async(session, code, days=7)

    if anns:

        for i,a in enumerate(anns,1):

            fl = " ⚠️" if any(k in a["title"] for k in ["减持","立案","严重异动"]) else ""

            tt = f" [{a['type']}]" if a['type'] else ""

            L(f"  {i}. [{a['date']}]{tt} {a['title']}{fl}")

        rc = sum(1 for a in anns if "减持" in a["title"])

        if rc>0: L(f"    ⚠️ 减持预警：近7日有 {rc} 条减持相关公告，请注意风险。")

    else: L("  近7日暂无触及关键词的重大公告")

    L("\n"+"━"*72); L("【十五、综合信号汇总】"); L("━"*72)

    signals = []

    lu2 = q.get("limit_up",0) if q else 0; b1v2 = q.get("bid1_vol",0) if q else 0; np3 = q.get("price",0) if q else 0

    is_lu2 = lu2>0 and abs(np3-lu2)/lu2<0.005

    _lu = q.get("limit_up",0) if q else 0; _ld = q.get("limit_down",0) if q else 0

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

        if q["change_pct"]>_limit_chg and price_today>=q.get("limit_up",0)*0.995: signals.append("🚀 强势涨停，封单密实，短线溢价预期强烈")

        elif q["change_pct"]>_near_limit: signals.append(f"📈 今日涨幅 {q['change_pct']:.1f}%，逼近涨停，短线动能充沛")

    if q and is_lu2 and b1v2>0:

        _tamt = q.get("amount_wan",0)*1e4

        if _tamt>0:

            _cr = (b1v2*lu2)/_tamt

            if _cr<_seal_ratio_warn: signals.append(f"⚠️ 封单预警：封单资金仅占今日成交额 {_cr*100:.1f}%，弱势烂板，极易炸板悶杀")

    if nb and len(nb)>=2:

        chg = nb[0]["hold_shares"]-nb[-1]["hold_shares"]

        if chg>0: signals.append(f"北向资金近{len(nb)}日净增持，外资看多信号")

    if ff["data"] and len(ff["data"])>=20:

        tmain2 = sum(d["main_net"] for d in ff["data"][-20:])

        if tmain2>0: signals.append(f"近20日主力累计净流入 {tmain2/1e8:.2f}亿，中线资金面偏多")

        else: signals.append(f"近20日主力净流出 {abs(tmain2)/1e8:.2f}亿，中线资金面偏空")

    if margin and len(margin)>=5:

        _rzye_trend = sum(1 for i in range(4) if margin[i]["rzye"]>margin[i+1]["rzye"])

        _rqye_trend = sum(1 for i in range(4) if margin[i]["rqye"]>margin[i+1]["rqye"])

        if _rzye_trend>=3 and _rqye_trend<=1:

            signals.append(f"🔥 两融多头共振：融资余额持续飙升而融券受压，杠杆资金锁仓强推，多头逼空动能强劲")

        if q and abs(q.get("change_pct",0))<3 and _rzye_trend>=3:

            signals.append(f"⚠️ 两融风险预警：股价滞涨而融资余额创新高，散户杠杆接盘筹码松动")

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

                            tl = 20 if (code.startswith("6") and "ST" not in info.get("name","")) else 30

                            if "ST" in info.get("name",""): tl=12

                            if dv>=tl: signals.append(f"异动雷达：3日偏离值{dv:+.2f}%>={tl}%，触发短期异动")

                            elif dv>=tl*0.9: signals.append(f"异动雷达：3日偏离值{dv:+.2f}%，距红线仅差{tl-dv:.2f}%，卡异动")

    except:

        pass

    L(f"  综合分析条目:")

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

                    _lb_pct = 20 if code.startswith(("300","301","688")) else (5 if "ST" in info.get("name","") else 10)

                    _lb2 = _lb_pct * 1.9

                    _lb3 = _lb_pct * 2.85

                    _lb_t = "3连板" if _lb3<=_3d<_lb3+_lb_pct else ("2连板" if _lb2<=_3d<_lb3 else ("首板" if _lb_pct*0.95<=_3d<_lb2 else f"高标{int(_3d/_lb_pct)}板" if _3d>=_lb3+_lb_pct else ""))

                    if _lb_t: L(f"  📊 连板追踪: 今日涨停，判定为{_lb_t}(3日累计{_3d:.1f}%)")

        except Exception as _e:

            pass

    if q:

        L(f"\n  股价: {price_today:.2f}元 | PE(TTM): {q['pe_ttm']:.1f}x  | PB: {q['pb']:.2f}")

        L(f"  市值: {q['mcap_yi']:.1f}亿元")

    else:

        L(f"\n  股价: {price_today:.2f}元")

    L("\n"+"━"*72); L("【仓位管理建议】"); L("━"*72)

    # V8.2: 使用统一评分接口
    from stock_common import ScoreData, calculate_score, save_score_snapshot
    
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
    
    # 资金流向
    if ff["data"] and len(ff["data"]) >= 20:
        score_data.main_net_inflow = sum(d["main_net"] for d in ff["data"][-20:])
        score_data.consecutive_inflow_days = sum(1 for d in ff["data"][-20:] if d["main_net"] > 0)
    
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
    result = calculate_score("sht", score_data)
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

    # 保存评分快照
    try:
        save_score_snapshot("sht", code, info.get('name', ''), _ps, price_today)
    except Exception:
        pass

    output = "\n".join(filter(None, lines))

    with open(output_path,"w",encoding="utf-8") as f: f.write(output)

    return output



# ═══════════════════════════════════════════

# 入口

# ═══════════════════════════════════════════



if __name__ == "__main__":

    args = parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))

    sn = os.path.basename(__file__)

    time_str = datetime.now().strftime("%Y%m%d_%H%M")

    try:

        report_type = sn.split("_")[1]

    except Exception:

        report_type = "sht"



    # ─── GD 认证（可跳过）────────────────────────────────────────
    drive, gd_proxy_set, gd_parent_folder_id, skip_upload = None, False, None, False
    if not args.no_upload:
        drive, gd_proxy_set, gd_parent_folder_id, skip_upload = init_gd(base_dir)



    # ─── 批量生成（缓存行业排名等）────────────────────────────────

    os.makedirs(args.output, exist_ok=True)

    _results = []

    _cached_ind_comp = get_industry_comparison()

    _cached_idx_q = {}

    for ic in ("sh000001", "sz399106", "sz399102", "sh000688"):

        _iq = _get_index_quote(ic)

        if _iq:

            _cached_idx_q[ic] = _iq

    _cached_hsgt = get_hsgt_macro_flow()



    # ─── Step 1: async 并行生成所有报告 ─────────────────────────

    async def _process_one(_session, code, time_str, _ind_comp, _idx_q, _hsgt_async):

        result_path = os.path.join(args.output, f"{code}_{report_type}_{time_str}.txt")

        try:

            await generate_report_async(_session, code, result_path,

                                          ind_comp=_ind_comp, idx_q=_idx_q, hsgt=_hsgt_async)

            print(f"  ✅ 已保存: {result_path}", flush=True)

            return {"code": code, "status": "成功", "error": ""}

        except Exception as e:

            print(f"❌ {code} 数据生成失败: {e}", flush=True)

            return {"code": code, "status": "数据失败", "error": str(e)}



    async def _main_async():

        _codes = clean_codes(args.codes, verbose=True)

        if not _codes:

            print("  ❌ 没有有效的股票代码")

            return []

        for code in _codes:
            print(f"  📋 加入队列: {code}", flush=True)



        _session = await create_async_session()

        try:

            _cached_hsgt_async = await get_hsgt_macro_flow_async(_session)



            sem = asyncio.Semaphore(3)

            async def _limited(code):

                async with sem:

                    return await _process_one(_session, code, time_str,

                                              _cached_ind_comp, _cached_idx_q, _cached_hsgt_async)



            tasks = [_limited(code) for code in _codes]

            results = await asyncio.gather(*tasks)

            return results

        finally:

            await _session.close()



    _results = asyncio.run(_main_async())



    # ─── Step 2: 串行上传至 Google Drive（GD API 有速率限制）────
    for _r in _results:
        if _r["status"] == "成功" and not skip_upload and drive and gd_parent_folder_id:
            code = _r["code"]
            result_path = os.path.join(args.output, f"{code}_{report_type}_{time_str}.txt")
            try:
                q_name = tdx_get_quote_full(code).get("name", "")
                if not upload_stock_report_by_code(drive, gd_parent_folder_id, code, q_name, result_path):
                    _r["status"] = "GD上传失败"
                    _r["error"] = _r["error"] or "上传返回 False"
            except Exception as gd_e:
                print(f"  ⚠️ GD 上传异常: {gd_e}", flush=True)
                _r["status"] = "GD上传异常"
                _r["error"] = str(gd_e)



    # ─── 汇总报告 ────────────────────────────────────────────────

    cleanup_gd_proxy(gd_proxy_set)

    holder_cache_flush()

    cleanup_tdx()



    total = len(_results)

    ok = [r for r in _results if r["status"] == "成功"]

    fd = [r for r in _results if r["status"] == "数据失败"]

    fg = [r for r in _results if r["status"] in ("GD上传失败", "GD上传异常", "GD文件夹失败", "GD未连接")]

    print(f"\n{'=' * 60}")

    print(f"  批量执行完成 — 共处理 {total} 只股票")

    print(f"{'=' * 60}")

    print(f"  ✅ 全部成功: {len(ok)}  |  ❌ 数据失败: {len(fd)}  |  ⚠️ GD上传失败: {len(fg)}")

    if fd:

        print(f"\n  ❌ 数据获取失败的股票:")

        for r in fd:

            print(f"    {r['code']} — {r['error'][:80]}")

    if fg:

        print(f"\n  ⚠️ GD上传失败的股票:")

        for r in fg:

            print(f"    {r['code']} — {r['error'][:80]}")

