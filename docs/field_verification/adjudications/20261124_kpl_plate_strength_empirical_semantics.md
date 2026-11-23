# 2026-11-24 开盘啦精选板块强度字段来源内核验

## 精确路径与结论

注册表来源为 `市场源(market_sources)`。本核验范围严格限定在该聚合采集器的 `kpl_plate_strength` 子接口：

| 注册路径 | 实际响应路径 | 结论 |
| --- | --- | --- |
| `strength` | `kpl_plate_strength.[*].strength` | 开盘啦精选板块强度综合数值 |
| `col_02` | `kpl_plate_strength.[*].raw_columns.col_02` | 原始数组 `row[2]`，与同记录归一化 `strength` 同值 |
| `col_03` | `kpl_plate_strength.[*].raw_columns.col_03` | 原始数组 `row[3]`，与同记录归一化 `change_pct` 同值 |
| `col_05` | `kpl_plate_strength.[*].raw_columns.col_05` | 原始数组 `row[5]`，与同记录归一化 `amount` 同值 |

字段 `strength` 的语义由开盘啦官方产品说明确认：它是用于比较板块强度的多维综合数值，涉及板块权重个股、涨停数量、人气、成交额及市场情绪。官方未公开计算公式和计量单位，故不填写单位，也不猜测分值算法。具体网页证据见[官方页面核验记录](public_web/20261124_kpl_plate_strength.md)。

## 原始响应与解析映射审计

按 `MIN_CAPTURE_DATE=2026-10-15` 读取保留样本中的 `raw_market_sources.json`，未读取边界前材料。审计涉及 21 个采集目录、420 条板块响应记录及 121 个不同板块代码。目录名仅用于定位归档批次，不当作来源实际数据日；本核验比较的是每条响应记录内同时保存的原始值和归一化值，不依赖行情日期推断。

`stock_common/sc_kpl.py::get_kpl_plate_strength` 将 `row[2]`、`row[3]`、`row[5]` 分别写入 `strength`、`change_pct`、`amount`；`capture_raw=True` 时保留对应 `raw_columns`。对全部记录用十进制定点解析后逐行比较：

| 原始列 | 归一化字段 | 比较数 | 完全相等 | 缺失 | 不一致 |
| --- | --- | ---: | ---: | ---: | ---: |
| `col_02` | `strength` | 420 | 420 | 0 | 0 |
| `col_03` | `change_pct` | 420 | 420 | 0 | 0 |
| `col_05` | `amount` | 420 | 420 | 0 | 0 |

逐行值见[审计 CSV](../research/20261124_kpl_plate_strength_columns_audit.csv)，输入文件 SHA-256 见[原始文件清单](../research/20261124_kpl_plate_strength_columns_manifest.csv)。`change_pct` 与 `amount` 的来源内释义已在注册表中确认；原始列与已确认归一化字段在同一记录内 420/420 相等，因此将释义收敛到对应原始列。金额单位沿用未声明状态，不推断元、万元或其他量级。

## 裁决范围与限制

- 注册表将 `market_sources` 作为聚合来源；本次只裁决上表中由 `kpl_plate_strength` 子接口产生的路径，不将含义推广到聚合采集器的其他接口。
- 本批不建立跨源 `mappings`，不把 KPL 与 KPH 合并，也不将板块强度解释为涨停数量、个股拉升强度或资金净额。
- 原始列与归一化字段的等值证明了解析映射，不单独证明日期、单位或其他接口语义。
- 其余 KPL 板块响应列（包括 `speed`、`pe_now`、`pe_next`、资金及市值字段）未包含在本次定案中，继续保持现有状态。
