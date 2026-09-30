# 文档索引

文档分为项目规则、字段结论和实测证据。字段语义以 `field_dict.md` 为准；证据按数据源或采集日期归档，避免把过程记录重复塞进主字典。

## 从这里开始

| 需要了解 | 入口 |
|---|---|
| 当前项目约束与阅读路径 | [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) |
| 模块、数据路由与架构约束 | [architecture.md](architecture.md)、[ARCHITECTURE_THEORY.md](ARCHITECTURE_THEORY.md) |
| 字段定义和来源 | [field_dict.md](field_dict.md) |
| 报告脚本的数据字段与 fallback | [script_data_dict.md](script_data_dict.md) |
| 术语、版本决策和已知偏离 | [domain_glossary.md](domain_glossary.md)、[roadmap.md](roadmap.md)、[DEBT_LEDGER.md](DEBT_LEDGER.md) |

## 证据与记录

- [`verify/`](verify/README.md)：按数据源整理的字段契约、样本和交叉核验资料。
- [`field_verification/`](field_verification/README.md)：采集流程、破解方法和按日期归档的原始数据与分析报告。
- [采集流水线整改计划](CAPTURE_PIPELINE_REMEDIATION_PLAN_20260930.md)：本轮采集完整度、失败诊断、限流与幂等重采的实施范围和验收项。
- [`session_notes/`](session_notes/README.md)：按日期保存的会话决策和待办。
- `PROJECT_AUDIT_REMEDIATION_*.md`、日期命名的核查文档：阶段性审计记录；判断当前状态时以代码和当次验证结果为准。

## 常用查阅路径

| 任务 | 顺序 |
|---|---|
| 核实字段定义 | `field_dict.md` → 该字段引用的 `verify/` 附录 |
| 破解未知字段 | `field_dict.md` → `field_verification/CRACKING_METHODOLOGY.md` → 对应日期采集与对撞报告 |
| 修改报告脚本 | `script_data_dict.md` → 架构文档 → 相关代码和测试 |
| 恢复项目上下文 | `PROJECT_CONTEXT.md` → 最新会话纪要；动态状态需现场核实 |

## 维护约定

- 主字典只记录字段结论、来源和必要摘要；详细样本与推理放入对应证据文档，并从主字典链接。
- 新增 `verify/` 附录时，同步登记到主字典附录索引；该目录结构由 [`verify/README.md`](verify/README.md) 维护。
- 新增采集源或归档产物时，更新 [`field_verification/README.md`](field_verification/README.md)，不要在本索引重复列出每日文件清单。
- 改变字段结构、单位或缓存语义时，按缓存文档升级相应 schema 版本。
