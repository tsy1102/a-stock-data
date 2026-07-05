#!/usr/bin/env python3
"""测试 tdx_get_financial_analysis 函数"""
import sys
import json
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tdx_client import tdx_get_financial_analysis


def test_code(code: str):
    print(f"\n{'='*60}")
    print(f"测试股票: {code}")
    print('='*60)
    result = tdx_get_financial_analysis(code)
    if not result:
        print(f"  ❌ 返回空数据")
        return

    # 1. 主要财务指标
    mi = result.get('main_indicators', [])
    print(f"\n[1] 主要财务指标: {len(mi)} 期")
    if mi:
        latest = mi[0]
        print(f"  最新期: {latest.get('period')}")
        print(f"  审计意见: {latest.get('审计意见', 'N/A')}")
        print(f"  归母净利(万): {latest.get('归母净利(未调整:万)', 'N/A')}")
        print(f"  营业总收(万): {latest.get('营业总收(未调整:万)', 'N/A')}")
        print(f"  基本每股收益: {latest.get('基本每股收益(元)', 'N/A')}")
        print(f"  每股净资产: {latest.get('每股净资产(元)', 'N/A')}")
        print(f"  加权净资产收益率: {latest.get('加权净资产收益率(%)', 'N/A')}")
        # 列出所有期
        print(f"  所有期: {[e.get('period') for e in mi]}")

    # 2. 偿债能力
    solv = result.get('solvency', [])
    print(f"\n[2] 偿债能力: {len(solv)} 期")
    if solv:
        print(f"  最新期: {solv[0].get('period')}")
        print(f"  流动比率: {solv[0].get('流动比率', 'N/A')}")
        print(f"  速动比率: {solv[0].get('速动比率', 'N/A')}")
        print(f"  资产负债比率: {solv[0].get('资产负债比率(%)', 'N/A')}")

    # 3. 营运能力
    oper = result.get('operation', [])
    print(f"\n[3] 营运能力: {len(oper)} 期")
    if oper:
        print(f"  最新期: {oper[0].get('period')}")
        print(f"  存货周转率: {oper[0].get('存货周转率', 'N/A')}")
        print(f"  应收账款周转率: {oper[0].get('应收账款周转率', 'N/A')}")

    # 4. 盈利能力
    prof = result.get('profitability', [])
    print(f"\n[4] 盈利能力: {len(prof)} 期")
    if prof:
        print(f"  最新期: {prof[0].get('period')}")
        print(f"  净资产收益率: {prof[0].get('净资产收益率', 'N/A')}")
        print(f"  销售毛利率: {prof[0].get('销售毛利率', 'N/A')}")
        print(f"  销售净利率: {prof[0].get('销售净利率', 'N/A')}")

    # 5. 成长能力
    grow = result.get('growth', [])
    print(f"\n[5] 成长能力: {len(grow)} 期")
    if grow:
        print(f"  最新期: {grow[0].get('period')}")
        print(f"  营业收入增长率: {grow[0].get('营业收入增长率', 'N/A')}")
        print(f"  净利润增长率: {grow[0].get('净利润增长率', 'N/A')}")

    # 6. 指标变动说明
    chg = result.get('indicator_changes', [])
    print(f"\n[6] 指标变动说明: {len(chg)} 期")
    if chg:
        for block in chg[:2]:  # 只显示前2期
            items = block.get('items', [])
            print(f"  期 {block.get('period')}: {len(items)} 条变动")
            for item in items[:2]:  # 每期显示前2条
                print(f"    - {item.get('subject')[:30]}: {item.get('current_value')} (上期 {item.get('previous_value')}, {item.get('change_pct')}%)")

    # 7. 资产负债表摘要
    bs = result.get('balance_sheet', [])
    print(f"\n[7] 资产负债表摘要: {len(bs)} 期")
    if bs:
        latest = bs[0]
        print(f"  最新期: {latest.get('period')}")
        print(f"  货币资金: {latest.get('货币资金', 'N/A')}")
        print(f"  存货: {latest.get('存货', 'N/A')}")
        print(f"  商誉: {latest.get('商誉', 'N/A')}")
        print(f"  资产总计: {latest.get('资产总计', 'N/A')}")
        print(f"  负债合计: {latest.get('负债合计', 'N/A')}")
        print(f"  归属母公司权益: {latest.get('归属母公司权益', 'N/A')}")

    # 8-10. 利润表/现金流/环比（可能空）
    print(f"\n[8] 利润表摘要: {len(result.get('income_statement', []))} 期")
    print(f"[9] 现金流量表摘要: {len(result.get('cash_flow', []))} 期")
    print(f"[10] 环比分析: {len(result.get('qoq_analysis', []))} 期")


if __name__ == '__main__':
    for code in ['600519', '000001']:
        try:
            test_code(code)
        except Exception as e:
            import traceback
            print(f"❌ {code} 测试异常: {e}")
            traceback.print_exc()
