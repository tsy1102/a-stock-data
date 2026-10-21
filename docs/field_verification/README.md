# 字段实测验证（Field Verification）

本目录保存固定股票池的多源原始采样、来源元数据、字段碰撞和人工复核证据，用于发现字段未知、错义、单位差异与来源映射问题。日常执行从 [`DAILY_RUNBOOK.md`](DAILY_RUNBOOK.md) 开始。

## 权威规则

- [`COLLISION_RULES.md`](COLLISION_RULES.md)：由 `scripts/collision_rules.py` 生成，镜像当前运行时碰撞阈值与状态机。
- [`CRACKING_METHODOLOGY.md`](CRACKING_METHODOLOGY.md)：候选生成、数据拆解和常见误判；按需读相关章节，不替代运行时阈值。
- [`EVIDENCE_COVERAGE.md`](EVIDENCE_COVERAGE.md)：字段覆盖、交易日/自然日、来源日期与证据边界。
- [`ADJUDICATION_WORKFLOW.md`](ADJUDICATION_WORKFLOW.md)：跨源关系、单源契约核验与注册表写回。
- [`review_templates/candidate_review_template.json`](review_templates/candidate_review_template.json)：人工候选审阅决定模板；审阅台账按需生成，默认不创建空状态文件。
- [`../../scripts/README.md`](../../scripts/README.md)：采集源顺序、限流、候选接口日轮和冗余退出/复验条件。

## 当前调查计划

- [`f118_ulist_source_semantics_plan.md`](f118_ulist_source_semantics_plan.md)：区分 push2 与 ulist239 的 `f107` / `f118` 逐源身份、含义和占位状态；计划未执行前不更新注册表。

## 归档格式

```text
docs/field_verification/<目标数据日>/
├── raw_<source>.json
├── meta.json
├── <报告日>_collision_report.md/.json
└── analysis.md（可选人工分析）
```

目录名表示目标数据日，不一定是运行自然日。`meta.json` 保存实际运行时间、`capture_date/run_date`、`data_date`/日期域、市场阶段、来源状态和各自 `as_of_date`；ZHB 还记录包实际数据日。保留原始目录和日期以维持溯源，碰撞器会按来源数据日去重与择优，不要通过改名或删除目录来“修正”日期。

schema 5 碰撞 JSON 为候选保存稳定 `candidate_id`；人工处置单独进入 `collision_candidate_reviews.json`，不会自动写入主字典。每条决定须引用包含该候选的碰撞报告并保留 SHA-256；审阅覆盖率、未审数量和重复组关系见当次报告的 `candidate_review`。状态文件不存在时代表本轮均为 `unreviewed`，不是人工审阅完成。

Fuyao raw 还保留 `auction_snapshot_meta` 信封摘要；竞价字段仅在源响应成功、来源日期明确且与目标交易日相同、状态确认就绪时参与碰撞。响应时间戳或采集器探测日不能代替来源数据日期；详情见 [`UPSTREAM_COMPATIBILITY.md`](../UPSTREAM_COMPATIBILITY.md)。

## 数据与历史

采集 raw 保留来源原始字段，不做面向报告的单位归一化。重复采集、增量 `--only`、`--overwrite` 与上下文采集的行为见日常运行卡和采集脚本说明。历史日期目录及分析报告用于追溯；当前字段定义以 `../field_dict.md`、逐源 registry 和后续裁决记录为准，旧的静态覆盖/里程碑摘要不代表当前源健康或字段状态。
