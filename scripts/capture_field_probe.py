#!/usr/bin/env python3
"""capture_field_probe.py — 字段实测验证采集脚本(V16.4.1)

固定股票池(docs/field_verification/pool.json)20 股,按天采集各源全字段:
  - ZHB    : full/stat/stat2/tipinfo 全字段(本地解析,零网络)
  - TDX    : 行情快照 + 财务 0x0010(TCP)
  - 腾讯   : qt.gtimg 单股全字段(~90 位,保存原始 split 数组)
  - 东财   : push2 stock/get 全字段(f1-f239,原样保存)

输出: docs/field_verification/{YYYYMMDD}/raw_{source}.json + meta.json
用法:
  python scripts/capture_field_probe.py                 # 采今天(用现有 ZHB 包)
  python scripts/capture_field_probe.py --date 20260812
  python scripts/capture_field_probe.py --dry-run       # 只检查源可用性,不发请求
"""
import sys, io, os, json, time, argparse
from datetime import datetime

for _s in (sys.stdout, sys.stderr):
    if _s is not None and hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from stock_common.sc_utils import em_secid_prefix  # V17.0 S3: 统一 secid 前缀

POOL_PATH = os.path.join(_ROOT, "docs", "field_verification", "pool.json")
OUT_BASE = os.path.join(_ROOT, "docs", "field_verification")


def load_pool() -> list:
    with open(POOL_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["fixed"] + data["dynamic"]


def collect_zhb(pool: list) -> dict:
    """ZHB 全字段(本地,零网络)。"""
    from core.zhb_client import (
        full_market_snapshot, market_stat_snapshot, market_stat2_snapshot,
        get_tip_info, get_stock_name_from_zhb, get_zhb,
    )

    zhb = get_zhb()
    zhb_date = zhb.date if zhb is not None else ""
    full = full_market_snapshot([p["code"] for p in pool]) or {}
    stat = market_stat_snapshot([p["code"] for p in pool]) or {}
    stat2 = market_stat2_snapshot([p["code"] for p in pool]) or {}
    out = {"zhb_date": zhb_date, "stocks": {}}
    for p in pool:
        c = p["code"]
        tip = get_tip_info(c)
        out["stocks"][c] = {
            "name": get_stock_name_from_zhb(c),
            "full": full.get(c),
            "stat": stat.get(c),
            "stat2": stat2.get(c),
            "tipinfo": tip,
        }
    return out


def collect_tdx(pool: list) -> dict:
    """TDX 行情快照 + 财务(失败标的记 None,不中断)。"""
    from core.tdx_client import tdx_get_quote_full, tdx_get_finance_info

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        rec = {}
        try:
            rec["quote_full"] = tdx_get_quote_full(c)
        except Exception as e:
            rec["quote_full"] = {"__error__": str(e)[:200]}
        try:
            rec["finance_info"] = tdx_get_finance_info(c)
        except Exception as e:
            rec["finance_info"] = {"__error__": str(e)[:200]}
        out["stocks"][c] = rec
    return out


def collect_tencent(pool: list) -> dict:
    """腾讯 qt.gtimg 单股全字段(保存原始 split 数组 + 索引名说明)。"""
    from stock_common import _quick_request

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        # V17.0 审查: 原三元 9 先于 92 → 北交所 920 误判 sh(昨日采集 920118/920508 空数据实证);
        # 92 北交所必须先行(与 em_secid_prefix 同口径)
        market = "bj" if c.startswith(("92", "8", "4", "43", "83", "87")) else (
            "sh" if c.startswith(("6", "9", "5")) else "sz")
        url = f"https://qt.gtimg.cn/q={market}{c}"
        try:
            r = _quick_request(url, timeout=10)
            if r is None:
                out["stocks"][c] = {"__error__": "request failed"}
                continue
            line = r.text.strip()
            if "=" not in line or '"' not in line:
                out["stocks"][c] = {"__error__": f"parse failed: {line[:100]}"}
                continue
            body = line.split('"')[1]
            fields = body.split("~")
            out["stocks"][c] = {
                "url": url,
                "n_fields": len(fields),
                "fields": fields,  # 原始全字段数组,索引对照 docs/verify/tencent_verify.md
            }
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:200]}
    return out


def collect_push2(pool: list) -> dict:
    """东财 push2 stock/get 全字段(不指定 fields → 服务端返回全量)。

    2026-08-12 实测: push2 半恢复状态——连接级风控仍在,首次连接约 50%
    概率 RemoteDisconnected(健康探测单次连接恰好成功)。V16.4.1 防封:
    失败**不再重试**(重试叠加失败连接会触发封禁),失败即记 error。
    """
    from stock_common import _quick_request

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        secid = em_secid_prefix(c) + c  # V17.0 S3: 统一(修复 92 北交所误判 1.)
        url = "https://push2.eastmoney.com/api/qt/stock/get"
        try:
            r = _quick_request(
                url,
                params={"secid": secid, "fltt": "2", "invt": "2", "ut": "fa5fd1943c7b386f172d6893dbfba10b"},
                headers={"Referer": "https://quote.eastmoney.com/"},
                timeout=10,
            )
        except Exception:
            r = None
        if r is None:
            out["stocks"][c] = {"__error__": "request failed (no retry)"}
            continue
        data = (r.json() or {}).get("data") or {}
        out["stocks"][c] = {"secid": secid, "n_fields": len(data), "data": data}
    return out


def collect_push2_full(pool: list) -> dict:
    """东财 push2 stock/get **显式全字段**(f1-f250)。

    V16.4.1: 原 collect_push2 未指定 fields → 服务端仅返回 58 字段基础子集
    (无 f162/f167 等估值字段)。字典 §12.9 破解为 f1~f250 全字段——
    此处显式请求全字段。失败重试一次(半恢复期连接级拒绝)。
    2026-08-12 实测: push2 半恢复期间歇全拒 → 自动切 push2delay 镜像域
    (字段同构, 字典 §12.15.5; 独立风控面, 1.0rps)。
    V16.4.1 防封(2026-08-12 封禁复盘): 失败**不再重试**——失败连接本身
    积累服务器侧风控(当日 ~300 次连接尝试含半数失败 → 触发连接级封禁)。
    每只: push2 一次 → 失败直接切 push2delay 一次; 连续 3 只 push2 失败
    → 剩余股票全部走 push2delay(域级熔断, 不继续捅 push2)。
    """
    from stock_common import _quick_request

    fields = ",".join(f"f{i}" for i in range(1, 251))
    push2_fail_streak = 0
    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        secid = em_secid_prefix(c) + c  # V17.0 S3: 统一(修复 92 北交所误判 1.)
        r = None
        used_host = ""
        if push2_fail_streak < 3:
            try:
                r = _quick_request(
                    "https://push2.eastmoney.com/api/qt/stock/get",
                    params={"secid": secid, "fltt": "2", "invt": "2", "fields": fields,
                            "ut": "fa5fd1943c7b386f172d6893dbfba10b"},
                    headers={"Referer": "https://quote.eastmoney.com/"},
                    timeout=10,
                )
                if r is not None:
                    used_host = "push2"
                    push2_fail_streak = 0
                else:
                    push2_fail_streak += 1
            except Exception:
                push2_fail_streak += 1
                r = None
        if r is None:
            try:
                r = _quick_request(
                    "https://push2delay.eastmoney.com/api/qt/stock/get",
                    params={"secid": secid, "fltt": "2", "invt": "2", "fields": fields,
                            "ut": "fa5fd1943c7b386f172d6893dbfba10b"},
                    headers={"Referer": "https://quote.eastmoney.com/"},
                    timeout=10,
                )
                if r is not None:
                    used_host = "push2delay"
            except Exception:
                r = None
        if r is None:
            out["stocks"][c] = {"__error__": "request failed (push2+delay, no retry)"}
            continue
        data = (r.json() or {}).get("data") or {}
        out["stocks"][c] = {"secid": secid, "host": used_host, "n_fields": len(data), "data": data}
    return out


def collect_sina(pool: list) -> dict:
    """新浪行情 hq.sinajs 全字段(需 Referer)。"""
    from stock_common import _quick_request, UA

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        pre = "sh" if c.startswith("6") else ("bj" if c.startswith(("92", "8", "4", "43", "83", "87")) else "sz")
        try:
            r = _quick_request(
                f"https://hq.sinajs.cn/list={pre}{c}",
                headers={"Referer": "https://finance.sina.com.cn/", "User-Agent": UA},
                timeout=8,
            )
            if r is None:
                out["stocks"][c] = {"__error__": "request failed"}
                continue
            text = r.text.strip()
            if "=" not in text:
                out["stocks"][c] = {"__error__": f"parse failed: {text[:80]}"}
                continue
            payload = text.split('"')[1] if '"' in text else ""
            fields = payload.split(",")
            out["stocks"][c] = {"n_fields": len(fields), "fields": fields}
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:200]}
    return out


def collect_axdata(pool: list) -> dict:
    """AxData 短线指标 34 字段(零网络,直读项目 zhb.zip,字典 §12.12.1)。"""
    from stock_common import get_shortline_indicators

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        try:
            rec = get_shortline_indicators(c) or {}
            out["stocks"][c] = {"n_fields": len(rec), "data": rec}
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:200]}
    return out


def collect_market_sources(pool: list) -> dict:
    """市场级源(一次性): 财联社情绪/涨停天梯/盘口异动 + KPL + 板块轮动 + 龙虎榜。"""
    out = {}
    try:
        from stock_common import get_cls_market_emotion, get_kph_limit_ladder, get_stock_changes
        out["cls_market_emotion"] = get_cls_market_emotion()
        out["kph_limit_ladder"] = get_kph_limit_ladder()
        out["stock_changes_8201"] = get_stock_changes("8201")
    except Exception as e:
        out["levistock_error"] = str(e)[:200]
    try:
        from stock_common import (get_kpl_market_sentiment, get_kpl_limit_up_detail,
                                  get_kpl_broken_ratio, get_kpl_up_down)
        out["kpl_sentiment"] = get_kpl_market_sentiment()
        out["kpl_up_down"] = get_kpl_up_down()
        out["kpl_limit_up_detail"] = get_kpl_limit_up_detail()
        out["kpl_broken_ratio"] = get_kpl_broken_ratio()
    except Exception as e:
        out["kpl_error"] = str(e)[:200]
    try:
        from stock_common import get_plate_rotation_matrix, get_plate_rotation_top
        out["plate_rotation_matrix"] = get_plate_rotation_matrix(source="kaipan", days=20, top_n=30)
        out["plate_rotation_top"] = get_plate_rotation_top()
    except Exception as e:
        out["plate_rot_error"] = str(e)[:200]
    try:
        from stock_common import eastmoney_datacenter
        r = eastmoney_datacenter(
            "RPT_DAILYBILLBOARD_DETAILSNEW",
            {"SECURITY_CODE": "1"}, page_size=50,
        )
        out["dragon_tiger_today"] = r
    except Exception as e:
        out["dragon_tiger_error"] = str(e)[:200]
    return out


def collect_tdx_f10(pool: list) -> dict:
    """TDX F10 财务九件套补充: 财务分析/股本/分红(TCP,免费)。"""
    from core.tdx_client import tdx_get_financial_analysis, tdx_get_share_capital, tdx_get_dividend_history

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        rec = {}
        for name, fn in [("financial_analysis", tdx_get_financial_analysis),
                         ("share_capital", tdx_get_share_capital),
                         ("dividend_history", tdx_get_dividend_history)]:
            try:
                rec[name] = fn(c)
            except Exception as e:
                rec[name] = {"__error__": str(e)[:150]}
        out["stocks"][c] = rec
    return out


def collect_thsdk(pool: list) -> dict:
    """同花顺 SDK 实时快照(正式账号;非交易时段服务器拒绝,容错记录)。"""
    from stock_common import get_ths_market_snapshot

    try:
        snap = get_ths_market_snapshot([p["code"] for p in pool]) or {}
        return {"stocks": snap}
    except Exception as e:
        return {"stocks": {}, "error": str(e)[:200]}


def collect_ulist239(pool: list) -> dict:
    """东财 push2delay ulist.np 批量全字段(1 次请求 20 只,字典 §12.9 ulist 239 字段)。"""
    from stock_common import _quick_request

    def _mkt(c):
        if c.startswith(("92", "8", "4", "43", "83", "87")):
            return "0."  # 北交所(920 等)必须先判——"9" 前缀会被沪市分支吃掉(V16.4.1 bug 修复)
        if c.startswith(("6", "5", "9")):
            return "1."
        return "0."

    secids = ",".join(_mkt(p["code"]) + p["code"] for p in pool)
    try:
        r = _quick_request(
            "https://push2delay.eastmoney.com/api/qt/ulist.np/get",
            params={"fltt": "2", "invt": "2", "secids": secids,
                    "fields": ",".join(f"f{i}" for i in range(1, 251))},
            headers={"Referer": "https://quote.eastmoney.com/"},
            timeout=15,
        )
        if r is None:
            return {"__error__": "request failed"}
        diff = (r.json() or {}).get("data", {}).get("diff") or []
        out = {"stocks": {}}
        for item in diff:
            code = str(item.get("f12", ""))
            if code:
                out["stocks"][code] = {"n_fields": len(item), "data": item}
        return out
    except Exception as e:
        return {"__error__": str(e)[:200]}


def collect_push2ex(pool: list) -> dict:
    """push2ex 涨停/跌停/炸板池(市场级,字典 §12.9.2)。"""
    out = {}
    try:
        from stock_common import get_limit_up_pool, get_limit_down_pool, get_limit_broken_pool
        out["limit_up_pool"] = get_limit_up_pool()
        out["limit_down_pool"] = get_limit_down_pool()
        out["limit_broken_pool"] = get_limit_broken_pool()
    except Exception as e:
        out["error"] = str(e)[:200]
    return out


def collect_em_hot(pool: list) -> dict:
    """东财人气榜(市场级,emappdata 域)。"""
    try:
        from stock_common import em_hot_rank
        return {"hot_rank": em_hot_rank(top=50)}
    except Exception as e:
        return {"error": str(e)[:200]}


def collect_cls(pool: list) -> dict:
    """财联社快讯(市场级)。"""
    try:
        from stock_common import cls_telegraph
        return {"telegraph": cls_telegraph(page_size=50)}
    except Exception as e:
        return {"error": str(e)[:200]}


def collect_datacenter(pool: list) -> dict:
    """东财 datacenter 个股级: 两融/北向/解禁(每只 3 请求,1.0rps)。"""
    from stock_common import get_margin_trading, get_northbound_hold, get_lockup_expiry

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        rec = {}
        for name, fn in [("margin_trading", get_margin_trading),
                         ("northbound_hold", get_northbound_hold),
                         ("lockup_expiry", get_lockup_expiry)]:
            try:
                v = fn(c)
                rec[name] = v if isinstance(v, (list, dict)) else {"value": v}
            except Exception as e:
                rec[name] = {"__error__": str(e)[:150]}
        out["stocks"][c] = rec
    return out


def collect_tdx_f10_more(pool: list) -> dict:
    """TDX F10 补充: 股东研究/公司新闻/异动提醒(TCP 免费)。"""
    from core.tdx_client import tdx_get_shareholder_research, tdx_get_company_news_f10, tdx_get_latest_reminders

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        rec = {}
        for name, fn in [("shareholder_research", tdx_get_shareholder_research),
                         ("company_news", lambda x: tdx_get_company_news_f10(x, count=10)),
                         ("reminders", tdx_get_latest_reminders)]:
            try:
                rec[name] = fn(c)
            except Exception as e:
                rec[name] = {"__error__": str(e)[:150]}
        out["stocks"][c] = rec
    return out


def collect_cninfo(pool: list) -> dict:
    """巨潮互动易(irm.cninfo,3rps;全 20 只)。"""
    from stock_common import cninfo_irm

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        try:
            out["stocks"][c] = cninfo_irm(c, page_size=10)
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:150]}
    return out


def collect_reports(pool: list) -> dict:
    """东财研报 reportapi(全 20 只,1.0rps)。"""
    from stock_common import get_reports

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        try:
            out["stocks"][c] = get_reports(c, max_pages=1)
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:150]}
    return out


def dry_run(pool: list) -> None:
    print(f"[dry-run] pool={len(pool)} 只")
    from core.zhb_client import get_zhb, is_data_fresh
    zhb = get_zhb()
    print(f"  ZHB     : date={zhb.date if zhb else 'N/A'} fresh={is_data_fresh()}")
    from core.tdx_client import _check_tdx
    print(f"  TDX     : {_check_tdx()}")
    from stock_common import _quick_request
    r = _quick_request("https://qt.gtimg.cn/q=sh600519", timeout=8)
    print(f"  腾讯    : {'OK' if r is not None else 'FAIL'}")
    r = _quick_request("https://push2.eastmoney.com/api/qt/stock/get",
                       params={"secid": "1.600519", "fltt": "2", "invt": "2"},
                       headers={"Referer": "https://quote.eastmoney.com/"}, timeout=8)
    print(f"  push2   : {'OK' if r is not None else 'FAIL'}")


def main() -> None:
    ap = argparse.ArgumentParser(description="字段验证采集")
    ap.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default="", help="只采指定源(逗号分隔: zhb,tdx,tencent,push2)")
    args = ap.parse_args()

    pool = load_pool()
    if args.dry_run:
        dry_run(pool)
        return

    t0 = time.time()
    print(f"▶ 采集开始: {args.date} | 股票 {len(pool)} 只 | 源: ZHB/TDX/腾讯/push2", flush=True)
    meta = {"date": args.date, "start": time.strftime("%Y-%m-%d %H:%M:%S"), "sources": {}}

    collectors = {
        "zhb": collect_zhb,
        "tdx": collect_tdx,
        "tencent": collect_tencent,
        "push2": collect_push2,
        "push2_full": collect_push2_full,   # V16.4.1: f1-f250 显式全字段
        "sina": collect_sina,               # V16.4.1: 新浪行情全字段
        "axdata": collect_axdata,           # V16.4.1: 短线指标 34 字段(零网络)
        "market_sources": collect_market_sources,  # V16.4.1: 财联社/KPL/板块轮动/龙虎榜
        "tdx_f10": collect_tdx_f10,         # V16.4.1: F10 财务/股本/分红
        "thsdk": collect_thsdk,             # V16.4.1: 同花顺 SDK(盘中才可用)
        "ulist239": collect_ulist239,       # V16.4.1: push2delay ulist 239 字段(批量)
        "push2ex": collect_push2ex,         # V16.4.1: 涨停/跌停/炸板池
        "em_hot": collect_em_hot,           # V16.4.1: 人气榜
        "cls": collect_cls,                 # V16.4.1: 财联社快讯
        "datacenter": collect_datacenter,   # V16.4.1: 两融/北向/解禁
        "tdx_f10_more": collect_tdx_f10_more,  # V16.4.1: 股东/新闻/提醒
        "cninfo": collect_cninfo,           # V16.4.1: 巨潮互动易
        "reports": collect_reports,         # V16.4.1: 研报
    }
    if args.only:
        collectors = {k: v for k, v in collectors.items() if k in [s.strip() for s in args.only.split(",")]}
    out_dir = os.path.join(OUT_BASE, args.date)
    os.makedirs(out_dir, exist_ok=True)

    for name, fn in collectors.items():
        try:
            t1 = time.time()
            data = fn(pool)
            path = os.path.join(out_dir, f"raw_{name}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=1, default=str)
            meta["sources"][name] = {"ok": True, "secs": round(time.time() - t1, 1), "file": path}
            print(f"  ✔ {name}: {meta['sources'][name]['secs']}s", flush=True)
        except Exception as e:
            meta["sources"][name] = {"ok": False, "error": str(e)[:300]}
            print(f"  ✖ {name}: {e}", flush=True)

    meta["end"] = time.strftime("%Y-%m-%d %H:%M:%S")
    meta["total_secs"] = round(time.time() - t0, 1)
    with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print(f"✔ 完成: {out_dir} | 总耗时 {meta['total_secs']}s", flush=True)


if __name__ == "__main__":
    main()
