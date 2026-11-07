# ELTDX 连板天梯字段公开资料与历史样本复核

查阅时间：2026-11-07 07:15（Asia/Shanghai）  
锁定上游版本：`electkismet/eltdx@af471f1adf38757f6aa0188968db8110eb23f6ad`  
历史碰撞报告：[`20261107_collision_report.json`](../../20261107/historical_final_review_refresh_20261107/20261107_collision_report.json)  
报告 SHA-256：`b0f574d269ac9e3857d340460114af5415d254e664404306b340ac238bef9a6e`

本记录复核五个完整字段路径：`limit_ladder.float_shares`、`limit_ladder.free_float_shares`、`limit_ladder.float_market_value`、`limit_ladder.free_float_market_value`、`limit_ladder.seal_amount`。报告含 5,649 条方法候选；本轮深入复核这五条路径，关闭或分组 18 条候选关系，不将其解释成全局候选均已人工审查。

## 公开上游资料

- [ELTDX 字段手册](https://github.com/electkismet/eltdx/blob/af471f1adf38757f6aa0188968db8110eb23f6ad/docs/FIELD_REFERENCE.md#L560-L608)将普通流通股本和自由流通股本分开定义；普通/自由流通市值分别按对应股本和当前行情价计算；`seal_amount` 是当前买一价乘买一量。
- [ELTDX 方法手册：财务基础信息](https://github.com/electkismet/eltdx/blob/af471f1adf38757f6aa0188968db8110eb23f6ad/docs/METHOD_REFERENCE.md#L871-L904)说明财务批次对应 TDX `0x0010`，`liu_tong_gu_ben_raw_float` 的原始单位为万股，`circulating_shares` 等于该原始值乘 10,000；同时列有 `updated_date`。
- [实时涨停梯队 Helper](https://github.com/electkismet/eltdx/blob/af471f1adf38757f6aa0188968db8110eb23f6ad/docs/helpers/%E8%BF%9E%E6%9D%BF%E5%A4%A9%E6%A2%AF.md#L177-L261)说明 `limit_ladder()` 是由实时行情、五档盘口、统计资源和财务快照组合的当前交易日数据；返回的 `trade_date`、`target_trade_date`、`stats_date` 和 `alignment_status` 各有不同日期含义。封板时 `seal_amount` 才能解释为封单额。
- [短线指标 Helper](https://github.com/electkismet/eltdx/blob/af471f1adf38757f6aa0188968db8110eb23f6ad/docs/helpers/%E7%9F%AD%E7%BA%BF%E6%8C%87%E6%A0%87.md#L219-L260)再次区分自由流通口径与普通流通口径，并说明统计资源可能按上一交易日对齐。

这些是上游公开源码仓库的接口与模型文档，不把它们称作交易所原始规范；字段语义由上游契约和本项目原始样本公式交叉确认。

## 本地原始路径和日期核对

实际文件结构为 `raw_eltdx.json → global_helpers.limit_ladder.rows[*]`。它不是 `stocks[code]` 下的字段。`stocks[code].shortline.*` 是另一个已登记的逐股输出路径；本轮不把两个不同完整路径合并，尽管抽中的 12 行两路数值逐值相同。

抽中的 12 行横跨 2026-10-16 至 2026-11-04 的 9 个采集/数据日期、6 只股票。12/12 行的 `target_trade_date` 与采集目录的 `meta.data_date` 一致；其中 8/12 行的 `stats_date` 早于目标交易日，并标记为 `previous_trading_day`。因此不能将统计文件日期误认为整行所有字段的行情日期。普通流通股本的财务记录还带独立 `updated_date`，这批样本覆盖 2026-08-22 至 2026-10-30。

本地保留的 ELTDX 原始采集到 2026-11-05 为止；没有 2026-11-06 的 `raw_eltdx.json`。本轮没有补采或伪造 11-06 样本。

## 历史数值复核

| 字段 | 本地逐值结果 | 结论 |
|---|---|---|
| `limit_ladder.float_shares` | 12/12 等于 `finance_batch.liu_tong_gu_ben_raw_float × 10,000`；12/12 也等于 `shortline.float_shares` | 财务快照口径的普通流通股本，单位股 |
| `limit_ladder.free_float_shares` | 上游定义为 TDX 自由流通口径；不等同于普通流通股本 | 自由流通股本，单位股 |
| `limit_ladder.float_market_value` | 12/12 等于 `quote_snapshot.last_price × float_shares` | 普通流通市值，单位元 |
| `limit_ladder.free_float_market_value` | 12/12 符合 `quote_snapshot.last_price × free_float_shares`；最大浮点表示残差约 `2.4e-7` 元 | 自由流通市值，单位元 |
| `limit_ladder.seal_amount` | 12/12 符合 `buy_levels[0].price × buy_levels[0].volume × 100`；两条只存在约 `1.9e-9` 元的二进制浮点残差，样本均为 `limit_status=sealed` | 当前买一金额；在封板状态下可解释为封单额，单位元 |

`float_shares` 与腾讯 `[72]/[76]` 的候选关系有 12 组、9 个日期、6 只股票：2/12 完全相等；最大差 56.75 股，最大相对差约 `1.57e-7`。11/12 的绝对差不超过 0.57 个 TDX 原始 float32 换算 ULP，另 1/12 为 1.36 ULP。差异很小且字段业务含义一致，但不全能由单一 float32 舍入解释，财务更新日期/来源精度也未逐条对齐。故本轮确认 ELTDX 字段语义，不把近似命中写成严格逐值跨源映射。

## 本轮候选 ID 与处置

候选审阅和理由见 [`20261107_eltdx_limit_ladder_candidate_reviews.json`](../20261107_eltdx_limit_ladder_candidate_reviews.json)。18 条关系按完整路径分组如下：

- `limit_ladder.float_shares`：Tencent `[72]` `cc1_f3c1f8cc476187a844d59eee5a33ac46232dff190030eae4e24636dc4fa6b2fd` 保留为 `needs_external_evidence`；Tencent `[76]` `cc1_c22e47da8af77f1a5595b9850a322eb5fcdeb8db1caa0a5ab1d7bb929e7d85e2` 按 `[76]`/`[72]` 已登记别名分组。`[73]` `cc1_59c18311104ddbbbe9f8dd5e53a5721ffbdb38fc9ecb4dfc6bfc9a364078bc35`、`[58]` `cc1_bb316e12b90a3fd636f3cd46ff934a98aac39a30f1ae1748721e4f0418f74972`、`[45]` `cc1_cf893281e4e1dc6e6c2bb0e60a987ec62c1bf6a350c0dd815327be5650fca0f5`、`[44]` `cc1_0517ad3e281c508dfdb6ef3ad6aea447232d550c5bc18a50808598b0e0abe6bd`、`[30]` `cc1_a76932f6ad266a00db9cc70f3bd73eaac580369bcebf68478ae80c2a89b62e16` 的具体配对均因单位/含义不同而拒绝。
- `limit_ladder.free_float_shares`：Tencent `[72]` `cc1_fbcff715f40a73949c48bd5296f825eea04de298d741602d993d470838dbc2fc` 因自由流通口径与普通流通股本不同而拒绝；`[76]` `cc1_1b2925414507665bf7296c532755b919687763e5f072df01278fdcd1f31b57c0` 分组到 `[72]`。`[58]` `cc1_2bc36509cf338f7484a869df982f5aa2545c0be2b5a0880a98e70b0e84f72ff2`、`[32]` `cc1_bdae1630e279eed1cf62bf122887b1617f9e2302b2a717011d2b27dd463b47d0` 的具体配对因单位/含义不同而拒绝。
- `limit_ladder.seal_amount`：对 Tencent `[50]` `cc1_cfecb52f87fa4221c871c397f0a4a7247685c5cff40699b3c7279cfa2014d35c`、Sina `[10]` `cc1_8c65ce8cb3fe5a125859e207eb89728ca501cb263924a4cb194fb17ee4d604bb`、Tencent `[79]` `cc1_59972dfa6d6db67161cbc845f23b3441f5f0bbc11a689b845af8692c4c7e9bbf`、`[71]` `cc1_753e613a037b7a9c15f382df8d20872988a6c6f7928e2a612cf403bdba40796b`、`[70]` `cc1_01b30b1a4da19e0290e8a1318548e4e77b395a025ee3bd393f7f18146e7013f6`、`[49]` `cc1_e291033700c7c6cefa88ee73fa0a0cdd19e69e58b8d5b7e3c5d57d8b7d918f06`、`[43]` `cc1_1a3a9b305e44cecdcb2268acaf0610f20c1306e85544f64cf3077f79d903d0fd` 的具体“数值相同”配对均拒绝：对应候选分别是委差、买一量、区间收益、量比或振幅，与人民币买一金额不是同一量纲/业务量。

拒绝只针对上表的具体候选配对，不表示右侧字段本身无效。注册表中旧的无前缀 `eltdx::float_shares` 映射不自动套用于新的 `eltdx::limit_ladder.float_shares` 完整身份。
