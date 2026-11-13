# 东财 `reports::emRatingValue` 来源内释义定案证据（2026-11-12）

## 裁决范围

将精确路径 `reports::emRatingValue` 解释为东财研报 API 的统一评级数值档位。本证据只确认保留样本中出现的三档：`1=持有`、`2=增持`、`3=买入`；不推断未观察到的其他数值，不建立跨来源映射。

## 项目采集路径与字段身份

`stock_common/sc_datasource/_financials.py::get_reports()` 请求东财公开的 `https://reportapi.eastmoney.com/report/list`，`scripts/capture_context_collectors.py::collect_reports()` 将响应行保留在 `raw_reports.json` 中，未重命名或换算 `emRatingValue`、`emRatingCode`、`emRatingName`。因此本次核验的字段身份是原始 JSON 的完整叶路径 `emRatingValue`，而不是统一层字段或推测的拼音别名。

对应保留原始样本为 `docs/field_verification/20261110/raw_reports.json`，SHA-256：`680F8DA5A5BBF3F5BF50D3C87850AFE2BF9FDA01D9A709FF66230FD1AA8CC5AA`。可复核的逐条评级记录另存于 [`20261112_reports_em_rating_value_samples.csv`](20261112_reports_em_rating_value_samples.csv)，含股票代码、名称、研报 `infoCode`、发布日期、评级代码、评级数值和评级中文名，共 350 条数据行；CSV SHA-256：`e45c3854725113c8fdfe462f5bed9c136ea3d26f01fc11cb5f1ebf654bf04db3`。

## 完整样本核对

对 2026-11-10 保留文件中的 20 只查询股票逐行检查，共 373 条研报记录，其中 12 只股票有非空评级、350 条评级记录；其余 8 只股票本次没有返回研报。评级映射如下：

| `emRatingValue` | `emRatingCode` | `emRatingName` | 样本数 |
|---:|---:|---|---:|
| 1 | `005` | 持有 | 3 |
| 2 | `006` | 增持 | 109 |
| 3 | `007` | 买入 | 238 |

350/350 条非空评级均同时满足上述数值、代码和名称配对，没有反例，也没有同一数值对应多个名称或代码的情况。另有 23 条记录的数值、代码和名称三项同时为空；这些是未评级记录，作为不可比较样本排除，未将空值解释成 0 或新的评级档位。完整范围内共 373 条，纳入比较 350 条，排除 23 条，股票数 12。

## 东财公开接口与研报页面抽查

直接读取东财公开 `report/list` 响应时，接口将数值、代码和中文名作为三个并列字段返回。以下两只股票的实时接口记录与东财研报详情页相互对应：

| 股票 | `infoCode` | API 返回 | 东财研报详情 |
|---|---|---|---|
| 贵州茅台（600519） | `AP202611101831583829` | `emRatingCode=007`、`emRatingValue=3`、`emRatingName=买入`，发布日期 2026-11-10 | [东财研报详情](https://data.eastmoney.com/report/info/AP202611101831583829.html) |
| 农业银行（601288） | `AP202611011831293587` | `emRatingCode=006`、`emRatingValue=2`、`emRatingName=增持`，发布日期 2026-11-01 | [东财研报详情](https://data.eastmoney.com/report/info/AP202611011831293587.html) |

可直接复核的接口请求：[贵州茅台 `report/list`](https://reportapi.eastmoney.com/report/list?pageSize=50&industry=%2A&rating=%2A&beginTime=2000-01-01&endTime=2030-01-01&pageNo=1&code=600519&qType=0)；[农业银行 `report/list`](https://reportapi.eastmoney.com/report/list?pageSize=50&industry=%2A&rating=%2A&beginTime=2000-01-01&endTime=2030-01-01&pageNo=1&code=601288&qType=0)。详情页的股票、研报标题、机构、作者和发布日期与接口 `infoCode` 对应；报告正文也给出与该研报相符的评级建议及预测内容。此处用公开接口的并列字段标签确认评级码值，并用详情页确认记录对应的公开研报，不将正文中的财务预测字段混同为评级字段。

## 结论及边界

本来源、精确路径和上述已观测取值的释义证据已经闭合：项目适配器原样保留接口字段；完整保留样本 350/350 一致且零反例；东财公开接口给出明确的值、代码和名称关系；两条公开详情页确认接口记录对应实际研报。因此足以将该字段从因参考材料标签冲突而形成的 `conflict` 定为来源内 `verified`。参考章节中的“未用”是字段使用状态，不能推翻接口字段的语义；冲突快照会由 E3 裁决记录保留。

本结论不声称已证明完整评级量表，不推广至其他来源的 `rating` 字段，也不推断 `emRatingCode` 的所有可能值。报告预测类字段（包括 `predictThisYear*`）不在本次裁决范围。
