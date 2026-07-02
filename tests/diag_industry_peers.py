#!/usr/bin/env python3
"""诊断脚本：测试 get_industry_peers 返回的同业股票数据是否正常

用法:
    python tests/diag_industry_peers.py 002409
"""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

code = sys.argv[1] if len(sys.argv) > 1 else "002409"

# 1. 直接测试 tdx_get_board_members — 看 TDX 返回了原始什么数据
print(f"{'='*60}")
print(f"  诊断: get_industry_peers('{code}')")
print(f"{'='*60}")

from tdx_client import tdx_get_belong_boards, tdx_get_board_members, _get_mac_client

print(f"\n【1】_get_mac_client() 是否可用:")
client = _get_mac_client()
print(f"  mac_client = {client is not None}")

boards = tdx_get_belong_boards(code)
industry = boards.get("industry", []) if boards else []
print(f"\n【2】tdx_get_belong_boards('{code}'): industry={len(industry)} 条")
if industry:
    primary = industry[0]
    print(f"  主行业: {primary['name']} (code={primary['code']})")
    
    # 2. 直接测 board_members — 看 TDX 返回了什么原始数据
    print(f"\n【3】tdx_get_board_members('{primary['code']}'):")
    members = tdx_get_board_members(primary["code"])
    print(f"  返回 {len(members)} 只股票")
    if members:
        # 检查关键字段是否有值
        bad = 0
        for m in members[:5]:
            has_price = m.get("price", 0) > 0
            has_chg = m.get("change_pct", 0) != -100 and m.get("price", 0) > 0
            status = "✅" if (has_price and m.get("price", 0) > 0) else "❌"
            print(f"  {status} {m['code']} {m['name']:<12} price={m['price']:<8.2f} chg={m['change_pct']:<8.2f}% mcap={m['mcap_yi']:<8.1f} pe={m['pe']:<8.1f}")
            if not has_price:
                bad += 1
        print(f"  ... (共 {len(members)} 只, price=0 的有 {bad} 只)")

# 3. 测试 get_industry_peers 整体
print(f"\n【4】get_industry_peers('{code}'):")
from stock_common import get_industry_peers
import time
t0 = time.time()
peer_data = get_industry_peers(code)
t1 = time.time()
print(f"  耗时: {t1-t0:.2f}s")
if peer_data and peer_data.get("peers"):
    print(f"  行业: {peer_data['industry']}")
    print(f"  本股市值排名: {peer_data['my_rank']}/{peer_data['industry_count']}")
    print(f"  同业列表:")
    for p in peer_data["peers"]:
        price_ok = p.get("price", 0) > 0
        chg_ok = p.get("change_pct", 0) != -100 or price_ok == False
        status = "✅" if price_ok else "❌"
        print(f"  {status} {p['code']:<8} {p['name']:<12} price={p['price']:<8.2f} chg={p['change_pct']:<7.2f}% mcap={p['mcap_yi']:<8.1f}")
else:
    print(f"  ❌ 无同业数据")
    print(f"  peer_data={peer_data}")

# 4. 对比腾讯行情的数据
print(f"\n【5】腾讯行情数据（对比验证）:")
from stock_common import get_tencent_quote
for p in (peer_data.get("peers", []) if peer_data else []):
    q = get_tencent_quote(p["code"])
    if q:
        print(f"  {p['code']} {p['name']:<12} 腾讯: price={q.get('price',0):.2f} chg={q.get('change_pct',0):.2f}%")
    else:
        print(f"  {p['code']} {p['name']:<12} 腾讯: None")
