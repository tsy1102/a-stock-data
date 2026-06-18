import argparse, requests, math, time, pandas as pd, re
import asyncio
from datetime import date, datetime, timedelta
import os, sys

from gd_uploader import init_gd, upload_stock_report_by_code, cleanup_gd_proxy
from tdx_client import (tdx_get_security_bars, tdx_get_quote_full,
                         tdx_get_index_bars,
                         tdx_get_historical_high, tdx_get_dividend_history,
                         tdx_get_belong_boards, tdx_get_board_list,
                         tdx_get_latest_announcements, cleanup_tdx)
from stock_common import (clean_codes, _safe_float, _request_with_retry, _quick_request, UA,
                           _market_code, eastmoney_datacenter, _em_filter,
                           _load_settings, _load_strategy_config, holder_change,
                           holder_cache_flush,
                           get_strategic_announcements, get_holder_structure,
                           get_dragon_tiger_board,
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
                           get_sina_balance_sheet, get_lockup_expiry,
                           get_eps_forecast_async, get_reports_async,
                           get_lockup_expiry_async, get_industry_peers,
                           get_sina_financial_report_async, get_sina_balance_sheet_async,
                           is_trading_day, get_market_status)

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# ==================== 长线价投核心数据模块 ====================

def industry_comparison(top_n=20):
    """V4: 全行业排名 → TDX board_list 替代 push2"""
    sectors = tdx_get_board_list(0)
    if not sectors:
        return []
    return sectors


def get_roe_trend(code, num_periods=8, financials=None, bs_data=None, total_shares=0):
    """V7.5: ROE/EPS/BPS → 从新浪财报本地计算（东财 MAINFINADATA 已删除）"""
    if not financials or not bs_data or total_shares <= 0:
        return []
    bs_map = {b.get("报告日", ""): b for b in bs_data}
    rows = []
    for fin in financials[:num_periods]:
        rd = fin.get("报告日", "")
        bs = bs_map.get(rd)
        if not bs: continue
        profit = _safe_float(fin.get("净利润", 0))
        equity = _safe_float(bs.get("归属于母公司股东权益合计", 0))
        roe = round(profit / equity * 100, 2) if equity > 0 else None
        eps = round(profit / total_shares, 4) if total_shares > 0 else None
        bps = round(equity / total_shares, 2) if total_shares > 0 else None
        rows.append({"date": rd, "roe": roe, "roe_kc": None, "eps": eps, "bps": bps})
    return rows


def get_historical_high(code):
    """V4: 历史最高价 → tdx_client 适配器（easy-tdx 替代 mootdx）"""
    return tdx_get_historical_high(code)


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
    except Exception:
        return None


# ==================== 报告生成引擎 ====================

def generate_report(code, output_path, ind_comp=None):
    """V4: 支持 ind_comp 外部缓存，批量模式下避免重复查询"""
    today_str = date.today().strftime("%Y-%m-%d")
    lines = []
    gm_rows = []
    def L(s=""): lines.append(s)

    L("=" * 72)
    L(f"  {code} 长线价投专属深度体检报告V8 — {today_str} {datetime.now().strftime('%H:%M:%S')}")
    L("=" * 72)
    L("")

    # ─── 1. 绝对估值基本盘 ───
    L("\n【一、企业基本盘与绝对估值锚点】")
    L("━" * 72)
    info = get_stock_info(code)
    q = get_tencent_quote(code)
    price_today = q.get("price", 0) if q else 0
    
    _is_td = is_trading_day()
    _mkt_status, _mkt_note = get_market_status()
    L(f"  企业名称: {info.get('name', 'N/A')} ({info.get('code', code)})（{_mkt_note}）")
    L(f"  所属板块: {info.get('industry', 'N/A')}")
    # V7.5 fix: 提前获取 peer_data_lng，避免先引用后赋值 Bug
    peer_data_lng = get_industry_peers(code, 3, info=info)
    # 行业周期定位
    try:
        _ind_name = info.get("industry", "")
        _ic_d = ind_comp if ind_comp is not None else industry_comparison(20)
        if _ic_d:
            for _id in _ic_d:
                if _id.get("name") == _ind_name or _ind_name in _id.get("name", ""):
                    _ind_rank = _id.get("rank", "?")
                    _ind_chg = _id.get("change_pct", 0)
                    # TDX BoardInfo 无涨跌家数，从 peer_data_lng.all_members 统计
                    _all_m = peer_data_lng.get("all_members", [])
                    if _all_m:
                        _ind_up = sum(1 for m in _all_m if m.get("change_pct", 0) > 0)
                        _ind_down = sum(1 for m in _all_m if m.get("change_pct", 0) < 0)
                    else:
                        _ind_up = _id.get("up_count", 0)
                        _ind_down = _id.get("down_count", 0)
                    L(f"  📊 行业周期定位: 全市场排名#{_ind_rank} | 涨幅{_ind_chg:+.2f}% | 上涨{_ind_up}家/下跌{_ind_down}家")
                    break
    except Exception: pass
    
    ext_list_date_raw = info.get("list_date", "")
    if ext_list_date_raw and len(ext_list_date_raw) >= 8:
        ext_list_year = int(ext_list_date_raw[:4])
        ext_years_listed = date.today().year - ext_list_year
        ext_list_fmt = f"{ext_list_date_raw[:4]}-{ext_list_date_raw[4:6]}-{ext_list_date_raw[6:8]}"
        ext_list_tag = "✅ 上市已满3年（长线安全标的）" if ext_years_listed >= 3 else "⚠️ 上市未满3年（次新股，警惕业绩变脸）"
        L(f"  上市日期: {ext_list_fmt}（已上市 {ext_years_listed} 年）{ext_list_tag}")
    else:
        L(f"  上市日期: {ext_list_date_raw}")
    
    ext_high_price = get_historical_high(code)
    if ext_high_price and price_today > 0:
        ext_deviation = (price_today / ext_high_price - 1) * 100
        L(f"  历史最高价: {ext_high_price:.2f}元 | 当前偏离度: {ext_deviation:+.2f}%")
        if ext_deviation <= -40:
            L(f"  🔔 深度回调：距历史最高点已下跌 {abs(ext_deviation):.0f}%，若基本面未恶化，或为长线黄金坑。")
        elif ext_deviation <= -20:
            L(f"  📉 显著回调：距历史最高点已下跌 {abs(ext_deviation):.0f}%，处于阶段性低位区域。")
    
    L(f"  总股本:   {info.get('total_shares', 0)/1e8:.2f}亿股 | 总市值: {q.get('mcap_yi', 0):.2f}亿元")
    L(f"  当前股价: {price_today:.2f}元")
    
    L(f"\n  ➤ 长线估值安全边际指标:")
    _pe = q.get('pe_ttm', 0)
    if _pe > 0:
        _ey = f"{100/_pe:.2f}%"
    else:
        _ey = "N/A"
        try:
            from tdx_client import _get_tdx_client
            c = _get_tdx_client()
            if c:
                fi = c.get_finance_info(_market_code(code), code)
                if fi is not None and not fi.empty:
                    _profit = _safe_float(fi.iloc[0].get('jing_lirun', 0))
                    _shares = _safe_float(fi.iloc[0].get('zong_guben', 0))
                    if _profit > 0 and _shares > 0 and price_today > 0:
                        _eps = _profit / _shares
                        _ey = f"{_eps / price_today * 100:.2f}%"
        except Exception: pass
    L(f"    市盈率 PE(TTM): {_pe:.2f}x (盈利收益率粗估: {_ey})")
    _pe_static = q.get('pe_static', 0)
    L(f"    市盈率 PE(静态): {_pe_static:.2f}x" if _pe > 0 and _pe_static > 0 else f"    市盈率 PE(静态): N/A（亏损）")
    L(f"    市净率 PB:      {q.get('pb', 0):.2f}x")
    
    if peer_data_lng.get("my_rank", 0) > 0 and peer_data_lng.get("industry_count", 0) > 0:
        L(f"  板块排名: 按总市值排序, 该股排名第 {peer_data_lng['my_rank']}/{peer_data_lng['industry_count']} 位")

    # ─── 2. 跨期财务纵深 ───
    # 同业估值对比
    try:
        _ic_data = _ic_d  # 预缓存或第一次结果复用
        if _ic_data and isinstance(_ic_data, list):
            _our_ind = info.get("industry", "")
            for _ind in _ic_data:
                if _ind.get("name") == _our_ind or _our_ind in _ind.get("name", ""):
                    L(f"  📊 板块横向对比: 本股PE={q.get('pe_ttm',0):.1f}x | 板块涨跌{_ind.get('change_pct',0):+.2f}%")
                    break
    except Exception: pass

    L("\n【二、跨期财务纵深与长效业绩验证 (近8个报告期)】")
    L("━" * 72)
    financials = get_sina_financial_report(code, num_periods=8)
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
            except:
                rev_yi, profit_yi = "N/A", "N/A"
            L(f"  {date_val:<12} {rev_yi:>14} {profit_yi:>14}")
        L("\n  💡 长线逻辑：观察其是否具备持续、平稳的造血能力，警惕大起大落的强周期股。")
    else:
        L("  (新浪财报数据获取失败)")

    bs_data = get_sina_balance_sheet(code)
    L(f"\n  ➤ 核心复利引擎（ROE净资产收益率追踪）:")
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

    # 毛利率 & 净利率趋势
    if financials and len(financials) >= 2:
        gm_rows = []
        for item in financials:
            try:
                rev = float(item.get("营业总收入", 0))
                cost = float(item.get("营业成本", 0))
                profit = float(item.get("净利润", 0))
                if rev > 0:
                    # 优先用东财官方毛利率(XSMLL)，手动计算为fallback
                    xsmll = item.get("XSMLL")
                    if xsmll is not None and str(xsmll) not in ("", "0"):
                        gm = float(xsmll)
                    else:
                        gm = (rev - cost) / rev * 100
                    npm = profit / rev * 100
                    gm_rows.append({"date": item.get("报告日", ""), "gm": gm, "npm": npm})
            except:
                pass
        if gm_rows:
            L(f"\n  ➤ 盈利能力与护城河追踪:")
            L(f"  {'报告期':<12} {'毛利率%':>10} {'净利率%':>10}")
            L(f"  {'-'*35}")
            for g in gm_rows:
                L(f"  {g['date']:<12} {g['gm']:>9.2f}% {g['npm']:>9.2f}%")
            latest_gm = gm_rows[0]["gm"]
            if latest_gm >= 40:
                L(f"  ✅ 毛利率 {latest_gm:.1f}% ≥ 40%，具备较强定价权与护城河。")
            elif latest_gm >= 25:
                L(f"  📊 毛利率 {latest_gm:.1f}%，处于中等水平，关注行业格局变化。")
            else:
                L(f"  ⚠️ 毛利率 {latest_gm:.1f}% < 25%，盈利能力偏薄，长线需警惕同质化竞争。")

    # ─── 3. 财务健康度排雷（经营现金流/商誉/毛利率） ───
    # CAGR计算（营收/利润3年复合增速）
    if financials and len(financials) >= 4:
        try:
            _rev3 = [_safe_float(f.get("营业总收入", "0")) for f in financials[:4] if f.get("报告日", "") > "2022-01-01"]
            _prf3 = [_safe_float(f.get("净利润", "0")) for f in financials[:4] if f.get("报告日", "") > "2022-01-01"]
            if len(_rev3) >= 4 and _rev3[0] > 0 and _rev3[-1] > 0:
                _rev_cagr = (pow(_rev3[0]/_rev3[-1], 1/3)-1)*100
                _prf_cagr_str = f"{(pow(_prf3[0]/_prf3[-1], 1/3)-1)*100:.1f}%" if _prf3[0] > 0 and _prf3[-1] > 0 else "N/A (亏损)"
                L(f"  📊 近3年营收CAGR: {_rev_cagr:.1f}% | 净利润CAGR: {_prf_cagr_str}")
        except Exception: pass

    L("\n【三、财务健康度排雷（现金流验证与商誉预警）】")
    L("━" * 72)
    # 从 TDX 获取经营现金流（统一口径，避免与 Sina 季度数据矛盾）
    _tdx_ocf = 0.0; _tdx_np = 0.0
    try:
        from tdx_client import _get_tdx_client
        c = _get_tdx_client()
        if c:
            fi = c.get_finance_info(_market_code(code), code)
            if fi is not None and not fi.empty:
                _tdx_ocf = _safe_float(fi.iloc[0].get('jingying_xianjinliu', 0))
                _tdx_np = _safe_float(fi.iloc[0].get('jing_lirun', 0))
    except Exception: pass

    # 商誉检测
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
                L(f"  ✅ 商誉占比在安全范围内 (< 20%)。")
        L(f"  资产负债率: {100 - equity_yi/asset_yi*100:.1f}%（截至 {bs_data[0].get('报告日','')}）" if asset_yi > 0 else "")
        # 有息负债率
        _st_loan = _safe_float(bs_data[0].get("短期借款", "0")) / 1e8
        _lt_loan = _safe_float(bs_data[0].get("长期借款", "0")) / 1e8
        _bd = _safe_float(bs_data[0].get("应付债券", "0")) / 1e8
        _int_debt = _st_loan + _lt_loan + _bd
        _int_ratio = _int_debt / asset_yi * 100 if asset_yi > 0 else 0
        L(f"  有息负债率: {_int_ratio:.1f}%（短期借款{_st_loan:.2f}亿+长期借款{_lt_loan:.2f}亿+债券{_bd:.2f}亿）")
        # 现金流对有息负债覆盖倍数（V7.5: 统一用 TDX）
        if _int_debt > 0 and _tdx_ocf > 0:
            _ocf_liab = _tdx_ocf / 1e8
            _cov = _ocf_liab / _int_debt
            if _cov > 2:
                L(f"    经营现金流/有息负债: {_cov:.1f}倍 ✅ 偿债能力充裕")
            elif _cov > 0.5:
                L(f"    经营现金流/有息负债: {_cov:.1f}倍 ⚠️ 偿债压力适中")
            else:
                L(f"    经营现金流/有息负债: {_cov:.1f}倍 ⚠️ 偿债压力较大")
    else:
        L("  (资产负债表数据获取失败)")
    # 经营现金流检测（V7.5: 统一用 TDX）
    if _tdx_ocf != 0 and _tdx_np != 0:
        ocf_yi = _tdx_ocf / 1e8
        np_yi = _tdx_np / 1e8
        if _tdx_np > 0:
            cash_ratio = _tdx_ocf / _tdx_np * 100
            L(f"\n  经营现金流: {ocf_yi:.2f}亿元 | 净利润: {np_yi:.2f}亿元 | 现金/利润比: {cash_ratio:.1f}%")
            if cash_ratio < 80:
                L(f"  ⚠️ 警惕：经营现金流仅为净利润的 {cash_ratio:.1f}%，存在利润造假或严重压货风险，现金含量不足！")
            else:
                L(f"  ✅ 经营现金流覆盖净利润充足 (> 80%)，利润含金量高。")
        elif _tdx_np < 0 and _tdx_ocf < 0:
            L(f"\n  经营现金流: {ocf_yi:.2f}亿元 | 净利润: {np_yi:.2f}亿元 (均为负值，持续失血状态)")
        else:
            L(f"\n  经营现金流: {ocf_yi:.2f}亿元 | 净利润: {np_yi:.2f}亿元")
    elif _tdx_ocf != 0:
        L(f"  经营现金流: {_tdx_ocf/1e8:.2f}亿元 (财务数据不足，无法计算现金/利润比)")
    else:
        L("  (经营现金流数据获取失败)")
    # 核心财务指标（V7.5: 从 Sina 财报 + TDX finance_info 本地计算）
    parts = []
    if gm_rows:
        parts.append(f"毛利率 {gm_rows[0]['gm']:.2f}%")
        parts.append(f"净利率 {gm_rows[0]['npm']:.2f}%")
    if ext_roe_data and ext_roe_data[0].get("roe") is not None:
        parts.append(f"ROE {ext_roe_data[0]['roe']:.2f}%")
    if ext_roe_data and ext_roe_data[0].get("eps") is not None:
        parts.append(f"EPS {ext_roe_data[0]['eps']:.4f}")
    # TDX 补充：经营现金流
    try:
        from tdx_client import _get_tdx_client
        client = _get_tdx_client()
        if client:
            tdx_fi = client.get_finance_info(_market_code(code), code)
            if tdx_fi is not None and not tdx_fi.empty:
                ocf = _safe_float(tdx_fi.iloc[0].get('jingying_xianjinliu', 0)) / 1e8
                if ocf != 0:
                    parts.append(f"经营现金流 {ocf:.2f}亿")
    except Exception: pass
    if parts:
        L("\n  ➤ 当期核心财务指标一览:")
        for p in parts:
            L(f"    {p}")
    L("\n  💡 长线排雷：持续的经营现金净流入是检验账面利润真实性的最佳标准，高商誉+低现金含量=高危组合。")

    # ─── 4. 未来三年预期与均值回归 ───
    L("\n【四、未来三年机构一致预期与 PEG 均值回归模型】")
    L("━" * 72)
    df_eps = get_eps_forecast(code)
    eps_cur = eps_next = None
    eps_has_data = False
    if not df_eps.empty and len(df_eps.columns) >= 3:
        L(f"  {'年度':<10} {'覆盖机构数':>7} {'预测EPS均值':<9}")
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
            L(f"  东财研报一致预期EPS (同花顺兜底):")
            L(f"  {'年度':<14} {'预测EPS'}")
            L(f"  {'-'*30}")
            if eps_cur:
                L(f"  {this_year:<14} {eps_cur:.3f}")
            if eps_next:
                L(f"  {this_year + 1:<14} {eps_next:.3f}")
    if eps_has_data and price_today and eps_cur and eps_cur > 0:
        pe_fwd = price_today / eps_cur
        L(f"\n  ➤ 基于机构预期的远期估值消化推演:")
        L(f"    前向市盈率 (本年度): {pe_fwd:.2f}x")
        if eps_next and eps_cur > 0:
            cagr = (eps_next / eps_cur) - 1
            L(f"    未来一年预期净利增速: {cagr*100:.1f}%")
            peg = pe_fwd / (cagr * 100) if cagr > 0 else float("inf")
            if peg > 5:
                L(f"    PEG: >5.0（增速过低或PE过高导致极端值，不具参考意义）")
            else:
                L(f"    PEG (市盈率相对盈利增长比率): {peg:.2f} (长线买入参考: <1低估, 1-1.5合理)")
            if cagr > 0:
                digest_25 = math.log(pe_fwd / 25) / math.log(1 + cagr) if pe_fwd > 25 else 0
                # PE历史分位数
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
                except Exception: pass
                if digest_25 > 0:
                    L(f"    模型测算：当前估值消化至 25 倍合理市盈率约需 {digest_25:.1f} 年")
                else:
                    L(f"    模型测算：当前估值已低于/等于 25 倍合理水位线，具备长线配置的安全垫。")
    else:
        L("  无足够机构覆盖（冷门标的，长线投研需完全依赖自主财务尽调）。")

    # ─── 5. 长效股东回报 ───
    L("\n【五、长效股东回报属性 (分红与股息历史)】")
    L("━" * 72)
    div = get_dividend_history(code)
    if div:
        L(f"  近5次分红除息记录:")
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
    else:
        L("  暂无任何分红派息记录 (一毛不拔，纯博弈型或极早期成长型企业，长线防御力弱)。")

    # ─── 6. 长线筹码沉淀与机构持股倾向 ───
    L("\n【六、长线筹码沉淀与机构持股倾向】")
    L("━" * 72)
    st = get_holder_structure(code)
    if st:
        L(f"  数据来源: 十大流通股东季报（最近 {len(st)} 期）")
        L("")
        # 表头
        _header = f"  {'截止':<12} {'北向':>6}  {'外资':>8}  {'境内机构':>8}  {'个人':>6}  {'Top10':>6}"
        L(_header)
        L(f"  {'-'*60}")
        for p in st:
            _cols = f"  {p['date']:<12} {p['northbound']:>5.1f}%"
            _cols += f"  {p['foreign']:>5.1f}%({p['foreign_count']})" if p['foreign_count'] else f"  {'-':>8}"
            _cols += f"  {p['domestic']:>5.1f}%({p['domestic_count']})" if p['domestic_count'] else f"  {'-':>8}"
            _cols += f"  {p['individual']:>5.1f}%({p['individual_count']})" if p['individual_count'] else f"  {'-':>6}"
            _cols += f"  {p['total']:>5.1f}%"
            L(_cols)
        L("")
        # 境内机构细分 + 筹码锁定度
        _dd = st[0].get("dm_detail", {})
        if _dd:
            _parts = [f"{k} {v:.1f}%" for k, v in _dd.items()]
            L(f"  境内机构细分: {' | '.join(_parts)}")
            # 筹码锁定度 = 国资 + 证金汇金 + 公募 + 险资 + 社保
            _lock = sum(v for v in _dd.values()) + st[0].get("northbound", 0)
            if _lock >= 60:
                L(f"  🔒 筹码锁定度: {_lock:.1f}%（含北向），流通盘高度锁定，稍有题材风口即易拉长阳")
        L("")

        # 最新一期分析
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

        # 多期趋势
        if len(st) >= 2:
            prv = st[-1]  # 最早一期
            chg = latest['total'] - prv['total']
            if abs(chg) >= 1:
                _dir = "↑" if chg > 0 else "↓"
                L(f"\n  持股集中度变化: {prv['total']:.1f}% → {latest['total']:.1f}% ({_dir}{abs(chg):.1f}个百分点)")
                if chg > 1:
                    L(f"    ✅ 筹码趋于集中，主力资金持续吸筹")
                elif chg < -1:
                    L(f"    ⚠️ 筹码趋于分散，主力可能在出货")
    else:
        L("  机构持股数据获取失败。")

    # ─── 7. 达摩克利斯之剑：解禁 ───
    L("\n【七、达摩克利斯之剑：长周期限售股解禁压力】")
    L("━" * 72)
    lockup = get_lockup_expiry(code, today_str, days=730)
    if lockup:
        total_upcoming = sum(h["shares"] for h in lockup)
        L(f"  ⚠️ 未来 2 年内待解禁总计: {total_upcoming/1e4:.0f} 万股")
        _price = q.get("price", 0) if q else 0
        _fmc = q.get("float_mcap_yi", 1) if q else 1
        for h in lockup:
            _jiejin_mc = (h['shares']/1e4 * _price / 1e8) if _price > 0 else 0
            _jiejin_pct = _jiejin_mc / _fmc * 100 if _fmc > 0 else 0
            _jiejin_tag = "🔴" if _jiejin_pct > 5 else ("🟡" if _jiejin_pct > 1 else "🟢")
            L(f"    - {h['date']}: {h['type']} ({h['shares']/1e4:.0f}万股, 解禁市值{_jiejin_mc:.1f}亿 占流通{_jiejin_pct:.1f}% {_jiejin_tag})")
        L("\n  💡 长线避雷：警惕首发原股东或巨额定向增发的集中解禁潮。")
    else:
        L("  ✅ 未来 2 年内无解禁压力，全流通或结构稳定。")

    # ─── 8. 战略级公告跟踪 ───
    L("\n【八、战略级别重大公告 (回购/增持/员工持股/年报)】")
    L("━" * 72)
    anns = get_strategic_announcements(code)
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



    # ─── 9. 机构长效共识度与投研透明度 ───
    L("\n【九、机构长效共识度与投研透明度】")
    L("━" * 72)
    reports = get_reports(code, max_pages=5)
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
        
        L(f"\n  最新 10 篇核心研报观点:")
        L(f"  {'日期':<12} {'机构':<16} {'评级':<10} {'标题'}")
        L(f"  {'-'*70}")
        _rp = [r for r in reports if str(r.get("publishDate",""))[:10] >= (date.today() - timedelta(days=730)).strftime("%Y-%m-%d")]
        for r in _rp[:10]:
            pub_date = str(r.get("publishDate", ""))[:10]
            org = r.get("orgSName", "")
            rating = r.get("emRatingName", "")
            title = r.get("title", "")[:50]
            L(f"  {pub_date:<12} {org:<16} {str(rating):<10} {title}")
        if len(org_set) > 10:
            L(f"\n  ✅ 结论：该股受到主流外脑机构的广泛覆盖，基本面透明度高，财务造假阻力大。")
        elif len(org_set) == 0:
            L(f"  ⚠️ 结论：机构荒漠，散户主导的冷门股，长线重仓需谨慎。")
    else:
        L("  暂无任何研报覆盖数据。")

    L("\n"+"━"*72); L("【仓位管理建议】"); L("━"*72)
    
    # V8.2: 使用统一评分接口
    from stock_common import ScoreData, calculate_score, save_score_snapshot
    
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
        _np = float(financials[0].get("净利润", 1)) if financials else 1
        if _np > 0:
            score_data.ocf_ratio = _tdx_ocf / _np
        if bs_data:
            _st = _safe_float(bs_data[0].get("短期借款", "0")) / 1e8
            _lt = _safe_float(bs_data[0].get("长期借款", "0")) / 1e8
            _ta = _safe_float(bs_data[0].get("资产总计", "1")) / 1e8
            if _ta > 0:
                score_data.asset_liability_ratio = (_st + _lt) / _ta
    
    # 机构持仓
    _inst = get_holder_structure(code)
    if _inst:
        score_data.institution_holding_pct = _inst[0].get("domestic", 0) + _inst[0].get("northbound", 0)
    
    # 计算评分
    result = calculate_score("lng", score_data)
    _ps = result.total_score
    _details = result.details
    
    L(f"  评分明细: {' | '.join(_details[:6])}" if _details else None)
    if _ps>=70: L(f"  长线评分: {_ps:.0f}/100 → 优质长线标的，仓位50%")
    elif _ps>=45: L(f"  长线评分: {_ps:.0f}/100 → 可配置，仓位30%")
    elif _ps>=20: L(f"  长线评分: {_ps:.0f}/100 → 观察仓，仓位15%")
    else: L(f"  长线评分: {_ps:.0f}/100 → 暂不建议，等待更好的安全边际")
    L("\n" + "=" * 72)
    L(f"  长线基石: 强劲自由现金流 / 持续高 ROE / 合理估值 / 高股息防御")
    L("=" * 72)

    # 保存评分快照
    try:
        save_score_snapshot("lng", code, info.get('name', ''), _ps, price_today)
    except Exception:
        pass

    output = "\n".join(filter(None, lines))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)
    return output


async def generate_report_async(session, code, output_path, ind_comp=None):
    """async 版: 长线价值体检报告生成引擎"""
    today_str = date.today().strftime("%Y-%m-%d")
    lines = []
    gm_rows = []
    def L(s=""): lines.append(s)

    L("=" * 72)
    L(f"  {code} 长线价投专属深度体检报告V8 — {today_str} {datetime.now().strftime('%H:%M:%S')}")
    L("=" * 72)
    L("")

    L("\n【一、企业基本盘与绝对估值锚点】")
    L("━" * 72)
    info = get_stock_info(code)
    q = get_tencent_quote(code)
    price_today = q.get("price", 0) if q else 0
    
    _is_td = is_trading_day()
    _mkt_status, _mkt_note = get_market_status()
    L(f"  企业名称: {info.get('name', 'N/A')} ({info.get('code', code)})（{_mkt_note}）")
    L(f"  所属板块: {info.get('industry', 'N/A')}")
    peer_data_lng = get_industry_peers(code, 3, info=info)
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
    except Exception: pass
    
    ext_list_date_raw = info.get("list_date", "")
    if ext_list_date_raw and len(ext_list_date_raw) >= 8:
        ext_list_year = int(ext_list_date_raw[:4])
        ext_years_listed = date.today().year - ext_list_year
        ext_list_fmt = f"{ext_list_date_raw[:4]}-{ext_list_date_raw[4:6]}-{ext_list_date_raw[6:8]}"
        ext_list_tag = "✅ 上市已满3年（长线安全标的）" if ext_years_listed >= 3 else "⚠️ 上市未满3年（次新股，警惕业绩变脸）"
        L(f"  上市日期: {ext_list_fmt}（已上市 {ext_years_listed} 年）{ext_list_tag}")
    else:
        L(f"  上市日期: {ext_list_date_raw}")
    
    ext_high_price = get_historical_high(code)
    if ext_high_price and price_today > 0:
        ext_deviation = (price_today / ext_high_price - 1) * 100
        L(f"  历史最高价: {ext_high_price:.2f}元 | 当前偏离度: {ext_deviation:+.2f}%")
        if ext_deviation <= -40:
            L(f"  🔔 深度回调：距历史最高点已下跌 {abs(ext_deviation):.0f}%，若基本面未恶化，或为长线黄金坑。")
        elif ext_deviation <= -20:
            L(f"  📉 显著回调：距历史最高点已下跌 {abs(ext_deviation):.0f}%，处于阶段性低位区域。")
    
    L(f"  总股本:   {info.get('total_shares', 0)/1e8:.2f}亿股 | 总市值: {q.get('mcap_yi', 0):.2f}亿元")
    L(f"  当前股价: {price_today:.2f}元")
    
    L(f"\n  ➤ 长线估值安全边际指标:")
    _pe = q.get('pe_ttm', 0)
    if _pe > 0:
        _ey = f"{100/_pe:.2f}%"
    else:
        _ey = "N/A"
        try:
            from tdx_client import _get_tdx_client
            c = _get_tdx_client()
            if c:
                fi = c.get_finance_info(_market_code(code), code)
                if fi is not None and not fi.empty:
                    _profit = _safe_float(fi.iloc[0].get('jing_lirun', 0))
                    _shares = _safe_float(fi.iloc[0].get('zong_guben', 0))
                    if _profit > 0 and _shares > 0 and price_today > 0:
                        _eps = _profit / _shares
                        _ey = f"{_eps / price_today * 100:.2f}%"
        except Exception: pass
    L(f"    市盈率 PE(TTM): {_pe:.2f}x (盈利收益率粗估: {_ey})")
    _pe_static = q.get('pe_static', 0)
    L(f"    市盈率 PE(静态): {_pe_static:.2f}x" if _pe > 0 and _pe_static > 0 else f"    市盈率 PE(静态): N/A（亏损）")
    L(f"    市净率 PB:      {q.get('pb', 0):.2f}x")
    
    if peer_data_lng.get("my_rank", 0) > 0 and peer_data_lng.get("industry_count", 0) > 0:
        L(f"  板块排名: 按总市值排序, 该股排名第 {peer_data_lng['my_rank']}/{peer_data_lng['industry_count']} 位")

    try:
        _ic_data = _ic_d if '_ic_d' in dir() else None
        if _ic_data and isinstance(_ic_data, list):
            _our_ind = info.get("industry", "")
            for _ind in _ic_data:
                if _ind.get("name") == _our_ind or _our_ind in _ind.get("name", ""):
                    L(f"  📊 板块横向对比: 本股PE={q.get('pe_ttm',0):.1f}x | 板块涨跌{_ind.get('change_pct',0):+.2f}%")
                    break
    except Exception: pass

    L("\n【二、跨期财务纵深与长效业绩验证 (近8个报告期)】")
    L("━" * 72)
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
            except:
                rev_yi, profit_yi = "N/A", "N/A"
            L(f"  {date_val:<12} {rev_yi:>14} {profit_yi:>14}")
        L("\n  💡 长线逻辑：观察其是否具备持续、平稳的造血能力，警惕大起大落的强周期股。")
    else:
        L("  (新浪财报数据获取失败)")

    bs_data = await get_sina_balance_sheet_async(session, code)
    L(f"\n  ➤ 核心复利引擎（ROE净资产收益率追踪）:")
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
            except:
                pass
        if gm_rows:
            L(f"\n  ➤ 盈利能力与护城河追踪:")
            L(f"  {'报告期':<12} {'毛利率%':>10} {'净利率%':>10}")
            L(f"  {'-'*35}")
            for g in gm_rows:
                L(f"  {g['date']:<12} {g['gm']:>9.2f}% {g['npm']:>9.2f}%")
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
        except Exception: pass

    L("\n【三、财务健康度排雷（现金流验证与商誉预警）】")
    L("━" * 72)
    _tdx_ocf = 0.0; _tdx_np = 0.0
    try:
        from tdx_client import _get_tdx_client
        c = _get_tdx_client()
        if c:
            fi = c.get_finance_info(_market_code(code), code)
            if fi is not None and not fi.empty:
                _tdx_ocf = _safe_float(fi.iloc[0].get('jingying_xianjinliu', 0))
                _tdx_np = _safe_float(fi.iloc[0].get('jing_lirun', 0))
    except Exception: pass

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
                L(f"  ✅ 商誉占比在安全范围内 (< 20%)。")
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
                L(f"    经营现金流/有息负债: {_cov:.1f}倍 ✅ 偿债能力充裕")
            elif _cov > 0.5:
                L(f"    经营现金流/有息负债: {_cov:.1f}倍 ⚠️ 偿债压力适中")
            else:
                L(f"    经营现金流/有息负债: {_cov:.1f}倍 ⚠️ 偿债压力较大")
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
                L(f"  ✅ 经营现金流覆盖净利润充足 (> 80%)，利润含金量高。")
        elif _tdx_np < 0 and _tdx_ocf < 0:
            L(f"\n  经营现金流: {ocf_yi:.2f}亿元 | 净利润: {np_yi:.2f}亿元 (均为负值，持续失血状态)")
        else:
            L(f"\n  经营现金流: {ocf_yi:.2f}亿元 | 净利润: {np_yi:.2f}亿元")
    elif _tdx_ocf != 0:
        L(f"  经营现金流: {_tdx_ocf/1e8:.2f}亿元 (财务数据不足，无法计算现金/利润比)")
    else:
        L("  (经营现金流数据获取失败)")
    parts = []
    if gm_rows and 'gm_rows' in dir():
        pass
    _gm_rows_ref = locals().get('gm_rows', [])
    if _gm_rows_ref:
        parts.append(f"毛利率 {_gm_rows_ref[0]['gm']:.2f}%")
        parts.append(f"净利率 {_gm_rows_ref[0]['npm']:.2f}%")
    if ext_roe_data and ext_roe_data[0].get("roe") is not None:
        parts.append(f"ROE {ext_roe_data[0]['roe']:.2f}%")
    if ext_roe_data and ext_roe_data[0].get("eps") is not None:
        parts.append(f"EPS {ext_roe_data[0]['eps']:.4f}")
    try:
        from tdx_client import _get_tdx_client
        client = _get_tdx_client()
        if client:
            tdx_fi = client.get_finance_info(_market_code(code), code)
            if tdx_fi is not None and not tdx_fi.empty:
                ocf = _safe_float(tdx_fi.iloc[0].get('jingying_xianjinliu', 0)) / 1e8
                if ocf != 0:
                    parts.append(f"经营现金流 {ocf:.2f}亿")
    except Exception: pass
    if parts:
        L("\n  ➤ 当期核心财务指标一览:")
        for p in parts:
            L(f"    {p}")
    L("\n  💡 长线排雷：持续的经营现金净流入是检验账面利润真实性的最佳标准，高商誉+低现金含量=高危组合。")

    L("\n【四、未来三年机构一致预期与 PEG 均值回归模型】")
    L("━" * 72)
    df_eps = await get_eps_forecast_async(session, code)
    eps_cur = eps_next = None
    eps_has_data = False
    if not df_eps.empty and len(df_eps.columns) >= 3:
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
            except:
                pass
    if not eps_has_data:
        em_eps = await _get_eps_from_em_reports_async(session, code)
        if em_eps:
            eps_cur = em_eps["eps_cur"]
            eps_next = em_eps["eps_next"]
            eps_has_data = True
            this_year = date.today().year
            L(f"  东财研报一致预期EPS (同花顺兜底):")
            L(f"  {'年度':<14} {'预测EPS'}")
            L(f"  {'-'*30}")
            if eps_cur:
                L(f"  {this_year:<14} {eps_cur:.3f}")
            if eps_next:
                L(f"  {this_year + 1:<14} {eps_next:.3f}")
    if eps_has_data and price_today and eps_cur and eps_cur > 0:
        pe_fwd = price_today / eps_cur
        L(f"\n  ➤ 基于机构预期的远期估值消化推演:")
        L(f"    前向市盈率 (本年度): {pe_fwd:.2f}x")
        if eps_next and eps_cur > 0:
            cagr = (eps_next / eps_cur) - 1
            L(f"    未来一年预期净利增速: {cagr*100:.1f}%")
            peg = pe_fwd / (cagr * 100) if cagr > 0 else float("inf")
            if peg > 5:
                L(f"    PEG: >5.0（增速过低或PE过高导致极端值，不具参考意义）")
            else:
                L(f"    PEG (市盈率相对盈利增长比率): {peg:.2f} (长线买入参考: <1低估, 1-1.5合理)")
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
                except Exception: pass
                if digest_25 > 0:
                    L(f"    模型测算：当前估值消化至 25 倍合理市盈率约需 {digest_25:.1f} 年")
                else:
                    L(f"    模型测算：当前估值已低于/等于 25 倍合理水位线，具备长线配置的安全垫。")
    else:
        L("  无足够机构覆盖（冷门标的，长线投研需完全依赖自主财务尽调）。")

    L("\n【五、长效股东回报属性 (分红与股息历史)】")
    L("━" * 72)
    div = get_dividend_history(code)
    if div:
        L(f"  近5次分红除息记录:")
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
    else:
        L("  暂无任何分红派息记录 (一毛不拔，纯博弈型或极早期成长型企业，长线防御力弱)。")

    L("\n【六、长线筹码沉淀与机构持股倾向】")
    L("━" * 72)
    st = get_holder_structure(code)
    if st:
        L(f"  数据来源: 十大流通股东季报（最近 {len(st)} 期）")
        L("")
        _header = f"  {'截止':<12} {'北向':>6}  {'外资':>8}  {'境内机构':>8}  {'个人':>6}  {'Top10':>6}"
        L(_header)
        L(f"  {'-'*60}")
        for p in st:
            _cols = f"  {p['date']:<12} {p['northbound']:>5.1f}%"
            _cols += f"  {p['foreign']:>5.1f}%({p['foreign_count']})" if p['foreign_count'] else f"  {'-':>8}"
            _cols += f"  {p['domestic']:>5.1f}%({p['domestic_count']})" if p['domestic_count'] else f"  {'-':>8}"
            _cols += f"  {p['individual']:>5.1f}%({p['individual_count']})" if p['individual_count'] else f"  {'-':>6}"
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
                    L(f"    ✅ 筹码趋于集中，主力资金持续吸筹")
                elif chg < -1:
                    L(f"    ⚠️ 筹码趋于分散，主力可能在出货")
    else:
        L("  机构持股数据获取失败。")

    L("\n【七、达摩克利斯之剑：长周期限售股解禁压力】")
    L("━" * 72)
    lockup = await get_lockup_expiry_async(session, code, today_str, days=730)
    if lockup:
        total_upcoming = sum(h["shares"] for h in lockup)
        L(f"  ⚠️ 未来 2 年内待解禁总计: {total_upcoming/1e4:.0f} 万股")
        _price = q.get("price", 0) if q else 0
        _fmc = q.get("float_mcap_yi", 1) if q else 1
        for h in lockup:
            _jiejin_mc = (h['shares']/1e4 * _price / 1e8) if _price > 0 else 0
            _jiejin_pct = _jiejin_mc / _fmc * 100 if _fmc > 0 else 0
            _jiejin_tag = "🔴" if _jiejin_pct > 5 else ("🟡" if _jiejin_pct > 1 else "🟢")
            L(f"    - {h['date']}: {h['type']} ({h['shares']/1e4:.0f}万股, 解禁市值{_jiejin_mc:.1f}亿 占流通{_jiejin_pct:.1f}% {_jiejin_tag})")
        L("\n  💡 长线避雷：警惕首发原股东或巨额定向增发的集中解禁潮。")
    else:
        L("  ✅ 未来 2 年内无解禁压力，全流通或结构稳定。")

    L("\n【八、战略级别重大公告 (回购/增持/员工持股/年报)】")
    L("━" * 72)
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
    L("━" * 72)
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
        
        L(f"\n  最新 10 篇核心研报观点:")
        L(f"  {'日期':<12} {'机构':<16} {'评级':<10} {'标题'}")
        L(f"  {'-'*70}")
        _rp = [r for r in reports if str(r.get("publishDate",""))[:10] >= (date.today() - timedelta(days=730)).strftime("%Y-%m-%d")]
        for r in _rp[:10]:
            pub_date = str(r.get("publishDate", ""))[:10]
            org = r.get("orgSName", "")
            rating = r.get("emRatingName", "")
            title = r.get("title", "")[:50]
            L(f"  {pub_date:<12} {org:<16} {str(rating):<10} {title}")
        if len(org_set) > 10:
            L(f"\n  ✅ 结论：该股受到主流外脑机构的广泛覆盖，基本面透明度高，财务造假阻力大。")
        elif len(org_set) == 0:
            L(f"  ⚠️ 结论：机构荒漠，散户主导的冷门股，长线重仓需谨慎。")
    else:
        L("  暂无任何研报覆盖数据。")

    L("\n"+"━"*72); L("【仓位管理建议】"); L("━"*72)
    
    # V8.2: 使用统一评分接口
    from stock_common import ScoreData, calculate_score, save_score_snapshot
    
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
        _np = float(financials[0].get("净利润", 1)) if financials else 1
        if _np > 0:
            score_data.ocf_ratio = _tdx_ocf / _np
        if bs_data:
            _st = _safe_float(bs_data[0].get("短期借款", "0")) / 1e8
            _lt = _safe_float(bs_data[0].get("长期借款", "0")) / 1e8
            _ta = _safe_float(bs_data[0].get("资产总计", "1")) / 1e8
            if _ta > 0:
                score_data.asset_liability_ratio = (_st + _lt) / _ta
    
    # 机构持仓
    _inst = get_holder_structure(code)
    if _inst:
        score_data.institution_holding_pct = _inst[0].get("domestic", 0) + _inst[0].get("northbound", 0)
    
    # 计算评分
    result = calculate_score("lng", score_data)
    _ps = result.total_score
    _details = result.details
    
    L(f"  评分明细: {' | '.join(_details[:6])}" if _details else None)
    if _ps>=70: L(f"  长线评分: {_ps:.0f}/100 → 优质长线标的，仓位50%")
    elif _ps>=45: L(f"  长线评分: {_ps:.0f}/100 → 可配置，仓位30%")
    elif _ps>=20: L(f"  长线评分: {_ps:.0f}/100 → 观察仓，仓位15%")
    else: L(f"  长线评分: {_ps:.0f}/100 → 暂不建议，等待更好的安全边际")
    L("\n" + "=" * 72)
    L(f"  长线基石: 强劲自由现金流 / 持续高 ROE / 合理估值 / 高股息防御")
    L("=" * 72)

    # 保存评分快照
    try:
        save_score_snapshot("lng", code, info.get('name', ''), _ps, price_today)
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
        report_type = "lng"

    # ─── GD 认证 ───────────────────────────────────────────────
    drive, gd_proxy_set, gd_parent_folder_id, skip_upload = None, False, None, False
    if not args.no_upload:
        drive, gd_proxy_set, gd_parent_folder_id, skip_upload = init_gd(base_dir)

    os.makedirs(args.output, exist_ok=True)
    _results = []
    _cached_ind_comp = industry_comparison(20)

    # ─── Step 1: async 并行生成所有报告 ─────────────────────────────
    async def _process_one(_session, code, ts):
        result_path = os.path.join(args.output, f"{code}_{report_type}_{ts}.txt")
        try:
            await generate_report_async(_session, code, result_path, ind_comp=_cached_ind_comp)
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

            if not gd_ok and drive:
                _r["status"] = "GD上传失败"
            elif not drive:
                _r["status"] = "GD未连接"

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