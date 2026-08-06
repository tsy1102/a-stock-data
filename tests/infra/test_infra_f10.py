"""测试 F10 章节在报告中的集成（阶段二验证）。

运行方式：
  - pytest 运行（需要真实网络）：pytest tests/test_f10_chapters_integration.py -v
  - 直接运行：python -m tests.test_f10_chapters_integration
"""
import os
import sys
os.environ['STOCK_NOCACHE'] = '1'

# 将项目根目录加入 sys.path，使从 tests/ 子目录运行时也能导入顶层模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import tempfile
import aiohttp

import pytest


@pytest.mark.real_network
@pytest.mark.asyncio
async def test_med_report():
    """测试中线报告中的 F10 财务深度/股东行为/主营构成章节，以及舆情与互动章节。"""
    from get_med_report import generate_report_async
    tmp = tempfile.NamedTemporaryFile(suffix='.txt', delete=False).name
    async with aiohttp.ClientSession() as s:
        r = await generate_report_async(s, '600519', tmp)
    assert '【三、历史财务业绩兑现追踪' in r, "缺少【历史财务业绩兑现追踪】章节"
    print("✅ med: 历史财务业绩兑现追踪章节存在")
    assert '【八、筹码稳定性与抛压评估' in r, "缺少【筹码稳定性与抛压评估】章节"
    print("✅ med: 筹码稳定性与抛压评估章节存在")
    assert '【四、资产负债表财务健康度' in r, "缺少【资产负债表财务健康度】章节"
    print("✅ med: 资产负债表财务健康度章节存在")
    assert '【十七、舆情与互动】' in r, "缺少【十七、舆情与互动】章节"
    print("✅ med: 舆情与互动章节存在")


@pytest.mark.real_network
@pytest.mark.asyncio
async def test_lng_report():
    """测试长线报告中的全部5个F10章节，以及舆情与互动章节。"""
    from get_lng_report import generate_report_async
    tmp = tempfile.NamedTemporaryFile(suffix='.txt', delete=False).name
    async with aiohttp.ClientSession() as s:
        r = await generate_report_async(s, '600519', tmp)
    assert '【二、跨期财务纵深与长效业绩验证' in r, "缺少【跨期财务纵深与长效业绩验证】章节"
    print("✅ lng: 跨期财务纵深与长效业绩验证章节存在")
    assert '【六、长线筹码沉淀与机构持股倾向' in r, "缺少【长线筹码沉淀与机构持股倾向】章节"
    print("✅ lng: 长线筹码沉淀与机构持股倾向章节存在")
    assert '【三、财务健康度排雷' in r, "缺少【财务健康度排雷】章节"
    print("✅ lng: 财务健康度排雷章节存在")
    assert '【五、长效股东回报属性' in r, "缺少【长效股东回报属性】章节"
    print("✅ lng: 长效股东回报属性章节存在")
    assert '【四、未来三年机构一致预期' in r, "缺少【未来三年机构一致预期】章节"
    print("✅ lng: 未来三年机构一致预期章节存在")
    assert '【十、舆情与互动】' in r, "缺少【十、舆情与互动】章节"
    print("✅ lng: 舆情与互动章节存在")


async def main():
    print("=" * 60)
    print("测试 F10 章节集成")
    print("=" * 60)

    print("\n--- 1. 中线报告 (med) ---")
    await test_med_report()

    print("\n--- 2. 长线报告 (lng) ---")
    await test_lng_report()

    print("\n" + "=" * 60)
    print("全部测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
