#!/usr/bin/env python3
"""
get_mak_report.py — A股异动及行业轮动扫描报告 (V9.3.3)
融合全市场异动扫描与行业轮动强度扫描

版本信息:
    V9.3.3 2026-07-10 - 代码质量提升：删除过时注释，精简代码
    V9.3.2 2026-07-09 - 基础设施修复：TDX K线假数据防护、SQLite WAL死锁修复、代理环境兼容（脚本本身无改动，受益于底层修复）
    V9.3 2026-07-07 - 盘前行情模式：9:30前使用上一交易日日K线数据；删除报告标题硬编码版本号
    V9.2 2026-07-05 - 异常处理规范化；缓存交叉验证机制启用
    V9.1 2026-07-04 - 版本号统一升级（无功能变更，F10 公告兜底已在 V9.0 实现）
    V9.0 2026-07-02 - 舆情互动层（Layer 10）；上市日期 push2 fallback；valid_if 校验；_has_zero_price 拦截
    V8.9 2026-06-29 - 修复模块导入；清理冗余空行输出；模块版本统一
    V8.7 2026-06-25 - 死代码清理：同步版替换为薄包装
"""
import argparse, requests, json, time, math, os, warnings
from datetime import date, datetime, timedelta
from collections import Counter
warnings.filterwarnings('ignore')
from gd_uploader import init_gd, upload_type_reports, cleanup_gd_proxy
from tdx_client import (tdx_get_security_bars, tdx_get_index_bars,
                         tdx_get_board_list, tdx_get_board_members,
                         tdx_get_quotes_batch, tdx_get_market_abnormal_data,
                         cleanup_tdx)
from stock_common import (_safe_float, _request_with_retry, _quick_request, UA, _debug_log,
                          _load_strategy_config, get_recent_dragon_tiger,
                          parse_args as common_parse_args,
                          is_trading_day, get_market_status)

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 加载策略阈值配置（模块级缓存，check_stock 函数中使用）
_sc_ma = _load_strategy_config()
_abnl = _sc_ma.get("abnormal", {})
_ret10_warn = _abnl.get("ret_10d_warn", 70.0)  # 10日累计涨幅警示阈值
_ret10_down = _abnl.get("ret_10d_severe_down", -50.0)  # 10日严重下跌阈值
_vol_locked = _abnl.get("volume_locked_pct", 3.0)  # 极度锁仓阈值
_vol_overload = _abnl.get("volume_overload_pct", 25.0)  # 爆量阈值


def _fmt_ret(v):
    if v is None: return "N/A"
    return f"{v:+.2f}"

INDEX_MAP = {"sh000001":"上证指数","sz399001":"深证成指","sz399102":"创业板综指","sz399106":"深证综指","sz399006":"创业板指","sh000688":"科创综指"}

def get_stock_index(code):
    if code.startswith("688"): return "sh000688"
    elif code.startswith(("300","301")): return "sz399102"
    elif code.startswith("6"): return "sh000001"
    elif code.startswith(("000","001","002","003")): return "sz399001"
    else: return "sz399001"

def get_threshold(code, name):
    if "ST" in name or "*ST" in name: return 12
    if code.startswith(("300","301","688")): return 30
    return 20

def get_board_name(code, name):
    if "ST" in name or "*ST" in name: return "ST"
    if code.startswith("688"): return "科创板"
    if code.startswith(("300","301")): return "创业板"
    return "主板"

def calc_official_deviation(stock_ret, index_ret):
    if index_ret is None: return 0.0
    s_val = 1 + stock_ret / 100.0
    i_val = 1 + index_ret / 100.0
    if i_val <= 0: return 0.0
    return round((s_val / i_val - 1) * 100, 2)

def get_market_abnormal_data():
    """V7: 全市场 + 多周期涨幅 → TDX MAC 协议（push2 fallback 已删除）"""
    return tdx_get_market_abnormal_data()

def get_baidu_kline(code, days=20):
    """V4: K线数据 → tdx_client 适配器（TDX日K线，自动fallback百度）"""
    keys, rows = tdx_get_security_bars(code, count=days + 10)
    if not keys or not rows:
        return [], []
    idx_map = {k: i for i, k in enumerate(keys)}
    ci = idx_map.get('close', -1)
    vi = idx_map.get('volume', -1)
    if ci < 0:
        return [], []
    closes = [_safe_float(r[ci]) for r in rows[-days:] if len(r) > ci]
    vols = [_safe_float(r[vi]) for r in rows[-days:] if len(r) > vi and vi >= 0] if vi >= 0 else []
    return closes, vols

def get_index_returns():
    def _calc(closes, days):
        if len(closes) < days + 1: return None
        return (closes[-1] - closes[-(days+1)]) / closes[-(days+1)] * 100 if closes[-(days+1)] > 0 else None
    def _get_kline(ic):
        """V7: 指数K线 → TDX → 百度PAE → 腾讯（兜底）"""
        keys, rows = tdx_get_index_bars(ic, count=250)
        if keys and rows:
            ci = next((i for i,k in enumerate(keys) if k in ("close","close_price")), -1)
            if ci >= 0:
                closes = [_safe_float(r[ci]) for r in rows if len(r) > ci]
                if closes:
                    return closes
        # 腾讯兜底：至少拿到最新收盘价（只能算 1 日回报）
        try:
            r = _quick_request(f"https://qt.gtimg.cn/q={ic}", timeout=10)
            if r:
                r.encoding = "gbk"
                v = r.text.split('"')[1].split("~")
                close = _safe_float(v[3])
                pre_close = _safe_float(v[4])
                return [pre_close, close] if close > 0 else []
        except Exception as _e:
            _debug_log(f"mak index_kline error: {_e}")
            return []
    result = {}; closes_pool = {}
    for ic in INDEX_MAP:
        closes = _get_kline(ic)
        closes_pool[ic] = closes
        result[ic] = {"ret_3d":_calc(closes,3),"ret_10d":_calc(closes,10),"ret_20d":_calc(closes,20),"ret_60d":_calc(closes,60)}
    return result, closes_pool

def get_abnormal_announcements(code):
    try:
        td = date.today().strftime("%Y-%m-%d"); sd = (date.today()-timedelta(days=7)).strftime("%Y-%m-%d")
        oid = "gssh0"+code if code.startswith("6") else ("gsbj0"+code if code.startswith(("8","4")) else "gssz0"+code)
        # orgId精准查询
        payload = {"orgId":oid,"stock":f"{code},{oid}","tabName":"fulltext","pageSize":"10","pageNum":"1",
            "column":"","category":"","plate":"","seDate":f"{sd}~{td}","searchkey":"","secid":"","sortName":"","sortType":"","isHLtitle":"true"}
        h = {"User-Agent":UA,"Content-Type":"application/x-www-form-urlencoded","Referer":"https://www.cninfo.com.cn/new/disclosure","Origin":"https://www.cninfo.com.cn"}
        r = _quick_request("https://www.cninfo.com.cn/new/hisAnnouncement/query", data=payload, headers=h, timeout=15, method="POST")
        d = r.json(); anns = (d.get("announcements",[]) or []) if r is not None else []
        if not anns:
            # fallback searchkey
            payload2 = {"orgId":"","stock":"","tabName":"fulltext","pageSize":"10","pageNum":"1","column":"","category":"","plate":"","seDate":f"{sd}~{td}","searchkey":str(code),"secid":"","sortName":"","sortType":"","isHLtitle":"true"}
            r2 = _quick_request("https://www.cninfo.com.cn/new/hisAnnouncement/query", data=payload2, headers=h, timeout=15, method="POST")
            if r2 is not None:
                d2 = r2.json(); anns = d2.get("announcements",[]) or []
        abnormal = [a for a in anns if "异常波动" in (a.get("announcementTitle","") or "")]
        severe = [a for a in abnormal if "严重" in (a.get("announcementTitle","") or "")]
        return len(abnormal), len(severe)
    except Exception as _e:
        _debug_log(f"mak get_abnormal_announcements: {_e}")
        return 0,0

def count_history_deviations(code, index_code, index_closes_pool, days_lookback=10):
    closes, _ = get_baidu_kline(code, days_lookback+5)
    if len(closes) < days_lookback+3: return 0, None
    idx_closes = index_closes_pool.get(index_code, [])
    if len(idx_closes) < days_lookback+3: return 0, None
    count = 0; last_dev = None
    for i in range(days_lookback):
        si = -(i+4)
        if abs(si) > len(closes) or abs(si+3) > len(closes): continue
        si2 = abs(si)
        if si2+2 >= len(closes): continue
        s_chg = (closes[si2] - closes[si2+2]) / closes[si2+2] * 100 if closes[si2+2] > 0 else 0
        ii = -(i+4)
        if abs(ii) > len(idx_closes) or abs(ii+3) > len(idx_closes): continue
        ii2 = abs(ii)
        if ii2+2 >= len(idx_closes): continue
        i_chg = (idx_closes[ii2] - idx_closes[ii2+2]) / idx_closes[ii2+2] * 100 if idx_closes[ii2+2] > 0 else 0
        dev = s_chg - i_chg
        if abs(dev) >= 20: count += 1; last_dev = dev
    return count, last_dev

def check_stock(s, idx_rets, index_closes_pool):
    code = s["code"]; name = s["name"]
    idx_code = get_stock_index(code)
    idx = idx_rets.get(idx_code, {})
    th = get_threshold(code, name)
    board = get_board_name(code, name)
    results = []
    if s["ret_3d"] != 0 and idx.get("ret_3d") is not None:
        dev = calc_official_deviation(s["ret_3d"], idx["ret_3d"])
        if board == "主板":
            if 18 <= abs(dev) < 20:
                results.append({"level":"卡异动","tag":"💎",
                    "desc":f"3日偏离值{dev:+.2f}%，距主板20%红线仅差{20-abs(dev):.2f}%",
                    "score":abs(dev)})
        elif board in ("创业板","科创板"):
            if 27 <= abs(dev) < 30:
                results.append({"level":"卡异动","tag":"💎",
                    "desc":f"3日偏离值{dev:+.2f}%，距{board}30%红线仅差{30-abs(dev):.2f}%",
                    "score":abs(dev)})
        if abs(dev) >= th:
            hist_cnt = 0
            try: hist_cnt, _ = count_history_deviations(code, idx_code, index_closes_pool, 10)
            except Exception as _e:
                _debug_log(f"mak hist_deviation error: {_e}")
                hist_cnt = 0
            cnt_warn = ""
            if board == "主板" and hist_cnt >= 3:
                cnt_warn = f" ⚠️ 近10日已触发{hist_cnt}次同向异动！再触发1次停牌核查！"
            elif board in ("创业板","科创板") and hist_cnt >= 2:
                cnt_warn = f" ⚠️ 近10日已触发{hist_cnt}次同向异动！再触发1次停牌核查！"
            _tr = s.get("turnover", 0); vol_note = ""
            if _tr < _vol_locked: vol_note = " [极度锁仓，动能强劲]"
            elif _tr > _vol_overload: vol_note = " [爆量滞涨，警惕派发]"
            results.append({"level":"已触发","tag":"🔥" if dev>0 else "💥",
                "desc":f"3日偏离值{dev:+.2f}%≥{th}%({board})触发短期异动{vol_note}{cnt_warn}",
                "score":abs(dev)})
    if s["ret_10d"] != 0 and idx.get("ret_10d") is not None:
        dev = round(s["ret_10d"] - idx["ret_10d"], 2)
        ceiling = 100 - dev if dev > 0 else None
        ceiling_note = ""
        if ceiling is not None and ceiling > 0:
            limit_pct = 10 if code.startswith("6") else 20
            remaining_stops = ceiling / limit_pct
            if remaining_stops <= 3:
                ceiling_note = f" 距100%仅剩{ceiling:.1f}%（约{remaining_stops:.1f}涨停）！"
        if dev >= _ret10_warn:
            results.append({"level":"严重","tag":"🔥🔥",
                "desc":f"10日偏离值{dev:+.2f}%≥+{_ret10_warn:.0f}%，触发严重异动！{ceiling_note}","score":dev})
        elif dev <= _ret10_down:
            results.append({"level":"严重","tag":"💥💥",
                "desc":f"10日偏离值{dev:+.2f}%≤{_ret10_down:.0f}%, 触发严重异动","score":-dev})
        elif ceiling is not None and ceiling <= 15:
            results.append({"level":"严重预警","tag":"🚨",
                "desc":f"10日偏离值{dev:+.2f}%（距100%仅剩{ceiling:.1f}%）{ceiling_note}","score":dev})
    if s["ret_60d"] != 0 and idx.get("ret_60d") is not None:
        dev_30d = round((s["ret_60d"] - idx["ret_60d"]) / 2, 2)
        if dev_30d >= 200:
            results.append({"level":"严重","tag":"🔥🔥🔥",
                "desc":f"30日偏离值{dev_30d:+.2f}%≥+200%, 触发严重异动！","score":dev_30d})
        elif dev_30d <= -70:
            results.append({"level":"严重","tag":"💥💥💥",
                "desc":f"30日偏离值{dev_30d:+.2f}%≤-70%, 触发严重异动","score":-dev_30d})
    return results

# Part 2: Sector rotation engine + generate_sector_report + __main__

_INDUSTRY_ALIASES = {
    "酿酒行业": "酿酒行业", "食品饮料": "食品饮料", "家电行业": "家电行业",
    "汽车行业": "汽车整车", "汽车零部件": "汽车零部件",
    "医药制造": "化学制药", "医疗行业": "医疗器械", "医药商业": "医药商业",
    "电子元件": "电子元件", "电子信息": "光学光电子", "软件服务": "软件开发",
    "通讯行业": "通信服务", "互联网": "互联网服务",
    "银行": "银行", "保险": "保险", "券商信托": "证券", "房地产": "房地产开发",
    "水泥建材": "水泥建材", "工程建设": "建筑装饰", "机械行业": "通用设备",
    "电力行业": "电力行业", "新能源": "光伏设备",
    "有色金属": "工业金属", "钢铁行业": "钢铁",
    "煤炭采选": "煤炭开采", "石油行业": "石油石化", "化工行业": "化学制品",
    "农牧饲渔": "种植业",
    "航天航空": "航天装备", "船舶制造": "船舶制造",
    "环保工程": "环境治理", "公用事业": "电力",
    "交运物流": "物流", "民航机场": "航空机场",
}

def normalize_industry(bk_name):
    if bk_name in _INDUSTRY_ALIASES:
        return _INDUSTRY_ALIASES[bk_name]
    for kw, target in _INDUSTRY_ALIASES.items():
        if kw in bk_name or bk_name in kw:
            return target
    return bk_name

def get_all_sectors():
    """V4: 两阶段评分 — 第1轮 change_pct 粗选前50，第2轮 board_members 精评"""
    sectors = tdx_get_board_list(0)
    if not sectors:
        return []
    # 第1轮: 所有板块粗评分（仅涨跌幅），取前 50 进入精评
    for s in sectors:
        sc = s["change_pct"]
        s["_rough"] = 30 if sc > 3 else (20 if sc > 1 else (10 if sc > 0 else (-10 if sc < -2 else 0)))
        s["up_count"] = 0; s["down_count"] = 0; s["amount_yi"] = 0
        s["main_inflow"] = 0; s["_member_codes"] = []; s["_member_count"] = 0
        s["leader_change"] = 0; s["leader"] = s.get("leader_name", "")
        s["mcap_yi"] = 0; s["turnover"] = 0
    sectors.sort(key=lambda x: x["_rough"], reverse=True)
    _top_n = min(50, len(sectors))
    # 第2轮: 前 50 板块精评（成分股成交额 + 涨跌家数 + 主力净流）
    for i in range(_top_n):
        s = sectors[i]
        members = get_sector_stocks(s["code"])
        if members:
            s["up_count"] = sum(1 for m in members if m.get("change_pct", 0) > 0)
            s["down_count"] = sum(1 for m in members if m.get("change_pct", 0) < 0)
            s["amount_yi"] = sum(m.get("amount_yi", 0) for m in members)
            s["main_inflow"] = sum(m.get("main_net_amount", 0) for m in members)
            s["_member_codes"] = [m["code"] for m in members]
            s["_member_count"] = len(members)
    return sectors

def get_sector_stocks(sector_code):
    """V4: 板块成分股 → TDX board_members 替代 push2"""
    members = tdx_get_board_members(sector_code)
    if not members:
        return []
    stocks = []
    for m in members:
        stocks.append({
            "code": m["code"], "name": m["name"],
            "change_pct": m.get("change_pct", 0), "price": m.get("price", 0),
            "mcap_yi": m.get("mcap_yi", 0), "turnover": m.get("turnover", 0),
            "amount_yi": m.get("mcap_yi", 0) * m.get("turnover", 0) / 100 if m.get("turnover", 0) > 0 else 0,
            "main_net_amount": m.get("main_net_amount", 0),
        })
    return stocks

# V7: get_recent_dragon_tiger 由 stock_common 统一提供

def get_ths_hot_pool(date_str):
    url = f"http://zx.10jqka.com.cn/event/api/getharden/date/{date_str}/orderby/date/orderway/desc/charset/GBK/"
    try:
        r = _quick_request(url, headers={"User-Agent": UA}, timeout=10)
        if r is None:
            return []
        try:
            d = r.json()
        except Exception as _e:
            _debug_log(f"mak sector_item: {_e}")
            try:
                r.encoding = "GBK"
                d = r.json()
            except Exception as _e:
                _debug_log(f"mak sector_inner: {_e}")
                return []
        if str(d.get("errocode", 0)) != "0" and str(d.get("errorcode", 0)) != "0":
            return []
        items = d.get("data", [])
        if not items:
            return []
        rows = []
        codes = []
        for item in items:
            code = str(item.get("code", ""))
            if not code:
                continue
            codes.append(code)
            rows.append({
                "code": code,
                "name": item.get("name", ""),
                "reason": item.get("reason", ""),
                "zhangfu": _safe_float(item.get("zhangfu", item.get("change", 0))),
            })
        quotes = tdx_get_quotes_batch(codes)
        for row in rows:
            q = quotes.get(row["code"], {})
            tdx_change = q.get("change_pct", 0)
            if tdx_change != 0:
                row["zhangfu"] = tdx_change
        rows = [r for r in rows if r["zhangfu"] != 0]
        rows.sort(key=lambda x: x["zhangfu"], reverse=True)
        return rows
    except Exception as e:
        print(f"get_ths_hot_pool error: {e}", flush=True)
        return []

def compute_rotation_scores(sectors):
    if not sectors: return {}
    for s in sectors:
        score = 0.0
        sc = s["change_pct"]
        if sc > 3: score += 30
        elif sc > 1: score += 20
        elif sc > 0: score += 10
        elif sc < -2: score -= 10
        a_yi = s.get("amount_yi",0)
        if a_yi > 200: score += 20
        elif a_yi > 50: score += 10
        if sc > 0 and (s.get("up_count",0)/max(s.get("down_count",0)+1,1)) > 3: score += 15
        if s.get("main_inflow",0) > 0: score += 10
        if s.get("leader_change",0) > 3: score += 10
        s["score"] = round(score, 1)
    return {s["name"]: s for s in sectors}

def analyze_top_stocks(top_sectors):
    result = []
    _sec_cache = {}
    for s in top_sectors:
        if s["code"] in _sec_cache:
            stocks = _sec_cache[s["code"]]
        else:
            stocks = get_sector_stocks(s["code"])
            _sec_cache[s["code"]] = stocks
        _sec_code = s["code"]
        _is_chuang = _sec_code.startswith(("300","301","688"))
        _limit_thr = 19.5 if _is_chuang else 9.5
        limit_up = [st for st in stocks if st.get("change_pct",0) >= _limit_thr]
        over7 = [st for st in stocks if 7 <= st.get("change_pct",0) < _limit_thr]
        over5 = [st for st in stocks if 5 <= st.get("change_pct",0) < 7]
        _leaders = limit_up[:3]
        if len(_leaders) < 3:
            _backup = [st for st in over7 if st not in _leaders]
            _leaders += _backup[:3-len(_leaders)]
        if len(_leaders) < 3:
            _backup2 = [st for st in over5 if st not in _leaders]
            _leaders += _backup2[:3-len(_leaders)]
        # TOP5涨幅（取前5只）
        _top5 = sorted(stocks, key=lambda x: x.get("change_pct",0) or 0, reverse=True)[:5]
        result.append({
            "sector":s["name"],"data":s,"total_stocks":len(stocks),
            "limit_up_count":len(limit_up),"over7_count":len(over7),"over5_count":len(over5),
            "limit_up_stocks":[{"code":st["code"],"name":st["name"],"change_pct":st.get("change_pct",0)} for st in _leaders],
            "top5_stocks":[{"code":st["code"],"name":st["name"],"change_pct":st.get("change_pct",0)} for st in _top5],
        })
    return result

def annotate_technical_pattern(code):
    try:
        closes, _ = get_baidu_kline(code, 25)
        if len(closes) < 20: return ""
        p = closes[-1]
        if p <= 0: return ""
        ma5 = sum(closes[-5:])/5; ma10 = sum(closes[-10:])/10; ma20 = sum(closes[-20:])/20
        tags = []
        if p > ma20 and all(closes[-i] > closes[-i-1] for i in range(1,4)):
            tags.append("多头排列")
        elif p > ma20 and closes[-1] > closes[-2] and closes[-2] <= ma20:
            tags.append("突破MA20")
        elif p > ma10 and closes[-1] > closes[-2] and closes[-2] <= ma10:
            tags.append("突破MA10")
        if ma5 > ma10 > ma20: tags.append("均线多头")
        return " | ".join(tags) if tags else ""
    except (ValueError, TypeError, IndexError): return ""

def generate_sector_report(output_path):
    _td = date.today()
    if not is_trading_day(_td):
        for _ in range(7):
            _td -= timedelta(days=1)
            if is_trading_day(_td): break
    today_str = _td.strftime("%Y-%m-%d")
    now = datetime.now()
    _mkt_status, _mkt_note = get_market_status(now)
    lines = []
    def L(s=""): lines.append(s)
    L("="*90)
    L(f"  📊 A股异动及行业轮动扫描报告 — {today_str} {now.strftime('%H:%M:%S')} {_mkt_note}")
    L("="*90)
    print("[数据装载] 获取全市场多日数据与指数基准...", flush=True)
    all_stocks = get_market_abnormal_data()
    idx_rets, index_closes_pool = get_index_returns()
    for ic, nm in INDEX_MAP.items():
        r = idx_rets.get(ic, {})
        L(f"  📈 {nm}: 3日{_fmt_ret(r.get('ret_3d'))}%  10日{_fmt_ret(r.get('ret_10d'))}%")
    print("[异动引擎] 扫描全市场异动信号...", flush=True)
    results = {"卡异动":[],"已触发":[],"严重":[],"严重预警":[]}
    for i, s in enumerate(all_stocks):
        if i % 1000 == 0: print(f"  已扫描 {i}/{len(all_stocks)}", flush=True)
        rules = check_stock(s, idx_rets, index_closes_pool)
        for r in rules:
            results[r["level"]].append({**r, "code":s["code"], "name":s["name"]})
    total_abnormal = len(results["已触发"]) + len(results["严重"])
    _zt_count = sum(1 for s in all_stocks if s.get("change_pct", 0) >= (19.5 if s["code"].startswith(("300","301","688")) else 9.5))
    _zt_float = sum(1 for s in all_stocks if 5 <= s.get("change_pct", 0) < 9.5); _zb_rate = _zt_float / max(_zt_count + _zt_float, 1) * 100
    _dt_count = sum(1 for s in all_stocks if s.get("change_pct", 0) <= -9.5)
    _lbp = _zt_count
    L(f"\n{'='*90}")
    L("【A. 全市场情绪监测看板】")
    L(f"{'─'*90}")
    _up_cnt = sum(1 for s in all_stocks if s.get("change_pct", 0) > 0)
    _down_cnt = sum(1 for s in all_stocks if s.get("change_pct", 0) < 0)
    _ud_ratio = _up_cnt / max(_down_cnt, 1)
    L(f"  🌡️ 短线情绪: 涨停{_zt_count} | 跌停{_dt_count} | 异动触发{total_abnormal}只")
    L(f"  📊 市场广度: 上涨{_up_cnt}/下跌{_down_cnt} | 涨跌比{_ud_ratio:.2f} | {'偏多' if _ud_ratio>1.5 else '偏空' if _ud_ratio<0.7 else '均衡'}")
    if _lbp > 80:
        L(f"    🔥 涨停{_lbp}家 > 80，情绪极度亢奋，警惕分化回落")
    if total_abnormal > 40 and _lbp > 60:
        L(f"    ⚠️ 异动+涨停双高，情绪高潮临界点，谨防次日退潮")
    if _dt_count > 20:
        L(f"    💥 跌停{_dt_count}家 > 20，亏钱效应扩散，防御优先")
    _zt_3d = [s for s in all_stocks if s.get("change_pct", 0) >= (19.5 if s["code"].startswith(("300","301","688")) else 9.5)]
    _lb_3d = {}
    _max_board = 0
    for s in _zt_3d:
        r3 = s.get("ret_3d", 0)
        code = s.get("code", "")
        # 按板块区分涨停阈值: 主板10%, 双创20%
        _lim = 20 if code.startswith(("300","301","688")) else 10
        if r3 >= _lim * 2.9: _lb_3d['3板+'] = _lb_3d.get('3板+', 0) + 1; _max_board = max(_max_board, 3)
        elif r3 >= _lim * 1.9: _lb_3d['2板'] = _lb_3d.get('2板', 0) + 1; _max_board = max(_max_board, 2)
        elif r3 >= _lim * 0.95: _lb_3d['首板'] = _lb_3d.get('首板', 0) + 1
    if _lb_3d:
        _ladder_str = ' | '.join(f'{k}: {v}家' for k,v in sorted(_lb_3d.items()))
        _max_desc = f", 最高{_max_board}板" if _max_board else ", 最高首板"
        L(f"  📊 连板梯队: {_ladder_str}{_max_desc}")
        if _max_board >= 4:
            L(f"    🔥 高标{_max_board}板打开空间，可积极做多")
        elif _max_board <= 1 and _zt_count > 30:
            L(f"    ⚠️ 涨停多但无高度板，首板跟风为主，持续性存疑")
    _up_abn = [r for r in results["已触发"] if r.get("tag")=="🔥"]
    if _up_abn:
        _pos_5d = 0
        for r in _up_abn[:30]:
            for s in all_stocks:
                if s["code"]==r["code"] and s.get("ret_5d",0) > 0:
                    _pos_5d += 1; break
        _win_rate = _pos_5d / min(len(_up_abn),30) * 100
        L(f"  📈 异动信号回测(近似): 多头异动后5日正收益概率{_win_rate:.0f}%（基于{min(len(_up_abn),30)}只样本）")
    L(f"{'─'*90}")
    L(f"  扫描汇总: 卡异动{len(results['卡异动'])}只 | 已触发{len(results['已触发'])}只 | 严重{len(results['严重'])}只")
    if total_abnormal > 40:
        L(f"  ⚠️ 全市场异动总数{total_abnormal}只处于历史高位，警惕监管降温")
    _tech_cache = {}
    def _tech(code):
        if code not in _tech_cache: _tech_cache[code] = annotate_technical_pattern(code)
        return _tech_cache[code]
    items = sorted(results["卡异动"], key=lambda x:x["score"], reverse=True)
    if items:
        L(f"\n  💎 黄金控盘区 —— 精准卡异动标的（距红线不足2%）:")
        for r in items[:10]:
            _tt = _tech(r["code"]); _tt_str = f" [{_tt}]" if _tt else ""
            L(f"    {r['tag']} {r['name']}({r['code']}){_tt_str}  {r['desc']}")
    items = sorted(results["严重预警"], key=lambda x:x["score"], reverse=True)
    if items:
        L(f"\n  🚨 雷区风控 —— 濒临严重异动/停牌:")
        for r in items[:8]:
            _tt = _tech(r["code"]); _tt_str = f" [{_tt}]" if _tt else ""
            L(f"    🚨 {r['name']}({r['code']})  {r['desc']}")
    items = sorted(results["严重"], key=lambda x:x["score"], reverse=True)
    if items:
        L(f"\n  🔥🔥 严重异动 —— 已触发:")
        for r in items[:8]:
            ann_info = ""
            _tt = _tech(r["code"]); _tt_str = f" [{_tt}]" if _tt else ""
            L(f"    {r['tag']} {r['name']}({r['code']}){_tt_str}  {r['desc']}{ann_info}")
    _up = sorted([r for r in results["已触发"] if r.get("tag")=="🔥"], key=lambda x:x["score"], reverse=True)
    _down = sorted([r for r in results["已触发"] if r.get("tag")=="💥"], key=lambda x:x["score"], reverse=True)
    if _up:
        L(f"\n  🔺 多头控盘 —— 新晋正向偏离异动:")
        for r in _up[:10]:
            L(f"    🔥 {r['name']}({r['code']})  {r['desc']}")
    if _down:
        L(f"\n  🔻 空头崩盘 —— 新晋负向偏离异动:")
        for r in _down[:5]:
            L(f"    💥 {r['name']}({r['code']})  {r['desc']}")
    # 板块-异动交叉分析
    L(f"\n{'='*90}")
    L("【B. 板块-异动集中度分析】")
    L(f"{'─'*90}")
    sectors = get_all_sectors()
    scored = compute_rotation_scores(sectors)
    sorted_sectors = sorted(sectors, key=lambda x:x.get("score",0), reverse=True)
    _abnormal_codes = set(r["code"] for r in results["已触发"]+results["严重"])
    _sector_density = []
    for _s in sorted_sectors:
        _sc = _s.get("_member_codes", [])
        _cnt = sum(1 for c in _sc if c in _abnormal_codes)
        _total = _s.get("_member_count", len(_sc)) or 1
        if _cnt > 0:
            _density = _cnt / _total * 100
            _sector_density.append((_s["name"], _cnt, _density))
    _sector_density.sort(key=lambda x: x[1], reverse=True)
    # 龙虎榜数据补全（近5日常规异动）
    _dt_map = get_recent_dragon_tiger(3)
    if _dt_map:
        _extra_dt_codes = set(_dt_map.keys()) - _abnormal_codes
    else:
        _extra_dt_codes = set()
    if _sector_density or _dt_map:
        L(f"  异动集聚板块TOP5（异动股数/密度，含龙虎榜补全）:")
        for _nm, _cnt, _den in _sector_density[:5]:
            L(f"    {normalize_industry(_nm)}: {_cnt}只异动（板块内密度{_den:.1f}%）")
            _s = next((s for s in sorted_sectors if s["name"] == _nm), None)
            if _s:
                _stocks = get_sector_stocks(_s["code"])
                _sc = [st["code"] for st in _stocks]
                for _abn in results["已触发"] + results["严重"]:
                    if _abn["code"] in _sc:
                        L(f"      {_abn['code']} {_abn['name']} - {_abn.get('desc','')}")
                # 补全龙虎榜异动股票
                for _c, _dt in _dt_map.items():
                    if _c in _sc and _c not in _abnormal_codes:
                        _dtn = _dt.get("name", ""); _dt_display = f"{_c} {_dtn}" if _dtn else _c
                        L(f"      {_dt_display} (龙虎榜) - {_dt['reason'][:40]} | 净买{_dt['net_buy']:.0f}万")
    else:
        L(f"  今日异动股较少，未形成明显板块集聚")
    # 近5日异动回溯（基于10日/20日/60日偏离值反推）
    _recent_high = []
    for s in all_stocks:
        _r3 = s.get("ret_3d", 0); _r10 = s.get("ret_10d", 0)
        _r20 = s.get("ret_20d", 0); _r60 = s.get("ret_60d", 0)
        _th = 20 if s["code"].startswith("6") else 30
        if "ST" in s["name"]: _th = 12
        _matched = False
        # 10日严重：近日可能触发过
        if abs(_r10) >= 80: _matched = True
        # 20日严重
        if abs(_r20) >= 150: _matched = True
        # 3日已触发（当天或最近几天内）
        if abs(_r3) >= _th: _matched = True
        if _matched:
            _recent_high.append((s["code"], s["name"], _r3, _r10, _r20))
    # 龙虎榜补全回溯名单
    if _dt_map:
        for _c, _dt in _dt_map.items():
            if _c not in {_r[0] for _r in _recent_high}:
                _s = next((s for s in all_stocks if s["code"] == _c), None)
                if _s:
                    _recent_high.append((_c, _s["name"], _s.get("ret_3d",0), _s.get("ret_10d",0), _s.get("ret_20d",0)))
                else:
                    # ST/退市不在 all_stocks 池中 → 从 TDX K线 临时算 3/10/20 日涨幅
                    _r3 = _r10 = _r20 = 0
                    try:
                        _k, _kr = tdx_get_security_bars(_c, count=30)
                        if _k and _kr:
                            _ci = next((i for i, kk in enumerate(_k) if kk in ("close","close_price")), -1)
                            if _ci >= 0:
                                _cls = [_safe_float(r[_ci]) for r in _kr if len(r) > _ci]
                                if len(_cls) >= 22:
                                    _r3 = (_cls[-1]/_cls[-4]-1)*100 if _cls[-4]>0 else 0
                                    _r10 = (_cls[-1]/_cls[-11]-1)*100 if _cls[-11]>0 else 0
                                    _r20 = (_cls[-1]/_cls[-21]-1)*100 if _cls[-21]>0 else 0
                    except Exception as _e:
                        _debug_log(f"mak recent_high_kline error: {_e}")
                    _recent_high.append((_c, _dt.get("name",""), _r3, _r10, _r20))
    _recent_high.sort(key=lambda x: abs(x[3]), reverse=True)
    if _recent_high:
        _recent_top = _recent_high[:50]
        _recent_ann = {}
        _ann_t0 = time.time()
        for _r in _recent_top[:15]:
            try:
                _a, _s = get_abnormal_announcements(_r[0])
                if _a > 0:
                    _recent_ann[_r[0]] = (_a, _s)
            except Exception as _e:
                _debug_log(f"mak abnormal_announcements error: {_e}")
        _ann_dt = time.time() - _ann_t0
        print(f"  公告查询耗时: {_ann_dt:.2f}s", flush=True)
        L(f"\n{'='*90}")
        L("【近3日异动回溯（高偏离值个股，可能近日触发过异动）】")
        L(f"{'─'*90}")
        L(f"  {'代码':<8} {'名称':<12} {'3日偏离':>9} {'10日偏离':>9} {'20日偏离':>9} {'公告':<12}")
        L(f"  {'-'*75}")
        _shown = 0
        for _r in _recent_top[:30]:
            _a_info = ""
            if _r[0] in _recent_ann:
                _a_cnt, _s_cnt = _recent_ann[_r[0]]
                _a_info = f"已发{_a_cnt}份(严重{_s_cnt}份)" if _s_cnt > 0 else f"已发{_a_cnt}份"
            else:
                continue
            L(f"  {_r[0]:<8} {_r[1]:<12} {_r[2]:>+9.2f}% {_r[3]:>+9.2f}% {_r[4]:>+9.2f}% {_a_info:<12}")
            _shown += 1
        if _shown == 0:
            L(f"  (近3日无股票触发异常波动公告)")
        L(f"  \n  💡 注: 回溯基于当日快照的10日/20日偏离值反推，非精确历史回放")

    L(f"\n{'='*90}")
    L("【C. 行业轮动强度扫描】")
    L(f"{'─'*90}")
    top10 = sorted_sectors[:10]
    L(f"  行业总数: {len(sectors)}个")
    L(f"  {'排名':<6} {'板块名称':<18} {'评分':>5} {'涨跌幅':>7} {'成交额(亿)':>9} {'主力净流(亿)':>11}")
    L(f"  {'-'*55}")
    for i, ts in enumerate(top10, 1):
        name = normalize_industry(ts["name"])
        _mfi = round(ts.get('main_inflow',0)/1e8, 2) if abs(ts.get('main_inflow',0)) > 0 else 0
        L(f"  {i:<6} {name:<18} {ts.get('score',0):>5.1f} {ts['change_pct']:>+7.2f}% {ts.get('amount_yi',0):>9.1f} {_mfi:>+11.2f}")
    if top10:
        L(f"\n  🏆 轮动冠军: {normalize_industry(top10[0]['name'])} 评分 {top10[0].get('score',0):.1f}")
    else:
        L(f"\n  ⚠️ 无法获取行业板块数据")
    L(f"\n{'='*90}")
    L("【D. TOP10 板块深度分析（涨停梯队 + 龙头股）】")
    L(f"{'─'*90}")
    top_analysis = analyze_top_stocks(top10)
    for ta in top_analysis:
        nm = normalize_industry(ta["sector"])
        L(f"\n  🔥 {nm} ({ta['data']['code']}) 总分={ta['data'].get('score',0):.1f}")

        L(f"     ├─ 成分股总数: {ta.get('total_stocks',0)} 只")
        if ta['limit_up_count'] > 0:
            _zt_names = ' '.join(st['name']+st['code'] for st in ta['limit_up_stocks'])
            L(f"     ├─ 涨停家数: {ta['limit_up_count']} 只 → {_zt_names}")
        else:
            L(f"     ├─ 涨停家数: 0 只")
        _top5 = ta.get('top5_stocks', [])
        if _top5:
            L(f"     └─ 涨幅 TOP5:")
            for _t5 in _top5:
                _t5_chg = _t5.get('change_pct', 0)
                _t5_icon = '🚀' if _t5_chg >= 10 else ('📈' if _t5_chg >= 5 else '  ')
                L(f"       {_t5_icon} {_t5['name']}({_t5['code']})  {_t5_chg:>+8.2f}%")
        _items = []
        for _st in ta['limit_up_stocks']:
            _limit = 19.5 if _st['code'].startswith(('300','301','688')) else 9.5
            _label = '涨停' if _st.get('change_pct',0) >= _limit else f"{_st.get('change_pct',0):+.1f}%"
            _items.append(f"{_st['name']}({_st['code']}, {_label})")
        L(f"    龙头: {' | '.join(_items)}")
    L(f"\n{'='*90}")
    L("【E. 资金流验证：真金白银 vs 虚涨】")
    L(f"{'─'*90}")
    with_money = [s for s in sectors[:50] if s.get("main_inflow",0) > 0]
    without_money = [s for s in sectors[:50] if s.get("main_inflow",0) <= 0]
    if with_money:
        _sorted_in = sorted(with_money, key=lambda x: x.get('main_inflow',0), reverse=True)
        L(f"  ✅ 真金白银: 高评分且主力净流入:")
        for s in _sorted_in[:10]:
            L(f"    {normalize_industry(s['name'])}: 评分{s.get('score',0):.1f} 涨幅{s['change_pct']:+.2f}% 净流入{round(s['main_inflow']/1e8,2):+.2f}亿")
    if without_money:
        _sorted_out = sorted(without_money, key=lambda x: x.get('main_inflow',0), reverse=True)
        L(f"  ⚠️ 虚涨（主力净流出）:")
        for s in _sorted_out[:10]:
            L(f"    {normalize_industry(s['name'])}: 评分{s.get('score',0):.1f} 涨幅{s['change_pct']:+.2f}% 主力净流出{round(abs(s['main_inflow'])/1e8,2):.2f}亿")
    _lurking = [s for s in sectors if s.get("main_inflow",0) > 3e8 and 1 <= s.get("change_pct",0) <= 5]
    _lurking.sort(key=lambda x: x.get("main_inflow",0), reverse=True)
    if _lurking:
        L(f"\n  🕵️ 潜伏信号（主力大幅流入但涨幅不大，可能正在建仓）:")
        L(f"  {'-'*60}")
        for _l in _lurking[:5]:
            _lnm = normalize_industry(_l["name"])
            _lfi = round(_l["main_inflow"]/1e8, 2)
            L(f"    {_lnm}: 涨幅{_l['change_pct']:+.2f}% 主力净流入{_lfi:+.2f}亿")
    L(f"\n{'='*90}")
    L("【F. 同花顺强势股情绪池验证】")
    L(f"{'─'*90}")
    _ths_limit = 50
    ths = get_ths_hot_pool(today_str)
    if ths:
        # 连板检测：按板块涨跌停线 + ret_3d判断
        def _get_limit_pct(code):
            if code.startswith(("300","301","688")): return 20
            return 10
        def _is_zt(h):
            lim = _get_limit_pct(h["code"])
            return h.get("zhangfu",0) >= lim * 0.95
        # 对应板块1/2/3连板的3日累计涨幅阈值
        def _lianban_level(code, ret3):
            lim = _get_limit_pct(code)
            if ret3 >= lim * 2.85: return 3   # 3连板+
            if ret3 >= lim * 1.9:  return 2   # 2连板
            if ret3 >= lim * 0.95: return 1   # 首板
            return 0
        _ths_zt = [h for h in ths if _is_zt(h)]
        # 查all_stocks获取ret_3d
        _stock_map = {s["code"]: s for s in all_stocks}
        _lb_list = []  # 连板股票
        _zt_list = []  # 涨停（非连板）
        for h in _ths_zt:
            s = _stock_map.get(h["code"])
            if s:
                _lv = _lianban_level(h["code"], s.get("ret_3d", 0))
                if _lv >= 2:
                    _lb_list.append((h["code"], h["name"], _lv))
                else:
                    _zt_list.append(h)
            else:
                _zt_list.append(h)
        L(f"  今日强势股: {len(ths)} 只（按涨幅取前{_ths_limit}名）")
        # 构建code→ths映射，便于连板股查表（连板股可能不在涨幅前50名内）
        _ths_map = {h["code"]: h for h in ths}
        if _lb_list:
            # 有连板：先展示连板表格，再展示涨停表格
            L(f"\n  连板: {len(_lb_list)} 只")
            _lb_detail = " | ".join(f"{name}({code}) {lv}连板" for code,name,lv in _lb_list)
            L(f"    连板明细: {_lb_detail}")
            L(f"  {'代码':<8} {'名称':<12} {'涨幅%':>7} {'题材':<30}")
            L(f"  {'-'*65}")
            # 连板表格：遍历_lb_list（已含全部连板股），从_ths_map取详情
            for code, name, lv in _lb_list:
                h = _ths_map.get(code)
                if h:
                    L(f"  {h['code']:<8} {h['name']:<12} {h['zhangfu']:>+7.2f}% {h.get('reason','')[:30]:<30}")
            L(f"\n  涨停: {len(_zt_list)} 只")
            L(f"  {'代码':<8} {'名称':<12} {'涨幅%':>7} {'题材':<30}")
            L(f"  {'-'*65}")
            # 涨停表格：_zt_list已排除连板股，取前_ths_limit只（先排除连板再取top N）
            for h in _zt_list[:_ths_limit]:
                L(f"  {h['code']:<8} {h['name']:<12} {h['zhangfu']:>+7.2f}% {h.get('reason','')[:30]:<30}")
        else:
            # 无连板：全量表
            L(f"  {'代码':<8} {'名称':<12} {'涨幅%':>7} {'题材':<30}")
            L(f"  {'-'*65}")
            for h in ths[:_ths_limit]:
                L(f"  {h['code']:<8} {h['name']:<12} {h['zhangfu']:>+7.2f}% {h.get('reason','')[:30]:<30}")
    else:
        L(f"  暂无数据（需交易所收盘后更新）")
    L(f"\n{'='*90}")
    output = "\n".join(filter(None, lines))
    with open(output_path,"w",encoding="utf-8") as f: f.write(output)
    return output

if __name__ == "__main__":
    args = common_parse_args("A股异动及行业轮动扫描报告")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sn = os.path.basename(__file__).replace(".py", "")
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    op = os.path.join(args.output, f"{sn}_{ts}.txt")
    print(f"🚀 A股异动及行业轮动扫描报告 — {date.today()}", flush=True)
    print("  ⏱ 预计 2-3 分钟", flush=True)

    os.makedirs(args.output, exist_ok=True)
    try:
        generate_sector_report(op)
        print(f"  ✅ 已保存: {op}", flush=True)
    except Exception as e:
        print(f"❌ 报告生成失败: {e}", flush=True)
        cleanup_tdx()
        exit(1)

    # GD 上传
    drive, gps, gd_parent_folder_id, skip_upload = None, False, None, False
    if not args.no_upload:
        drive, gps, gd_parent_folder_id, skip_upload = init_gd(base_dir)
        if drive and not skip_upload:
            if upload_type_reports(drive, gd_parent_folder_id, "mak", [op]) <= 0:
                print("  ⚠️ GD 上传失败", flush=True)
    cleanup_gd_proxy(gps)
    cleanup_tdx()
    print(f"\n📋 扫描结束: {op}")
