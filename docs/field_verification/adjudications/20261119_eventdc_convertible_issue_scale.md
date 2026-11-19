# Eastmoney `RPT_BOND_CB_LIST` `ACTUAL_ISSUE_SCALE` 来源内定案

复核日期：2026-11-19。精确字段身份：`东财-event_dc(可转债列表)::convertible_bonds[].ACTUAL_ISSUE_SCALE`。

## 项目路径与样本

- `stock_common/sc_datasource/_convertible.py` 将 `convertible_bonds` 明确请求到 Eastmoney Data Center 的 `RPT_BOND_CB_LIST`，响应行原样保留 `ACTUAL_ISSUE_SCALE`；`scripts/capture_context_collectors.py` 将列表写入 `raw_event_dc.json` 的 `convertible_bonds` 数组。逐行完整路径为 `convertible_bonds[].ACTUAL_ISSUE_SCALE`。
- 使用保留目录 `docs/field_verification/20261119/raw_event_dc.json`，采集运行时间为 `2026-11-19 19:52:11`，目录数据日为 `20261119`。响应含 500 条可转债记录，`ACTUAL_ISSUE_SCALE` 500/500 非空且为数值。接口未提供逐债券的来源数据日期；本字段表示历史发行时形成的静态发行属性，不把采集运行日当成发行日或字段的来源日期。
- 抽核两只具有发行人正式年报佐证的可转债：

| 债券 | 归档原始值 | 发行人正式披露 | 统一单位后 | 结果 |
|---|---:|---:|---:|---|
| 新钢转债 `110003` | 27.6 | 发行总额 276,000 万元 | 27.6 亿元 | 精确吻合 |
| 厦工转债 `110004` | 6 | 发行 60,000 万元 | 6 亿元 | 精确吻合 |

抽核没有差异或反例；发行人报告明确记载的是可转债发行总额。该外部抽核样本为 2 条，并不声称已逐只复算全部 500 家发行人文件。

## 公开定义与结论

- 东方财富可转债列表的官方页面将该列标为“发行规模（亿元）”；可转债详情页另列“债券发行总额(亿)”及“实际募集资金总额(亿元)”。这里登记发行规模/发行总额口径，不把它误写为当前剩余规模，也不与可能扣除费用后的净募集资金混为一项。
- 新钢股份 2011 年年报记载新钢转债发行总额 276,000 万元：[巨潮资讯 PDF](https://static.cninfo.com.cn/finalpage/2012-04-10/60805813.PDF)。厦工股份 2011 年年报记载厦工转债发行 60,000 万元：[巨潮资讯 PDF](https://static.cninfo.com.cn/finalpage/2012-03-06/60629354.PDF)。东方财富官方列表和详情页：[可转债列表](https://data.eastmoney.com/xg/xg/?mkt=kzz)、[新钢转债详情](https://data.eastmoney.com/kzz/detail/110003.html)。
- 因此定案含义为**可转债初始发行规模（债券发行总额，亿元）**。这仅确认该精确来源路径的语义，不建立跨源 `mappings`。历史项目碰撞路径曾丢失 `convertible_bonds[]` 集合段，已在 v8 报告中修正并保留完整字段身份。

## 可复核样本定位

- 原始归档：`docs/field_verification/20261119/raw_event_dc.json`，SHA-256 `736515264e120d739ba4d85f77a11513b98ab08218b5dc170d1d748e6729ce93`。
- 新钢转债行：`SECURITY_CODE=110003`、`ACTUAL_ISSUE_SCALE=27.6`；厦工转债行：`SECURITY_CODE=110004`、`ACTUAL_ISSUE_SCALE=6`。
- 发行人报告分别列明：新钢转债代码 110003、发行总额 276,000 万元；厦工转债代码 110004、发行 60,000 万元、面值 100 元/张。
