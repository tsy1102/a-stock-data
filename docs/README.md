# 文档索引

文档按职责维护单一权威入口。动态数值、当前运行状态和历史报告不构成现行规则；需要核实时回到代码、生成来源和当次产物。

## 项目与开发入口

| 需要了解 | 权威入口 |
|---|---|
| 项目任务路由 | [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) |
| Agent 执行规约 | [`../AGENTS.md`](../AGENTS.md) |
| 稳定术语定义 | [`domain_glossary.md`](domain_glossary.md)；不定义运行策略或字段口径 |
| 架构原则、模块数据流和已知偏离 | [`ARCHITECTURE_THEORY.md`](ARCHITECTURE_THEORY.md)、[`architecture.md`](architecture.md)、[`DEBT_LEDGER.md`](DEBT_LEDGER.md) |
| 报告脚本实际消费的字段与来源 | [`script_data_dict.md`](script_data_dict.md) |
| 依赖版本和上游兼容判断 | [`UPSTREAM_COMPATIBILITY.md`](UPSTREAM_COMPATIBILITY.md)、[`source_repository_map.md`](source_repository_map.md) |
| 测试运行方式与模块说明 | [`../tests/README.md`](../tests/README.md) |

## 字段采集、碰撞与裁决

| 问题 | 权威入口 |
|---|---|
| 日常采集、碰撞、完整报告审阅 | [`field_verification/DAILY_RUNBOOK.md`](field_verification/DAILY_RUNBOOK.md) |
| 公开网页字段核验 | [`field_verification/PUBLIC_WEB_VERIFICATION.md`](field_verification/PUBLIC_WEB_VERIFICATION.md) |
| 当前执行阈值与状态机 | `scripts/collision_rules.py`；[`COLLISION_RULES.md`](field_verification/COLLISION_RULES.md) 是生成镜像 |
| 日期、样本资格与窗口 | `scripts/collision_dates.py`、[`field_verification/temporal_policy.json`](field_verification/temporal_policy.json) |
| 字段身份和状态 | [`field_verification/field_registry.json`](field_verification/field_registry.json)；[`field_dict.md`](field_dict.md) 是生成导航 |
| 待审字段 | [`unknown_fields.md`](unknown_fields.md)、[`field_metadata_gaps.md`](field_metadata_gaps.md) |
| 候选生成与证据判断 | [`field_verification/CRACKING_METHODOLOGY.md`](field_verification/CRACKING_METHODOLOGY.md) |
| 候选人工审阅、单源契约和注册表写回 | [`field_verification/ADJUDICATION_WORKFLOW.md`](field_verification/ADJUDICATION_WORKFLOW.md) |
| 每日覆盖与来源日期边界 | [`field_verification/EVIDENCE_COVERAGE.md`](field_verification/EVIDENCE_COVERAGE.md) |

## 证据和历史记录

- [`field_verification/`](field_verification/README.md)：保留期内原始样本、来源元数据和裁决证据；具体数据边界见 AGENTS 与每日运行卡。
- [`verify/`](verify/README.md)：上游契约、样本和交叉核验资料。
- [`field_source_reference.md`](field_source_reference.md)：重整前字段原文，只读历史归档。
- [`session_notes/`](session_notes/README.md)：仍影响项目决策的会话记录。
- [`roadmap.md`](roadmap.md)：历史路线图的结项入口；当前待办不从旧版本计划恢复。
- [`PROJECT_ARCHITECTURE_REFINEMENT_PLAN.md`](PROJECT_ARCHITECTURE_REFINEMENT_PLAN.md)：已结项的整改摘要。
- [`PROJECT_MODULE_MAP.md`](PROJECT_MODULE_MAP.md)：2026-10-21 模块拆分快照，使用前须对照当前代码。
- 日期命名的审计报告、旧 registry 快照及 `PROJECT_AUDIT_REMEDIATION_*.md` 均为历史记录，不是现行状态源。

## 常用路径

| 任务 | 阅读顺序 |
|---|---|
| 核实字段 | `field_dict.md` → `unknown_fields.md` / registry → 对应证据 |
| 研究候选 | `DAILY_RUNBOOK.md` → `COLLISION_RULES.md` → 方法论相关章节 → 裁决工作流 |
| 修改报告数据 | `script_data_dict.md` → 架构说明 → 对应代码和测试 |
| 修改数据契约 | AGENTS 事实门 → registry/适配器 → 消费方和测试 → 生成视图/parity |
| 完整离线验收 | `scripts/run_offline_checks.ps1`；实际结果以当次输出为准 |

生成的字段视图只能由对应生成器更新；原始样本、主字典和裁决报告按各自保留/写回规则维护。
