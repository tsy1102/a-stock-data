"""测试 F10 章节在报告中的集成（阶段二验证）。"""
import os
import sys
os.environ['STOCK_NOCACHE'] = '1'

# 将项目根目录加入 sys.path，使从 tests/ 子目录运行时也能导入顶层模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import tempfile
import aiohttp


async def test_med_report():
    """测试中线报告中的 F10 财务深度/股东行为/主营构成章节。"""
    from get_med_report import generate_report_async
    tmp = tempfile.NamedTemporaryFile(suffix='.txt', delete=False).name
    async with aiohttp.ClientSession() as s:
        r = await generate_report_async(s, '600519', tmp)
    assert '财务深度分析' in r, "缺少【财务深度分析】章节"
    print("✅ med: 财务深度分析章节存在")
    assert '股东行为分析' in r, "缺少【股东行为分析】章节"
    print("✅ med: 股东行为分析章节存在")
    assert '主营构成分析' in r, "缺少【主营构成分析】章节"
    print("✅ med: 主营构成分析章节存在")


async def test_lng_report():
    """测试长线报告中的全部5个F10章节。"""
    from get_lng_report import generate_report_async
    tmp = tempfile.NamedTemporaryFile(suffix='.txt', delete=False).name
    async with aiohttp.ClientSession() as s:
        r = await generate_report_async(s, '600519', tmp)
    for ch in ['财务深度分析', '股东行为分析', '治理结构', '研发与创新', '主营构成分析']:
        assert ch in r, f"缺少【{ch}】章节"
        print(f"✅ lng: {ch}章节存在")


def test_ful_report():
    """测试全维度报告中的全部6个F10章节。"""
    from get_ful_report import analyze_stock
    r = analyze_stock('600519')
    for ch in ['异动与风险提示', '财务深度分析', '股东行为分析',
               '治理结构', '研发与创新', '主营构成分析']:
        assert ch in r, f"缺少【{ch}】章节"
        print(f"✅ ful: {ch}章节存在")


async def main():
    print("=" * 60)
    print("测试 F10 章节集成")
    print("=" * 60)

    print("\n--- 1. 中线报告 (med) ---")
    await test_med_report()

    print("\n--- 2. 长线报告 (lng) ---")
    await test_lng_report()

    print("\n--- 3. 全维度报告 (ful) ---")
    test_ful_report()

    print("\n" + "=" * 60)
    print("全部测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
