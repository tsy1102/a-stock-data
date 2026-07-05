#!/usr/bin/env python3
"""测试 tdx_get_latest_reminders 函数"""
import sys
import json
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tdx_client import tdx_get_latest_reminders

for code in ["600519", "000001"]:
    print(f"\n{'='*60}")
    print(f"测试 {code}")
    print('='*60)
    result = tdx_get_latest_reminders(code)
    if not result:
        print("  结果为空!")
        continue

    # 打印关键指标
    ind = result.get('latest_indicators', {})
    print(f"\n[最新指标]")
    print(f"  EPS: {ind.get('eps')}")
    print(f"  每股净资产: {ind.get('net_asset')}")
    print(f"  ROE: {ind.get('roe')}")
    print(f"  总股本: {ind.get('total_capital')}")
    print(f"  变动原因: {ind.get('change_reason')}")
    if 'holder_count' in ind:
        print(f"  股东人数: {ind['holder_count']}")
    if 'financial_yoy' in ind:
        print(f"  财务同比: {ind['financial_yoy']}")

    # 互动问答
    qa = result.get('interaction_qa', [])
    print(f"\n[互动问答] {len(qa)} 条")
    for q in qa[:2]:
        print(f"  {q['date']}: {q['question'][:50]}...")

    # 最新公告
    anns = result.get('latest_announcements', [])
    print(f"\n[最新公告] {len(anns)} 条")
    for a in anns[:2]:
        print(f"  {a['date']}: {a['title'][:50]}...")

    # 最新报道
    news = result.get('latest_news', [])
    print(f"\n[最新报道] {len(news)} 条")
    for n in news[:2]:
        print(f"  {n['date']}: {n['title'][:50]}...")

    # 大宗交易
    bt = result.get('block_trades', [])
    print(f"\n[大宗交易] {len(bt)} 条")
    for b in bt[:3]:
        print(f"  {b['date']}: 价格={b['price']}, 数量={b['volume']}, 买方={b['buyer']}, 卖方={b['seller']}")

    # 融资融券
    mt = result.get('margin_trading', [])
    print(f"\n[融资融券] {len(mt)} 条")
    for m in mt[:3]:
        print(f"  {m['date']}: 融资余额={m['finance_balance']}, 融资买入={m['finance_buy']}")

    # 风险提示
    risk = result.get('risk_warnings', {})
    print(f"\n[风险提示]")
    if risk:
        print(f"  违规稽查: {risk.get('violation', {})}")
        print(f"  交易所问询: {risk.get('inquiry')}")
        print(f"  特别处理: {risk.get('special_treatment')}")
    else:
        print("  无")
