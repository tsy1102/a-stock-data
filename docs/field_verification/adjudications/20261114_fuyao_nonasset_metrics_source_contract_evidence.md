# Fuyao 偿债、营运与现金流指标字段核验（2026-11-14）

## 裁决范围

按同花顺 Fuyao 官方财务指标接口的精确分组、`index_id` 和中文标签，核验 13 个完整来源路径：3 个偿债能力字段、5 个营运能力字段、5 个现金流字段。本次只确认来源内字段身份与官方文档明确的单位；单位未明确的字段保留空单位，不推断公式、期间年化或跨源等价关系。

## 官方契约与项目路径

[Fuyao 官方财务指标文档](https://fuyao.aicubes.cn/docs/api-reference/financial-indicators/) 定义 `GET /api/a-share/financials/indicators`。响应按 `data.abilities[]` 的 `ability` 分组，指标项以精确 `index_id` 和 `value` 表示；偿债、营运和现金流分组表逐项列出以下指标及中文标签。文档说明周转率通常按“次”、已获利息倍数按“倍”展示，百分数类依中文指标名解释；其余指标没有明确的数值量纲时，本次不补单位。仓库契约镜像见 [`docs/verify/fuyao_api_full.md`](../../verify/fuyao_api_full.md) §财务指标数据。

项目适配器 [`stock_common/sc_fuyao.py`](../../../stock_common/sc_fuyao.py) 的 `get_fuyao_fin_indicators` 按 `out[ability][index_id] = value` 保留分组；[`scripts/capture_verified_collectors.py`](../../../scripts/capture_verified_collectors.py) 把结果存入 `fin_indicators`。完整路径因此是 `fin_indicators.<ability>.<index_id>`，不是无分组叶名。

## 保留期样本与空值

- 只读取 `20261015` 起含 `raw_fuyao.json` 的 18 个目录、360 条股票记录；另有 8 个保留期目录没有 Fuyao raw 文件，不计入。未读取保留起点之前的 raw、ZHB 压缩包或解析缓存。
- 18 个 Fuyao `as_of_date` 与各自目录数据日一致。首日 20 条记录没有该报告期指标；之后 17 个来源数据日均记录 `fin_report=2026-2`，每只股票对应一条报告期数据。
- 13 个完整嵌套路径各出现 340 次；13 个 `fin_indicators.<leaf>` 无分组路径在全部 360 条记录中均为 0。逐日期、逐股票、原值及空值状态见 [`20261114_fuyao_nonasset_metrics_path_inventory.csv`](../research/20261114_fuyao_nonasset_metrics_path_inventory.csv)。重复快照只用于路径和空值分布核验，不作为独立财报样本。

## 字段清单

| 完整路径 | 官方中文名 | 单位 | 340 条已就绪路径中的值状态 |
|---|---|---|---|
| `solvency.current_ratio` | 流动比率 | 未明确，留空 | 323 个值、17 个 `null` |
| `solvency.quick_ratio` | 速动比率 | 未明确，留空 | 323 个值、17 个 `null` |
| `solvency.cash_ratio` | 现金比率 | % | 323 个值、17 个 `null` |
| `operation.long_term_debt_equity_ratio` | 长期负债权益比率 | 未明确，留空 | 340 个值 |
| `operation.total_assets_turnover_ratio` | 总资产周转率 | 次 | 340 个值 |
| `operation.inventory_turnover_ratio` | 存货周转率 | 次 | 323 个值、17 个 `null` |
| `operation.current_assets_turnover_ratio` | 流动资产周转率 | 次 | 323 个值、17 个 `null` |
| `operation.receive_account_turnover_ratio` | 应收账款周转率 | 次 | 323 个值、17 个 `null` |
| `solvency.earned_interest_multiple` | 已获利息倍数 | 倍 | 102 个值、238 个 `null` |
| `cash-flow.cash_operating_index` | 现金营运指数 | 未明确，留空 | 340 个值 |
| `cash-flow.operating_cash_flow_net_divide_income` | 销售现金比率 | % | 340 个值 |
| `cash-flow.net_profit_cash_content` | 净利润现金含量 | 未明确，留空 | 340 个值 |
| `cash-flow.cash_meet_invest_ratio` | 现金满足投资比率 | 未明确，留空 | 340 个值 |

官方响应契约说明上游缺失值会标准化为 `null`。本表仅记录项目样本中的空值分布，不把 `null` 当作零值，也不据此推断不适用范围或计算规则。

## 裁决结论

官方接口逐项定义了这 13 个 `index_id` 的分组和中文含义，项目适配器及保留 raw 保存了相同嵌套路径，因此按来源契约定案。仅将文档明确支持的单位登记为“次”“倍”或“%”；其他单位保留空白。该裁决不表示已经复算各项财务公式、不代表所有报告期均有非空值，也不建立跨源 `mappings`。
