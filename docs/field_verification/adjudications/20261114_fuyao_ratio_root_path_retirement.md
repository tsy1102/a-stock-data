# Fuyao 财务比率裸根路径身份退役（2026-11-14）

## 决定

将以下四个无分组裸叶身份标记为 `disproved` / `retired_legacy_path`，并把 `canonical` 指向其当前完整嵌套路径：

| 旧身份 | 当前完整身份 |
|---|---|
| `同花顺-fuyao::index_weighted_avg_roe` | `同花顺-fuyao::profitability.index_weighted_avg_roe` |
| `同花顺-fuyao::sale_gross_margin` | `同花顺-fuyao::profitability.sale_gross_margin` |
| `同花顺-fuyao::sale_net_interest_ratio` | `同花顺-fuyao::profitability.sale_net_interest_ratio` |
| `同花顺-fuyao::assets_debt_ratio` | `同花顺-fuyao::solvency.assets_debt_ratio` |

这里的退役仅表示裸叶不是当前独立根级来源字段，不代表嵌套路径不存在或含义被证伪。

## 路径证据

- 官方接口文档的响应结构是 `data.abilities[] → ability → indicators[] → index_id/value`，指标名按 `profitability` 或 `solvency` 分组。
- `stock_common/sc_fuyao.py::get_fuyao_fin_indicators` 直接执行 `out[ability][index_id] = value`，`scripts/capture_verified_collectors.py` 将对象放入 `fin_indicators`，不会把 ID 提升到根级。
- 保留起点 `20261015` 之后 18 个目录、360 条股票记录中，四个裸根路径各出现 0 次；四个完整嵌套键各在 340 条已就绪报告期记录中出现。首日 20 条未形成该报告期指标，不用来推断指标值。逐样本记录见 [`20261114_fuyao_ratio_path_inventory.csv`](../research/20261114_fuyao_ratio_path_inventory.csv)。
- 所有路径均不读取 `20261015` 之前的 raw、ZHB 压缩包或解析缓存。

## 不产生的结论

不创建跨来源 `mappings`；不把 17 个重复报告期采集算作 17 个独立财报样本；不把该退役扩展到未来版本或其他 Fuyao 接口。精确嵌套路径的语义裁决单独见 [`20261114_fuyao_ratio_source_contract_evidence.md`](20261114_fuyao_ratio_source_contract_evidence.md)。
