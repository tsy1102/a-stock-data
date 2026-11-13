# 东财 `reports::indvIsNew` 来源内释义定案证据（2026-11-12）

## 裁决范围

将精确路径 `reports::indvIsNew` 定义为东财个股研报的新股研报栏目标记。保留样本中 `002` 对应新股研报栏目，`001` 对应其他个股研报栏目；空值仍视为缺失，不推断未观察到的其他代码。本结论不建立跨源映射，也不声称存在已公开的东财 API 字段字典。

## 项目采集路径

`stock_common/sc_datasource/_financials.py::get_reports()` 请求东财 `https://reportapi.eastmoney.com/report/list`，以 `qType=0` 读取个股研报，并将接口行直接加入返回列表；`scripts/capture_context_collectors.py::collect_reports()` 将这些原始行写入 `raw_reports.json`。`indvIsNew` 和 `column` 都在同一原始记录中，没有在上述路径中被改名或重算。

## 保留样本全量核对

按 AGENTS.md 的保留边界，只读 2026-10-15 至 2026-11-10 的 16 份日期化 `raw_reports.json`，未读更早 raw、ZHB 压缩包或解析缓存。对每个文件中的研报记录按 `infoCode` 去重，避免把重复采集当成独立报告：

- 原始观察 6,051 条；443 个不同 `infoCode`，覆盖 15 只含非空标记的股票。
- 430 个不同报告 ID 的 `indvIsNew` 为非空：`001` 有 424 个，`002` 有 6 个。6 个 `002` 分布于 3 只股票。
- 所有 6 个 `002` 报告均在同条记录中带有 `column=002004003`；424 个 `001` 报告均未使用该栏目码。430/430 可比较报告相符，零反例。
- 另有 13 个不同报告 ID 的 `indvIsNew` 为空，均排除比较并保持缺失语义。16 份 raw 快照中，同一 `infoCode` 的标记值和栏目码没有发生变化。

逐报告样本见 [`20261112_reports_indv_is_new_samples.csv`](20261112_reports_indv_is_new_samples.csv)：SHA-256 `44c32beaf29756cdbcaac8254f508c6d73ca8cdd0bd487e70f7a88f2613af931`。16 份源文件路径、长度和 SHA-256 见 [`20261112_reports_indv_is_new_raw_manifest.csv`](20261112_reports_indv_is_new_raw_manifest.csv)：SHA-256 `a15bf1af0940074a13662e67962743918e801f228f51202d4e93466f0b9f4c5c`。

## 东方财富官网核对

东方财富将“新股研报”作为独立的研报栏目：[新股研报页面](https://data.eastmoney.com/report/newstock.jshtml)；[个股研报页面](https://data.eastmoney.com/report/stock/)则列出一般个股研报。原始记录中的 6 个 `002` 均属于 `column=002004003`，与该新股栏目对应。

可逐条复核的正、反例来自同一只股票云从科技（688327）：

- `AP202204291562364108` 在保留 raw 中为 `indvIsNew=002`、`column=002004003`；东方财富详情页标题为“新股专题覆盖：云从科技（2022年第43期）”，明确展示股票代码 688327：[研报详情](https://data.eastmoney.com/report/info/AP202204291562364108.html)。
- `AP202605181822392317` 在保留 raw 中为 `indvIsNew=001`、栏目码不为 `002004003`；东方财富详情页展示常规的“经营质量好转，围绕AI重塑产品”研报及股票代码 688327：[研报详情](https://data.eastmoney.com/report/zw_stock.jshtml?encodeUrl=tI3AI4wMjmLQAmSmXTMCq5YKttnF7dBiyeMKuZolBAw%3D)。

## 结论与边界

同条原始记录的标记和栏目码在完整保留样本中稳定一致；东方财富公开栏目及同股正、反例说明 `002` 表示新股研报栏目，`001` 表示其他已观测个股研报栏目。故该精确来源路径达到来源内 E3 定案条件。将不外推的观测范围写入定义，保留空值语义；不要求 L1、额外采集日或固定股票数，也不对未出现的代码作猜测。
