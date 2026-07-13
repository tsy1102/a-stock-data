#!/usr/bin/env python3
"""前复权算法调试"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tdx_client import _get_tdx_client, tdx_get_security_bars
from stock_common import _safe_float as sf

keys, rows = tdx_get_security_bars('600519', count=800)
client = _get_tdx_client()
xdxr_df = client.get_xdxr_info(1, '600519')

# 构建adj_list
adj_list = []
for _, row in xdxr_df.iterrows():
    cat = int(row.get('category', 0))
    if cat != 1: continue
    date_str = str(row.get('date', ''))[:10]
    fh = sf(row.get('fenhong', 0)) / 10
    szg = sf(row.get('songzhuangu', 0)) / 10
    pg = sf(row.get('peigu', 0)) / 10
    pgj = sf(row.get('peigujia', 0))
    dilution = 1.0 + szg + pg
    if dilution <= 0: dilution = 1.0
    adj_list.append({
        'date': date_str,
        'dilution_factor': 1.0 / dilution,
        'bonus_per_share': fh,
        'allot_cost_per_share': pg * pgj,
    })

adj_list.sort(key=lambda x: x['date'])
print(f'adj_list count: {len(adj_list)}')

# 取2023-06-29的K线行
test_date = '2023-06-29'
test_idx = None
for i, r in enumerate(rows):
    if r[0] == test_date:
        test_idx = i
        break

if test_idx is not None:
    orig_close = sf(rows[test_idx][2])
    print(f'原始收盘: {orig_close}')
    
    new_close = orig_close
    applied_count = 0
    for adj in reversed(adj_list):
        if test_date >= adj['date']:
            continue
        dilution = adj['dilution_factor']
        bonus = adj['bonus_per_share']
        allot_cost = adj['allot_cost_per_share']
        new_close = (new_close - bonus + allot_cost) * dilution
        applied_count += 1
        print(f'  除权日{adj["date"]}: bonus={bonus:.4f} factor={dilution:.6f} -> new_close={new_close:.2f}')
    
    print(f'应用了{applied_count}次除权调整')
    print(f'前复权收盘: {new_close:.2f}')
    print(f'差异: {orig_close - new_close:.2f}')
