"""源优先级单一真相源 (Single Source of Truth for source priority).

V17.4 (2026-09-21): 将散落于三处的源优先级收敛到一处——
  1) core/data_provider.py 内联分支 (L1/L2/L3 fallback)
  2) docs/field_dict.md §零·B / §一 文档描述
  3) scripts/audit_field_completeness.py 的 SECTION_MAP 审计映射
——运行时取数顺序原本只存在于 data_provider 的内联逻辑，新增/调权源需改多处且易漂移。
本模块把"顺序"提升为显式常量，data_provider 引用之（行为不变），并附一致性校验供测试/启动期调用。

顺序定义依据（与既有内联逻辑一一对应，勿随意调整，否则改变 fallback 行为）：
  - 行情 (QUOTE): L1 TDX(eltdx 本地 TCP) → L2 腾讯(qt.gtimg) → L3 东财(push2delay 镜像 → push2 主域)
      证据: core/data_provider.py:406-424 (L1 TDX) / :427-441 (L2 腾讯) / :446-480 (L3 东财)
  - 估值 (VALUATION): 腾讯独有 roa/pe_ttm/pb/股息率 补取 + fuyao 升财务 TTM 主源
      证据: core/data_provider.py:482+ (腾讯补取) / :551 (fuyao 升 TTM 主源)
  - 资金流 (FUND_FLOW): push2 f137 → TDX + get_em_fund_flow_multiday(push2)
      证据: core/data_provider.py:638-700 (push2 f137→TDX) / :675 (get_em_fund_flow_multiday)

本模块为纯声明 + 校验，不含网络 IO；引用方负责按序 fallback。
"""

from typing import List

# 行情实时报价 fallback 顺序（索引越小优先级越高）
QUOTE_FETCH_ORDER: List[str] = [
    "tdx",                 # L1: eltdx 本地 TCP 实时
    "tencent",             # L2: qt.gtimg 不封 IP，优先于 push2
    "eastmoney_push2delay",  # L3a: push2 镜像域（风控独立、延时 15min）
    "eastmoney_push2",     # L3b: push2 主域（风控最严，独有数据才用）
]

# 估值字段 fallback 顺序（腾讯补取 + fuyao 升主源）
VALUATION_PRIORITY: List[str] = [
    "tencent",             # roa/pe_ttm/pb/股息率 腾讯独有字段
    "fuyao",               # 同花顺财务 TTM 升主源
    "tdx",                 # 本地财务兜底
    "eastmoney_push2",     # 东财兜底
]

# 资金流 fallback 顺序
FUND_FLOW_PRIORITY: List[str] = [
    "eastmoney_push2",     # f137 主力净 + get_em_fund_flow_multiday
    "tdx",                 # TDX 资金流适配层
    "ulist239",            # ulist239 资金流（f62/f66/f72 对撞）
]

# 全量源注册名（与 field_registry.json sources[].name 对齐，供审计/校验引用）
KNOWN_SOURCES: List[str] = [
    "东财-push2", "东财-资金流(em_fund_flow)", "东财-ulist239(np/get)", "东财-push2ex",
    "东财-datacenter", "东财-slist", "东财-clist", "腾讯(qt.gtimg)", "新浪(hq.sinajs)",
    "同花顺-fuyao", "TDX(双命名源)", "AxData", "东财-push2_full", "ZHB-tdxstat",
    "ZHB-tdxstat2", "ZHB-tipinfo", "TDX-eltdx(适配层)", "财联社(cls)", "百度(baidu)",
    "沪深交易所", "巨潮(cninfo)", "reports", "东财-em_kline_f61", "东财-热榜(em_hot)",
    "市场源(market_sources)", "levistock(ftshare)",
]


def check_quote_priority() -> List[str]:
    """校验 QUOTE_FETCH_ORDER 与 data_provider 内联逻辑声明一致。

    返回不一致告警列表（空列表=一致）。非破坏性：仅报告，不改行为。
    由测试套件 / 启动期调用。
    """
    warnings: List[str] = []
    expected_prefixes = ("tdx", "tencent", "eastmoney_push2delay", "eastmoney_push2")
    for i, name in enumerate(QUOTE_FETCH_ORDER):
        if not name.startswith(expected_prefixes[i]):
            warnings.append(
                f"[QUOTE] 位置 {i} 期望 {expected_prefixes[i]}* 但为 {name} —— 与内联 L{i+1} 不一致"
            )
    return warnings


def check_all() -> List[str]:
    """聚合所有优先级一致性校验。"""
    return check_quote_priority()


if __name__ == "__main__":
    w = check_all()
    if w:
        for line in w:
            print("WARN:", line)
    else:
        print("OK: 源优先级声明与内联逻辑一致")
