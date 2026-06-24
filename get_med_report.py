import argparse, requests, math, time, pandas as pd
import asyncio
from datetime import date, datetime, timedelta
import os, sys, re

from gd_uploader import init_gd, upload_stock_report_by_code, cleanup_gd_proxy
from tdx_client import (tdx_get_security_bars, tdx_get_quote_full,
                         tdx_get_quotes_batch, tdx_get_index_bars,
                         tdx_get_fund_flow, tdx_get_history_fund_flow,
                         tdx_get_eps_from_reports,
                         tdx_get_belong_boards, tdx_get_board_list,
                         tdx_get_board_members, tdx_get_board_by_name,
                         tdx_get_latest_announcements, tdx_get_dividend_history, cleanup_tdx)

from stock_common import (clean_codes, _safe_float, _request_with_retry, _quick_request, UA,
                           _market_code, eastmoney_datacenter, _em_filter,
                           holder_change, holder_cache_flush,
                           get_strategic_announcements, get_holder_structure,
                           _load_strategy_config, get_dragon_tiger_board,
                           create_async_session, eastmoney_datacenter_async,
                           _em_filter_async, _async_request_with_retry,
                           _async_quick_request, get_dragon_tiger_board_async,
                           holder_change_async, get_strategic_announcements_async,
                           parse_args, get_tencent_quote, baidu_kline_full,
                           get_reports, get_eps_forecast, get_northbound_hold,
                           get_margin_trading, get_block_trade,
                           get_dividend_history, get_industry_comparison,
                           print_batch_summary,
                           get_stock_info, get_sina_financial_report,
                           get_sina_balance_sheet, get_hsgt_macro_flow,
                           get_lockup_expiry, get_gross_margin_and_roe,
                           get_eps_forecast_async, get_reports_async,
                           get_northbound_hold_async, get_margin_trading_async,
                           get_block_trade_async, get_lockup_expiry_async,
                           get_gross_margin_and_roe_async, get_industry_peers,
                           get_sina_financial_report_async, get_sina_balance_sheet_async,
                           get_hsgt_macro_flow_async,
                           is_trading_day, get_market_status,
                           calculate_multi_school_scores)

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 模块级策略配置（加载一次，全局共享）
_sc = _load_strategy_config()
_mkt_cfg = _sc.get("market", {})
_peers_low = _mkt_cfg.get("peers_mcap_low", 0.3)
_peers_high = _mkt_cfg.get("peers_mcap_high", 3.0)


# ==================== 核心数据抓取模块 ====================

def get_cninfo_announcements(code, page_size=20):
    """V4: 近7日重大公告 — TDX F10 优先 + 巨潮 HTTP 兜底"""
    # 1. TDX F10 公告摘要（TCP 直连，永不封IP）
    tdx_anns = tdx_get_latest_announcements(code, days=7)
    if tdx_anns:
        keywords = ["回购", "增持", "减持", "年报", "分红", "派息", "激励", "员工持股", "战略合作",
                     "业绩预告", "中标", "立案", "合同", "收购", "股权转让", "异动", "严重异动"]
        return [{"title": a["title"], "date": a["date"], "type": a.get("category", "")}
                for a in tdx_anns if any(k in a.get("title", "") for k in keywords)]
    # 2. 兜底: 巨潮 HTTP
    try:
        td_str = date.today().strftime("%Y-%m-%d")
        sd_str = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        oid = "gssh0" + code if code.startswith("6") else ("gsbj0" + code if code.startswith(("8","4")) else "gssz0" + code)
        payload = {
            "orgId": oid, "stock": f"{code},{oid}",
            "tabName": "fulltext", "pageSize": str(page_size), "pageNum": "1",
            "column": "", "category": "", "plate": "",
            "seDate": f"{sd_str}~{td_str}",
            "searchkey": "", "secid": "", "sortName": "", "sortType": "",
            "isHLtitle": "true",
        }
        headers = {"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded",
                   "Referer": "https://www.cninfo.com.cn/new/disclosure"}
        r = _quick_request("https://www.cninfo.com.cn/new/hisAnnouncement/query",
                                data=payload, headers=headers, timeout=15, method="POST")
        if r is None: return []
        d = r.json()
        anns = d.get("announcements") or []
        if not anns:
            # orgId 失败 → searchkey 兜底
            payload2 = {"orgId":"","stock":"","tabName":"fulltext","pageSize":str(page_size),"pageNum":"1","column":"","category":"","plate":"","seDate":f"{sd_str}~{td_str}","searchkey":str(code),"secid":"","sortName":"","sortType":"","isHLtitle":"true"}
            r2 = _quick_request("https://www.cninfo.com.cn/new/hisAnnouncement/query", data=payload2, headers=headers, timeout=15, method="POST")
            if r2 is not None:
                d2 = r2.json()
                anns2 = d2.get("announcements") or []
                if anns2:
                    anns = anns2
        keywords = ["回购", "增持", "减持", "年报", "分红", "派息", "激励", "员工持股", "战略合作",
                     "业绩预告", "中标", "立案", "合同", "收购", "股权转让", "异动", "严重异动"]
        rows = []
        for item in anns:
            _sc = str(item.get("secCode", ""))
            if _sc and _sc != str(code):
                continue
            title = re.sub(r'<[^>]+>', '', item.get("announcementTitle", ""))
            if not any(k in title for k in keywords):
                continue
            ts = item.get("announcementTime", 0)
            if isinstance(ts, int) and ts > 1000000000000:
                date_str = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
            else:
                date_str = str(ts)[:10]
            rows.append({"title": title, "type": item.get("announcementTypeName", "") or "", "date": date_str})
        return rows
    except Exception:
        return []






def _get_eps_from_em_reports(code):
    try:
        reports = get_reports(code, max_pages=1)
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
    except Exception:
        return None



def get_fund_flow_120d(code):
    """V7.5: 60日资金流 → TDX TCP（同花顺 fallback 已删除）"""
    tdx_data = tdx_get_history_fund_flow(code, 60)
    if tdx_data:
        return {"data": tdx_data, "error": "", "source": "tdx"}
    return {"data": [], "error": "资金流数据获取失败"}

# V7.5: get_dragon_tiger_board 由 stock_common 统一提供

def get_holder_change(code):
    """V7.5: 股东户数变化 → 东财优先 + 内存缓存"""
    return holder_change(code)


async def get_holder_change_async(session, code):
    """async 版: 股东户数变化"""
    return await holder_change_async(session, code)


def get_stock_sector_rank(code, info=None):
    """V4: 板块内排名 — TDX 优先，不可用时回退 board_by_name"""
    boards = tdx_get_belong_boards(code)
    industry_boards = boards.get("industry", []) if boards else []
    if industry_boards:
        primary = industry_boards[0]
        members = tdx_get_board_members(primary["code"])
        if members:
            members_by_chg = sorted(members, key=lambda x: x.get("change_pct", 0), reverse=True)
            for i, m in enumerate(members_by_chg, 1):
                if m["code"] == code:
                    q = tdx_get_quote_full(code)
                    my_chg = q.get("change_pct", m["change_pct"])
                    return {"rank": i, "total": len(members), "change_pct": my_chg}
    ind_name = (industry_boards[0].get("name","") if industry_boards else "") or (info.get("industry","") if info else "")
    if ind_name:
        st = tdx_get_board_by_name(ind_name, board_type=0)
        if st:
            st_sorted = sorted(st, key=lambda x: x["change_pct"], reverse=True)
            for i, s in enumerate(st_sorted, 1):
                if s["code"] == code:
                    q = tdx_get_quote_full(code)
                    my_chg = q.get("change_pct", s["change_pct"])
                    return {"rank": i, "total": len(st), "change_pct": my_chg}
    return None


# ==================== 报告生成引擎 ====================

def generate_report(code, output_path, ind_comp=None, hsgt=None):
    """V4: 支持 ind_comp/hsgt 外部缓存，批量模式下避免重复查询"""
    today_str = date.today().strftime("%Y-%m-%d")
    lines = []
    def L(s=""): lines.append(s)

    L("=" * 72)
    L(f"  {code} 中线深度投研报告V8.5.1 — {today_str} {datetime.now().strftime('%H:%M:%S')}")
    L("=" * 72)
    L("")
    # 加载策略阈值配置
    _sc = _load_strategy_config()
    _val = _sc.get("valuation", {})
    _fund = _sc.get("fundamental", {})
    _pe_mid = _val.get("pe_mid", 30.0)
    _peg_good = _val.get("peg_good", 0.8)
    _peg_rational = _val.get("peg_rational", 1.5)
    _debt_ratio_warn = _fund.get("debt_ratio_warn", 60.0)
    _ar_ratio_warn = _fund.get("ar_ratio_warn", 20.0)
    _cash_debt_ratio = _fund.get("cash_debt_ratio_warn", 1.0)
    _gw_ratio = _fund.get("gw_ratio_warn", 30.0)
    _ar_rev_ratio = _fund.get("ar_rev_warn_ratio", 30.0)

    # 时段标注
    _now = datetime.now()
    _is_td = is_trading_day(_now.date())
    _mkt_status, _mkt_note = get_market_status(_now)

    # 生成详细提示
    if _mkt_status == "closed":
        note = f"（休市日，数据为最近交易日快照）"
    elif _mkt_status == "pre_market":
        note = "⚠️ 当前为盘前时段，行情数据/北向资金为上交易日值，龙虎榜/融资融券为最近一期已发布数据"
    elif _mkt_status in ("morning", "afternoon"):
        note = ("⚠️ 当前为盘中时段，行情数据实时跳动，龙虎榜/融资融券/大宗交易需收盘后更新，"
                "其余基本面数据（财报/ROE/股东/分红等）为最新报告期数据不受影响")
    elif _mkt_status == "lunch":
        note = "⚠️ 当前为午休时段（11:30-13:00），行情暂停但基本面数据正常"
    elif _mkt_status == "post_market":
        note = "⚠️ 当前为盘后结算时段，部分数据（龙虎榜约16:30后）尚在更新中"
    else:
        note = ""
    if note:
        print(f"\033[93m{note}\033[0m", flush=True)
        L(f"  {note}")
        L("")

    # ─── 0. 宏观资金风向标 ───
    L("\n【一、宏观资金面背景】")
    L("─" * 72)
    if hsgt is None:
        hsgt = get_hsgt_macro_flow()
    if hsgt:
        signal = "偏多" if hsgt['total'] > 0 else "偏空"
        L(f"  今日北向资金总净流入: {hsgt['total']:.2f} 亿元 (沪股通 {hsgt['hgt']:.2f}亿 | 深股通 {hsgt['sgt']:.2f}亿)")
        L(f"  大盘外资情绪: {signal} （中线仓位参考点）")
    else:
        L("  (北向宏观资金流向获取失败)")

    # ─── 1. 基本信息与实时估值 ───
    L("\n【二、个股基本信息与估值锚点】")
    L("─" * 72)
    info = get_stock_info(code)
    q = get_tencent_quote(code)
    price_today = q.get("price", 0) if q else 0
    
    L(f"  股票名称: {info.get('name', 'N/A')} ({info.get('code', code)})")
    L(f"  所属板块: {info.get('industry', 'N/A')}")
    list_date_raw = info.get("list_date", "")
    if list_date_raw and len(list_date_raw) >= 8:
        list_date_fmt = f"{list_date_raw[:4]}-{list_date_raw[4:6]}-{list_date_raw[6:8]}"
    else:
        list_date_fmt = list_date_raw
    L(f"  上市日期: {list_date_fmt}")
    
    if ind_comp is None:
        ind_comp = get_industry_comparison()
    stock_ind = info.get('industry', '')
    peer_data = {"industry": "", "my_mcap": 0, "my_rank": 0, "industry_count": 0, "peers": []}
    fin_metrics = {}
    if stock_ind and ind_comp:
        _ind_all = ind_comp.get("all", ind_comp)  # 兼容新旧格式
        for row in _ind_all:
            if stock_ind in row["name"] or row["name"] in stock_ind:
                L(f"  板块排名: 当日全市场第 {row['rank']} 名 (涨跌幅 {row['change_pct']}%)")
                # V4 fix: TDX BoardInfo 无涨跌家数，从 peer_data.all_members 全量统计
                _all_m = peer_data.get("all_members", [])
                if _all_m:
                    _up = sum(1 for m in _all_m if m.get("change_pct", 0) > 0)
                    _down = sum(1 for m in _all_m if m.get("change_pct", 0) < 0)
                    L(f"  板块涨跌: 上涨 {_up} 家 / 下跌 {_down} 家")
                # 个股在板块内的涨跌幅排名
                try:
                    _rank_info = get_stock_sector_rank(code, info=info)
                    if _rank_info:
                        L(f"  本股今日{_rank_info['change_pct']:+.2f}%，板块内排名第{_rank_info['rank']}/{_rank_info['total']}名")
                except Exception:
                    pass
                if row['rank'] <= 10:
                    L(f"  🔥 板块共振: 该板块处于全市场 TOP 10 热门赛道，板块共振溢价效应显著")
                if row.get("leader"):
                    leader_code = row["leader"]
                    leader_name = ""
                    try:
                        li = get_stock_info(leader_code)
                        leader_name = li.get("name", "")
                    except Exception:
                        pass
                    if leader_name:
                        L(f"  板块龙头: {leader_code} {leader_name}")
                    else:
                        L(f"  板块龙头: {leader_code}")
                break

    # 个股在行业内的市值排名
    time.sleep(0.5)
    peer_data = get_industry_peers(code, 3, info=info)
    if peer_data.get("my_rank", 0) > 0 and peer_data.get("industry_count", 0) > 0:
        L(f"  板块内排名: 按总市值排序, 该股排名第 {peer_data['my_rank']}/{peer_data['industry_count']} 位")
                
    L(f"  总市值:   {q.get('mcap_yi', 0):.2f}亿元 (流通股本 {info.get('float_shares', 0)/1e8:.2f}亿股)")
    L(f"  当前价:   {price_today:.2f}元  (今日涨跌: {q.get('change_pct', 0):.2f}%)")
    _pe_ttm = q.get('pe_ttm', 0); _pe_static = q.get('pe_static', 0)
    _pe_s = f"{_pe_static:.2f}x" if _pe_ttm > 0 and _pe_static > 0 else "N/A（亏损）"
    L(f"  动态市盈率 PE(TTM): {_pe_ttm:.2f}x | 静态PE: {_pe_s} | 市净率 PB: {q.get('pb', 0):.2f}")

    # ─── 2. 财务业绩兑现追踪 ───
    L("\n【三、历史财务业绩兑现追踪 (近5季度)】")
    L("─" * 72)
    financials = get_sina_financial_report(code)
    if financials:
        L(f"  {'报告期':<12} {'营业总收入':>11} {'净利润':>13} {'净利率':>8}")
        L(f"  {'-'*60}")
        for item in financials:
            date_val = item.get("报告日", "")
            rev = item.get("营业总收入", "0")
            profit = item.get("净利润", "0")
            
            # 格式化金额为“亿元”
            try:
                rv = float(rev) if rev and rev != "0" else 0
                pf = float(profit) if profit and profit != "0" else 0
                rev_yi = f"{rv/1e8:.2f} 亿" if rv else "N/A"
                profit_yi = f"{pf/1e8:.2f} 亿" if pf else "N/A"
                npm = f"{pf/rv*100:.2f}%" if rv > 0 else "N/A"
            except:
                rev_yi, profit_yi, npm = "N/A", "N/A", "N/A"
                
            L(f"  {date_val:<12} {rev_yi:>15} {profit_yi:>15} {npm:>8}")
        L("\n  💡 中线逻辑核实：观察收入与净利润是否保持同步增长。")
    else:
        L("  (新浪财报数据获取失败或该股暂无相关数据)")

    # ─── 4. 资产负债表财务健康度（应收账款/存货/商誉排雷） ───
    L("\n【四、资产负债表财务健康度（排雷）】")
    L("─" * 72)
    bs_data = get_sina_balance_sheet(code)
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
            try: return float(v) / 1e8
            except: return 0.0

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
            L(f"  ⚠️ 资产总计为0，跳过占比计算")

        if prev:
            ar_prev = to_yi(prev.get("应收账款", "0"))
            inv_prev = to_yi(prev.get("存货", "0"))
            gw_prev = to_yi(prev.get("商誉", "0"))
            def pct_chg(cur, prv):
                if prv > 0: return (cur - prv) / prv * 100
                return 0
            L(f"\n  📈 环比变动（本期 vs 上期）:")
            L(f"    - 应收账款: {ar_yi:.2f}亿 (环比 {pct_chg(ar_yi, ar_prev):+.1f}%)")
            L(f"    - 存货: {inv_yi:.2f}亿 (环比 {pct_chg(inv_yi, inv_prev):+.1f}%)")
            L(f"    - 商誉: {gw_yi:.2f}亿 (环比 {pct_chg(gw_yi, gw_prev):+.1f}%)")

        flags = []
        if asset_yi > 0 and ar_yi / asset_yi > _ar_ratio_warn / 100:
            flags.append(f"⚠️ 应收账款占比{ar_yi/asset_yi*100:.0f}% > {_ar_ratio_warn:.0f}%，回款风险预警")
        _total_debt = st_debt_yi + due_debt_yi
        if cash_yi > 0 and _total_debt > 0 and cash_yi / _total_debt < 1.5:
            flags.append(f"⚠️ 货币资金{cash_yi:.1f}亿仅覆盖短期债务{_total_debt:.1f}亿的{cash_yi/_total_debt*100:.0f}%，偿债压力较大")
        # 商誉风险预警：需同时满足净资产>0和商誉占比超阈值
        if equity_yi > 0 and gw_yi > equity_yi * _gw_ratio / 100:
            flags.append(f"⚠️ 商誉占净资产{gw_yi/equity_yi*100:.0f}% > {_gw_ratio:.0f}%，减值风险预警")
        elif gw_yi > 0 and equity_yi == 0:
            flags.append(f"⚠️ 商誉{gw_yi:.1f}亿，但净资产数据缺失，无法计算占比")
        if asset_yi > 0 and liab_yi / asset_yi > _debt_ratio_warn / 100:
            flags.append(f"⚠️ 资产负债率{liab_yi/asset_yi*100:.0f}% > {_debt_ratio_warn:.0f}%，杠杆偏高")
        # 营收水分预警：应收账款激增 vs 营收
        if prev and financials:
            try:
                _rev_latest = _safe_float(financials[0].get("营业总收入", "0"))
                _rev_prev = _safe_float(financials[1].get("营业总收入", "0")) if len(financials) > 1 else 0
                _ar_incr = ar_yi - ar_prev
                _rev_decr = (_rev_latest - _rev_prev) / 1e8 if _rev_latest > 1e5 else _rev_latest - _rev_prev
                if _rev_decr < 0 and _ar_incr > 0:
                    flags.append(f"⚠️ 营收下滑但应收账款逆势增长{_ar_incr:.2f}亿，回款风险加剧")
                elif _ar_incr / max(_rev_decr, 1) > 0.3:
                    flags.append(f"⚠️ 应收账款增量占营收增量{_ar_incr/max(_rev_decr,1)*100:.0f}%，营收含金量偏低")
            except: pass
        if flags:
            L("")
            for flag in flags:
                L(f"  {flag}")
        else:
            L("\n  ✅ 资产负债表整体健康，未触发预警阈值。")
    else:
        L("  (资产负债表数据获取失败)")

    # ─── 5. 一致预期与PEG成长估值 ───
    L("\n【五、机构一致预期与前向 PEG】")
    L("─" * 72)
    df_eps = get_eps_forecast(code)
    eps_cur = eps_next = None
    eps_has_data = False
    if not df_eps.empty and len(df_eps.columns) >= 3:
        L(f"  {'年度':<10} {'覆盖机构数':<10} {'预测EPS均值':<12}")
        L(f"  {'-'*40}")
        for i, row in df_eps.iterrows():
            try:
                year = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
                cnt = int(row.iloc[1]) if pd.notna(row.iloc[1]) else 0
                mean_v = float(row.iloc[3]) if pd.notna(row.iloc[3]) else 0  # 均值列
                L(f"  {year:<10} {cnt:<10} {mean_v:<12.3f}")
                if i == 0:
                    eps_cur = mean_v
                    eps_has_data = True
                elif i == 1:
                    eps_next = mean_v
            except:
                pass
    if not eps_has_data:
        em_eps = _get_eps_from_em_reports(code)
        if em_eps:
            eps_cur = em_eps["eps_cur"]
            eps_next = em_eps["eps_next"]
            eps_has_data = True
            this_year = date.today().year
            this_month = date.today().month
            label_cur = f"预测{this_year}年" if this_month > 4 else f"{this_year}年"
            label_next = f"预测{this_year + 1}年" if this_month > 4 else f"预测{this_year}年"
            L(f"  东财研报一致预期EPS (同花顺兜底):")
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
        # 技术面辅助
        _sk_m, _sr_m = baidu_kline_full(code)
        if len(_sr_m) >= 26:
            _ci_m = next((i for i,k in enumerate(_sk_m) if k in ("close","close_price")), -1)
            if _ci_m >= 0:
                _cls_m = [_safe_float(rr[_ci_m]) for rr in _sr_m[-26:] if len(rr) > _ci_m]
                if len(_cls_m) >= 26:
                    def _ema(data, n):
                        e = [data[0]]
                        m = 2/(n+1)
                        for i in range(1,len(data)):
                            e.append(data[i]*m + e[-1]*(1-m))
                        return e[-1]
                    _ema12 = _ema(_cls_m[-25:], 12)
                    _ema26 = _ema(_cls_m[-45:], 26)
                    _dif = _ema12 - _ema26
                    _dea = _dif*2/9 + _dif*7/9  # simplified
                    _macd_sig = "金叉" if _dif > _dea else "死叉" if _dif < _dea else "粘合"
                    L(f"  [MACD] DIF={_dif:.3f} DEA={_dea:.3f}（{_macd_sig}）")
                    _ma20 = sum(_cls_m[-20:])/20
                    _ma60 = sum(_cls_m[-60:])/60 if len(_cls_m) >= 60 else _ma20
                    _ma_st = "多头排列" if _cls_m[-1]>_ma20>_ma60 else ("空头排列" if _cls_m[-1]<_ma20 else "震荡")
                    L(f"  [均线] MA20={_ma20:.2f} | {_ma_st}")
            if pe_fwd > _pe_mid and cagr > 0:
                digest = math.log(pe_fwd / _pe_mid) / math.log(1 + cagr)
                L(f"  ➤ 估值消化到30x需: {digest:.1f} 年")
            # 估值分位数
            try:
                _sk_p, _sr_p = baidu_kline_full(code)
                _ci_p = next((i for i,k in enumerate(_sk_p) if k in ("close","close_price")), -1)
                if _ci_p >= 0 and eps_cur > 0:
                    _hp = [_safe_float(rr[_ci_p]) for rr in _sr_p if len(rr) > _ci_p]
                    if len(_hp) > 20:
                        _hpe = [p/eps_cur for p in _hp if p > 0]
                        if _hpe:
                            _pc = sum(1 for p in _hpe if p < pe_fwd)/len(_hpe)*100
                            L(f"  PE历史分位: {_pc:.0f}%（低于{_pc:.0f}%的历史时间）")
            except: pass
    else:
        # 无机构覆盖 → 检查是否已有财务改善趋势（黑马潜质）
        has_black_horse = False
        _st_name = info.get("name","")
        if "ST" in _st_name or "*ST" in _st_name or "退" in _st_name:
            L("  ⚠️ 该股为ST/风险警示股，不具备黑马潜质，中线严禁左侧建仓！")
        elif financials and len(financials) >= 2:
            try:
                p1, p2 = _safe_float(financials[-1]["净利润"]), _safe_float(financials[-2]["净利润"])
                r1, r2 = _safe_float(financials[-1]["营业总收入"]), _safe_float(financials[-2]["营业总收入"])
                if p1 > p2 and r1 > r2:
                    has_black_horse = True
            except Exception:
                pass
        if has_black_horse:
            L("  ⚡ 无机构覆盖，但近两季度净利润+营收连续环比改善，具备黑马潜质预警！")
        else:
            L("  无机构覆盖数据（中线建议规避无主流机构覆盖的冷门股）")

    # ─── 4. 研报评级风向标 ───
    L("\n【六、研报评级统计与风向变动 (近3个月)】")
    L("─" * 72)
    reports = get_reports(code, max_pages=3)
    if reports:
        buy_count, add_count = 0, 0
        for r in reports:
            rating = str(r.get("emRatingName", ""))
            if "买入" in rating: buy_count += 1
            elif "增持" in rating: add_count += 1
            
        L(f"  统计样本：近 {len(reports)} 篇研报")
        L(f"  ➤ 【买入】评级: {buy_count} 篇 | 【增持】评级: {add_count} 篇")
        
        L(f"\n  最新 5 篇核心研报观点:")
        for r in reports[:5]:
            pub_date = str(r.get("publishDate", ""))[:10]
            org = r.get("orgSName", "")
            title = r.get("title", "")[:45]
            rating = r.get("emRatingName", "无")
            L(f"    - [{pub_date}] {org} ({rating}): {title}")
    else:
        L("  暂无相关研报评级数据。")

    # ─── 5. 重大公告追踪 (排雷/催化) ───
    L("\n【七、重大实质性公告追踪 (避雷与催化)】")
    L("─" * 72)
    anns = get_strategic_announcements(code, days=30)
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
    L("\n【八、筹码稳定性与抛压评估】")
    L("─" * 72)
    
    # 股东户数
    holders = get_holder_change(code)
    if holders:
        L(f"  ➤ 股东户数变化趋势:")
        for h in holders[:5]:
            _cr = h['change_ratio']
            # 边界检查：变化率超过±500%视为异常数据，不显示
            _cr_disp = _cr if abs(_cr) <= 500 else (999.99 if _cr > 500 else -999.99)
            _cr_flag = " ⚠️" if abs(_cr) > 500 else ""
            L(f"    截止 {h['date']}: 股东数 {h['holder_num']:,} 户 | 环比变化 {_cr_disp:+.2f}%{_cr_flag}")
        latest = holders[0]
        if latest["change_ratio"] <= -3:
            L("    ✅ 结论: 筹码正在集中，利好中线。")
        elif latest["change_ratio"] >= 3:
            L("    ⚠️ 结论: 筹码趋于分散，散户增多，注意风险。")
    
    # 解禁抛压
    lockup = get_lockup_expiry(code, today_str, days=180)
    # 未来事件日历
    if lockup:
        _cal_evts = [f"{_h['date']} 解禁{_h['ratio']:.1f}%" for _h in lockup if _h.get('ratio',0) > 0]
        L(f"\n  ➤ 未来可预期事件:")
        if _cal_evts:
            for _ev in _cal_evts[:5]:
                L(f"    📅 {_ev}")
        else:
            L("    (暂无已披露近期事件)")
    if lockup:
        total_upcoming = sum(h["shares"] for h in lockup)
        L(f"\n  ➤ 解禁抛压预警 (未来180天):")
        L(f"    ⚠️ 待解禁总计: {total_upcoming/1e4:.0f}万股")
        for h in lockup:
            L(f"    - {h['date']}: {h['type']} ({h['shares']/1e4:.0f}万股, 占 {h['ratio']:.2f}%)")
    else:
        L("\n  ➤ 解禁抛压预警: 未来半年内无解禁压力 ✅")

    # ─── 北向资金持仓动态 ───
    L("\n【九、北向资金持仓动态】")
    L("─" * 72)
    nb = get_northbound_hold(code, 20)
    if nb:
        L(f"  近 {len(nb)} 个交易日北向持仓数据:")
        L(f"  {'日期':<12} {'持股数量(万)':>12} {'持股市值(万)':>12} {'持股占比%':>10} {'变动股数(万)':>12}")
        L(f"  {'-'*65}")
        for d in nb:
            # V4 fix: 推算缺失的市值/占比（东财有时返回0）
            _mcap = d.get('market_cap', 0) or 0
            _ratio = d.get('hold_ratio', 0) or 0
            _shares = d.get('hold_shares', 0) or 0
            if _mcap == 0 and _shares > 0 and price_today > 0:
                _mcap = _shares * price_today
                _ratio = _shares / info.get('total_shares', 1) if info.get('total_shares', 0) > 0 else 0
            L(f"  {d['date']:<12} {_shares/1e4:>12.0f} {_mcap/1e4:>12.0f} {_ratio:>9.4f}% {d['change_shares']/1e4:>+12.0f}")
        if len(nb) >= 2:
            ratio_change = nb[0]["hold_ratio"] - nb[-1]["hold_ratio"]
            if ratio_change > 0:
                L(f"  ➤ 信号: 近{len(nb)}日北向持股比例 +{ratio_change:.4f}%，外资增持")
            elif ratio_change < 0:
                L(f"  ➤ 信号: 近{len(nb)}日北向持股比例 {ratio_change:.4f}%，外资减持")
    else:
        L("  该股暂无北向资金持仓数据（可能非陆股通标的或数据延迟）")

    # ─── 同业龙头横向对比 ───
    L("\n【十、同业龙头横向对比（赛道身位监测）】")
    L("─" * 72)
    if peer_data["peers"]:
        if "note" in peer_data["peers"][0]:
            L(f"  ⚠️ {peer_data['peers'][0]['note']}")
        else:
            L(f"  所属板块: {peer_data['industry']}")
            L(f"  本股市值: {peer_data['my_mcap']:.1f}亿元")
            if peer_data.get("my_rank", 0) > 0:
                L(f"  业内排名: 第 {peer_data['my_rank']}/{peer_data['industry_count']} 位（按总市值）")
            L(f"  {'代码':<8} {'名称':<12} {'股价':>8} {'涨跌幅%':>8} {'市值(亿)':>10} {'PE':>8} {'换手率%':>8}")
            L(f"  {'-'*70}")
            L(f"  {code:<8} {info.get('name','N/A'):<12} {price_today:>8.2f} {q.get('change_pct',0):>7.2f}% {peer_data['my_mcap']:>9.1f} {q.get('pe_ttm',0):>7.1f} {q.get('turnover_pct',0):>7.2f}% ← 本股")
            for p in peer_data["peers"]:
                L(f"  {p['code']:<8} {p['name']:<12} {p['price']:>8.2f} {p['change_pct']:>7.2f}% {p['mcap_yi']:>9.1f} {p['pe']:>7.1f} {p['turnover']:>7.2f}%")
            # 本股毛利率 & ROE
            fin_metrics = get_gross_margin_and_roe(code, fin_report=financials, bs_data=bs_data)
            if fin_metrics:
                gm = fin_metrics.get("gross_margin")
                roe = fin_metrics.get("roe")
                parts = []
                if gm is not None: parts.append(f"毛利率 {gm:.1f}%")
                if roe is not None: parts.append(f"ROE {roe:.1f}%")
                if parts:
                    L(f"\n  📊 本股财务质量: {' | '.join(parts)}")
    else:
        L(f"  无法获取同业数据（板块: {peer_data.get('industry', '未知')}）")

    # ─── 中线主力资金底仓流向 ───
    L("\n【十一、中线主力资金流向 (60日基准)】")
    L("─" * 72)
    fund_flow = get_fund_flow_120d(code)
    if fund_flow["data"]:
        fund_data = fund_flow["data"]
        recent_20 = fund_data[-20:]
        total_main_20 = sum(d["main_net"] for d in recent_20)
        days_bullish_20 = sum(1 for d in recent_20 if d["main_net"] > 0)
        recent_60 = fund_data[-60:]
        total_main_60 = sum(d["main_net"] for d in recent_60)
        L(f"  ➤ 近 20 个交易日：")
        L(f"    主力净流入天数: {days_bullish_20} 天 / 20 天")
        L(f"    累计主力净流入: {total_main_20/1e8:.2f} 亿元")
        L(f"  ➤ 近 60 个交易日（中期视角）：")
        L(f"    累计主力净流入: {total_main_60/1e8:.2f} 亿元")
        if total_main_60 > 0:
            L(f"    ✅ 资金面结论: 中线资金呈吸筹/护盘状态。")
        else:
            L(f"    ⚠️ 资金面结论: 中线资金呈流出状态，需结合估值谨慎判断。")
    elif fund_flow["error"]:
        L(f"  {fund_flow['error']}")
    else:
        L("  中线资金流数据获取失败。")

    # ─── 融资融券 ───
    # 资金流背离检测
    if fund_flow.get("data") and len(fund_flow["data"]) >= 20:
        _p20 = [d["main_net"] for d in fund_flow["data"][-20:]]
        _pc_chg = q.get("change_pct", 0) if q else 0
        _cum_f = sum(_p20)
        if _cum_f < 0 and _pc_chg > 3:
            L(f"  ⚠️ 量价背离：近20日主力净流出{abs(_cum_f)/1e8:.2f}亿，股价涨{_pc_chg:.1f}%缺支撑")
        elif _cum_f > 0 and _pc_chg < -3:
            L(f"  💎 资金背离：股价下跌但主力净流入{_cum_f/1e8:.2f}亿，资金暗中介入")

    L("\n【十二、融资融券（两融数据，近15日）】")
    L("─" * 72)
    margin = get_margin_trading(code)
    if margin:
        L(f"  {'日期':<12} {'融资余额(万)':>10} {'融资买入(万)':>10} {'融资偿还(万)':>10}")
        L(f"  {'-'*55}")
        for d in margin[:10]:
            L(f"  {d['date']:<12} {d['rzye']/1e4:>14.0f} {d['rzmre']/1e4:>14.0f} {d['rzche']/1e4:>14.0f}")
    else:
        L("  该股无融资融券数据（可能不是两融标的）。")

    # ─── 大宗交易 ───
    L("\n【十三、大宗交易（机构建仓痕迹）】")
    L("─" * 72)
    bt = get_block_trade(code)
    _one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    bt_filtered = [d for d in bt if d.get("date", "") >= _one_year_ago] if bt else []
    if bt_filtered:
        L(f"  近1年共 {len(bt_filtered)} 笔大宗交易（历史共 {len(bt)} 笔）:")
        L(f"  {'日期':<12} {'成交价':>6} {'溢价%':>6} {'成交量':>8} {'买方':<24}")
        L(f"  {'-'*75}")
        for d in bt_filtered:
            L(f"  {d['date']:<12} {d['price']:>8.2f} {d['premium_pct']:>7.2f}% {d['vol']/1e4:>8.0f}万 {d['buyer']:<24}")
    else:
        L("  无大宗交易记录。")

    L("\n【十四、龙虎榜机构动向】")
    L("─" * 72)
    dtb = get_dragon_tiger_board(code, today_str, days=180)
    if dtb["records"]:
        L(f"  近180日上榜 {len(dtb['records'])} 次:")
        L(f"  {'日期':<12} {'上榜原因':<50} {'净买入(万)':>9} {'换手率':>6}")
        L(f"  {'-'*85}")
        for r in dtb["records"]:
            reason = r.get("reason", "")[:48]
            L(f"  {r['date']:<12} {reason:<50} {r['net_buy']:>12.1f} {r['turnover']:>7.2f}%")

        seats = dtb["seats"]
        if seats["buy"]:
            L(f"\n  最近买入席位 TOP5:")
            L(f"  {'营业部名称':<30} {'买入(万)':>9} {'卖出(万)':>9} {'净额(万)':>9}")
            L(f"  {'-'*70}")
            for s in seats["buy"]:
                L(f"  {s['name']:<30} {s['buy_amt']:>12.1f} {s['sell_amt']:>12.1f} {s['net']:>12.1f}")
        if seats["sell"]:
            L(f"\n  最近卖出席位 TOP5:")
            L(f"  {'营业部名称':<30} {'买入(万)':>9} {'卖出(万)':>9} {'净额(万)':>9}")
            L(f"  {'-'*70}")
            for s in seats["sell"]:
                L(f"  {s['name']:<30} {s['buy_amt']:>12.1f} {s['sell_amt']:>12.1f} {s['net']:>12.1f}")

        inst = dtb["institution"]
        if inst and (inst.get("buy_amt", 0) > 0 or inst.get("sell_amt", 0) > 0):
            L(f"\n  机构买卖统计:")
            L(f"    机构买入金额: {inst['buy_amt']}万元")
            L(f"    机构卖出金额: {inst['sell_amt']}万元")
            L(f"    机构净买入: {inst['net_amt']}万元")
    else:
        L("  近180日无龙虎榜记录（白马蓝筹或近期未触发异动标准的个股，无龙虎榜属正常现象）。")

    # ─── 9. 高股息防御属性 (分红历史) ───
    L("\n【十五、高股息防御属性 (近十次分红)】")
    L("─" * 72)
    div = get_dividend_history(code)
    # 分红持续性分析
    if div and len(div) >= 3:
        _dy = len(set(d["date"][:4] for d in div if d.get("bonus_rmb",0) > 0))
        L(f"  📊 分红持续性: 连续{_dy}年分红")
        if _dy >= 5:
            L(f"    💎 连续5年以上分红，具备稳定防御属性")
    if div:
        L(f"  近5次分红除息记录:")
        L(f"  {'除权除息日':<14} {'每股派息(元)':>8} {'折算对应股价股息率参考'}")
        L(f"  {'-'*55}")
        for d in div[:5]:
            yield_str = f"{(d['bonus_rmb'] / price_today) * 100:.2f}%" if price_today > 0 else "N/A"
            L(f"  {d['date']:<14} {d['bonus_rmb']:>12.4f}  约 {yield_str} (按现价计)")
    else:
        L("  暂无分红记录（非防御型收息标的）。")

    # ─── 16. 十大流通股东机构动向 ───
    L("\n【十六、十大流通股东机构动向】")
    L("─" * 72)
    st = get_holder_structure(code)  # 复用长线缓存
    if st:
        L(f"  数据来源: 十大流通股东季报（最近 {len(st)} 期）")
        L("")
        _header = f"  {'截止':<12} {'北向':>6}  {'外资':>8}  {'境内机构':>8}  {'个人':>6}  {'Top10':>6}"
        L(_header)
        L(f"  {'-'*60}")
        for p in st:
            _cols = f"  {p['date']:<12} {p['northbound']:>5.1f}%"
            _cols += f"  {p['foreign']:>5.1f}%({p['foreign_count']})" if p['foreign_count'] else f"  {'N/A':>8}"
            _cols += f"  {p['domestic']:>5.1f}%({p['domestic_count']})" if p['domestic_count'] else f"  {'N/A':>8}"
            _cols += f"  {p['individual']:>5.1f}%({p['individual_count']})" if p['individual_count'] else f"  {'N/A':>6}"
            _cols += f"  {p['total']:>5.1f}%"
            L(_cols)
        # 境内细分类
        _dd = st[0].get("dm_detail", {})
        if _dd:
            _parts = [f"{k} {v:.1f}%" for k, v in _dd.items()]
            L(f"\n  境内机构细分: {' | '.join(_parts)}")
        # 分析
        latest = st[0]
        if latest['foreign'] > 30:
            L(f"  🔍 外资机构合计持股 {latest['foreign']:.1f}%，话语权极强")
        if latest['northbound'] > 10:
            L(f"  🔍 北向资金持股 {latest['northbound']:.1f}% > 10%，重要边际定价力量")
        if latest['individual'] > 10:
            L(f"  🔍 个人大股东合计持股 {latest['individual']:.1f}%，利益深度绑定")
    else:
        L("  十大流通股东数据获取失败。")

    L("\n" + "=" * 72)
    # 历史胜率回测（近似统计）
    _bt_items = []
    if holders and len(holders) >= 2:
        _hd_chg = holders[0].get("change_ratio", 0)
        if _hd_chg < -3:
            _bt_items.append(f"股东户数减少{abs(_hd_chg):.1f}%（历史类似信号后中线偏多）")
    if nb and len(nb) >= 5:
        _nb_s = _safe_float(nb[-1].get("hold_shares", 0))
        _nb_e = _safe_float(nb[0].get("hold_shares", 0))
        if _nb_s > 0:
            _nb_chg = (_nb_e-_nb_s)/_nb_s*100
            _bt_items.append(f"北向近{len(nb)}日持仓{_nb_chg:+.1f}%")
    if _bt_items:
        L("【回测参考】")
        for _bi in _bt_items:
            L(f"  📊 {_bi}")

    L("\n"+"─"*72); L("【仓位管理建议】"); L("─"*72)
    
    # V8.2: 使用统一评分接口
    from stock_common import ScoreData, calculate_score, save_score_snapshot
    
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
    if q:
        score_data.pe_ttm = q.get("pe_ttm", 0) or 0
    if peer_data and peer_data.get("peers"):
        score_data.industry_pe = sum(p.get("pe", 0) for p in peer_data["peers"]) / max(len(peer_data["peers"]), 1)
    
    # 北向数据
    if nb and len(nb) >= 2:
        score_data.northbound_change = nb[0]["hold_shares"] - nb[-1]["hold_shares"]
    
    # 机构持仓
    _st = get_holder_structure(code)
    if _st:
        score_data.institution_holding_pct = _st[0].get("domestic", 0)
    
    # 筹码数据
    if holders and len(holders) >= 2:
        score_data.holder_change_ratio = holders[0]["change_ratio"]
    
    # 计算评分
    result = calculate_score("med", score_data)
    _ps = result.total_score
    _details = result.details
    
    L(f"  评分明细: {' | '.join(_details[:6])}" if _details else None)
    if _ps>=70: L(f"  中线评分: {_ps:.0f}/100 → 强烈推荐，仓位40%")
    elif _ps>=45: L(f"  中线评分: {_ps:.0f}/100 → 建议配置，仓位25%")
    elif _ps>=20: L(f"  中线评分: {_ps:.0f}/100 → 观察仓，仓位10%")
    else: L(f"  中线评分: {_ps:.0f}/100 → 暂不建议，等待基本面拐点")
    
    # V8.5新增：价值派+成长派双评分
    L("\n  ★ 中线双派评分（V8.5）")
    L("  ─────────────────────────────────────────────────────────────────────")
    try:
        # 价值派评分（估值安全边际+财务健康）
        value_score = 50
        value_comment = ""
        
        # 估值加分
        pe = q.get("pe_ttm", 0) if q else 0
        if pe > 0 and pe < 15:
            value_score += 15
            value_comment = "低估值安全边际"
        elif pe > 0 and pe < 25:
            value_score += 8
            value_comment = "估值合理"
        elif pe > 0 and pe < 40:
            value_score += 0
            value_comment = "估值偏高"
        else:
            value_score -= 5
            value_comment = "高估值风险"
        
        # ROE加分
        if gross_roe and gross_roe.get("roe"):
            roe_val = gross_roe["roe"]
            if roe_val > 15:
                value_score += 12
            elif roe_val > 10:
                value_score += 6
        
        # 负债率加分
        if fina and fina.get("asset_liability_ratio"):
            debt_ratio = fina["asset_liability_ratio"]
            if debt_ratio < 40:
                value_score += 8
            elif debt_ratio < 60:
                value_score += 4
            elif debt_ratio > 80:
                value_score -= 10
        
        # 机构持仓加分
        if _st and _st[0].get("domestic", 0) > 30:
            value_score += 8
        
        # 成长派评分（业绩增速+行业景气）
        growth_score = 50
        growth_comment = ""
        
        # EPS增速加分
        if eps_fc and eps_fc.get("data"):
            try:
                # 计算EPS增长趋势
                eps_data = eps_fc["data"]
                if len(eps_data) >= 2:
                    cur_eps = float(eps_data[-1].get("均值", 0) or 0)
                    prev_eps = float(eps_data[-2].get("均值", 0) or 0)
                    if prev_eps > 0 and cur_eps > prev_eps:
                        growth_rate = (cur_eps - prev_eps) / prev_eps * 100
                        if growth_rate > 30:
                            growth_score += 15
                            growth_comment = "高增长赛道"
                        elif growth_rate > 15:
                            growth_score += 10
                            growth_comment = "稳健增长"
                        elif growth_rate > 5:
                            growth_score += 5
                            growth_comment = "温和增长"
            except:
                pass
        
        # 北向增持加分
        if nb and len(nb) >= 2:
            nb_chg = nb[0]["hold_shares"] - nb[-1]["hold_shares"]
            if nb_chg > 0:
                growth_score += 8
        
        # 行业对比加分
        if peer_data and peer_data.get("my_rank"):
            my_rank = peer_data["my_rank"]
            total_peers = len(peer_data.get("peers", []))
            if my_rank <= total_peers * 0.3:
                growth_score += 5
        
        # 限制分数范围
        value_score = max(0, min(100, value_score))
        growth_score = max(0, min(100, growth_score))
        
        # 综合建议
        if value_score >= 70 and growth_score >= 70:
            suggestion = "价值+成长双优，中线重点配置"
        elif value_score >= 60 and growth_score >= 60:
            suggestion = "价值成长均衡，中线稳健配置"
        elif value_score >= 60:
            suggestion = "价值派主导，适合稳健型中线配置"
        elif growth_score >= 60:
            suggestion = "成长派主导，适合进取型中线配置"
        else:
            suggestion = "价值成长双弱，中线观望"
        
        L(f"    价值派评分: {value_score:.0f}分 ({value_comment})")
        L(f"    成长派评分: {growth_score:.0f}分 ({growth_comment})")
        L(f"    综合建议: {suggestion}")
    except Exception as e:
        L(f"    双派评分计算异常: {str(e)}")
    
    L(f"  核心驱动: 基本面拐点 / 估值 PEG / 筹码结构 / 重大事件")
    L("=" * 72)

    # 保存评分快照
    try:
        save_score_snapshot("med", code, info.get('name', ''), _ps, price_today)
    except Exception:
        pass

    output = "\n".join(filter(None, lines))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)
    return output


async def generate_report_async(session, code, output_path, ind_comp=None, hsgt=None):
    """async 版: 支持 ind_comp/hsgt 外部缓存，批量模式下避免重复查询"""
    today_str = date.today().strftime("%Y-%m-%d")
    lines = []
    def L(s=""): lines.append(s)

    L("=" * 72)
    L(f"  {code} 中线深度投研报告V8.5.1 — {today_str} {datetime.now().strftime('%H:%M:%S')}")
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
    _cash_debt_ratio = _fund.get("cash_debt_ratio_warn", 1.0)
    _gw_ratio = _fund.get("gw_ratio_warn", 30.0)
    _ar_rev_ratio = _fund.get("ar_rev_warn_ratio", 30.0)

    _now = datetime.now()
    _is_td = is_trading_day(_now.date())
    _mkt_status, _mkt_note = get_market_status(_now)

    # 生成详细提示
    if _mkt_status == "closed":
        note = f"（休市日，数据为最近交易日快照）"
    elif _mkt_status == "pre_market":
        note = "⚠️ 当前为盘前时段，行情数据/北向资金为上交易日值，龙虎榜/融资融券为最近一期已发布数据"
    elif _mkt_status in ("morning", "afternoon"):
        note = ("⚠️ 当前为盘中时段，行情数据实时跳动，龙虎榜/融资融券/大宗交易需收盘后更新，"
                "其余基本面数据（财报/ROE/股东/分红等）为最新报告期数据不受影响")
    elif _mkt_status == "lunch":
        note = "⚠️ 当前为午休时段（11:30-13:00），行情暂停但基本面数据正常"
    elif _mkt_status == "post_market":
        note = "⚠️ 当前为盘后结算时段，部分数据（龙虎榜约16:30后）尚在更新中"
    else:
        note = ""
    if note:
        print(f"\033[93m{note}\033[0m", flush=True)
        L(f"  {note}")
        L("")

    # ─── 0. 宏观资金风向标 ───
    L("\n【一、宏观资金面背景】")
    L("─" * 72)
    if hsgt is None:
        hsgt = await get_hsgt_macro_flow_async(session)
    if hsgt:
        signal = "偏多" if hsgt['total'] > 0 else "偏空"
        L(f"  今日北向资金总净流入: {hsgt['total']:.2f} 亿元 (沪股通 {hsgt['hgt']:.2f}亿 | 深股通 {hsgt['sgt']:.2f}亿)")
        L(f"  大盘外资情绪: {signal} （中线仓位参考点）")
    else:
        L("  (北向宏观资金流向获取失败)")

    # ─── 1. 基本信息与实时估值 ───
    L("\n【二、个股基本信息与估值锚点】")
    L("─" * 72)
    info = get_stock_info(code)
    q = get_tencent_quote(code)
    price_today = q.get("price", 0) if q else 0

    L(f"  股票名称: {info.get('name', 'N/A')} ({info.get('code', code)})")
    L(f"  所属板块: {info.get('industry', 'N/A')}")
    list_date_raw = info.get("list_date", "")
    if list_date_raw and len(list_date_raw) >= 8:
        list_date_fmt = f"{list_date_raw[:4]}-{list_date_raw[4:6]}-{list_date_raw[6:8]}"
    else:
        list_date_fmt = list_date_raw
    L(f"  上市日期: {list_date_fmt}")

    if ind_comp is None:
        ind_comp = get_industry_comparison()
    stock_ind = info.get('industry', '')
    peer_data = {"industry": "", "my_mcap": 0, "my_rank": 0, "industry_count": 0, "peers": []}
    fin_metrics = {}
    if stock_ind and ind_comp:
        _ind_all = ind_comp.get("all", ind_comp)
        for row in _ind_all:
            if stock_ind in row["name"] or row["name"] in stock_ind:
                L(f"  板块排名: 当日全市场第 {row['rank']} 名 (涨跌幅 {row['change_pct']}%)")
                _all_m = peer_data.get("all_members", [])
                if _all_m:
                    _up = sum(1 for m in _all_m if m.get("change_pct", 0) > 0)
                    _down = sum(1 for m in _all_m if m.get("change_pct", 0) < 0)
                    L(f"  板块涨跌: 上涨 {_up} 家 / 下跌 {_down} 家")
                try:
                    _rank_info = get_stock_sector_rank(code, info=info)
                    if _rank_info:
                        L(f"  本股今日{_rank_info['change_pct']:+.2f}%，板块内排名第{_rank_info['rank']}/{_rank_info['total']}名")
                except Exception:
                    pass
                if row['rank'] <= 10:
                    L(f"  🔥 板块共振: 该板块处于全市场 TOP 10 热门赛道，板块共振溢价效应显著")
                if row.get("leader"):
                    leader_code = row["leader"]
                    leader_name = ""
                    try:
                        li = get_stock_info(leader_code)
                        leader_name = li.get("name", "")
                    except Exception:
                        pass
                    if leader_name:
                        L(f"  板块龙头: {leader_code} {leader_name}")
                    else:
                        L(f"  板块龙头: {leader_code}")
                break

    await asyncio.sleep(0.5)
    peer_data = get_industry_peers(code, 3, info=info)
    if peer_data.get("my_rank", 0) > 0 and peer_data.get("industry_count", 0) > 0:
        L(f"  板块内排名: 按总市值排序, 该股排名第 {peer_data['my_rank']}/{peer_data['industry_count']} 位")

    L(f"  总市值:   {q.get('mcap_yi', 0):.2f}亿元 (流通股本 {info.get('float_shares', 0)/1e8:.2f}亿股)")
    L(f"  当前价:   {price_today:.2f}元  (今日涨跌: {q.get('change_pct', 0):.2f}%)")
    _pe_ttm = q.get('pe_ttm', 0); _pe_static = q.get('pe_static', 0)
    _pe_s = f"{_pe_static:.2f}x" if _pe_ttm > 0 and _pe_static > 0 else "N/A（亏损）"
    L(f"  动态市盈率 PE(TTM): {_pe_ttm:.2f}x | 静态PE: {_pe_s} | 市净率 PB: {q.get('pb', 0):.2f}")

    # ─── 2. 财务业绩兑现追踪 ───
    L("\n【三、历史财务业绩兑现追踪 (近5季度)】")
    L("─" * 72)
    financials = await get_sina_financial_report_async(session, code)
    if financials:
        L(f"  {'报告期':<12} {'营业总收入':>11} {'净利润':>13} {'净利率':>8}")
        L(f"  {'-'*60}")
        for item in financials:
            date_val = item.get("报告日", "")
            rev = item.get("营业总收入", "0")
            profit = item.get("净利润", "0")
            try:
                rv = float(rev) if rev and rev != "0" else 0
                pf = float(profit) if profit and profit != "0" else 0
                rev_yi = f"{rv/1e8:.2f} 亿" if rv else "N/A"
                profit_yi = f"{pf/1e8:.2f} 亿" if pf else "N/A"
                npm = f"{pf/rv*100:.2f}%" if rv > 0 else "N/A"
            except:
                rev_yi, profit_yi, npm = "N/A", "N/A", "N/A"
            L(f"  {date_val:<12} {rev_yi:>15} {profit_yi:>15} {npm:>8}")
        L("\n  💡 中线逻辑核实：观察收入与净利润是否保持同步增长。")
    else:
        L("  (新浪财报数据获取失败或该股暂无相关数据)")

    # ─── 4. 资产负债表财务健康度 ───
    L("\n【四、资产负债表财务健康度（排雷）】")
    L("─" * 72)
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
            try: return float(v) / 1e8
            except: return 0.0

        ar_yi = to_yi(ar); inv_yi = to_yi(inv); gw_yi = to_yi(gw)
        cash_yi = to_yi(cash); st_debt_yi = to_yi(st_debt); due_debt_yi = to_yi(due_debt)
        equity_yi = to_yi(equity); asset_yi = to_yi(total_assets); liab_yi = to_yi(total_liab)

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
            L(f"  ⚠️ 资产总计为0，跳过占比计算")

        if prev:
            ar_prev = to_yi(prev.get("应收账款", "0"))
            inv_prev = to_yi(prev.get("存货", "0"))
            gw_prev = to_yi(prev.get("商誉", "0"))
            def pct_chg(cur, prv):
                if prv > 0: return (cur - prv) / prv * 100
                return 0
            L(f"\n  📈 环比变动（本期 vs 上期）:")
            L(f"    - 应收账款: {ar_yi:.2f}亿 (环比 {pct_chg(ar_yi, ar_prev):+.1f}%)")
            L(f"    - 存货: {inv_yi:.2f}亿 (环比 {pct_chg(inv_yi, inv_prev):+.1f}%)")
            L(f"    - 商誉: {gw_yi:.2f}亿 (环比 {pct_chg(gw_yi, gw_prev):+.1f}%)")

        flags = []
        if asset_yi > 0 and ar_yi / asset_yi > _ar_ratio_warn / 100:
            flags.append(f"⚠️ 应收账款占比{ar_yi/asset_yi*100:.0f}% > {_ar_ratio_warn:.0f}%，回款风险预警")
        _total_debt = st_debt_yi + due_debt_yi
        if cash_yi > 0 and _total_debt > 0 and cash_yi / _total_debt < 1.5:
            flags.append(f"⚠️ 货币资金{cash_yi:.1f}亿仅覆盖短期债务{_total_debt:.1f}亿的{cash_yi/_total_debt*100:.0f}%，偿债压力较大")
        # 商誉风险预警：需同时满足净资产>0和商誉占比超阈值
        if equity_yi > 0 and gw_yi > equity_yi * _gw_ratio / 100:
            flags.append(f"⚠️ 商誉占净资产{gw_yi/equity_yi*100:.0f}% > {_gw_ratio:.0f}%，减值风险预警")
        elif gw_yi > 0 and equity_yi == 0:
            flags.append(f"⚠️ 商誉{gw_yi:.1f}亿，但净资产数据缺失，无法计算占比")
        if asset_yi > 0 and liab_yi / asset_yi > _debt_ratio_warn / 100:
            flags.append(f"⚠️ 资产负债率{liab_yi/asset_yi*100:.0f}% > {_debt_ratio_warn:.0f}%，杠杆偏高")
        if prev and financials:
            try:
                _rev_latest = _safe_float(financials[0].get("营业总收入", "0"))
                _rev_prev = _safe_float(financials[1].get("营业总收入", "0")) if len(financials) > 1 else 0
                _ar_incr = ar_yi - ar_prev
                _rev_decr = (_rev_latest - _rev_prev) / 1e8 if _rev_latest > 1e5 else _rev_latest - _rev_prev
                if _rev_decr < 0 and _ar_incr > 0:
                    flags.append(f"⚠️ 营收下滑但应收账款逆势增长{_ar_incr:.2f}亿，回款风险加剧")
                elif _ar_incr / max(_rev_decr, 1) > 0.3:
                    flags.append(f"⚠️ 应收账款增量占营收增量{_ar_incr/max(_rev_decr,1)*100:.0f}%，营收含金量偏低")
            except: pass
        if flags:
            L("")
            for flag in flags: L(f"  {flag}")
        else:
            L("\n  ✅ 资产负债表整体健康，未触发预警阈值。")
    else:
        L("  (资产负债表数据获取失败)")

    # ─── 5. 一致预期与PEG成长估值 ───
    L("\n【五、机构一致预期与前向 PEG】")
    L("─" * 72)
    df_eps = await get_eps_forecast_async(session, code)
    eps_cur = eps_next = None
    eps_has_data = False
    if not df_eps.empty and len(df_eps.columns) >= 3:
        L(f"  {'年度':<10} {'覆盖机构数':<10} {'预测EPS均值':<12}")
        L(f"  {'-'*40}")
        for i, row in df_eps.iterrows():
            try:
                year = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
                cnt = int(row.iloc[1]) if pd.notna(row.iloc[1]) else 0
                mean_v = float(row.iloc[3]) if pd.notna(row.iloc[3]) else 0
                L(f"  {year:<10} {cnt:<10} {mean_v:<12.3f}")
                if i == 0: eps_cur = mean_v; eps_has_data = True
                elif i == 1: eps_next = mean_v
            except: pass
    if not eps_has_data:
        reports_em = await get_reports_async(session, code, max_pages=1)
        em_eps = None
        if reports_em:
            for r in reports_em:
                ty = r.get("predictThisYearEps")
                ny = r.get("predictNextYearEps")
                if ty is not None and str(ty).strip(): em_eps = {"eps_cur": float(ty), "eps_next": float(ny) if ny is not None and str(ny).strip() else None}
                if em_eps: break
        if em_eps:
            eps_cur = em_eps["eps_cur"]
            eps_next = em_eps.get("eps_next")
            eps_has_data = True
            this_year = date.today().year
            this_month = date.today().month
            label_cur = f"预测{this_year}年" if this_month > 4 else f"{this_year}年"
            label_next = f"预测{this_year + 1}年" if this_month > 4 else f"预测{this_year}年"
            L(f"  东财研报一致预期EPS (同花顺兜底):")
            L(f"  {'年度':<14} {'预测EPS'}")
            L(f"  {'-'*30}")
            if eps_cur: L(f"  {label_cur:<14} {eps_cur:.3f}")
            if eps_next: L(f"  {label_next:<14} {eps_next:.3f}")
    if eps_has_data and price_today and eps_cur and eps_cur > 0:
        pe_fwd = price_today / eps_cur
        L(f"\n  ➤ 前向市盈率 (预测今年): {pe_fwd:.2f}x")
        if eps_next and eps_cur > 0:
            cagr = (eps_next / eps_cur) - 1
            L(f"  ➤ 预期净利增速: {cagr*100:.1f}%")
            peg = pe_fwd / (cagr * 100) if cagr > 0 else float("inf")
            if peg == float("inf"): eval_str = "无法计算"
            elif peg < _peg_good: eval_str = "偏低估 (合理区间之下)"
            elif peg <= _peg_rational: eval_str = "估值合理"
            else: eval_str = "偏高估 (存在透支预期风险)"
            L(f"  ➤ 核心 PEG 指标: {peg:.2f} → {eval_str}")
        _sk_m, _sr_m = baidu_kline_full(code)
        if len(_sr_m) >= 26:
            _ci_m = next((i for i,k in enumerate(_sk_m) if k in ("close","close_price")), -1)
            if _ci_m >= 0:
                _cls_m = [_safe_float(rr[_ci_m]) for rr in _sr_m[-26:] if len(rr) > _ci_m]
                if len(_cls_m) >= 26:
                    def _ema(data, n):
                        e = [data[0]]; m = 2/(n+1)
                        for i in range(1, len(data)): e.append(data[i]*m + e[-1]*(1-m))
                        return e[-1]
                    _ema12 = _ema(_cls_m[-25:], 12)
                    _ema26 = _ema(_cls_m[-45:], 26)
                    _dif = _ema12 - _ema26; _dea = _dif*2/9 + _dif*7/9
                    _macd_sig = "金叉" if _dif > _dea else "死叉" if _dif < _dea else "粘合"
                    L(f"  [MACD] DIF={_dif:.3f} DEA={_dea:.3f}（{_macd_sig}）")
                    _ma20 = sum(_cls_m[-20:])/20
                    _ma60 = sum(_cls_m[-60:])/60 if len(_cls_m) >= 60 else _ma20
                    _ma_st = "多头排列" if _cls_m[-1]>_ma20>_ma60 else ("空头排列" if _cls_m[-1]<_ma20 else "震荡")
                    L(f"  [均线] MA20={_ma20:.2f} | {_ma_st}")
            if pe_fwd > _pe_mid and cagr > 0:
                digest = math.log(pe_fwd / _pe_mid) / math.log(1 + cagr)
                L(f"  ➤ 估值消化到30x需: {digest:.1f} 年")
            try:
                _sk_p, _sr_p = baidu_kline_full(code)
                _ci_p = next((i for i,k in enumerate(_sk_p) if k in ("close","close_price")), -1)
                if _ci_p >= 0 and eps_cur > 0:
                    _hp = [_safe_float(rr[_ci_p]) for rr in _sr_p if len(rr) > _ci_p]
                    if len(_hp) > 20:
                        _hpe = [p/eps_cur for p in _hp if p > 0]
                        if _hpe:
                            _pc = sum(1 for p in _hpe if p < pe_fwd)/len(_hpe)*100
                            L(f"  PE历史分位: {_pc:.0f}%（低于{_pc:.0f}%的历史时间）")
            except: pass
    else:
        has_black_horse = False
        _st_name = info.get("name", "")
        if "ST" in _st_name or "*ST" in _st_name or "退" in _st_name:
            L("  ⚠️ 该股为ST/风险警示股，不具备黑马潜质，中线严禁左侧建仓！")
        elif financials and len(financials) >= 2:
            try:
                p1, p2 = _safe_float(financials[-1]["净利润"]), _safe_float(financials[-2]["净利润"])
                r1, r2 = _safe_float(financials[-1]["营业总收入"]), _safe_float(financials[-2]["营业总收入"])
                if p1 > p2 and r1 > r2: has_black_horse = True
            except Exception: pass
        if has_black_horse:
            L("  ⚡ 无机构覆盖，但近两季度净利润+营收连续环比改善，具备黑马潜质预警！")
        else:
            L("  无机构覆盖数据（中线建议规避无主流机构覆盖的冷门股）")

    # ─── 4. 研报评级风向标 ───
    L("\n【六、研报评级统计与风向变动 (近3个月)】")
    L("─" * 72)
    reports = await get_reports_async(session, code, max_pages=3)
    if reports:
        buy_count, add_count = 0, 0
        for r in reports:
            rating = str(r.get("emRatingName", ""))
            if "买入" in rating: buy_count += 1
            elif "增持" in rating: add_count += 1
        L(f"  统计样本：近 {len(reports)} 篇研报")
        L(f"  ➤ 【买入】评级: {buy_count} 篇 | 【增持】评级: {add_count} 篇")
        L(f"\n  最新 5 篇核心研报观点:")
        for r in reports[:5]:
            pub_date = str(r.get("publishDate", ""))[:10]
            org = r.get("orgSName", "")
            title = r.get("title", "")[:45]
            rating = r.get("emRatingName", "无")
            L(f"    - [{pub_date}] {org} ({rating}): {title}")
    else:
        L("  暂无相关研报评级数据。")

    # ─── 5. 重大公告追踪 ───
    L("\n【七、重大实质性公告追踪 (避雷与催化)】")
    L("─" * 72)
    anns = await get_strategic_announcements_async(session, code, days=30)
    if anns:
        for i, a in enumerate(anns[:10], 1):
            L(f"  {i}. [{a['date']}] {a['title']}")
        rc = sum(1 for a in anns if "减持" in a["title"])
        if rc > 0: L(f"\n  ⚠️ 减持预警：近期有 {rc} 条减持相关公告，请仔细甄别。")
        L("\n  💡 中线提醒：重点关注定增、股权激励、减持计划及大额中标公告。")
    else:
        L("  近期无过滤后的重大公告。")

    # ─── 6. 筹码稳定性分析 ───
    L("\n【八、筹码稳定性与抛压评估】")
    L("─" * 72)
    holders = await get_holder_change_async(session, code)
    if holders:
        L(f"  ➤ 股东户数变化趋势:")
        for h in holders[:5]:
            _cr = h['change_ratio']
            # 边界检查：变化率超过±500%视为异常数据，不显示
            _cr_disp = _cr if abs(_cr) <= 500 else (999.99 if _cr > 500 else -999.99)
            _cr_flag = " ⚠️" if abs(_cr) > 500 else ""
            L(f"    截止 {h['date']}: 股东数 {h['holder_num']:,} 户 | 环比变化 {_cr_disp:+.2f}%{_cr_flag}")
        latest = holders[0]
        if latest["change_ratio"] <= -3:
            L("    ✅ 结论: 筹码正在集中，利好中线。")
        elif latest["change_ratio"] >= 3:
            L("    ⚠️ 结论: 筹码趋于分散，散户增多，注意风险。")

    lockup = await get_lockup_expiry_async(session, code, today_str, days=180)
    if lockup:
        _cal_evts = [f"{_h['date']} 解禁{_h['ratio']:.1f}%" for _h in lockup if _h.get('ratio', 0) > 0]
        L(f"\n  ➤ 未来可预期事件:")
        if _cal_evts:
            for _ev in _cal_evts[:5]: L(f"    📅 {_ev}")
        else:
            L("    (暂无已披露近期事件)")
    if lockup:
        total_upcoming = sum(h["shares"] for h in lockup)
        L(f"\n  ➤ 解禁抛压预警 (未来180天):")
        L(f"    ⚠️ 待解禁总计: {total_upcoming/1e4:.0f}万股")
        for h in lockup:
            L(f"    - {h['date']}: {h['type']} ({h['shares']/1e4:.0f}万股, 占 {h['ratio']:.2f}%)")
    else:
        L("\n  ➤ 解禁抛压预警: 未来半年内无解禁压力 ✅")

    # ─── 北向资金持仓动态 ───
    L("\n【九、北向资金持仓动态】")
    L("─" * 72)
    nb = await get_northbound_hold_async(session, code, 20)
    if nb:
        L(f"  近 {len(nb)} 个交易日北向持仓数据:")
        L(f"  {'日期':<12} {'持股数量(万)':>12} {'持股市值(万)':>12} {'持股占比%':>10} {'变动股数(万)':>12}")
        L(f"  {'-'*65}")
        for d in nb:
            _mcap = d.get('market_cap', 0) or 0
            _ratio = d.get('hold_ratio', 0) or 0
            _shares = d.get('hold_shares', 0) or 0
            if _mcap == 0 and _shares > 0 and price_today > 0:
                _mcap = _shares * price_today
                _ratio = _shares / info.get('total_shares', 1) if info.get('total_shares', 0) > 0 else 0
            L(f"  {d['date']:<12} {_shares/1e4:>12.0f} {_mcap/1e4:>12.0f} {_ratio:>9.4f}% {d['change_shares']/1e4:>+12.0f}")
        if len(nb) >= 2:
            ratio_change = nb[0]["hold_ratio"] - nb[-1]["hold_ratio"]
            if ratio_change > 0:
                L(f"  ➤ 信号: 近{len(nb)}日北向持股比例 +{ratio_change:.4f}%，外资增持")
            elif ratio_change < 0:
                L(f"  ➤ 信号: 近{len(nb)}日北向持股比例 {ratio_change:.4f}%，外资减持")
    else:
        L("  该股暂无北向资金持仓数据（可能非陆股通标的或数据延迟）")

    # ─── 同业龙头横向对比 ───
    L("\n【十、同业龙头横向对比（赛道身位监测）】")
    L("─" * 72)
    if peer_data["peers"]:
        if "note" in peer_data["peers"][0]:
            L(f"  ⚠️ {peer_data['peers'][0]['note']}")
        else:
            L(f"  所属板块: {peer_data['industry']}")
            L(f"  本股市值: {peer_data['my_mcap']:.1f}亿元")
            if peer_data.get("my_rank", 0) > 0:
                L(f"  业内排名: 第 {peer_data['my_rank']}/{peer_data['industry_count']} 位（按总市值）")
            L(f"  {'代码':<8} {'名称':<12} {'股价':>8} {'涨跌幅%':>8} {'市值(亿)':>10} {'PE':>8} {'换手率%':>8}")
            L(f"  {'-'*70}")
            L(f"  {code:<8} {info.get('name','N/A'):<12} {price_today:>8.2f} {q.get('change_pct',0):>7.2f}% {peer_data['my_mcap']:>9.1f} {q.get('pe_ttm',0):>7.1f} {q.get('turnover_pct',0):>7.2f}% ← 本股")
            for p in peer_data["peers"]:
                L(f"  {p['code']:<8} {p['name']:<12} {p['price']:>8.2f} {p['change_pct']:>7.2f}% {p['mcap_yi']:>9.1f} {p['pe']:>7.1f} {p['turnover']:>7.2f}%")
            fin_metrics = await get_gross_margin_and_roe_async(session, code, fin_report=financials, bs_data=bs_data)
            if fin_metrics:
                gm = fin_metrics.get("gross_margin"); roe = fin_metrics.get("roe")
                parts = []
                if gm is not None: parts.append(f"毛利率 {gm:.1f}%")
                if roe is not None: parts.append(f"ROE {roe:.1f}%")
                if parts: L(f"\n  📊 本股财务质量: {' | '.join(parts)}")
    else:
        L(f"  无法获取同业数据（板块: {peer_data.get('industry', '未知')}）")

    # ─── 中线主力资金底仓流向 ───
    L("\n【十一、中线主力资金流向 (60日基准)】")
    L("─" * 72)
    fund_flow = get_fund_flow_120d(code)
    if fund_flow["data"]:
        fund_data = fund_flow["data"]
        recent_20 = fund_data[-20:]
        total_main_20 = sum(d["main_net"] for d in recent_20)
        days_bullish_20 = sum(1 for d in recent_20 if d["main_net"] > 0)
        recent_60 = fund_data[-60:]
        total_main_60 = sum(d["main_net"] for d in recent_60)
        L(f"  ➤ 近 20 个交易日：")
        L(f"    主力净流入天数: {days_bullish_20} 天 / 20 天")
        L(f"    累计主力净流入: {total_main_20/1e8:.2f} 亿元")
        L(f"  ➤ 近 60 个交易日（中期视角）：")
        L(f"    累计主力净流入: {total_main_60/1e8:.2f} 亿元")
        if total_main_60 > 0:
            L(f"    ✅ 资金面结论: 中线资金呈吸筹/护盘状态。")
        else:
            L(f"    ⚠️ 资金面结论: 中线资金呈流出状态，需结合估值谨慎判断。")
    elif fund_flow["error"]:
        L(f"  {fund_flow['error']}")
    else:
        L("  中线资金流数据获取失败。")

    if fund_flow.get("data") and len(fund_flow["data"]) >= 20:
        _p20 = [d["main_net"] for d in fund_flow["data"][-20:]]
        _pc_chg = q.get("change_pct", 0) if q else 0
        _cum_f = sum(_p20)
        if _cum_f < 0 and _pc_chg > 3:
            L(f"  ⚠️ 量价背离：近20日主力净流出{abs(_cum_f)/1e8:.2f}亿，股价涨{_pc_chg:.1f}%缺支撑")
        elif _cum_f > 0 and _pc_chg < -3:
            L(f"  💎 资金背离：股价下跌但主力净流入{_cum_f/1e8:.2f}亿，资金暗中介入")

    L("\n【十二、融资融券（两融数据，近15日）】")
    L("─" * 72)
    margin = await get_margin_trading_async(session, code)
    if margin:
        L(f"  {'日期':<12} {'融资余额(万)':>10} {'融资买入(万)':>10} {'融资偿还(万)':>10}")
        L(f"  {'-'*55}")
        for d in margin[:10]:
            L(f"  {d['date']:<12} {d['rzye']/1e4:>14.0f} {d['rzmre']/1e4:>14.0f} {d['rzche']/1e4:>14.0f}")
    else:
        L("  该股无融资融券数据（可能不是两融标的）。")

    L("\n【十三、大宗交易（机构建仓痕迹）】")
    L("─" * 72)
    bt = await get_block_trade_async(session, code)
    _one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    bt_filtered = [d for d in bt if d.get("date", "") >= _one_year_ago] if bt else []
    if bt_filtered:
        L(f"  近1年共 {len(bt_filtered)} 笔大宗交易（历史共 {len(bt)} 笔）:")
        L(f"  {'日期':<12} {'成交价':>6} {'溢价%':>6} {'成交量':>8} {'买方':<24}")
        L(f"  {'-'*75}")
        for d in bt_filtered:
            L(f"  {d['date']:<12} {d['price']:>8.2f} {d['premium_pct']:>7.2f}% {d['vol']/1e4:>8.0f}万 {d['buyer']:<24}")
    else:
        L("  无大宗交易记录。")

    L("\n【十四、龙虎榜机构动向】")
    L("─" * 72)
    dtb = await get_dragon_tiger_board_async(session, code, today_str, days=180)
    if dtb and dtb.get("records"):
        L(f"  近180日上榜 {len(dtb['records'])} 次:")
        L(f"  {'日期':<12} {'上榜原因':<50} {'净买入(万)':>9} {'换手率':>6}")
        L(f"  {'-'*85}")
        for r in dtb["records"]:
            reason = r.get("reason", "")[:48]
            L(f"  {r['date']:<12} {reason:<50} {r['net_buy']:>12.1f} {r['turnover']:>7.2f}%")

        seats = dtb["seats"]
        if seats["buy"]:
            L(f"\n  最近买入席位 TOP5:")
            L(f"  {'营业部名称':<30} {'买入(万)':>9} {'卖出(万)':>9} {'净额(万)':>9}")
            L(f"  {'-'*70}")
            for s in seats["buy"]:
                L(f"  {s['name']:<30} {s['buy_amt']:>12.1f} {s['sell_amt']:>12.1f} {s['net']:>12.1f}")
        if seats["sell"]:
            L(f"\n  最近卖出席位 TOP5:")
            L(f"  {'营业部名称':<30} {'买入(万)':>9} {'卖出(万)':>9} {'净额(万)':>9}")
            L(f"  {'-'*70}")
            for s in seats["sell"]:
                L(f"  {s['name']:<30} {s['buy_amt']:>12.1f} {s['sell_amt']:>12.1f} {s['net']:>12.1f}")
        inst = dtb["institution"]
        if inst and (inst.get("buy_amt", 0) > 0 or inst.get("sell_amt", 0) > 0):
            L(f"\n  机构买卖统计:")
            L(f"    机构买入金额: {inst['buy_amt']}万元")
            L(f"    机构卖出金额: {inst['sell_amt']}万元")
            L(f"    机构净买入: {inst['net_amt']}万元")
    else:
        L("  近180日无龙虎榜记录（白马蓝筹或近期未触发异动标准的个股，无龙虎榜属正常现象）。")

    # ─── 9. 高股息防御属性 (分红历史) ───
    L("\n【十五、高股息防御属性 (近十次分红)】")
    L("─" * 72)
    div = get_dividend_history(code)
    if div and len(div) >= 3:
        _dy = len(set(d["date"][:4] for d in div if d.get("bonus_rmb", 0) > 0))
        L(f"  📊 分红持续性: 连续{_dy}年分红")
        if _dy >= 5:
            L(f"    💎 连续5年以上分红，具备稳定防御属性")
    if div:
        L(f"  近5次分红除息记录:")
        L(f"  {'除权除息日':<14} {'每股派息(元)':>8} {'折算对应股价股息率参考'}")
        L(f"  {'-'*55}")
        for d in div[:5]:
            yield_str = f"{(d['bonus_rmb'] / price_today) * 100:.2f}%" if price_today > 0 else "N/A"
            L(f"  {d['date']:<14} {d['bonus_rmb']:>12.4f}  约 {yield_str} (按现价计)")
    else:
        L("  暂无分红记录（非防御型收息标的）。")

    # ─── 16. 十大流通股东机构动向 ───
    L("\n【十六、十大流通股东机构动向】")
    L("─" * 72)
    st = get_holder_structure(code)
    if st:
        L(f"  数据来源: 十大流通股东季报（最近 {len(st)} 期）")
        L("")
        _header = f"  {'截止':<12} {'北向':>6}  {'外资':>8}  {'境内机构':>8}  {'个人':>6}  {'Top10':>6}"
        L(_header)
        L(f"  {'-'*60}")
        for p in st:
            _cols = f"  {p['date']:<12} {p['northbound']:>5.1f}%"
            _cols += f"  {p['foreign']:>5.1f}%({p['foreign_count']})" if p['foreign_count'] else f"  {'N/A':>8}"
            _cols += f"  {p['domestic']:>5.1f}%({p['domestic_count']})" if p['domestic_count'] else f"  {'N/A':>8}"
            _cols += f"  {p['individual']:>5.1f}%({p['individual_count']})" if p['individual_count'] else f"  {'N/A':>6}"
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
            _nb_chg = (_nb_e - _nb_s)/_nb_s*100
            _bt_items.append(f"北向近{len(nb)}日持仓{_nb_chg:+.1f}%")
    if _bt_items:
        L("【回测参考】")
        for _bi in _bt_items: L(f"  📊 {_bi}")

    L("\n"+"─"*72); L("【仓位管理建议】"); L("─"*72)
    
    # V8.2: 使用统一评分接口
    from stock_common import ScoreData, calculate_score, save_score_snapshot
    
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
    if q:
        score_data.pe_ttm = q.get("pe_ttm", 0) or 0
    if peer_data and peer_data.get("peers"):
        score_data.industry_pe = sum(p.get("pe", 0) for p in peer_data["peers"]) / max(len(peer_data["peers"]), 1)
    
    # 北向数据
    if nb and len(nb) >= 2:
        score_data.northbound_change = nb[0]["hold_shares"] - nb[-1]["hold_shares"]
    
    # 机构持仓
    _st = get_holder_structure(code)
    if _st:
        score_data.institution_holding_pct = _st[0].get("domestic", 0)
    
    # 筹码数据
    if holders and len(holders) >= 2:
        score_data.holder_change_ratio = holders[0]["change_ratio"]
    
    # 计算评分
    result = calculate_score("med", score_data)
    _ps = result.total_score
    _details = result.details
    
    L(f"  评分明细: {' | '.join(_details[:6])}" if _details else None)
    if _ps >= 70: L(f"  中线评分: {_ps:.0f}/100 → 强烈推荐，仓位40%")
    elif _ps >= 45: L(f"  中线评分: {_ps:.0f}/100 → 建议配置，仓位25%")
    elif _ps >= 20: L(f"  中线评分: {_ps:.0f}/100 → 观察仓，仓位10%")
    else: L(f"  中线评分: {_ps:.0f}/100 → 暂不建议，等待基本面拐点")
    L(f"  核心驱动: 基本面拐点 / 估值 PEG / 筹码结构 / 重大事件")
    L("=" * 72)

    # 保存评分快照
    try:
        save_score_snapshot("med", code, info.get('name', ''), _ps, price_today)
    except Exception:
        pass

    output = "\n".join(filter(None, lines))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)
    return output


if __name__ == "__main__":
    args = parse_args()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sn = os.path.basename(__file__)
    time_str = datetime.now().strftime("%Y%m%d_%H%M")
    try:
        report_type = sn.split("_")[1]
    except Exception:
        report_type = "med"

    # ─── GD 认证 ───────────────────────────────────────────────
    drive, gd_proxy_set, gd_parent_folder_id, skip_upload = None, False, None, False
    if not args.no_upload:
        drive, gd_proxy_set, gd_parent_folder_id, skip_upload = init_gd(base_dir)

    os.makedirs(args.output, exist_ok=True)
    _results = []
    _cached_ind_comp = get_industry_comparison()

    # ─── Step 1: async 并行生成所有报告 ─────────────────────────────
    async def _process_one(_session, code, ts):
        result_path = os.path.join(args.output, f"{code}_{report_type}_{ts}.txt")
        try:
            await generate_report_async(_session, code, result_path,
                                        ind_comp=_cached_ind_comp, hsgt=None)
            print(f"  ✅ 已保存: {result_path}", flush=True)
            return {"code": code, "status": "成功", "error": "", "path": result_path}
        except Exception as e:
            print(f"❌ {code} 数据生成失败: {e}", flush=True)
            return {"code": code, "status": "数据失败", "error": str(e), "path": ""}

    async def _main_async():
        _codes = clean_codes(args.codes, verbose=True)
        if not _codes:
            print("  ❌ 没有有效的股票代码")
            return []
        for code in _codes:
            print(f"  📋 加入队列: {code}", flush=True)

        _session = await create_async_session()
        try:
            sem = asyncio.Semaphore(3)

            async def _limited(code):
                async with sem:
                    return await _process_one(_session, code, time_str)

            results = await asyncio.gather(*[_limited(code) for code in _codes])
            return results
        finally:
            await _session.close()

    _results = asyncio.run(_main_async())

    # ─── Step 2: 串行上传至 Google Drive（GD API 有速率限制） ──────
    for _r in _results:
        if _r["status"] == "成功" and not skip_upload and drive and gd_parent_folder_id:
            code = _r["code"]
            result_path = _r.get("path", os.path.join(args.output, f"{code}_{report_type}_{time_str}.txt"))
            gd_ok = False
            try:
                q_name = tdx_get_quote_full(code).get("name", "")
                if upload_stock_report_by_code(drive, gd_parent_folder_id, code, q_name, result_path):
                    gd_ok = True
            except Exception as gd_e:
                print(f"  ⚠️ GD 上传异常: {gd_e}", flush=True)
                _r["status"] = "GD上传异常"
                _r["error"] = str(gd_e)
            if not gd_ok:
                if _r["status"] == "成功":
                    _r["status"] = "GD上传失败"

    # 汇总
    cleanup_gd_proxy(gd_proxy_set)
    holder_cache_flush()
    cleanup_tdx()
    total = len(_results)
    ok = [r for r in _results if r["status"] == "成功"]
    fd = [r for r in _results if r["status"] == "数据失败"]
    fg = [r for r in _results if r["status"] in ("GD上传失败", "GD上传异常", "GD未连接")]
    print(f"\n{'=' * 60}\n  批量执行完成 — 共处理 {total} 只股票\n{'=' * 60}")
    print(f"  ✅ 全部成功: {len(ok)}  |  ❌ 数据失败: {len(fd)}  |  ⚠️ GD上传失败: {len(fg)}")
    for r in fd:
        print(f"    ❌ {r['code']} — {r['error'][:80]}")
    for r in fg:
        print(f"    ⚠️ {r['code']}")