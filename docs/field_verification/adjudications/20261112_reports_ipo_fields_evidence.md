# 东方财富研报 IPO 基础字段来源内 E3 定案证据（2026-11-12）

## 定案范围

本记录分别裁定三个精确字段身份：`reports::newIssuePrice`、`reports::newListingDate`、`reports::newPeIssueA`。结论仅描述东方财富研报列表 `report/list` 当前原样返回字段的来源内含义，不建立与其他数据源的 `mappings`，也不主张 Eastmoney F10 与 reportapi 是独立提供方。

## 项目采集路径与身份

`stock_common/sc_datasource/_financials.py::get_reports()` 请求东方财富 `https://reportapi.eastmoney.com/report/list`，`qType=0`，将响应 `data` 项直接追加并返回；该函数未改名、重算或格式化这三个字段。`scripts/capture_context_collectors.py::collect_reports()` 调用 `get_reports(c, max_pages=1)` 并把返回记录写入 `raw_reports.json`。因此本次核对的是 reportapi 原始记录中完整路径 `newIssuePrice`、`newListingDate`、`newPeIssueA`，不是从报告模板生成的派生值。

## 东方财富公开页面与 F10 字段释义

东方财富新股详情页[农业银行（601288）](https://data.eastmoney.com/xg/xg/detail/601288.html)在同一股票记录中展示“发行价格(元/股)”“上市日期”“发行市盈率”，其页面对象分别使用 `ISSUE_PRICE=2.68`、`LISTING_DATE=2010-07-15`、`AFTER_ISSUE_PE=9.45`。同一股票的 reportapi 样本 `newIssuePrice=2.68`、`newListingDate=2010-07-15`、`newPeIssueA=9.45`，三项逐值一致。

进一步对 15 只留存样本股票逐一查询东方财富 F10 `CompanySurvey/PageAjax` 的 `fxxg` 发行信息行；响应字段分别为 `ISSUE_PRICE`、`LISTING_DATE`、`AFTER_ISSUE_PE`。每个请求的可复核 URL、reportapi 值、F10 值和逐项比较结果列在[样本对照 CSV](20261112_reports_ipo_fields_samples.csv)。所有 15 个请求均返回 HTTP 200。该核验是同一提供方内两个公开页面/接口之间的语义和数值核对，不用于声称来源独立性。

## 留存样本与去重方法

按项目样本保留边界，只读取 `20261015` 至 `20261110` 共 16 份日期化 `raw_reports.json`；没有读取保留起点以前的 raw、ZHB 压缩包或解析缓存。原始观察 6,051 条，按 `infoCode` 去重后为 443 份唯一研报，覆盖 15 只股票。每个唯一 `infoCode` 的三个字段在跨采集快照中均未漂移；每只股票的非空 IPO 值也各只有一个唯一值。重复采集与重复研报均未被计作独立股票样本。

- 样本对照 CSV SHA-256：85603dccdd90f3a1f5a221d41e70b0abad035896b4742039d4477e7d93f111f5
- 16 个保留 raw 文件及 SHA-256 清单：[raw manifest](20261112_reports_ipo_fields_raw_manifest.csv)，SHA-256：ed7610f1816bded329a58f6dcc99d00ec4f2360146a7dc760f1f4cd0eed682f4
- 比较样本单位为唯一股票；采集目录日期只是留存快照定位。IPO 发行价、上市日期和发行市盈率属于历史发行事实，不将采集自然日、交易日或报告发布日期当成这些字段的 as-of 日期。

## 全量逐股比较

| 精确来源路径 | 有值的股票比较数 | 一致 | 反例 | 排除/缺失 | 对应 F10 含义 |
|---|---:|---:|---:|---|---|
| `reports::newIssuePrice` | 15 | 15 | 0 | 无 | `ISSUE_PRICE`，发行价格，元/股 |
| `reports::newListingDate` | 14 | 14 | 0 | `920508` 的 reportapi 字段为空；F10 有 `2020-07-27`。这是 reportapi 缺值，不是语义反例 | `LISTING_DATE`，上市日期 |
| `reports::newPeIssueA` | 13 | 13 | 0 | `000568`、`688327` 两边均为空，排除空值比较 | `AFTER_ISSUE_PE`，发行市盈率，倍 |

发行价格按 0.005 元/股绝对容差比较，发行市盈率按 0.01 倍绝对容差比较；15 只股票的数值均逐字相同，无需使用舍入容差。日期按 `YYYY-MM-DD` 归一化后精确比较。所有可比非空值均吻合，没有反例。留存 CSV 中的唯一研报数用于覆盖说明，裁决的独立横向比较数按股票计，不把同股多篇研报或重复快照夸大为独立样本。

## 结论与边界

- `newIssuePrice` 定义为该股票首次公开发行价格，单位元/股。
- `newListingDate` 定义为该股票上市交易日期，格式 `YYYY-MM-DD`；空值表示本条 reportapi 记录未返回日期，不表示股票没有上市日期。
- `newPeIssueA` 定义为该股票首次公开发行时的发行市盈率，对应 Eastmoney F10 `AFTER_ISSUE_PE`，单位倍；空值保持缺失，不外推。
- 三项达到来源内 E3：项目原始路径映射明确，Eastmoney 公开页面对字段给出明确标签，全部可比留存股票与 F10 发行信息一致且没有反例。没有增加 L1、多日独立样本数、第二报告期或交叉来源映射门槛。
- `field_source_reference.md` `12.9.2` 的“❌ 未用”表示生产流程未消费该字段，不是字段含义未知。它与 `12.8.4.1` 的明确语义标签被聚合器混为同一种状态，制造了 `reference_status_conflict`。该历史使用状态继续保留，但不阻止来源语义定案。