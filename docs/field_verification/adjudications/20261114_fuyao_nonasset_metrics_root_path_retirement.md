# Fuyao 偿债、营运与现金流指标无分组根路径退役（2026-11-14）

## 决定

退役下列 13 个历史无分组叶名身份，将其与当前官方分组路径区分：

| 旧路径身份 | 当前完整路径 |
|---|---|
| `同花顺-fuyao::current_ratio` | `同花顺-fuyao::solvency.current_ratio` |
| `同花顺-fuyao::quick_ratio` | `同花顺-fuyao::solvency.quick_ratio` |
| `同花顺-fuyao::cash_ratio` | `同花顺-fuyao::solvency.cash_ratio` |
| `同花顺-fuyao::earned_interest_multiple` | `同花顺-fuyao::solvency.earned_interest_multiple` |
| `同花顺-fuyao::long_term_debt_equity_ratio` | `同花顺-fuyao::operation.long_term_debt_equity_ratio` |
| `同花顺-fuyao::total_assets_turnover_ratio` | `同花顺-fuyao::operation.total_assets_turnover_ratio` |
| `同花顺-fuyao::inventory_turnover_ratio` | `同花顺-fuyao::operation.inventory_turnover_ratio` |
| `同花顺-fuyao::current_assets_turnover_ratio` | `同花顺-fuyao::operation.current_assets_turnover_ratio` |
| `同花顺-fuyao::receive_account_turnover_ratio` | `同花顺-fuyao::operation.receive_account_turnover_ratio` |
| `同花顺-fuyao::cash_operating_index` | `同花顺-fuyao::cash-flow.cash_operating_index` |
| `同花顺-fuyao::operating_cash_flow_net_divide_income` | `同花顺-fuyao::cash-flow.operating_cash_flow_net_divide_income` |
| `同花顺-fuyao::net_profit_cash_content` | `同花顺-fuyao::cash-flow.net_profit_cash_content` |
| `同花顺-fuyao::cash_meet_invest_ratio` | `同花顺-fuyao::cash-flow.cash_meet_invest_ratio` |

退役只表示 `fin_indicators.<leaf>` 不是当前独立根路径；不否定任一分组指标，不合并字段，也不推断空值所代表的业务状态。

## 证据边界

- 官方接口按 `ability` 分组，项目解析器按 `out[ability][index_id]` 保存，采集器把结果放入 `fin_indicators`。
- 保留起点 `20261015` 之后的 18 个含 Fuyao raw 目录共 360 条股票记录中，每个旧无分组路径出现 0 次；对应嵌套路径在 340 条有报告期字段的记录中出现。首日 20 条没有所选报告期字段，已排除数值观察。
- 逐条记录及 `null` 状态见 [`20261114_fuyao_nonasset_metrics_path_inventory.csv`](../research/20261114_fuyao_nonasset_metrics_path_inventory.csv)。无分组身份的退役与完整路径的官方契约裁决分开登记，后者见 [`20261114_fuyao_nonasset_metrics_source_contract_evidence.md`](20261114_fuyao_nonasset_metrics_source_contract_evidence.md) 和 [`20261114_fuyao_nonasset_metrics_source_contract.json`](20261114_fuyao_nonasset_metrics_source_contract.json)。

本次没有读取 `20261015` 之前的样本，没有把重复采集日算作独立报告期，也没有创建跨源映射。
