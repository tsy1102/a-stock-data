# 文档索引

文档分为项目规则、字段登记、字段导航和实测证据。逐源字段身份、完整路径与状态以 `field_verification/field_registry.json.source_fields` 为准；`field_dict.md` 是生成的治理入口，历史原文单独归档供追溯。

## 从这里开始

| 需要了解 | 入口 |
|---|---|
| 当前项目约束与阅读路径 | [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) |
| 模块、数据路由与架构约束 | [architecture.md](architecture.md)、[ARCHITECTURE_THEORY.md](ARCHITECTURE_THEORY.md) |
| 已批准并分阶段实施的架构整改方案 | [PROJECT_ARCHITECTURE_REFINEMENT_PLAN.md](PROJECT_ARCHITECTURE_REFINEMENT_PLAN.md) |
| 字段治理入口 | [field_dict.md](field_dict.md) |
| 待破解字段与状态冲突 | [unknown_fields.md](unknown_fields.md) |
| 已验证字段的缺失规范名/含义 | [field_metadata_gaps.md](field_metadata_gaps.md) |
| 字段×源矩阵 | [field_matrix.md](field_matrix.md) |
| 来源与 GitHub 仓库谱系 | [source_repository_map.md](source_repository_map.md) |
| 重整前完整字段原文 | [field_source_reference.md](field_source_reference.md) |
| 机器权威字段注册表 | [field_verification/field_registry.json](field_verification/field_registry.json) |
| 字段字典迁移审计与运营闭环 | [FIELD_DICTIONARY_MIGRATION_AUDIT_20261005.md](FIELD_DICTIONARY_MIGRATION_AUDIT_20261005.md)、[FIELD_DICTIONARY_OPERATIONAL_CLOSURE_20261006.md](FIELD_DICTIONARY_OPERATIONAL_CLOSURE_20261006.md) |
| 碰撞、上游契约和公式证据定案 | [field_verification/ADJUDICATION_WORKFLOW.md](field_verification/ADJUDICATION_WORKFLOW.md) |
| 报告脚本的数据字段与 fallback | [script_data_dict.md](script_data_dict.md) |
| 术语、版本决策和已知偏离 | [domain_glossary.md](domain_glossary.md)、[roadmap.md](roadmap.md)、[DEBT_LEDGER.md](DEBT_LEDGER.md) |

## 证据与记录

- [`verify/`](verify/README.md)：按数据源整理的字段契约、样本和交叉核验资料。
- [`field_verification/`](field_verification/README.md)：采集流程、破解方法和按日期归档的原始数据与分析报告。
- [`field_verification/f118_ulist_source_semantics_plan.md`](field_verification/f118_ulist_source_semantics_plan.md)：ulist239 两条待确认路径的逐来源核验计划。
- [`session_notes/`](session_notes/README.md)：按日期保存的会话决策和待办。
- [`PROJECT_AUDIT_20261015.md`](PROJECT_AUDIT_20261015.md)：本轮全仓审计范围、修复结果、验证和保留事项。
- `PROJECT_AUDIT_REMEDIATION_*.md`、日期命名的核查文档：历史阶段记录；判断当前状态时以代码和当次验证结果为准。
- [`field_verification/_upstream_SKILL_v310.md`](field_verification/_upstream_SKILL_v310.md)：上游项目公开 Skill 的历史快照，仅作来源核对资料，不是当前运行契约。
- [`field_verification/field_registry.json.bak_round3`](field_verification/field_registry.json.bak_round3) 与 [`_reg_tmp_test.json`](field_verification/_reg_tmp_test.json)：2026-09-24 的旧注册表快照，不是当前权威状态；因含有未映射到现行逐源结构的历史记录而保留。

## 常用查阅路径

| 任务 | 顺序 |
|---|---|
| 核实字段定义 | `field_dict.md` → `unknown_fields.md` / `field_registry.json` → 该字段引用的 `verify/` 附录 |
| 破解未知字段 | `unknown_fields.md` → `field_verification/CRACKING_METHODOLOGY.md` → 对应日期采集与对撞报告 → `field_verification/ADJUDICATION_WORKFLOW.md` |
| 核查来源独立性或上游实现 | `source_repository_map.md` → `field_verification/source_lineage.json` → 映射中的项目内证据 |
| 修改报告脚本 | `script_data_dict.md` → 架构文档 → 相关代码和测试 |
| 恢复项目上下文 | `PROJECT_CONTEXT.md` → 最新会话纪要；动态状态需现场核实 |
| 提交前完整离线验收 | `scripts/run_offline_checks.ps1` → 核对 [`tests/README.md`](../tests/README.md) 中的实际结果 |

## 维护约定

- 主字典只记录字段结论、来源和必要摘要；详细样本与推理放入对应证据文档，并从主字典链接。
- 新增 `verify/` 附录时，同步登记到主字典附录索引；该目录结构由 [`verify/README.md`](verify/README.md) 维护。
- 新增采集源或归档产物时，更新 [`field_verification/README.md`](field_verification/README.md)，不要在本索引重复列出每日文件清单。
- 改变字段结构、单位或缓存语义时，按缓存文档升级相应 schema 版本。
