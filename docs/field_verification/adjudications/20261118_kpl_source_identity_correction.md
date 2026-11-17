# KPL 字段来源身份更正（2026-11-18）

## 裁决结论

2026-11-18 的三项 KPL 语义裁决使用了 `DailyLimitPerformance` 证据，但注册到了 `开盘啦(kpl)::amplitude`、`开盘啦(kpl)::main_buy`、`开盘啦(kpl)::main_sell`。这不是证据本身失效，而是精确来源身份写错：[`source_lineage.json`](../source_lineage.json) 将 `开盘啦(kpl)` 关联到运行时别名 `market_sources`；实际证据来自别名 `kpl` 的独立采集器 `get_kpl_limit_up_detail()`，落在 `raw_kpl.json`，其精确注册来源为 `开盘啦(kpl_limit_up_detail)`。

因此，旧身份的状态恢复到本次裁决前的 `unverified / aggregate_status_scope_unresolved`。这表示现有证据不能解释这三个旧路径，不表示其字段语义已被证伪。旧裁决文件和原始样本保持不变，作为审计历史保留；本记录明确撤回它们对旧身份的证明效力，并将相同语义证据登记到正确身份。

旧身份此前留下的 `field_matrix` 映射也随裁决撤回：`amplitude`、`main_buy`、`main_sell` 的验证覆盖投影现归属于 `开盘啦(kpl_limit_up_detail)`；旧 `开盘啦(kpl)` 身份继续留在待核队列，不在已核实矩阵中占一个来源标签。

| 旧身份（恢复待核） | 曾误用的裁决 | 更正后证据身份 |
|---|---|---|
| `开盘啦(kpl)::amplitude` | `20261118-kpl-daily-limit-amplitude` | `开盘啦(kpl_limit_up_detail)::amplitude`、`开盘啦(kpl_limit_up_detail)::raw_columns.col_17` |
| `开盘啦(kpl)::main_buy` | `20261118-kpl-daily-limit-main-buy` | `开盘啦(kpl_limit_up_detail)::main_buy`、`开盘啦(kpl_limit_up_detail)::raw_columns.col_09` |
| `开盘啦(kpl)::main_sell` | `20261118-kpl-daily-limit-main-sell` | `开盘啦(kpl_limit_up_detail)::main_sell`、`开盘啦(kpl_limit_up_detail)::raw_columns.col_10` |

## 来源路径核对

- `source_lineage.json` 中 `开盘啦(kpl)` 的运行时别名是 `market_sources`，来源容器和字段路径未确认。它保存的 KPL 板块强度数据路径是 `kpl_plate_strength.[].main_buy` / `main_sell`，由 [`stock_common.get_kpl_plate_strength()`](../../../stock_common/sc_kpl.py) 请求 `RealRankingInfo`；这是板块级接口，不能用来证明 `DailyLimitPerformance` 个股行。
- `source_lineage.json` 中 `开盘啦(kpl_limit_up_detail)` 的运行时别名是 `kpl`。采集元数据 [`20261117/meta.json`](../20261117/meta.json) 将 `kpl` 标为 `kpl.limit_up_detail`，并把文件指向 [`20261117/raw_kpl.json`](../20261117/raw_kpl.json)。[`get_kpl_limit_up_detail()`](../../../stock_common/sc_kpl.py) 请求 `a=DailyLimitPerformance`，将 `row[9]`、`row[10]`、`row[17]` 分别写入 `main_buy`、`main_sell`、`amplitude`，并在 `capture_raw=True` 时保存为 `raw_columns.col_09`、`col_10`、`col_17`。
- 两组接口同属开盘啦产品，不等于同一个来源字段路径。此次没有建立跨接口或跨源 `mappings`。

## 语义证据及其适用范围

### `main_buy` 与 `main_sell`

原主力买卖审计记录了开盘啦官网产品页的“主力买入”“主力卖出”标签、项目对 `DailyLimitPerformance` 的精确数组映射，以及 2026-10-15 至 2026-11-17 的 20 个来源交易日样本。1,195 条个股记录中，1,165 条留有原始列；原始位置与归一字段逐值一致（两字段各 1,165/1,165），全部 1,195 条均满足 `main_inflow = main_buy + main_sell`，且买入非负、卖出非正。第三方逆向材料只用于定位数组项，不当作官方接口合同。含样本全集、排除项和 SHA-256 的审计表见 [`20261118_kpl_money_field_sample_audit.csv`](../research/20261118_kpl_money_field_sample_audit.csv)；原语义研究见 [`20261118_kpl_main_buy_sell_empirical_semantics.md`](20261118_kpl_main_buy_sell_empirical_semantics.md)。

### `amplitude`

原振幅审计记录了日振幅公开公式、`DailyLimitPerformance row[17]` 到 `raw_columns.col_17` 的映射，以及同股票、同来源交易日的东财日 K 核对。1,195 条 KPL 记录中有 1,165 条保留原列，原始值与归一值 1,165/1,165 相同；其中 13 组有效东财日 K 对照覆盖 11 个交易日、6 只股票，KPL 值、东财 `f58` 与公式结果均一致，无反例。其余无对应日 K 的记录不计作命中或反例。完整逐行证据见 [`20261118_kpl_amplitude_sample_audit.csv`](../research/20261118_kpl_amplitude_sample_audit.csv)；原语义研究见 [`20261118_kpl_amplitude_empirical_semantics.md`](20261118_kpl_amplitude_empirical_semantics.md)。

这些证据只验证 `开盘啦(kpl_limit_up_detail)` 的对应字段。它们不证明 `market_sources` 下同名的板块级路径等价，也不确定 KPL 的资金分类阈值、振幅服务端计算细节或未观测路径。

## 盘前采集与碰撞边界

2026-11-18 约 03:02（北京时间）运行了默认字段采集入口。目标数据日为 2026-11-17；完整收盘采集已存在，入口按同日幂等规则跳过原始源重请求，只刷新日验证摘要。08:00 前 ZHB 按运行规约跳过；现有 ZHB 样本 `as_of_date=2026-11-16`，不作为 11 月 17 日的新来源日证据。此次碰撞使用保留期内已存在的 11 月 17 日完整样本，不把盘前运行时间伪装成新样本。

更正后的来源内 E3 决策见 [`20261118_kpl_detail_source_semantics.json`](20261118_kpl_detail_source_semantics.json)。按更正后的 registry 重新生成的报告见 [`20261118_collision_report.md`](../20261118/preopen_0302_identity_corrected/20261118_collision_report.md) 和 [`20261118_collision_report.json`](../20261118/preopen_0302_identity_corrected/20261118_collision_report.json)。
