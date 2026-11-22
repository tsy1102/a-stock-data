# 东方财富可转债 `IS_CONVERT_STOCK` 来源内实证定案

复核日期：2026-11-22。精确字段身份：`东财-event_dc(可转债列表)::convertible_bonds[].IS_CONVERT_STOCK`。

## 采集路径与官方参照

- 项目适配器 [`stock_common/sc_datasource/_convertible.py`](../../../stock_common/sc_datasource/_convertible.py) 将 `convertible_bonds` 请求映射到东方财富 Data Center `RPT_BOND_CB_LIST`；响应行写入 `raw_event_dc.json` 的 `convertible_bonds[]`。适配器 `_trace` 在请求结束后添加 `fetched_at`，它是采集观察时点，不是来源业务日期。
- 东方财富官方[可转债详情页](https://data.eastmoney.com/kzz/detail/110099.html)列出“转股开始日”和“转股结束日”。官方详情脚本 [`detail.js`](https://data.eastmoney.com/newstatic/js/kzz/detail.js) 将 `TRANSFER_START_DATE`、`TRANSFER_END_DATE` 绑定到这两个页面标签；脚本快照 SHA-256：`ca2b2b77647eabdd03121487f6540c0918212c176c42cf6bed0ce0028e4c7dcc`，抓取时间 `2026-11-22T21:18:04+08:00`（Asia/Shanghai）。官方页面和脚本提供起止日释义，但没有直接公开 `IS_CONVERT_STOCK` 的布尔字段定义；以下“当前转股状态”是逐来源保留样本的实证结论。

## 样本范围与日期处理

仅使用 2026-10-15 保留边界内已有的 `raw_event_dc.json`，没有执行采集请求。原始目录目标数据日为 2026-10-15 至 2026-11-19；21 个文件中 20 个非空批次，各 500 条，共 10,000 条观测、503 个不同债券代码。每条观测按同一响应行的 `IS_CONVERT_STOCK`、`TRANSFER_START_DATE`、`TRANSFER_END_DATE` 比较，并以该批次 `fetched_at` 作为观察时点，不以目录名替代来源实际日期。

| 对照结果 | 数量 | 处理 |
|---|---:|---|
| 有“是/否”状态且起止日有效，可比较 | 9,980 | 全部纳入 |
| 与包含边界的起止日区间按日期直接吻合 | 9,978 | 匹配 |
| 起止日边界上需结合观察时点解释 | 2 | 均符合当前状态解释 |
| 未解释反例 | 0 | 无 |
| 排除 | 20 | 全部为 `115003 中兴债1`，同批记录缺少状态与起止日 |

仅按日期判断的两条边界记录如下。`113702` 在转股开始日 08:01 观察为“否”，次一条保留快照转为“是”；`113046` 在转股结束日 20:07（收盘后）观察为“否”。这两条说明不能仅凭目录日期裁决边界状态，必须结合实际采集观察时点；不据此声称接口精确到某个盘中切换时刻。

| 债券 | 观察时点（上海） | 转股区间 | 状态 | 边界情形 |
|---|---|---|---|---|
| 113702 斯达转债 | `2026-10-22T08:01:10+08:00` | 2026-10-22 至 2032-04-15 | 否 | transfer_start_date_preopen |
| 113046 金田转债 | `2026-10-23T20:07:06+08:00` | 2021-09-27 至 2026-10-23 | 否 | transfer_end_date_after_close |

五个有连续状态变化的债券均在样本观察跨过其转股起止边界时变更状态：

| 债券 | 状态变化 | 观察时点（上海） | 转股区间 |
|---|---|---|---|
| 113605 大参转债 | 是 → 否 | 2026-10-22T08:01:10+08:00 | 2021-04-28 至 2026-10-21 |
| 113046 金田转债 | 是 → 否 | 2026-10-23T20:07:06+08:00 | 2021-09-27 至 2026-10-23 |
| 113702 斯达转债 | 否 → 是 | 2026-10-23T20:07:06+08:00 | 2026-10-22 至 2032-04-15 |
| 110076 华海转债 | 是 → 否 | 2026-10-31T09:45:40+08:00 | 2021-05-06 至 2026-10-30 |
| 110077 洪城转债 | 是 → 否 | 2026-11-20T06:59:11+08:00 | 2021-05-26 至 2026-11-19 |

## 定案

规范名：`convertible_bond_conversion_status`。含义：东方财富可转债记录中的当前转股状态标记，原始值为“是/否”。在保留样本中，该状态与同一响应记录的转股开始日、转股结束日及采集观察时点相符；它表示当前是否处于可转股期间，不是债券是否具有转股条款的静态属性。具体盘中切换时刻和接口刷新规则未公开。 单位留空，因为这是“是/否”枚举状态，不是数量型物理量。该结论针对精确路径 `convertible_bonds[].IS_CONVERT_STOCK`，不建立跨源映射，也不推广到其他来源或其他接口。

依据是保留期 9,980 条同记录、日期合格样本全部得到解释（9,978 条日期窗口直接吻合，2 条边界记录由采集时点解释），且 5 个观察到的状态转变均与转股期间边界相符。缺失状态的 20 条都来自同一只无起止日记录，已排除而非作为命中。

## 可复核材料

- 逐条审计：[CSV](../research/20261122_eventdc_is_convert_stock_audit.csv)，SHA-256 `f6c889b82f5e1ff94079164c06c8aafa0fd846da098e75e224b67be5108726ec`。
- 审计清单：[JSON](../research/20261122_eventdc_is_convert_stock_audit.json)，记录比较口径、状态转变、排除项、官方参照及下列 raw 文件摘要。

| 目录数据日 | 记录数 | 原始文件 | SHA-256 |
|---|---:|---|---|
| `20261015` | 0 | `docs/field_verification/20261015/raw_event_dc.json` | `4a1b99df272af4f2dc4afaab67bd16fa0056920623246982c7cc7b436000172a` |
| `20261016` | 500 | `docs/field_verification/20261016/raw_event_dc.json` | `f60429030f24e2385887fb9abc5c456274fffc054cad26f250663ee8efa13971` |
| `20261020` | 500 | `docs/field_verification/20261020/raw_event_dc.json` | `ec54f6d668b3a8d251fd77ab56ee7780cde511d511e12aa14fd68d2f7d08a2b8` |
| `20261021` | 500 | `docs/field_verification/20261021/raw_event_dc.json` | `b1ad47c71aa1c267f716f55a8650eee7b69b0b92245576cbacbed49867216a18` |
| `20261023` | 500 | `docs/field_verification/20261023/raw_event_dc.json` | `5aa490e76cc9231cfc4813f1abc6ccd1338e6456755c95cf09f35e46764a015d` |
| `20261026` | 500 | `docs/field_verification/20261026/raw_event_dc.json` | `a5bdbabd6bf2ed61c3ae24f99eeee00a20693a3a355eeb5997821c49eae06a59` |
| `20261028` | 500 | `docs/field_verification/20261028/raw_event_dc.json` | `fb69ba930115fab1882bd1abc2bc3c72f4edc6ec78a45d4af90ff57bbe7b1194` |
| `20261029` | 500 | `docs/field_verification/20261029/raw_event_dc.json` | `d70ed4c2d75786015f43105475badb6cf02f6d0495650e678bdadf2c6477a674` |
| `20261030` | 500 | `docs/field_verification/20261030/raw_event_dc.json` | `24d47a03f90c2b6b58c7bae3da9c3e686105c22fc2e59ba3708091e14defedf7` |
| `20261102` | 500 | `docs/field_verification/20261102/raw_event_dc.json` | `533fedb0a3c313d5cfc4d51d19b52f3afdfa41377730ba17830ebd0f876a301b` |
| `20261103` | 500 | `docs/field_verification/20261103/raw_event_dc.json` | `3897b1c5261412fa7cab259b70a20af81ddd731c33b9cfd961026b0744c1474d` |
| `20261104` | 500 | `docs/field_verification/20261104/raw_event_dc.json` | `13147056ddc14520e8592f5c76d3602b0c5479b50915ccedbfe54436d6cba239` |
| `20261105` | 500 | `docs/field_verification/20261105/raw_event_dc.json` | `1ab381045a17d835600b33964cabd8ec060009f444ff0f499519da3f4bacee15` |
| `20261106` | 500 | `docs/field_verification/20261106/raw_event_dc.json` | `f2876121066b57e3845cc4e0c58e618d16fa3d16a0ecab1ee2b343a17088b2aa` |
| `20261109` | 500 | `docs/field_verification/20261109/raw_event_dc.json` | `8719156ec3e2b4a583ca5f698b7232baaf6dad02f4e9cec3be2bc37102e08e1d` |
| `20261110` | 500 | `docs/field_verification/20261110/raw_event_dc.json` | `4fc8e0208f5a632f1502223e5604f5b75a859805cc09eb171248f84667c2aa96` |
| `20261112` | 500 | `docs/field_verification/20261112/raw_event_dc.json` | `62601f6539553944ac1cdadd7c6de7741615560c2c9197691259ac2dcfec1565` |
| `20261116` | 500 | `docs/field_verification/20261116/raw_event_dc.json` | `a5cd24596c82044172bca57ef4d2fb6b145e7afd7dda862df9b591f4dbbbdc37` |
| `20261117` | 500 | `docs/field_verification/20261117/raw_event_dc.json` | `a90631853d5a3f93f08c2af59f70fb9965c1e33ce237fd34782812287a035de2` |
| `20261118` | 500 | `docs/field_verification/20261118/raw_event_dc.json` | `121aa5ef015340a4465679ecd593ca4be70149fbf571173bbd27d17cb3c58ab5` |
| `20261119` | 500 | `docs/field_verification/20261119/raw_event_dc.json` | `41fe019b29d038e1cf4726f69700af303aae0206a6fdb8d7399912290065b091` |
