# 项目静态上下文（PROJECT_CONTEXT）

> **用途**：项目架构、稳定约束与文档索引。任务开始时先按下表读取相关部分，不必重复扫描整份文档。
> **维护规则**：结构、入口或稳定流程变化时更新；字段语义以主字典为准，运行状态与测试结果以实际检查为准。
> **更新日期**：2026-10-08（`VERSION`：17.4.29）

## 0. 指引目录

| 任务类型 | 热区（必读） | 温区（建议） | 冷区（按需） |
|---|---|---|---|
| 字段破解/字典 | `AGENTS.md` §5、§8 | 权威顺序与来源谱系 | `field_dict.md`、`unknown_fields.md`、registry、当日采集归档 |
| 脚本修改/新功能 | `AGENTS.md` §5、§8 | §2 架构、相关脚本 | 字段字典与缓存契约 |
| 测试/回归 | `AGENTS.md` §2.1、§9 | 被修改模块 | 对应测试文件 |
| 运行/报告核查 | `AGENTS.md`、§1 | 最新报告与运行记录 | 历史报告 |
| 性能/限流 | `AGENTS.md` §8.4 | §2 架构、`sc_network` | 性能记录 |
| 发布/版本 | `AGENTS.md` §5、§10 | `CHANGELOG.md`、`roadmap.md` | Git 历史 |
| 数据采集/验证 | `AGENTS.md`、§1 | 当日 `field_verification` 目录 | 历史采集归档 |
| 上游/依赖复核 | `AGENTS.md` §8 | `UPSTREAM_COMPATIBILITY.md` | `source_repository_map.md`、requirements |
| Agent/测试临时目录 | `AGENTS.md` §1.3 | 仓库根 `.tmp/` | `scripts/run_with_system_python.ps1` |

## 1. 项目目标与运行概况

- A 股分析项目由 5 个报告入口生成个股与全市场 Markdown 报告：`get_sht_report.py`、`get_med_report.py`、`get_lng_report.py`、`get_val_report.py`、`get_mak_report.py`。
- `main.py` 负责调度子进程。生产任务按配置顺序执行；报告脚本负责自身流水线与上传。
- 数据分为离线 ZHB 与实时行情等数据。是否读取 ZHB 或实时源取决于交易日和时段；不能概括成“ZHB 始终优先”。
- 报告写入 `reports/`，运行缓存位于 `cache/` 或各模块配置的缓存目录；采集原始数据位于 `docs/field_verification/`。

## 2. 当前架构与数据路由

| 层 | 入口/模块 | 职责 |
|---|---|---|
| 调度层 | `main.py` | 解析任务、启动报告子进程、汇总退出结果 |
| 报告层 | 5 个 `get_*_report.py`、`stock_common/sc_report_runner.py` | 组装分析流程、渲染报告、上传结果 |
| Tier 1 统一门面 | `core/data_provider.get_canonical_stock_data()` | 核心字段归一化、来源选择、fallback、单位统一与 `field_sources` 溯源 |
| Tier 2 专项适配器 | `stock_common/sc_datasource`、`sc_fuyao`、`core/tdx_client.py` 等公开函数 | CYQ、F10、涨停梯队、龙虎榜、行业和其他专用数据 |
| 原始客户端 | `stock_common/`、`core/tdx_client.py` 内部 | HTTP、TCP、SDK 等底层访问；生产报告脚本不得绕过公开门面直连 |
| 缓存 | `core/stock_cache.py` 及模块适配器 | 按分类 TTL 缓存；数据单位或语义变化时须同步使旧缓存失效 |

路由要点（以代码为准）：

- 非交易日/节假日以及交易日 09:30 前，`_should_use_zhb_for_realtime()` 允许走 ZHB 路径。
- 交易日 09:30 起走实时行情路径；盘后仍需实时来源，因为本地 ZHB 快照可能还是 T-1。
- 单股行情 fallback 顺序由 `core/data_provider.py` 的运行分支实现：TDX → 腾讯 → push2delay → push2。`core/source_priority.py` 中同名顺序只作为测试契约，不能当作运行时路由配置。
- 字段新鲜度 A/B/C/D 分类由 `sc_datasource.zhb_field_safe()` 控制；字段是否标注“实时”与上述源选择逻辑不是同一概念。
- 完整架构公理见 `docs/ARCHITECTURE_THEORY.md`，已知偏离见 `docs/DEBT_LEDGER.md`。

## 3. 工程与测试约束

- 本仓库默认 Windows PowerShell 5.1；Shell、路径、外部程序和验证流程按 `AGENTS.md` 执行。
- Python 目标版本为 3.10+；项目开发/测试使用 Python 3.12。解释器通过 `scripts/run_with_system_python.ps1` 选择。
- 运行测试使用 `scripts/run_tests.ps1`，不要从 Shell 直接调用 `pytest`。`real_network` 测试须明确选择。
- 最近离线复核（2026-10-06）：pytest 收集 736 项，688 passed、1 skipped、47 deselected；本轮 6 个 Python 文件通过 Black 与编译检查，3 个源码文件 mypy 零错误；A1/A7 闸门均 0 HARD FAIL / 0 WARN。`real_network` 按配置未运行。字段逐源身份仍为 2,469 条；元数据清单显示 239 条 verified 记录缺少规范名或含义（207 缺含义、47 缺规范名、15 两者皆缺），详见 `docs/field_metadata_gaps.md`。来源仓库对话确认 7 项，21 项待确认。运行状态以当次命令输出为准。
- 修改后按 `AGENTS.md` §8 做数据契约影响调查，并按 §9 验证；每次改动记录一个可计数指标。
- `.gitignore` 对运行时缓存和采集原始数据按路径规则处理；清理前应保留仍需离线复核的研究证据。

## 4. 文档索引

| 文档 | 权威范围 |
|---|---|
| `docs/field_dict.md` | 生成的字段治理入口与权威顺序 |
| `docs/unknown_fields.md` | 按逐源完整路径列出的未验证、候选、冲突和已证伪字段 |
| `docs/field_metadata_gaps.md` | 已验证字段中缺少规范名或含义的生成式补录清单 |
| `docs/field_matrix.md` | registry 派生的字段×源矩阵 |
| `docs/source_repository_map.md` | 数据提供方、独立来源族及有证据的 GitHub 仓库映射 |
| `docs/field_source_reference.md` | 重整前字典原文的逐字节历史归档；不是当前状态权威 |
| `docs/field_verification/field_registry.json` | 逐源完整路径的机器权威字段登记表 |
| `docs/field_verification/ADJUDICATION_WORKFLOW.md` | 碰撞候选人工复核、字段定案和注册表同步流程 |
| `docs/field_verification/CRACKING_METHODOLOGY.md` | 字段破解方法论和证据要求 |
| `docs/FIELD_DICTIONARY_RESTRUCTURE_PLAN_20261005.md` | 字段字典、来源谱系与碰撞锚点重整步骤 |
| `docs/FIELD_DICTIONARY_OPERATIONAL_CLOSURE_20261006.md` | 定案写回闭环及来源对话确认状态 |
| `docs/FIELD_DICTIONARY_MIGRATION_AUDIT_20261005.md` | 字段身份逐项核对、证据保留、测试与已知覆盖遗留 |
| `docs/script_data_dict.md` | 报告脚本、字段与数据源的消费关系 |
| `docs/ARCHITECTURE_THEORY.md` | 架构公理与数据访问边界 |
| `docs/DEBT_LEDGER.md` | 已知偏离、偿还状态及理由 |
| `docs/domain_glossary.md` | 项目术语与单位口径 |
| `docs/field_verification/` | 破解方法、采集数据及字段验证归档 |
| `docs/roadmap.md`、`CHANGELOG.md` | 决策记录与版本历史 |
| `docs/PROJECT_AUDIT_REMEDIATION_20260928.md` | 本轮审计整改项目、验收进度与结果 |
| `docs/UPSTREAM_COMPATIBILITY.md` | 上游仓库、依赖版本与项目适配边界 |
| `docs/DEPENDENCY_ADAPTER_COMPATIBILITY_PLAN_20261008.md` | Levistock/AxData 适配器兼容核验、回归及实施结果 |

## 5. 动态信息

测试结果、Git 状态、采集日期、运行日志和报告质量都可能变化；需要核实时应读取当次命令输出与对应文件，不能沿用历史快照。
