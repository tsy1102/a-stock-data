# Push2EX `HHMMSS` 是时间编码格式，不是独立返回字段

裁决日期：2026-11-15
精确身份：`东财-push2ex::HHMMSS`

## 问题

注册表把 `HHMMSS` 列为未验证 code path，但没有 canonical、meaning、unit、section 或来源参考状态。需要区分两种可能：它是接口真实返回的字段键，或仅是记录时间值格式的标注。

## 证据

1. [`field_source_reference.md`](../../field_source_reference.md) §12.8.1 的 Push2EX 字段表把 `HHMMSS` 放在“单位”列：`fbt` → `first_limit_time`、`lbt` → `last_limit_time`；昨日池的 `yfbt` 对应 `y_first_seal`，同样标作 `HHMMSS`。表中没有名为 `HHMMSS` 的接口字段。
2. 当前适配器 [`stock_common/sc_datasource/_pools.py`](../../../stock_common/sc_datasource/_pools.py) 的 `_parse_limit_pool` 输出具名的 `first_limit_time`、`last_limit_time` 等键；昨日池解析器输出 `y_first_seal`。它没有构造 `HHMMSS` 键。`HHMMSS` 描述这些时间值的编码形状，不能单独说明对应事件日期或来源数据日。
3. 对保留期内每个含 `raw_push2ex.json` 的目录，先要求目录名不早于 `20261015`，再验证 `meta.json.data_date` 与目录名完全相同；没有读取保留起点前的 raw、ZHB 包或解析缓存。合格归档为 18 个不同数据日：`20261015`、`20261016`、`20261019`、`20261020`、`20261021`、`20261023`、`20261026`、`20261028`、`20261029`、`20261030`、`20261102`、`20261103`、`20261104`、`20261105`、`20261106`、`20261109`、`20261110`、`20261112`。
4. 对上述 18 个 Push2EX 原始 JSON 的所有对象键作精确区分大小写扫描，`HHMMSS` 键出现次数为 0。涨停池 1,054 条、炸板池 533 条、跌停池 0 条；涨停池 1,054 条均有 `sector` 键。逐目录记录了池容器类型、行数、`meta.data_date`、`source_as_of_dates.push2ex` 是否存在，以及每个 raw/meta 文件的 SHA-256，见 [`research/20261115_push2ex_hhmmss_path_audit.csv`](../research/20261115_push2ex_hhmmss_path_audit.csv)。该扫描验证的是响应结构，不把目录日期替代来源日期。
5. 18 个目录的 `source_as_of_dates.push2ex` 均缺失。因此这些 raw 结果未用于正式数值碰撞，也没有据此判定任何时间值的实际日期。

## 结论和范围

将 `东财-push2ex::HHMMSS` 标记为 `disproved` / `not_field_schema_token`：它是时间值格式 token，不是独立返回路径，退出未知字段破解队列。该处理不否认时间值有业务意义；实际承载时间值的是具名路径，例如 `first_limit_time`、`last_limit_time` 和待核的 `y_first_seal`。

本裁决不确认 `y_first_seal` / `yfbt` 的字段语义、`y_limit_count` / `ylbc` 的取值日期或昨日池其余路径，也不建立跨源映射。尤其不能把 `HHMMSS` 当作数据日期或事件日期。上述字段仍按各自完整来源路径待核。
