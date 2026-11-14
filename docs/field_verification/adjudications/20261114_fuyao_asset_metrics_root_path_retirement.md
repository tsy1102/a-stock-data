# Fuyao 总资产指标无分组根路径退役（2026-11-14）

## 决定

退役三个历史上只登记叶名、没有 ability 分组的来源路径身份：

| 旧路径身份 | 当前完整路径 |
|---|---|
| `同花顺-fuyao::total_assets_growth_ratio` | `同花顺-fuyao::growth.total_assets_growth_ratio` |
| `同花顺-fuyao::total_assets_net_ratio` | `同花顺-fuyao::profitability.total_assets_net_ratio` |
| `同花顺-fuyao::index_deduct_weighted_avg_roe` | `同花顺-fuyao::profitability.index_deduct_weighted_avg_roe` |

退役只表示 `fin_indicators.<leaf>` 不是当前独立根路径；不否定对应的分组字段、不把多个字段合并，也不改变它们的语义裁决。

## 证据

- 官方响应结构为 `data.abilities[] → ability → indicators[] → index_id/value`；官方表把这三个 ID 分别放在 `growth` 或 `profitability` 分组。
- 项目解析器按 `out[ability][index_id]` 保留分组，采集器把对象保存在 `fin_indicators`，因此完整路径是 `fin_indicators.<ability>.<index_id>`。
- 自 `20261015` 起，18 个含 Fuyao raw 的保留目录、360 条股票记录中，每个无分组路径均出现 0 次；每个完整嵌套路径在 340 条有报告期指标的记录中出现。首日 20 条记录没有该报告期指标，已明确排除其值核验。完整逐样本记录见 [`20261114_fuyao_asset_metrics_path_inventory.csv`](../research/20261114_fuyao_asset_metrics_path_inventory.csv)。
- 同一 `2026-2` 报告期的重复采集不算独立财报样本；所有文件均在 `20261015` 保留边界内。

## 配套裁决

新登记的三个完整路径按官方源契约定案，见 [`20261114_fuyao_asset_metrics_source_contract_evidence.md`](20261114_fuyao_asset_metrics_source_contract_evidence.md) 与 [`20261114_fuyao_asset_metrics_source_contract.json`](20261114_fuyao_asset_metrics_source_contract.json)。本次不新增跨源映射。
