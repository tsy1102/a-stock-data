# 碰撞报告完整性与候选审阅

本页规定碰撞报告的结构审阅和候选明细检查。数值门槛见 [`COLLISION_RULES.md`](COLLISION_RULES.md) 与 `scripts/collision_rules.py`；字段分析方法见 [`CRACKING_METHODOLOGY.md`](CRACKING_METHODOLOGY.md)；候选正式写回见 [`ADJUDICATION_WORKFLOW.md`](ADJUDICATION_WORKFLOW.md)。日常执行顺序见 [`DAILY_RUNBOOK.md`](DAILY_RUNBOOK.md)。

## 1. 完整性与日期资格

对报告下语义结论前，先核对 JSON 中的 `report_completeness`：状态必须是 `complete`，方法候选生成数、全量明细数、重复数和缺失数应能对平。若有 `candidate_review`，另行核对机器候选完整性、身份校验、人工审阅覆盖率及待处理量。`report_completeness.status=complete` 只代表报告结构和明细对账完整，不代表人工审阅完成、交易日连续或所有来源采集成功。

同时核对 `trading_window` 是否为报告要求的最近 N 个交易日，并检查缺采集目录、来源日期、采集阶段、每日样本量、信息配对、来源独立性、来源失败和告警。逐源读取 JSON 的完整 `source_coverage` 并与 Markdown 汇总对照；契约字段数不是实测覆盖数。来源日期和字段时效按 [`temporal_policy.json`](temporal_policy.json) 与 `scripts/temporal_policy.py` 判断。

报告候选审阅不能只看 Markdown Top-N。先按 `candidate_triage.targets` 的 `review_route` 排序：优先检查官方契约锚强匹配，再检查官方锚诊断/无结果、日期业务语义，最后检查一般数值方法线索。官方锚只为来源内语义提供起点；建立跨源映射仍须逐项核路径、单位、日期域、来源独立性和反例。然后按需审阅 JSON 中完整的 `method_candidate_inventory`、L1/L4、目标诊断、公式候选、来源状态、告警和 `candidate_triage.approximate_matches`。近似命中只用于安排复核，不计入 L1/L1-U、正式候选审阅量或注册表证据。已登记映射的复验与新候选分开记录。

同时检查 `source_relation_review`、`candidate_triage.low_information_fields` 和 `candidate_triage.date_value_candidates`。来源关系只比较完整路径上数据域、来源日期和阶段对齐的样本；两来源可用不同但已确认的日期依据，只要实际来源日期一致。强重叠要求相同样本覆盖、无精确值失配或未对齐样本，且排除恒定低信息路径。舍入窗口命中单独列作近似线索，不计强匹配。该队列用于调查接口重复/互补，不等同提供方身份结论，也不自动停采。低信息字段等到出现有效变化后再进入普通碰撞。日期值队列需把字段值与股票、样本键日期、来源 `as_of_date` 联看，再查官方字段定义，以判定上市日、报告期末、披露/事件日、生效日或其他业务角色。

## 2. 使用只读查询器

大报告先用 `scripts/query_collision_report.py` 列章节并筛选分页，避免一次性载入完整 JSON。替换示例中的报告路径为本轮实际产物：

```powershell
$report = 'docs\field_verification\YYYYMMDD\YYYYMMDD_collision_report.json'
.\scripts\run_with_system_python.ps1 scripts\query_collision_report.py --report $report --list-sections
.\scripts\run_with_system_python.ps1 scripts\query_collision_report.py --report $report `
    --section method_candidate_inventory --source ftshare_rest --limit 25
.\scripts\run_with_system_python.ps1 scripts\query_collision_report.py --report $report `
    --section method_candidate_inventory --field ftshare_rest.turnover_rate --limit 10 --format json
```

查询器只读当前完整 schema 5 报告。`--source` 按完整来源名匹配且忽略大小写；`--field` 按完整字段路径区分大小写。未传 `--section` 而使用筛选条件时，默认搜索规范候选集合，避免摘要副本重复计数。

每次查询都应核对报告 SHA-256、完整性状态、匹配总数、选择集 SHA-256、页偏移和 `exhausted`。分页时保持相同筛选条件并按 `next_offset` 继续，直到 `exhausted=true`。默认 `compact` 输出通过列定义、行数组和 `present_columns` 区分缺失键与显式 `null`；需要读取完整对象时使用 `--format json`。查询记录不代表候选已人工审阅。

## 3. 报告异常与人工审阅

- 完整性状态异常、候选身份不一致、集合缺失或数量无法对账时，暂停语义结论和主字典裁决。
- 报告缺少完整方法候选明细时，只能从允许读取的保留归档重新生成；样本保留起点遵守根目录 [`AGENTS.md`](../../AGENTS.md)，不得恢复或读取更早 raw、ZHB 压缩包或解析缓存。无法重建时记录未审数量、字段范围和缺失原因。
- 旧版报告若没有完整性字段或全量候选清单，按可能截断处理；查询器不能接受时先依保留边界重建报告，不要把缺失内容当作“无候选”。
- `candidate_review.human_review.status=pending` 表示人工审阅未完成，即使机器报告完整也不能宣称候选已审。
- 候选的处置、审阅台账和显式写回方式统一按 [`ADJUDICATION_WORKFLOW.md`](ADJUDICATION_WORKFLOW.md) 执行；本页的查询和报告检查不会改变注册表或主字典。

## 4. 解释边界

字段名拆词、公式/时间序列、AxData/Levistock 汇总接口和网页页面可提供候选线索或来源身份辅助证据，不能绕过现有 L1/L1-U、独立性或单源契约门槛。网页核验的来源顺序、逐样本留证和候选限额见 [`PUBLIC_WEB_VERIFICATION.md`](PUBLIC_WEB_VERIFICATION.md)。
