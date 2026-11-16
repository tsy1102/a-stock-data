# Push2EX 昨日涨停池根路径是采集容器，不是字段

裁决日期：2026-11-16
范围：`东财-push2ex::yesterday_limit_pool`

## 证据

1. [`capture_catalog.py`](../../../scripts/capture_catalog.py) 将 `push2ex.yesterday_limit_pool` 登记为 `getYesterdayZTPool` 采集单元，`output_paths` 明确为 `yesterday_limit_pool`。该单元的日期契约还明确说明响应不回显数据日期，且昨日字段和行情字段可能对应不同交易日。
2. [`capture_http_collectors.py`](../../../scripts/capture_http_collectors.py) 的 `collect_push2ex()` 调用 `get_yesterday_limit_pool()`，将适配器返回值整体写入 `out["yesterday_limit_pool"]`。适配器返回的是列表；[`test_capture_field_probe.py`](../../../tests/test_capture_field_probe.py) 验证该输出为逐股记录列表，字段 `y_limit_count` 位于列表项内。字段完整性审计 [`audit_field_completeness.py`](../../../scripts/audit_field_completeness.py) 只从非空池列表项收集记录键，不把根容器名登记为业务字段。
3. 2026-11-16 本机采集成功，raw 中 `yesterday_limit_pool` 的 JSON 类型为数组、长度为 0。`source_as_of_dates.push2ex` 未回显；该样本只用于结构观察，空列表不表示接口失效，也不用于判断字段数据日期或数值含义。按仓库 `.gitignore` 规则，每日 raw 与 `meta.json` 属于可重采本地产物，不提交；[`结构审计表`](../research/20261116_push2ex_yesterday_pool_container_audit.csv)记录路径和摘要供本地复核。此裁决可在无 raw 文件的干净检出中由采集目录、适配器和测试复核。

## 结论和范围

将精确身份 `东财-push2ex::yesterday_limit_pool` 标记为 `disproved` / `collector_output_container`，使其退出未知字段破解队列并保留可审计记录。它是采集器的列表容器，不是上游单一业务字段。池中每条记录的键（包括 `y_first_seal`、`y_limit_count`）仍按各自完整来源路径维护；本裁决不确认这些叶字段的语义、来源实际日期或跨日对应关系，也不改变采集行为。

注册表写回前该精确身份在 `source_fields` 和聚合视图中均缺失，但仍属于只读字段来源基线。因此本次增加带证据的逐源记录，以保持历史 parity；`collector_output_container` 不会把它从原生 parity 基线中删除。
