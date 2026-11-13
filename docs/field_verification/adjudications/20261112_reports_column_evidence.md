# 东方财富 `reports::column` 来源内字段释义定案证据（2026-11-12）

## 裁决范围

将精确路径 `reports::column` 定义为东方财富个股研报记录的栏目代码。保留样本中观测到 11 个代码；仅确认 `002004003` 对应新股研报栏目。其余已见代码的细分类别和完整代码表不在本次结论范围内，不按代码形态或标题猜测。

## 项目采集路径与东财接口

`stock_common/sc_datasource/_financials.py::get_reports()` 调用东财 `https://reportapi.eastmoney.com/report/list`，参数 `qType=0` 查询个股研报，并直接将响应行加入结果；`scripts/capture_context_collectors.py::collect_reports()` 把这些原始行保存至日期目录的 `raw_reports.json`。`column` 是响应行的原始键，采集过程不改名或重算。

东方财富个股研报页面把“个股研报”与“新股研报”分别列为研究报告栏目：[个股研报页面](https://data.eastmoney.com/report/stock/)。其官方前端脚本 `https://data.eastmoney.com/newstatic/js/report/stock.js` 配置个股研报请求 `report/list`、`qType=0`；官方研报接口返回记录中包含 `column`。2026-11-12 对该页面实际使用的 `report/list2` 官方接口作单次只读核验，返回的研报行同样保留 `column`、`infoCode`、`title`、`stockCode` 和 `reportType`。

## 保留样本

仅读取 2026-10-15 起的 16 份 `raw_reports.json`。6,051 条抓取观察按 `infoCode` 去重为 443 条不同研报记录，覆盖 15 只股票；443 条记录均有 `column`，包含 11 个不同代码。同一 `infoCode` 在不同快照中的 `column` 均稳定，未发现采集错误或代码漂移。逐条样本见 [`20261112_reports_column_samples.csv`](20261112_reports_column_samples.csv)，来源文件路径及 SHA-256 见 [`20261112_reports_indv_is_new_raw_manifest.csv`](20261112_reports_indv_is_new_raw_manifest.csv)。

其中 430 条记录的 `indvIsNew` 非空：424 条 `001` 分布于 10 个其他已观察栏目代码；6 条 `002` 全部属于 `column=002004003`，分布于 3 只股票，零反例。另 13 条标记为空，不用它们推断栏目标签。相同 `infoCode` 的栏目码在 16 份快照间没有变化，重复抓取不计作独立报告样本。

东方财富官方页面提供独立的“新股研报”栏目；保留样本中的云从科技研报 `AP202204291562364108` 同时记录 `column=002004003`、`indvIsNew=002`。东财详情页标题为“新股专题覆盖：云从科技（2022年第43期）”，正文明确标示云从科技（688327）：[研报详情](https://data.eastmoney.com/report/info/AP202204291562364108.html)。`indvIsNew` 与该栏目关系已由本目录中的 [`20261112_reports_indv_is_new_evidence.md`](20261112_reports_indv_is_new_evidence.md) 独立按完整留存样本和东财正反例定案。

## 结论与边界

原始路径、东财个股研报接口记录和公开栏目页相互对应；全部可比较的非空标记记录均支持 `002004003` 为新股研报栏目，零反例。因此将 `reports::column` 定案为东财个股研报栏目代码，并只登记这一项已验证代码释义。不要求跨源 L1、额外采集日或完整枚举表。其他 10 个已见代码仅确认其为栏目代码，细分类别继续留白；空 `indvIsNew` 也继续保留缺失语义。

## 文件校验

- 逐报告样本 CSV SHA-256：`2ee65b29a589e62382ce98db03c624fae941a4b7db2570707cbf6a3ab6bbf6a2`
- 原始文件清单 SHA-256：见 [`20261112_reports_indv_is_new_raw_manifest.csv`](20261112_reports_indv_is_new_raw_manifest.csv) 及其既有证据记录。
