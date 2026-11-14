# Push2EX 池根路径是采集容器，不是字段

裁决日期：2026-11-15
范围：`东财-push2ex::limit_up_pool`、`::limit_down_pool`、`::limit_broken_pool`

## 证据

1. [`capture_catalog.py`](../../../scripts/capture_catalog.py) 将三条 Push2EX 接口分别登记为采集单元，并把对应名称登记在 `output_paths`。[`capture_http_collectors.py`](../../../scripts/capture_http_collectors.py) 的 `collect_push2ex()` 调用 `get_limit_up_pool`、`get_limit_down_pool`、`get_limit_broken_pool`，再将返回列表写入 `out[output_name]`。因此这三个名称是项目采集器的列表容器路径，不是接口记录中的字段键。
2. [`_pools.py`](../../../stock_common/sc_datasource/_pools.py) 的限价池解析器返回按股票拆分的字典列表。字段完整性审计 [`audit_field_completeness.py`](../../../scripts/audit_field_completeness.py) 也只合并这些列表项的键作为 `东财-push2ex` 字段，不把根层容器名登记为字段。
3. 对保留起点 `20261015` 之后且 `meta.json.data_date` 与目录名一致的 18 个归档逐一检查：三条根路径在 18/18 个目录里均为列表。涨停池累计 1,054 行，炸板池 533 行，跌停池 0 行。逐日类型、行数、目录日期、来源日期字段和 raw/meta SHA-256 见 [`研究审计表`](../research/20261115_push2ex_pool_container_audit.csv)。未读取保留起点前的样本。
4. 18 个归档都没有 `source_as_of_dates.push2ex`。这里的归档只用于验证项目输出形状；没有把其列表值作为数值碰撞样本，也没有把目录日期当作来源实际日期。`limit_down_pool` 在这些样本中长度为 0，只表示观察到的列表为空，不能推断上游始终无记录或接口失效。

## 结论和范围

将三个精确身份标记为 `disproved` / `collector_output_container`，从未知字段队列移出：它们是采集器生成的集合容器名，字段应从列表中每条股票记录的完整键路径识别。这个分类不否定三个接口或池内字段，也不改变采集行为。

本裁决不处理 `sector`、池内行情字段或昨日池的 `yfbt` / `ylbc` / `y_first_seal` / `y_limit_count`。昨日池尚需后续交易日生成日期合格样本后再核验。
