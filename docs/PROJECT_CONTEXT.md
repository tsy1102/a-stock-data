# 项目静态上下文

> 本文件只做任务路由和稳定结构摘要，不维护测试数、接口数、版本状态或采集快照等易变信息。

## 0. 任务路由

| 任务 | 先读 | 按需读取 |
|---|---|---|
| 公开网页字段核验 | [`field_verification/PUBLIC_WEB_VERIFICATION.md`](field_verification/PUBLIC_WEB_VERIFICATION.md) | `field_dict.md`、[`field_verification/ADJUDICATION_WORKFLOW.md`](field_verification/ADJUDICATION_WORKFLOW.md)、当日完整候选报告与原始来源日期 |
| 日常采集与碰撞 | [`field_verification/DAILY_RUNBOOK.md`](field_verification/DAILY_RUNBOOK.md) | 当日 `meta.json`、[`scripts/README.md`](../scripts/README.md) |
| 未知字段分析与裁决 | [`field_dict.md`](field_dict.md)、[`field_verification/COLLISION_RULES.md`](field_verification/COLLISION_RULES.md) | [`field_verification/CRACKING_METHODOLOGY.md`](field_verification/CRACKING_METHODOLOGY.md)、原始证据、[`field_verification/ADJUDICATION_WORKFLOW.md`](field_verification/ADJUDICATION_WORKFLOW.md) |
| 字典或采集器改动 | [`../AGENTS.md`](../AGENTS.md) §8、逐源 registry | 生成视图、适配器、实际消费者和测试 |
| 报告数据或路由改动 | [`script_data_dict.md`](script_data_dict.md)、[`architecture.md`](architecture.md) | 报告入口、数据适配器和相关测试 |
| 架构边界或偏离 | [`ARCHITECTURE_THEORY.md`](ARCHITECTURE_THEORY.md) | [`DEBT_LEDGER.md`](DEBT_LEDGER.md)、对应调用链 |
| 上游或依赖复核 | [`UPSTREAM_COMPATIBILITY.md`](UPSTREAM_COMPATIBILITY.md) | [`source_repository_map.md`](source_repository_map.md)、requirements |
| 测试与验收 | [`../tests/README.md`](../tests/README.md)、[`../AGENTS.md`](../AGENTS.md) §9 | 被改模块及相关测试 |
| 模块拆分历史 | [`PROJECT_MODULE_MAP.md`](PROJECT_MODULE_MAP.md) | 对照当前代码重新核实调用方和状态所有权 |

## 1. 项目结构

- 五个报告入口为 `get_sht_report.py`、`get_med_report.py`、`get_lng_report.py`、`get_val_report.py`、`get_mak_report.py`；`main.py` 负责调度。
- 字段采集、候选分析和正式裁决是分开的流程：入口分别在 `scripts/capture_field_probe.py`、`scripts/collide.py` 和 `scripts/apply_collision_adjudications.py`。
- Tier 1 统一入口位于 `core/data_provider.py`；专精数据通过 `stock_common/` 和 `core/tdx_client.py` 的公开适配器提供。具体路由以执行代码和测试为准。
- 报告、缓存和字段证据分别位于 `reports/`、各数据适配器配置位置及 `docs/field_verification/`。

## 2. 规则真源

- 字段身份和状态：`field_verification/field_registry.json` 的 `(source, 完整 code path)`；生成视图仅供导航。
- 碰撞阈值与状态机：`scripts/collision_rules.py`；日期和样本资格：`scripts/collision_dates.py` 与 `temporal_policy.json`。
- 架构原则：`ARCHITECTURE_THEORY.md`；运行规约：根目录 `AGENTS.md`；明确接受的偏离：`DEBT_LEDGER.md`。
- 操作步骤：`DAILY_RUNBOOK.md`；候选证据分析：`CRACKING_METHODOLOGY.md`；正式写回：`ADJUDICATION_WORKFLOW.md`。

## 3. 上下文与状态

大体积 registry、候选报告和 raw 样本按需查询，不要全量载入上下文。碰撞报告先检查完整性，再通过 `scripts/query_collision_report.py` 定位和分页读取；筛选条件及报告哈希必须保持一致。

Git 状态、数据日、源健康、候选数量和测试结果都是动态信息。核实时读取当次状态与产物，不从本文件、路线图、变更记录或旧报告推断当前值。

Python 环境和验收入口见 [`../AGENTS.md`](../AGENTS.md) 与 [`../tests/README.md`](../tests/README.md)。
