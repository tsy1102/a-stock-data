# 项目路由与权威索引

> 本页只维护任务入口、稳定架构边界和规则真源，不保存测试计数、接口数量、当前采集状态或历史快照。按任务读取对应材料，不默认加载整份 registry、raw 或历史报告。

## 1. 任务路由

| 任务 | 先读 | 按需读取 |
|---|---|---|
| 五大报告生成与日报质检 | [`../README.md`](../README.md)、[`../scripts/README.md`](../scripts/README.md) | [`script_data_dict.md`](script_data_dict.md)、[`../tests/reports/README.md`](../tests/reports/README.md) |
| 日常字段采集与碰撞 | [`field_verification/DAILY_RUNBOOK.md`](field_verification/DAILY_RUNBOOK.md) | 当日 `meta.json`、[`../scripts/README.md`](../scripts/README.md) |
| 碰撞报告完整性与候选审阅 | [`field_verification/COLLISION_REPORT_REVIEW.md`](field_verification/COLLISION_REPORT_REVIEW.md) | 当日报告 JSON、[`field_verification/ADJUDICATION_WORKFLOW.md`](field_verification/ADJUDICATION_WORKFLOW.md) |
| 未知字段分析与定案 | [`field_dict.md`](field_dict.md)、[`field_verification/COLLISION_RULES.md`](field_verification/COLLISION_RULES.md) | [`field_verification/CRACKING_METHODOLOGY.md`](field_verification/CRACKING_METHODOLOGY.md)、原始证据、[`field_verification/ADJUDICATION_WORKFLOW.md`](field_verification/ADJUDICATION_WORKFLOW.md) |
| 官方网页字段核验 | [`field_verification/PUBLIC_WEB_VERIFICATION.md`](field_verification/PUBLIC_WEB_VERIFICATION.md) | `field_dict.md`、候选报告与原始来源日期 |
| 字典或采集器改动 | [`../AGENTS.md`](../AGENTS.md) §3、[`field_registry.json`](field_verification/field_registry.json) | 生成视图、适配器、消费者和测试 |
| 报告数据或路由改动 | [`script_data_dict.md`](script_data_dict.md)、[`architecture.md`](architecture.md) | 报告入口、数据适配器和相关测试 |
| 网络、DNS 或限流故障 | [`../scripts/README.md`](../scripts/README.md)、[`architecture.md`](architecture.md) | [`../stock_common/sc_network.py`](../stock_common/sc_network.py)、[`../core/tdx_client.py`](../core/tdx_client.py)、对应测试；网页核验按上方专用流程 |
| 架构边界或实现偏离 | [`ARCHITECTURE_THEORY.md`](ARCHITECTURE_THEORY.md) | [`DEBT_LEDGER.md`](DEBT_LEDGER.md)、对应调用链 |
| 上游或依赖复核 | [`UPSTREAM_COMPATIBILITY.md`](UPSTREAM_COMPATIBILITY.md) | [`source_repository_map.md`](source_repository_map.md)、requirements |
| 测试与验收 | [`../tests/README.md`](../tests/README.md)、[`../AGENTS.md`](../AGENTS.md) §4 | 被改模块及相关测试 |
| 模块拆分历史 | [`PROJECT_MODULE_MAP.md`](PROJECT_MODULE_MAP.md) | 仅在相关拆分任务中读取，并按当前代码复核 |

## 2. 稳定架构与规则真源

- `main.py` 调度五个报告入口；字段核验依次经过采集、碰撞、候选审阅和正式裁决。模块边界见 [`architecture.md`](architecture.md)。
- Tier 1 字段门面位于 `core/data_provider.py`；Tier 2 公开适配器位于 `stock_common/` 和 `core/tdx_client.py`。具体路由以代码、测试和 [`ARCHITECTURE_THEORY.md`](ARCHITECTURE_THEORY.md) 为准。
- 字段身份与状态以 `field_verification/field_registry.json` 的 `(source, 完整 code path)` 为准；生成的字典和未知队列只作导航。
- 碰撞阈值与状态机以 `scripts/collision_rules.py` 为准；日期、样本择优和资格由 `scripts/collision_dates.py`、`scripts/temporal_policy.py` 与 `field_verification/temporal_policy.json` 共同决定。
- 架构原则以 `ARCHITECTURE_THEORY.md` 为准；接受的实现偏离登记在 `DEBT_LEDGER.md`。采集日常操作、报告复核、网页核验和注册表写回分别遵循上表对应流程。
- 项目数据采集和公开数据 HTTP 请求走直连策略；[`core/gd_uploader.py`](../core/gd_uploader.py) 是配置代理的 Google Drive 上传入口。Chrome 网页核验不以 TUN/直连状态预检作为启动条件，细则见 [`PUBLIC_WEB_VERIFICATION.md`](field_verification/PUBLIC_WEB_VERIFICATION.md)。

## 3. 上下文与动态状态

- 大体积 registry、raw 样本和碰撞报告按需查询。报告先通过 [`query_collision_report.py`](../scripts/query_collision_report.py) 定位和分页读取；翻页时保持相同筛选条件并核对报告与选择集哈希。
- Git 状态、数据日、来源健康、候选数量和测试结果都是动态信息。核实时读取当次状态与产物，不从本文件、路线图、变更记录或旧报告推断当前值。
- 样本保留边界遵循根目录 [`AGENTS.md`](../AGENTS.md)；更早的历史材料只按权威规则作背景引用，不恢复为当前样本。
