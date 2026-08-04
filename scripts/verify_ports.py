#!/usr/bin/env python3
"""端口连通性与数据真实性验证（V16 联网测试，用户已授权）

逐端口实测（每端口 1-2 请求，避免触发限流）:
  1. 腾讯 qt.gtimg.cn      — 实时价/PE/PB/市值（不封 IP，首选）
  2. mootdx TCP            — 通达信行情（不封 IP，首选）
  3. 新浪 quotes.sina.cn   — 财报/行情（低风险）
  4. push2.eastmoney.com   — 个股行情（风控最严，末位）—— 验证限流间隔生效
  5. datacenter-web        — 龙虎榜/资金流（中风险）
结果写 docs/port_verification.md
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, r"D:\GitHub\test")
ROOT = Path(r"D:\GitHub\test")
CODE = "600519"  # 贵州茅台（沪深主板代表）

results: list[dict] = []


def record(name: str, ok: bool, detail: str, ms: float) -> None:
    results.append({"port": name, "ok": ok, "detail": detail, "ms": round(ms, 1)})
    status = "OK" if ok else "FAIL"
    print(f"  [{status}] {name}: {detail} ({ms:.0f}ms)")


# ── 1. 腾讯行情 ──
print("=== 1. 腾讯 qt.gtimg.cn（实时价/PE/PB，不封 IP）===")
t0 = time.time()
try:
    import requests
    r = requests.get(
        f"https://qt.gtimg.cn/q=sh{CODE}",
        headers={"Referer": "https://gu.qq.com/"}, timeout=8)
    txt = r.text
    ok = "v_sh" in txt and CODE in txt
    sample = txt.split("~")[1:6] if "~" in txt else []
    record("tencent_quote", ok, f"HTTP {r.status_code} 字段样例: {sample}", (time.time() - t0) * 1000)
except Exception as e:
    record("tencent_quote", False, f"{type(e).__name__}: {str(e)[:80]}", (time.time() - t0) * 1000)

# ── 2. mootdx TCP ──
print("=== 2. mootdx TCP（通达信，不封 IP）===")
t0 = time.time()
try:
    from tdx_client import _get_tdx_client
    c = _get_tdx_client()
    if c is None:
        raise RuntimeError("_get_tdx_client 返回 None（服务器探测失败）")
    bars = c.bars(symbol=CODE, frequency=9, offset=1)
    ok = bars is not None and len(bars) > 0
    record("mootdx_tcp", bool(ok), f"最新收盘={bars['close'].iloc[-1] if ok else 'N/A'}", (time.time() - t0) * 1000)
except Exception as e:
    record("mootdx_tcp", False, f"{type(e).__name__}: {str(e)[:80]}", (time.time() - t0) * 1000)

# ── 3. 新浪行情 ──
print("=== 3. 新浪 quotes.sina.cn（低风险）===")
t0 = time.time()
try:
    r = requests.get(
        f"https://hq.sinajs.cn/list=sh{CODE}",
        headers={"Referer": "https://finance.sina.com.cn/"}, timeout=8)
    ok = CODE in r.text and "=" in r.text
    record("sina_quote", ok, f"HTTP {r.status_code}", (time.time() - t0) * 1000)
except Exception as e:
    record("sina_quote", False, f"{type(e).__name__}: {str(e)[:80]}", (time.time() - t0) * 1000)

# ── 4. push2（限流验证）──
print("=== 4. push2.eastmoney.com（风控最严，验证限流间隔）===")
try:
    from stock_common.sc_network import em_get, _DOMAIN_LIMITS
    cfg = _DOMAIN_LIMITS.get("push2.eastmoney.com", {})
    print(f"  push2 限流配置: sleep_ms={cfg.get('sleep_ms')} rps={cfg.get('rps')}")
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {"secid": f"1.{CODE}", "fields": "f43,f58,f57,f162,f167,f116"}
    t0 = time.time()
    r = em_get(url, params=params, timeout=8)
    elapsed = (time.time() - t0) * 1000
    data = r.json().get("data") if r.status_code == 200 else None
    ok = r.status_code == 200 and data
    record("push2_stock", bool(ok),
           f"HTTP {r.status_code} 映射字段 f43(price)={data.get('f43') if data else 'N/A'}", elapsed)
except Exception as e:
    record("push2_stock", False, f"{type(e).__name__}: {str(e)[:80]}", (time.time() - t0) * 1000)

# ── 5. datacenter-web ──
print("=== 5. datacenter-web（龙虎榜/资金流，中风险）===")
t0 = time.time()
try:
    from stock_common.sc_network import _request_with_retry, DATACENTER_URL
    r = _request_with_retry(DATACENTER_URL, params={
        "reportName": "RPT_LHB_BOARDINFO", "columns": "ALL",
        "filter": f"(SECURITY_CODE=\"{CODE}\")", "pageSize": "1", "pageNumber": "1",
    }, timeout=10)
    ok = r is not None and r.status_code == 200
    record("datacenter_lhb", bool(ok), f"HTTP {r.status_code if r else 'None'}", (time.time() - t0) * 1000)
except Exception as e:
    record("datacenter_lhb", False, f"{type(e).__name__}: {str(e)[:80]}", (time.time() - t0) * 1000)

# ── 汇总 ──
print("\n=== 汇总 ===")
ok_count = sum(1 for r in results if r["ok"])
for r in results:
    print(f"  {r['port']:20s} {'✓' if r['ok'] else '✗'} {r['detail'][:70]} ({r['ms']}ms)")
print(f"\n通过 {ok_count}/{len(results)}")

# 写结果文件
out = ROOT / "docs" / "port_verification.md"
lines = ["# 端口连通性验证报告（V16 联网实测）", "", f"- 验证时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
         f"- 测试股票: {CODE}", "", "| 端口 | 状态 | 详情 | 耗时 |", "|:---|:---:|:---|:---:|"]
for r in results:
    lines.append(f"| {r['port']} | {'✅' if r['ok'] else '❌'} | {r['detail'][:70]} | {r['ms']}ms |")
lines.append("")
out.write_text("\n".join(lines), encoding="utf-8")
print(f"\n结果已写 {out}")
sys.exit(0 if ok_count == len(results) else 1)
