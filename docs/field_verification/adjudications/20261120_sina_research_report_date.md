# 新浪研报日期字段来源契约裁决

复核日期：2026-11-20。对象为独立运行来源 `新浪(研报列表)::date`，即新浪研报列表记录中的日期字段。它与 `新浪(扩展API)` 的财报、资金流等接口同属新浪提供方家族，但运行接口不同，分别保留来源身份。此处判定的是研报发布日期，不是财报报告期、网页抓取时间或来源响应的 `as_of_date`；不建立跨来源映射。

## 官方字段定义与项目路径

新浪财经[最新滚动研报列表](https://vip.stock.finance.sina.com.cn/q/go.php/vReport_List/kind/lastest/index.phtml)将列依次标为“序号、标题、报告类型、发布日期、机构、研究员”。新浪财经[行业研报列表](https://vip.stock.finance.sina.com.cn/q/go.php/vReport_List/kind/industry/index.phtml)展示同一列定义。项目的 [`_research_sina.py`](../../../stock_common/sc_datasource/_research_sina.py) 请求官方 `kind=lastest` 或 `kind=search` 页面；`_SINA_REPORT_ROW` 按该列顺序解析，第四个单元格 `day` 经 `normalize_compact_date()` 转成 ISO 日期并写入返回记录的 `date`。采集器 [`capture_context_collectors.py`](../../../scripts/capture_context_collectors.py) 保留市场最新列表与抽样个股列表，分别位于 `market_latest[].date` 和 `stocks[code][].date`。

项目将运行别名 `research_sina` 单独登记为 `新浪(研报列表)`，不重映射到 `新浪(扩展API)` 的 `sina_extended`。因此 `date` 的确切含义是该研报在新浪列表登记的发布日期。它不是报告所述财报期末日、公告日的自动替代项，也不代表这次接口响应的更新日期。用户需要对齐研报内容的业务事件日时，仍应核对报告正文。

## 保留样本

使用数据日为 2026-11-19、采集日为 2026-11-20 的现有归档 `raw_research_sina.json`。市场最新列表与 5 个抽样个股列表合计 233 条记录，报告 ID 均唯一，日期均可解析，包含 101 个不同发布日期。该批是一次接口采集中的多条研报记录，不按 233 个独立日期样本计数，也不把目录数据日或采集日当作研报日期。

- 原始归档 SHA-256：`fdfbd5319408ab2e8bef5e668ac35ec685f7b7cb6bc8c36b1883ca1c613c178a`
- 逐条样本 CSV：[`research/20261120_sina_research_publish_date_samples.csv`](../research/20261120_sina_research_publish_date_samples.csv)，规范 LF SHA-256：`3fdae728671c9bf487d92efb00dcbfa03b62786977f21724b0d25b3d6e1f1486`
- 来源实际响应 `as_of_date`：未提供；此缺口不影响官方列名对研报发布日期的释义，但不能据此宣称列表快照的新鲜度。

## 裁决范围

将精确路径 `新浪(研报列表)::date` 定为研报发布日期，规范名 `sina_research_report_publication_date`，单位为日期。只确认新浪研报列表返回记录中的此路径；不将 `新浪(扩展API)`、新浪行情或其它来源的 `date` 字段及网页采集日期并入该身份。
