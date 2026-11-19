# Eastmoney `RPT_BOND_CB_LIST` `BOND_EXPIRE` 来源内定案

复核日期：2026-11-20。精确字段身份：`东财-event_dc(可转债列表)::convertible_bonds[].BOND_EXPIRE`。

## 项目路径与留存样本

- `stock_common/sc_datasource/_convertible.py` 的 `convertible_bonds()` 请求 Eastmoney Data Center `RPT_BOND_CB_LIST` 并保留返回行原始键；`scripts/capture_context_collectors.py` 将该列表写入 `raw_event_dc.json` 的 `convertible_bonds[]`。因此完整路径为 `convertible_bonds[].BOND_EXPIRE`，不把相邻的 `EXPIRE_DATE` 日期字段混为一谈。
- 使用保留样本 `docs/field_verification/20261119/raw_event_dc.json`：500/500 行的 `BOND_EXPIRE` 非空，`VALUE_DATE` 和 `EXPIRE_DATE` 均有值。文件 SHA-256：`736515264e120d739ba4d85f77a11513b98ab08218b5dc170d1d748e6729ce93`。
- 对 500 行比较 `BOND_EXPIRE × 365` 与 `EXPIRE_DATE - VALUE_DATE` 的日数差：499/500 行差值不超过 3 日，500/500 行不超过 7 日。这支持字段表示年化债券期限的量纲与范围；不能据此断言统一的日数基准或结束日算法。

## 官方释义与提前终止边界

- 东方财富官方蓝思转债详情页在“债券信息”中明确列出“债券期限(年)”，并显示期限 `2.1671`、起息日 `2017-12-08`、转股结束日 `2020-02-07`、到期日 `2020-02-10`：[蓝思转债详情页](https://data.eastmoney.com/kzz/detail/123003.html)。项目同日留存原始行 `SECURITY_CODE=123003` 的 `BOND_EXPIRE` 也是 `2.1671`。
- 蓝思科技正式募集说明书规定原发行期限为六年，即 `2017-12-08` 至 `2023-12-08`：[巨潮资讯募集说明书](https://static.cninfo.com.cn/finalpage/2017-12-06/1204195752.PDF)。东方财富详情页记录的 `2.1671` 明显不是募集说明书的原始约定期限；它与提前赎回后的生命周期相符。该样本的 `2.1671` 恰为 `2017-12-08` 至 `2020-02-07` 的 791 日除以 365，但不得把这一单例推广为全源精确公式。
- 因此，将该字段定案为东方财富展示的**可转债存续期限（年）**：债券提前终止/赎回后，值可短于募集说明书原始期限；它不是剩余期限，也不是到期日期。项目样本支持其与起息日至有效终止期间相近，但 Eastmoney 未公开统一的年化和终止日取值规则，该公式边界继续留白。
- 该字段属于债券生命周期属性；`raw_event_dc.json` 的采集日期只是快照日期，不是债券期限的业务日期。此裁决只确认该精确来源路径，不建立跨来源映射。

## 可复核定位

- 原始文件：`docs/field_verification/20261119/raw_event_dc.json`，记录 `convertible_bonds[]` 中 `SECURITY_CODE=123003`。
- 原始值：`BOND_EXPIRE=2.1671`；同期同一行 `VALUE_DATE=2017-12-08`、`TRANSFER_END_DATE=2020-02-07`、`EXPIRE_DATE=2020-02-10`。
- 官方页面标签和值：东方财富“债券期限(年)”=`2.1671`。
- 原始合同期限：蓝思科技募集说明书“债券期限”=`6年`。
