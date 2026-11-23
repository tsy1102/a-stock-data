# Ulist239 `f63` 与 Fuyao 官方竞价字段审计

## 审计范围

本轮只审查候选 `ulist239.f63 ↔ fuyao.auction_final.auction_amount` 是否为同值字段或固定单位换算关系，不据此解释 `f63` 的整体语义。候选 ID 为 `cc1_5a40db878242eb4c88ef7b2a6339d47ad6336c883392690c4e348a39db2d5af6`，来自完整碰撞报告 [`20261123_collision_report.json`](../collision_research_20261123/exploratory/20261123/fuyao_contract_fields/20261123_collision_report.json)，SHA-256 `0105ea0ca7e0674530a6e43da611e48d8eb7f61ca770a00a03928dac2fcefc9a`。

没有运行采集器，也没有新增或补写原始样本。日期资格沿用 [Fuyao 批次日期见证](20261123_fuyao_auction_batch_date_witness.md)：19 个完整终态批次、380 条记录均由已确认日期的新浪开盘价锚唯一定位；该见证只对哈希匹配的 `auction_final` 子树生效。本次仅有 9 个见证批次与 Ulist 留存日重叠。Ulist 行用已验证的 `f297`，缺失时用同记录 `f124` 北京时间日期；只有它等于目录数据日才纳入。最终配对为 9 个交易日、20 只股票、180 行，`auction_amount` 有值 177 行、缺值 3 行。

逐行数据、来源原件与摘要见 [CSV](20261123_ulist239_f63_fuyao_auction_contract_audit.csv)（SHA-256 `250c8b1cec7003efd10f4b39e167fdae7e216e1797afb77a1bebe7d5e32732a6`）和 [审计 JSON](20261123_ulist239_f63_fuyao_auction_contract_audit.json)（SHA-256 `22ef530a3c15db72c7a19e8a5abf7df7290bfbe7b69a2999dc2f34bc0f5f57b9`）。

## 官方来源核查

2026-11-23 11:48:32（北京时间）读取[同花顺金融数据 API 集合竞价文档](https://fuyao.aicubes.cn/docs/api-reference/auction/)，页面 HTTP 200，SHA-256 `a510d83a3ff5f7702fb50737fb52f530866c571cf6dc7c5c2d66b9f1c52519ca`。文档将 `auction_amount` 标为“竞价成交额”、`auction_volume` 标为“竞价成交量”、`open_price` 标为“开盘价”，但字段表没有明确金额或数量单位。文档示例 `12600 × 1421.0 = 17904600`，在示例中符合 `auction_amount = auction_volume × open_price`。

同一时刻读取东方财富官方行情中心静态资源 [`index.js`](https://quote.eastmoney.com/center/static/build/index.js)（HTTP 200，SHA-256 `1224df21d3aa5cef8659acd9293b1f44047e0398080e6bce72fe881d755dc59b`）和 [`miniquotechart2023.js`](https://quote.eastmoney.com/center/static/libs/miniquotechart2023.js)（HTTP 200，SHA-256 `c878caf11f90c0d049fb91246d7411d230df3ff66bc2dc16b0ef6ea8956abf78`）。`index.js` 中 Ulist helper 请求 `api/qt/ulist.np/get`，字段列表由调用方动态传入并序列化；资源没有提供可将该接口完整路径 `f63` 对应到特定官方指标的表。该文件出现的两个字面量 `f63` 分别位于 `kamt/get` 与 `stock/fflow/kline/get` 请求；另一资源中的字面量位于 `stock/kline/get` 请求。它们的接口路径都不是 `ulist.np/get`，所以不能移用其字段语义。此次检查未能从东方财富公开材料取得 Ulist `f63` 的精确接口定义。

## 日期合格样本结果

| 对照项 | 配对数 | 原值完全相等 | 差值不超过 1 | Pearson（仅诊断） |
| --- | ---: | ---: | ---: | ---: |
| `f63` / `auction_amount` | 177 | 0 | 2 | 0.8950 |
| `f63` / `auction_volume` | 179 | 0 | 0 | 0.4173 |
| `f63` / `auction_unmatched` | 177 | 0 | 0 | -0.3075 |
| `f63` / `auction_turnover_pct` | 179 | 0 | 0 | 0.3675 |
| `f63` / `auction_yesterday_ratio_pct` | 179 | 0 | 0 | 0.3484 |
| `f63` / `auction_volume_ratio` | 180 | 0 | 0 | -0.0384 |
| `f63` / `auction_price` | 177 | 0 | 0 | 0.7353 |
| `f63` / `auction_pct` | 177 | 0 | 0 | -0.0832 |
| `f63` / `last_price` | 180 | 0 | 0 | 0.7383 |
| `f63` / `pre_close_price` | 180 | 0 | 0 | 0.7335 |
| `f63` / `float_market_cap` | 180 | 0 | 0 | 0.5655 |

对 `auction_amount` 的中位原值比率为 2.79745，范围 0.99993–30.92683；按中位数拟合一个固定倍率后，相对误差中位数仍为 31.32%、P90 为 67.34%、最大为 90.95%。各股票内比率的中位变异系数为 0.5919。这些误差不能由统一单位换算或舍入解释。Pearson 0.8950、Spearman 0.9758 和 20/20 股票方向一致只表示共同变化，不能推翻逐值及倍率反证。

另发现 Fuyao 留存原样本的金额与 `auction_volume × open_price × 100` 在 177 行中有 155 行精确到分、176 行误差不超过 1 元；但上述官方文档示例是乘数 1。由于实样本与官方示例存在数量尺度冲突，本审计不据此判定 Fuyao 原始数量单位，也不把这一矛盾用于重新解释 `f63`。

## 裁决

已将该精确候选登记为 `rejected`：排除 `f63` 与 Fuyao 官方 `auction_amount` 的直接等值或固定单位倍率关系。裁决不外推到未比较的其他竞价指标，不把相关性当作映射，不改字段注册表、主字典或 `mappings`。`ulist239.f63` 仍是含义与单位未知，后续仅在出现新的可区分假设、精确接口定义或新的合格证据时重开对应候选。
