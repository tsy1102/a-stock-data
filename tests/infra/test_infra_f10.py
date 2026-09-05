"""测试 F10 章节在报告中的集成（阶段二验证）。

运行方式：
  - pytest 运行（需要真实网络 + fuyao API Key）：
        .\\scripts\\run_tests.ps1 -Mode module -Path tests\\infra\\test_infra_f10.py
  - 直接运行：python -m tests.infra.test_infra_f10

环境依赖说明（2026-09-04 修订）：
  本文件断言的 F10 财务深度章节依赖 fuyao REST 实时返回。此前这是
  回归基线里**恒定的 2 个 FAILED**——属环境性失败，非代码回归，但它
  让"有 2 个红"变成常态，反而掩盖了真正的新增失败。

  现按公理 A8 拆成三层判定，业务断言一个不动：
    1. fuyao API Key 缺失          → skip（环境未配置）
    2. Key 在但上游网络不可达      → skip（环境不具备）
    3. 上游可达而章节缺失          → FAIL（真实回归，必须修）

  ⚠️ 另修复一处测试隔离缺陷：原模块顶层 ``os.environ['STOCK_NOCACHE'] = '1'``
  在 **import（收集）阶段**即生效，会把"禁用缓存"泄漏给整个 pytest 会话，
  影响其他用例。现改为 fixture 内 monkeypatch，作用域收束到本文件。
"""
import os
import sys

# 将项目根目录加入 sys.path（本文件在 tests/infra/ 下，需上溯两级）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import asyncio
import tempfile

import aiohttp
import pytest

_FUYAO_BASE = "https://fuyao.aicubes.cn"


@pytest.fixture(autouse=True)
def _f10_env(monkeypatch):
    """F10 章节集成测试的专属环境。

    - STOCK_NOCACHE=1：让 @cached 成纯透传，确保断言的是**实时返回**的章节，
      而不是命中缓存的旧产物（本测试的价值就在于验证实时链路）。
    - 作用域仅限本文件（原实现写在模块顶层，会泄漏给整个会话）。
    """
    monkeypatch.setenv("STOCK_NOCACHE", "1")


def _require_fuyao(skip_if_upstream_down) -> None:
    """F10 章节的实时数据源前置条件检查（不满足则 skip，不弱化任何断言）。"""
    from stock_common.sc_fuyao import is_fuyao_enabled

    if not is_fuyao_enabled():
        pytest.skip(
            "fuyao API Key 未配置（设 THS_FUYAO_API_KEY 或写入 "
            "credentials/fuyao_key.txt）——环境性跳过，非代码回归"
        )
    skip_if_upstream_down("fuyao", _FUYAO_BASE)


@pytest.mark.real_network
@pytest.mark.asyncio
async def test_med_report(skip_if_upstream_down):
    """测试中线报告中的 F10 财务深度/股东行为/主营构成章节，以及舆情与互动章节。"""
    _require_fuyao(skip_if_upstream_down)
    from get_med_report import generate_report_async
    tmp = tempfile.NamedTemporaryFile(suffix='.txt', delete=False).name
    async with aiohttp.ClientSession() as s:
        r = await generate_report_async(s, '600519', tmp)
    assert '【三、历史财务业绩兑现追踪' in r, "缺少【历史财务业绩兑现追踪】章节"
    assert '【八、筹码稳定性与抛压评估' in r, "缺少【筹码稳定性与抛压评估】章节"
    assert '【四、资产负债表财务健康度' in r, "缺少【资产负债表财务健康度】章节"
    assert '【十七、舆情与互动】' in r, "缺少【十七、舆情与互动】章节"


@pytest.mark.real_network
@pytest.mark.asyncio
async def test_lng_report(skip_if_upstream_down):
    """测试长线报告中的全部5个F10章节，以及舆情与互动章节。"""
    _require_fuyao(skip_if_upstream_down)
    from get_lng_report import generate_report_async
    tmp = tempfile.NamedTemporaryFile(suffix='.txt', delete=False).name
    async with aiohttp.ClientSession() as s:
        r = await generate_report_async(s, '600519', tmp)
    assert '【二、跨期财务纵深与长效业绩验证' in r, "缺少【跨期财务纵深与长效业绩验证】章节"
    assert '【六、长线筹码沉淀与机构持股倾向' in r, "缺少【长线筹码沉淀与机构持股倾向】章节"
    assert '【三、财务健康度排雷' in r, "缺少【财务健康度排雷】章节"
    assert '【五、长效股东回报属性' in r, "缺少【长效股东回报属性】章节"
    assert '【四、未来三年机构一致预期' in r, "缺少【未来三年机构一致预期】章节"
    assert '【十、舆情与互动】' in r, "缺少【十、舆情与互动】章节"


async def main():
    print("=" * 60)
    print("测试 F10 章节集成")
    print("=" * 60)

    from stock_common.sc_fuyao import is_fuyao_enabled
    if not is_fuyao_enabled():
        print("跳过：fuyao API Key 未配置，无法验证 F10 实时章节")
        return

    print("\n--- 1. 中线报告 (med) ---")
    await test_med_report(lambda *a, **k: None)

    print("\n--- 2. 长线报告 (lng) ---")
    await test_lng_report(lambda *a, **k: None)

    print("\n" + "=" * 60)
    print("全部测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
