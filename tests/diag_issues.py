#!/usr/bin/env python3
"""测试脚本 - 验证各功能问题"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from stock_common import (
    get_tencent_quote, get_stock_sector_rank, get_industry_peers,
    get_dragon_tiger_board, get_stock_info,
    calculate_multi_school_scores, ScoreData
)

def test_index_data():
    """测试问题1: 指数涨跌幅"""
    print("\n=== 测试1: 指数涨跌幅 ===")
    indexes = ["sh000001", "sz399001", "sz399006", "sh000688"]
    for idx in indexes:
        data = get_tencent_quote(idx)
        print(f"{idx}: price={data.get('price', 'N/A')}, change_pct={data.get('change_pct', 'N/A')}")
        if data.get('change_pct') == 0:
            print("   ⚠️ 涨跌幅为0，可能存在问题")

def test_sector_rank():
    """测试问题3: 板块涨跌排名"""
    print("\n=== 测试3: 板块涨跌排名 ===")
    rank = get_stock_sector_rank("600206")
    if rank:
        print(f"上涨家数: {rank.get('up_count', 'N/A')}")
        print(f"下跌家数: {rank.get('down_count', 'N/A')}")
        print(f"本股排名: {rank.get('my_rank', 'N/A')}/{rank.get('total', 'N/A')}")
        if rank.get('up_count') == 0 and rank.get('down_count') > 0:
            print("   ⚠️ 上涨家数为0，可能存在问题")

def test_industry_peers():
    """测试问题4: 同业对比数据"""
    print("\n=== 测试4: 同业对比数据 ===")
    peers = get_industry_peers("600206", 4)
    if peers:
        print(f"本股: {peers.get('my_name', 'N/A')}")
        for p in peers.get('peers', []):
            print(f"{p.get('code')} {p.get('name')[:12]:<12} price={p.get('price', 'N/A')} change={p.get('change_pct', 'N/A')}%")
            if p.get('price') == 0 or p.get('change_pct') == -100:
                print(f"   ⚠️ 数据异常: price={p.get('price')}, change={p.get('change_pct')}")

def test_dragon_tiger():
    """测试问题6/7: 龙虎榜席位增强"""
    print("\n=== 测试6/7: 龙虎榜席位增强 ===")
    today = datetime.now().strftime("%Y-%m-%d")
    dtb = get_dragon_tiger_board("600206", today)
    print(f"上榜次数: {len(dtb.get('records', []))}")
    print(f"买入席位: {len(dtb.get('seats', {}).get('buy', []))}")
    print(f"卖出席位: {len(dtb.get('seats', {}).get('sell', []))}")
    print(f"席位分析: {dtb.get('seat_analysis', 'None')}")
    if not dtb.get('seat_analysis'):
        print("   ⚠️ seat_analysis为空，席位增强功能未生效")

def test_multi_school_score():
    """测试问题5(ful): 多评委评分"""
    print("\n=== 测试多评委评分 ===")
    try:
        score_data = ScoreData(
            code="600206",
            name="有研新材",
            price=27.5,
            technical_score=69,
            valuation_score=50,
            fundamental_score=65,
            flow_score=58,
            theme_score=68,
        )
        result = calculate_multi_school_scores(score_data)
        print(f"value_score: {result.get('value', {}).total_score}")
        print(f"growth_score: {result.get('growth', {}).total_score}")
        print(f"speculator_score: {result.get('speculator', {}).total_score}")
        print("✅ 多评委评分计算正常")
    except Exception as e:
        print(f"   ❌ 多评委评分计算异常: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("测试脚本启动 - 验证各功能问题")
    print("=" * 60)
    
    test_index_data()
    test_sector_rank()
    test_industry_peers()
    test_dragon_tiger()
    test_multi_school_score()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)